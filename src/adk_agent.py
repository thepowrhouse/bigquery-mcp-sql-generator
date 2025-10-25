#!/usr/bin/env python3
"""
Hybrid ADK Agent that demonstrates LLM-based decision making with BigQuery MCP tools
"""

import os
import sys
import asyncio
import json
import re
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load configuration from centralized config module
from src.config import (
    ADK_MODEL,
    ADK_AGENT_NAME,
    MCP_HOST,
    MCP_PORT,
    GOOGLE_API_KEY,
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID
)

# Import the BigQuery client from our MCP server
from src.mcp_server import bq_client

# Define the tools available to the agent
TOOLS_DESCRIPTION = f"""
Available BigQuery Tools:
1. list_dataset_ids() - Lists all dataset IDs in the project
2. get_dataset_info(dataset_id: str) - Gets information about a specific dataset
3. list_table_ids(dataset_id: str) - Lists all table IDs in a dataset
4. get_table_info(dataset_id: str, table_id: str) - Gets information about a specific table
5. execute_sql(query: str) - Executes a SQL query and returns the results

When generating SQL queries, always use proper BigQuery syntax.
For example, to get the first 10 rows of a table, use: SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` LIMIT 10
Always be specific about which dataset and table you want to query.
"""

# Define the actual tool functions that map to MCP server functions
async def list_dataset_ids():
    """List all dataset IDs in the project"""
    return bq_client.list_datasets()

async def get_dataset_info(dataset_id: str):
    """Get information about a specific dataset"""
    return bq_client.get_dataset_info(dataset_id)

async def list_table_ids(dataset_id: str):
    """List all table IDs in a dataset"""
    return bq_client.list_tables(dataset_id)

async def get_table_info(dataset_id: str, table_id: str):
    """Get information about a specific table"""
    return bq_client.get_table_info(dataset_id, table_id)

async def execute_sql(query: str):
    """Execute a SQL query and return the results"""
    return bq_client.execute_query(query)

def extract_json_from_response(response_text):
    """Extract JSON from response text, handling various formatting issues"""
    # First, try to find JSON between code blocks
    json_match = re.search(r"```(?:json)?\s*({.*?})\s*```", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # If no code blocks, try to find JSON object directly
    json_match = re.search(r"({.*?})\s*$", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Return original text if no JSON found
    return response_text

def format_sql_results_as_table(results):
    """Format SQL results as a markdown table"""
    if not results or not isinstance(results, list):
        return str(results)
    
    # Check if results contain an error
    if len(results) > 0 and isinstance(results[0], dict) and 'error' in results[0]:
        return f"Error: {results[0]['error']}"
    
    # If results is empty, return a message
    if len(results) == 0:
        return "No results found."
    
    # Get column names from the first row
    if not isinstance(results[0], dict):
        return str(results)
    
    columns = list(results[0].keys())
    
    # Create table header
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["---" for _ in columns]) + "|"
    
    # Create table rows
    rows = []
    for row in results:
        if isinstance(row, dict):
            row_values = []
            for col in columns:
                value = row.get(col, "")
                # Handle different data types
                if value is None:
                    row_values.append("NULL")
                elif isinstance(value, (int, float, bool)):
                    row_values.append(str(value))
                else:
                    # Truncate long strings for better display
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:47] + "..."
                    row_values.append(str_value)
            rows.append("| " + " | ".join(row_values) + " |")
    
    # Combine all parts
    table_lines = [header, separator] + rows
    return "\n".join(table_lines)

async def run_agent(prompt: str):
    """Run the agent with a given prompt using the LLM to decide what tools to use"""
    print(f"DEBUG: GOOGLE_API_KEY is set: {bool(GOOGLE_API_KEY)}")
    print(f"DEBUG: GOOGLE_API_KEY value: {GOOGLE_API_KEY[:10] if GOOGLE_API_KEY else 'None'}...")
    
    try:
        # If Google API key is available, use the LLM to decide what tools to use
        if GOOGLE_API_KEY:
            try:
                # Import Google GenAI
                import google.generativeai as genai
                
                # Configure Google GenAI
                genai.configure(api_key=GOOGLE_API_KEY)
                
                # Create the model
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Create the prompt with tool descriptions
                full_prompt = f"""
You are a helpful AI assistant that can analyze data in Google BigQuery and answer questions about it.

You have access to BigQuery tools and can:
1. List datasets in the project (`list_dataset_ids`)
2. Get information about datasets (`get_dataset_info`)
3. List tables in datasets (`list_table_ids`)
4. Get information about tables (`get_table_info`)
5. Execute SQL queries to analyze data (`execute_sql`)

Important context:
- The available dataset is: {DATASET_ID}
- The available table is: {TABLE_ID} (in the {DATASET_ID} dataset)
- This table contains Indian stock market data with columns including ticker, stock names, sectors, industries, and other financial information
- The table has 93 rows and 17 columns

For each user question, decide which tool(s) to use based on what information is needed:
- For questions about what datasets/tables exist, use list_dataset_ids, list_table_ids, etc.
- For questions about the nature, structure, or summary of data, first get table info, then execute appropriate SQL queries
- For questions asking to see sample data, use execute_sql with LIMIT queries
- For analytical questions about stocks, use execute_sql with appropriate WHERE clauses
- For questions about stocks with specific criteria, use execute_sql with filtering conditions

Available schema:
`{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`

User question: {prompt}

CRITICAL INSTRUCTIONS:
1. ALWAYS respond with valid JSON in the exact format specified
2. Think step by step about what information is needed to answer the question
3. For analytical questions, generate appropriate SQL queries that directly answer the user's question
4. For stock-related questions, remember that the {TABLE_ID} table contains stock data
5. Use proper BigQuery syntax with backticks for table names: `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
6. For filtering queries, use appropriate WHERE clauses to get exactly what the user is asking for

Respond ONLY with a JSON object in this format:
{{
  "tool_calls": [
    {{
      "name": "tool_name",
      "arguments": {{"param1": "value1", "param2": "value2"}}
    }}
  ]
}}

If you need multiple tools, include them in the array.
If you don't need any tools, respond with an empty array.

Examples:
- For "What datasets do I have?" -> use list_dataset_ids
- For "What tables are in the {DATASET_ID} dataset?" -> use list_table_ids with dataset_id="{DATASET_ID}"
- For "What is the nature of data in the {TABLE_ID} table?" -> use get_table_info then execute_sql with descriptive queries
- For "Summarize the {TABLE_ID} table" -> use get_table_info then execute_sql with aggregation queries
- For "Show me sample data from {TABLE_ID}" -> use execute_sql with SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` LIMIT 10
- For "Fetch stocks with valid industry" -> use execute_sql with SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` WHERE Industry IS NOT NULL AND Industry != '' LIMIT 10
- For "How many stocks are there?" -> use execute_sql with SELECT COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
- For "What sectors are represented?" -> use execute_sql with SELECT DISTINCT Sector FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` WHERE Sector IS NOT NULL
"""
                
                print("DEBUG: About to call LLM...")
                # Generate the response
                response = await model.generate_content_async(full_prompt)
                print(f"DEBUG: LLM response received: {response}")
                
                # Clean up the response text by removing markdown code block formatting
                response_text = response.text.strip()
                print(f"DEBUG: Raw LLM response text: {response_text}")
                
                # Extract JSON from response
                json_text = extract_json_from_response(response_text)
                json_text = json_text.strip()
                print(f"DEBUG: Extracted JSON text: {json_text}")
                
                # Try to parse the response as JSON
                try:
                    tool_decision = json.loads(json_text)
                    tool_calls = tool_decision.get("tool_calls", [])
                    
                    print(f"DEBUG: Tool calls to execute: {tool_calls}")
                    
                    # Execute the tool calls
                    results = []
                    for tool_call in tool_calls:
                        tool_name = tool_call.get("name")
                        arguments = tool_call.get("arguments", {})
                        
                        print(f"DEBUG: Executing tool: {tool_name} with args: {arguments}")
                        
                        # Call the appropriate tool function
                        if tool_name == "list_dataset_ids":
                            result = await list_dataset_ids()
                        elif tool_name == "get_dataset_info":
                            # Handle the case where LLM might generate extra parameters
                            valid_args = {k: v for k, v in arguments.items() if k in ['dataset_id']}
                            result = await get_dataset_info(**valid_args)
                        elif tool_name == "list_table_ids":
                            result = await list_table_ids(**arguments)
                        elif tool_name == "get_table_info":
                            # Handle the case where LLM might generate extra parameters like project_id
                            valid_args = {k: v for k, v in arguments.items() if k in ['dataset_id', 'table_id']}
                            result = await get_table_info(**valid_args)
                        elif tool_name == "execute_sql":
                            # Handle the case where LLM generates 'sql' or 'sql_query' instead of 'query'
                            if 'sql' in arguments and 'query' not in arguments:
                                arguments['query'] = arguments['sql']
                                del arguments['sql']
                            elif 'sql_query' in arguments and 'query' not in arguments:
                                arguments['query'] = arguments['sql_query']
                                del arguments['sql_query']
                            result = await execute_sql(**arguments)
                        else:
                            result = {"error": f"Unknown tool: {tool_name}"}
                        
                        results.append({"tool": tool_name, "result": result})
                        print(f"DEBUG: Tool result: {result}")
                    
                    # If we have results, format them nicely
                    if results:
                        # Enhanced handling for analytical/summary questions
                        analysis_keywords = ["analyse", "analyze", "analysis", "understand", "summary", "summarize", "nature", "explain", "insight", "provide", "find", "different", "compare", "trend", "pattern"]
                        is_analysis_query = any(keyword in prompt.lower() for keyword in analysis_keywords)
                        
                        if is_analysis_query:
                            # For analytical queries, we want to provide insights, not just raw data
                            response = f"## Analysis Results\n\n"
                            
                            # Process table info if available
                            table_info = None
                            query_results = None
                            
                            for r in results:
                                if r['tool'] == 'get_table_info':
                                    table_info = r['result']
                                    query_results = r['result']  # For table info, use the result directly
                                elif r['tool'] == 'execute_sql':
                                    query_results = r['result']
                            
                            # Provide insights based on the query results
                            if query_results and isinstance(query_results, list) and len(query_results) > 0:
                                # Check if this is a list of dictionaries (successful query result)
                                if isinstance(query_results[0], dict) and 'error' not in query_results[0]:
                                    # Check if this is a sector analysis query
                                    if 'sector' in prompt.lower() and any('Sector' in str(key) for key in query_results[0].keys()):
                                        response += "**Sector Analysis:**\n\n"
                                        response += "This query reveals the different industrial sectors represented in the IndianAPI dataset.\n\n"
                                        
                                        # Show all sectors found
                                        response += f"**Total sectors identified**: {len(query_results)}\n\n"
                                        
                                        response += "**Sector List:**\n"
                                        for i, sector_data in enumerate(query_results[:10], 1):  # Show top 10
                                            sector_name = sector_data.get('Sector', 'Unknown')
                                            response += f"{i}. {sector_name}\n"
                                        
                                        if len(query_results) > 10:
                                            response += f"... and {len(query_results) - 10} more sectors\n\n"
                                        
                                        response += "**Analysis Observations:**\n"
                                        response += "- The dataset covers a diverse range of industrial sectors\n"
                                        response += "- Major sectors include Industrials, Technology, and Basic Materials\n"
                                        response += "- Sector diversity indicates comprehensive market coverage\n\n"
                                        
                                        response += "**Recommended Actions:**\n"
                                        response += "- Analyze sector distribution and representation\n"
                                        response += "- Compare performance across different sectors\n"
                                        response += "- Identify sector-specific investment opportunities\n\n"
                                    else:
                                        # Generic analysis for other queries
                                        response += "**Query Results:**\n\n"
                                        table_output = format_sql_results_as_table(query_results)
                                        response += table_output
                                        response += "\n\n"
                                else:
                                    # Handle error case
                                    response += "Unable to retrieve query results for detailed analysis.\n\n"
                            elif query_results and isinstance(query_results, dict) and 'table_id' in query_results:
                                # Handle table info results
                                response += "**Table Summary:**\n\n"
                                response += f"- **Table Name**: {query_results.get('table_id', 'Unknown')}\n"
                                response += f"- **Number of Rows**: {query_results.get('num_rows', 'Unknown')}\n"
                                response += f"- **Number of Columns**: {query_results.get('num_columns', 'Unknown')}\n\n"
                                
                                response += "**Table Characteristics:**\n"
                                response += "This table contains Indian stock market data with comprehensive financial and technical analysis information.\n\n"
                                
                                response += "**Data Structure:**\n"
                                response += "- Stock identification information (tickers, company names)\n"
                                response += "- Sector and industry classifications\n"
                                response += "- Technical trading indicators and recommendations\n"
                                response += "- Price data and performance metrics\n\n"
                            else:
                                response += "No data found for the requested analysis.\n\n"
                            
                            return response
                            
                            return response
                        else:
                            # Regular formatting for other queries
                            formatted_results = []
                            for r in results:
                                if r['tool'] == 'execute_sql':
                                    # Format SQL results as a table
                                    table_output = format_sql_results_as_table(r['result'])
                                    formatted_results.append(f"{r['tool']}:\n{table_output}")
                                else:
                                    formatted_results.append(f"{r['tool']}: {r['result']}")
                            
                            return f"Based on your question, I used the following tools:\n" + "\n".join(formatted_results)
                    else:
                        return f"I analyzed your question but didn't need to use any tools.\n\nYou asked: '{prompt}'"
                except json.JSONDecodeError as je:
                    # If we can't parse as JSON, return the raw response
                    return f"LLM Response (JSON parsing error): {json_text}\nError: {str(je)}"
            except Exception as e:
                # If there's an error with the LLM, fall back to simple responses
                print(f"DEBUG: Error with LLM: {e}")
                import traceback
                traceback.print_exc()
                pass
        
        # If no Google API key is configured or LLM fails, provide a minimal fallback
        # that encourages using the LLM path
        prompt_lower = prompt.lower()
        
        # Handle common basic queries even without LLM
        if "dataset" in prompt_lower and ("what" in prompt_lower or "list" in prompt_lower or "have" in prompt_lower):
            # List datasets query
            datasets = bq_client.list_datasets()
            return f"Here are your datasets: {', '.join(datasets) if datasets else 'No datasets found'}"
        
        elif ("show" in prompt_lower or "display" in prompt_lower or "get" in prompt_lower) and "indianapi" in prompt_lower and ("row" in prompt_lower or "data" in prompt_lower or "record" in prompt_lower):
            # Execute SQL query to show first 10 rows - this is a common basic query
            query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}` LIMIT 10"
            result = bq_client.execute_query(query)
            table_output = format_sql_results_as_table(result)
            return f"First 10 rows of {TABLE_ID} table:\n{table_output}"
        
        elif "help" in prompt_lower or "what can" in prompt_lower:
            # Provide basic help
            return f"""I'm an AI agent connected to your BigQuery data through an MCP server. 
I can help you explore your data in the {DATASET_ID} dataset, specifically the {TABLE_ID} table.
For best results, please configure your GOOGLE_API_KEY in the .env file to enable full LLM-powered analysis.
Try asking questions like:
- 'What datasets do I have?'
- 'Show me the first 10 rows of data'
- 'How many rows are in my table?'
- 'What stocks have a valid industry?'

You asked: '{prompt}'"""
        
        else:
            # For all other queries, encourage setting up the LLM
            return f"""For more intelligent analysis of your query: '{prompt}', 
please configure your GOOGLE_API_KEY in the .env file. 
This will enable the LLM to understand your question and generate appropriate SQL queries.
Currently, I can help with basic dataset listing. For advanced analysis, LLM configuration is required."""
    except Exception as e:
        return f"Error running agent: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        response = asyncio.run(run_agent(prompt))
        print(response)
    else:
        print(f"BigQuery ADK Agent ({ADK_AGENT_NAME}) using {ADK_MODEL}")
        print(f"Connected to MCP Server at http://{MCP_HOST}:{MCP_PORT}")
        print("Usage: python adk_agent.py 'Your question here'")
        print("For full LLM capabilities, ensure GOOGLE_API_KEY is set in .env")