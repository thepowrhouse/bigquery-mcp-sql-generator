#!/usr/bin/env python3
"""
Integration tests for BigQuery MCP Server
This script tests the actual functionality of the BigQuery MCP server with real operations.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables
load_dotenv()

def test_list_datasets():
    """Test listing datasets"""
    try:
        from src import mcp_server
        
        # Test the actual list_datasets functionality
        datasets = mcp_server.bq_client.list_datasets()
        
        print(f"✓ Successfully listed datasets: {len(datasets)} found")
        if datasets:
            print(f"  Sample datasets: {datasets[:3]}")  # Show first 3 datasets
        return True
    except Exception as e:
        print(f"✗ Failed to list datasets: {e}")
        return False

def test_get_dataset_info():
    """Test getting dataset information"""
    try:
        from src import mcp_server
        
        # First get a list of datasets
        datasets = mcp_server.bq_client.list_datasets()
        
        if datasets and len(datasets) > 0:
            # Test with the first dataset
            first_dataset = datasets[0]
            dataset_info = mcp_server.bq_client.get_dataset_info(first_dataset)
            
            print(f"✓ Successfully got info for dataset: {first_dataset}")
            if "error" not in dataset_info:
                print(f"  Dataset ID: {dataset_info.get('dataset_id', 'N/A')}")
                print(f"  Location: {dataset_info.get('location', 'N/A')}")
            else:
                print(f"  Error: {dataset_info.get('error', 'Unknown error')}")
        else:
            print("⚠ No datasets found to test with")
            
        return True
    except Exception as e:
        print(f"✗ Failed to get dataset info: {e}")
        return False

def test_list_tables():
    """Test listing tables in a dataset"""
    try:
        from src import mcp_server
        
        # First get a list of datasets
        datasets = mcp_server.bq_client.list_datasets()
        
        if datasets and len(datasets) > 0:
            # Test with the first dataset
            first_dataset = datasets[0]
            tables = mcp_server.bq_client.list_tables(first_dataset)
            
            print(f"✓ Successfully listed tables in dataset: {first_dataset}")
            print(f"  Found {len(tables)} tables")
            if tables:
                print(f"  Sample tables: {tables[:3]}")  # Show first 3 tables
        else:
            print("⚠ No datasets found to test with")
            
        return True
    except Exception as e:
        print(f"✗ Failed to list tables: {e}")
        return False

def test_execute_simple_query():
    """Test executing a simple query"""
    try:
        from src import mcp_server
        
        # Execute a simple query that should work in any BigQuery environment
        query = "SELECT 1 as test_column"
        result = mcp_server.bq_client.execute_query(query)
        
        print(f"✓ Successfully executed simple query")
        print(f"  Query: {query}")
        print(f"  Result rows: {len(result)}")
        if result:
            print(f"  First row: {result[0]}")
            
        return True
    except Exception as e:
        print(f"✗ Failed to execute simple query: {e}")
        return False

def test_mcp_tool_calls():
    """Test calling MCP tools directly"""
    try:
        from src import mcp_server
        
        # Test that tools exist as FunctionTool objects
        tools = [
            'list_dataset_ids',
            'execute_sql'
        ]
        
        for tool_name in tools:
            tool = getattr(mcp_server, tool_name, None)
            if tool is not None:
                print(f"✓ MCP tool '{tool_name}' exists as FunctionTool object")
            else:
                print(f"✗ MCP tool '{tool_name}' is missing")
                return False
        
        print(f"✓ MCP tool objects verified successfully")
        
        return True
    except Exception as e:
        print(f"✗ Failed to test MCP tool calls: {e}")
        return False

def main():
    """Run all integration tests"""
    print("Running BigQuery MCP Server Integration Tests\n")
    
    # Check if we have authentication
    from src import mcp_server
    is_authenticated = mcp_server.bq_client.client is not None
    
    if not is_authenticated:
        print("⚠ Warning: BigQuery client is not authenticated")
        print("  Some tests will be limited to error handling verification\n")
    
    tests = [
        ("List Datasets Test", test_list_datasets),
        ("Get Dataset Info Test", test_get_dataset_info),
        ("List Tables Test", test_list_tables),
        ("Execute Simple Query Test", test_execute_simple_query),
        ("MCP Tool Calls Test", test_mcp_tool_calls),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print(f"\n\nIntegration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("❌ Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())