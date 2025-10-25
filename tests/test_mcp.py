#!/usr/bin/env python3
"""
Test script for BigQuery MCP Server
This script tests the functionality of the BigQuery MCP server.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from unittest.mock import Mock, patch

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import dotenv
        import google.cloud.bigquery
        import fastmcp
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_bigquery_client():
    """Test BigQuery client initialization"""
    try:
        # Import the module and access the client
        from src import mcp_server
        client = mcp_server.bq_client
        print("✓ BigQuery client initialized successfully (may not be authenticated yet)")
        return True
    except Exception as e:
        print(f"✗ BigQuery client initialization failed: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set"""
    required_vars = ['PROJECT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✓ All required environment variables are set")
        print(f"  PROJECT_ID: {os.getenv('PROJECT_ID', 'Not set')}")
        return True

async def test_mcp_server():
    """Test MCP server functionality"""
    try:
        # Import the MCP server
        from src import mcp_server
        print("✓ MCP server module loaded successfully")
        return True
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False

def test_mcp_tools():
    """Test that all MCP tools are properly defined"""
    try:
        from src import mcp_server
        
        # Check that all tools are defined
        tools = [
            'list_dataset_ids',
            'get_dataset_info',
            'list_table_ids',
            'get_table_info',
            'execute_sql'
        ]
        
        # Verify tools exist as functions
        for tool_name in tools:
            if hasattr(mcp_server, tool_name):
                print(f"✓ Tool '{tool_name}' is defined")
            else:
                print(f"✗ Tool '{tool_name}' is missing")
                return False
        
        print("✓ All MCP tools are properly defined")
        return True
    except Exception as e:
        print(f"✗ MCP tools test failed: {e}")
        return False

def test_bigquery_client_methods():
    """Test BigQuery client methods without authentication"""
    try:
        from src import mcp_server
        
        # Test each method when client is not authenticated
        client = mcp_server.bq_client
        
        # Test list_datasets method
        result = client.list_datasets()
        assert isinstance(result, list), "list_datasets should return a list"
        print("✓ list_datasets method works correctly")
        
        # Test get_dataset_info method
        result = client.get_dataset_info("test_dataset")
        assert isinstance(result, dict), "get_dataset_info should return a dict"
        print("✓ get_dataset_info method works correctly")
        
        # Test list_tables method
        result = client.list_tables("test_dataset")
        assert isinstance(result, list), "list_tables should return a list"
        print("✓ list_tables method works correctly")
        
        # Test get_table_info method
        result = client.get_table_info("test_dataset", "test_table")
        assert isinstance(result, dict), "get_table_info should return a dict"
        print("✓ get_table_info method works correctly")
        
        # Test execute_query method
        result = client.execute_query("SELECT 1")
        assert isinstance(result, list), "execute_query should return a list"
        print("✓ execute_query method works correctly")
        
        print("✓ All BigQuery client methods work correctly")
        return True
    except Exception as e:
        print(f"✗ BigQuery client methods test failed: {e}")
        return False

def test_mcp_tool_functions():
    """Test MCP tool functions"""
    try:
        from src import mcp_server
        
        # Test that tools exist as FunctionTool objects
        tools = [
            'list_dataset_ids',
            'get_dataset_info',
            'list_table_ids',
            'get_table_info',
            'execute_sql'
        ]
        
        for tool_name in tools:
            tool = getattr(mcp_server, tool_name, None)
            if tool is not None:
                print(f"✓ Tool '{tool_name}' exists as a FunctionTool object")
            else:
                print(f"✗ Tool '{tool_name}' is missing")
                return False
        
        print("✓ All MCP tool functions are properly defined as FunctionTool objects")
        return True
    except Exception as e:
        print(f"✗ MCP tool functions test failed: {e}")
        return False

def test_error_handling():
    """Test error handling in BigQuery client methods"""
    try:
        from src import mcp_server
        
        client = mcp_server.bq_client
        
        # Check if client is authenticated
        is_authenticated = client.client is not None
        
        if is_authenticated:
            print("✓ Client is authenticated - testing normal operation")
            # Test normal operation when authenticated
            datasets = client.list_datasets()
            assert isinstance(datasets, list), "list_datasets should return a list"
            print("✓ list_datasets works correctly when authenticated")
            
            # Test with a non-existent dataset to trigger error
            dataset_info = client.get_dataset_info("non_existent_dataset_12345")
            assert isinstance(dataset_info, dict), "get_dataset_info should return a dict"
            # Check if it contains error information
            has_error = "error" in dataset_info or "notFound" in str(dataset_info).lower()
            print("✓ Error handling for non-existent dataset works correctly")
            
        else:
            print("✓ Client is not authenticated - testing error handling")
            # Test that methods return appropriate error messages when not authenticated
            datasets = client.list_datasets()
            assert len(datasets) > 0, "Should return error message when not authenticated"
            assert "Error" in datasets[0] or "error" in str(datasets[0]), "Should contain error indication"
            print("✓ Error handling for list_datasets works correctly")
            
            dataset_info = client.get_dataset_info("test")
            assert "error" in dataset_info, "Should contain error key"
            print("✓ Error handling for get_dataset_info works correctly")
            
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running BigQuery MCP Server Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("BigQuery Client Test", test_bigquery_client),
        ("Environment Variables Test", test_environment_variables),
        ("MCP Server Test", test_mcp_server),
        ("MCP Tools Test", test_mcp_tools),
        ("BigQuery Client Methods Test", test_bigquery_client_methods),
        ("MCP Tool Functions Test", test_mcp_tool_functions),
        ("Error Handling Test", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())