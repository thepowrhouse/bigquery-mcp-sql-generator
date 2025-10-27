#!/usr/bin/env python3
"""
Planning Agent that orchestrates the SQL Agent and adds intelligent reasoning
"""

import os
import sys
import asyncio
import json
import re
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load configuration
from src.config import (
    ADK_MODEL,
    LLM_PROVIDER,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID
)

# Import the SQL agent (current ADK agent)
from src.adk_agent import run_agent as run_sql_agent

# Import LLM manager
from src.llm_manager import generate_llm_response

async def run_planning_agent(user_query: str):
    """
    Planning Agent that orchestrates the SQL Agent and adds intelligent reasoning
    
    Args:
        user_query (str): The user's natural language query
        
    Returns:
        str: Enhanced response with planning and reasoning
    """
    print(f"Planning Agent received query: {user_query}")
    
    # First, let's determine if this query needs complex reasoning or can be handled directly
    needs_complex_reasoning = _needs_complex_reasoning(user_query)
    
    if needs_complex_reasoning:
        # For complex queries, we'll break them down and add reasoning
        return await _handle_complex_query(user_query)
    else:
        # For simple queries, just relay the SQL agent's response
        return await _handle_simple_query(user_query)

def _needs_complex_reasoning(query: str) -> bool:
    """
    Determine if a query needs complex reasoning based on keywords
    Uses word boundary matching to avoid false positives
    """
    complex_keywords = [
        'analyze', 'analysis', 'compare', 'trend', 'pattern', 'insight', 
        'relationship', 'correlation', 'forecast', 'predict', 'summary',
        'recommend', 'suggestion', 'why', 'how', 'explain', 'understand'
    ]
    
    query_lower = query.lower()
    # Use word boundary matching to avoid false positives
    for keyword in complex_keywords:
        # Create a regex pattern with word boundaries
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, query_lower):
            return True
    
    return False

async def _handle_simple_query(user_query: str) -> str:
    """
    Handle simple queries by directly using the SQL agent
    """
    print("Planning Agent: Handling simple query, relaying to SQL agent")
    sql_response = await run_sql_agent(user_query)
    return sql_response

async def _handle_complex_query(user_query: str) -> str:
    """
    Handle complex queries by adding reasoning and planning
    """
    print("Planning Agent: Handling complex query with reasoning")
    
    # First, get the raw data from the SQL agent
    sql_response = await run_sql_agent(user_query)
    
    # Then, enhance it with reasoning if we have an API key available
    if (LLM_PROVIDER == 'gemini' and GOOGLE_API_KEY) or (LLM_PROVIDER == 'openai' and OPENAI_API_KEY):
        enhanced_response = await _add_reasoning(user_query, sql_response)
        return enhanced_response
    else:
        # Without API key, return the SQL response with a note
        note = ""
        if LLM_PROVIDER == 'gemini' and not GOOGLE_API_KEY:
            note = "Note: For detailed analysis and insights, please configure your GOOGLE_API_KEY in the .env file.\n\n"
        elif LLM_PROVIDER == 'openai' and not OPENAI_API_KEY:
            note = "Note: For detailed analysis and insights, please configure your OPENAI_API_KEY in the .env file.\n\n"
        
        return f"{note}{sql_response}"
    
async def _add_reasoning(original_query: str, sql_response: str) -> str:
    """
    Add intelligent reasoning to the SQL response using LLM
    """
    try:
        # Create the reasoning prompt
        reasoning_prompt = f"""
You are an expert data analyst and business intelligence consultant. Your task is to analyze SQL query results and provide insightful, actionable interpretations.

Original User Query: {original_query}

SQL Agent Response: {sql_response}

Please provide a comprehensive analysis that includes:

1. Key Insights: What are the most important findings from the data?
2. Business Implications: What do these findings mean in a business context?
3. Trends or Patterns: Are there any notable trends or patterns in the data?
4. Recommendations: Based on the findings, what actionable recommendations would you suggest?
5. Data Quality Notes: Are there any limitations or considerations about the data?

Format your response in a clear, professional manner suitable for business stakeholders.
Use markdown formatting for better readability with headers, bullet points, and emphasis where appropriate.
"""
        
        print("Planning Agent: Generating reasoning with LLM...")
        # Generate the reasoning response using our LLM manager
        response_text = await generate_llm_response(reasoning_prompt)
        
        # Combine the original SQL response with the enhanced reasoning
        enhanced_response = f"""## Original Response
{sql_response}

## Enhanced Analysis
{response_text}
"""
        return enhanced_response
        
    except Exception as e:
        print(f"Planning Agent: Error in reasoning generation: {e}")
        # Fallback to original response with error note
        return f"""## Original Response
{sql_response}

## Analysis
Unable to generate enhanced analysis due to: {str(e)}

The raw data from the SQL query is shown above.
"""

def _extract_key_metrics(sql_response: str) -> dict:
    """
    Extract key metrics from SQL response for quick analysis
    """
    # This is a simplified extraction - in a real implementation, 
    # you would parse the actual data structure
    metrics = {
        "response_length": len(sql_response),
        "has_error": "error" in sql_response.lower(),
        "has_table": "|" in sql_response,  # Simple markdown table detection
        "row_count": sql_response.count("\n") - 2 if "|" in sql_response else 0
    }
    return metrics

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        response = asyncio.run(run_planning_agent(query))
        print(response)
    else:
        print("Planning Agent")
        print("Usage: python planning_agent.py 'Your question here'")
        print("This agent orchestrates the SQL agent and adds intelligent reasoning")