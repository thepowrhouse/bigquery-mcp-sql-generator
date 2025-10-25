#!/usr/bin/env python3
"""
Demo script for testing BigQuery MCP Server functionality
This script demonstrates how to interact with the MCP server programmatically.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables
load_dotenv()

async def demo_mcp_functionality():
    """Demonstrate MCP server functionality"""
    try:
        print("=== BigQuery MCP Server Demo ===\n")
        
        # Import the server
        from src import mcp_server
        
        print("1. Testing BigQuery Client Methods:")
        print("-" * 40)
        
        # Test list_datasets
        datasets = mcp_server.bq_client.list_datasets()
        print(f"Datasets found: {len(datasets)}")
        if datasets:
            print(f"First dataset: {datasets[0]}")
        
        # Test get_dataset_info with first dataset
        if datasets:
            dataset_info = mcp_server.bq_client.get_dataset_info(datasets[0])
            print(f"\nDataset Info for '{datasets[0]}':")
            for key, value in dataset_info.items():
                print(f"  {key}: {value}")
        
        # Test list_tables with first dataset
        if datasets:
            tables = mcp_server.bq_client.list_tables(datasets[0])
            print(f"\nTables in '{datasets[0]}': {len(tables)}")
            if tables:
                print(f"First table: {tables[0]}")
        
        # Test execute simple query
        print("\n2. Testing SQL Execution:")
        print("-" * 40)
        query_result = mcp_server.bq_client.execute_query("SELECT 1 as demo, 'test' as value")
        print(f"Query executed successfully")
        print(f"Rows returned: {len(query_result)}")
        if query_result:
            print(f"First row: {query_result[0]}")
        
        print("\n3. Testing MCP Tool Objects:")
        print("-" * 40)
        tools = [
            'list_dataset_ids',
            'get_dataset_info', 
            'list_table_ids',
            'get_table_info',
            'execute_sql'
        ]
        
        for tool_name in tools:
            tool = getattr(mcp_server, tool_name, None)
            if tool:
                print(f"✓ Tool '{tool_name}' is available")
                # Show tool metadata if available
                if hasattr(tool, '__name__'):
                    print(f"  Function name: {getattr(tool, '__name__', 'N/A')}")
                if hasattr(tool, '__doc__') and tool.__doc__:
                    print(f"  Description: {tool.__doc__.strip()}")
            else:
                print(f"✗ Tool '{tool_name}' is missing")
        
        print("\n=== Demo Completed Successfully ===")
        return True
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the demo"""
    try:
        result = asyncio.run(demo_mcp_functionality())
        return 0 if result else 1
    except Exception as e:
        print(f"Demo failed to run: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())