#!/usr/bin/env python3
"""
Test script to verify the MCP server is running with HTTP
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# Load environment variables
load_dotenv()

# Get configuration from environment
MCP_HOST = os.getenv('MCP_HOST', 'localhost')
MCP_PORT = int(os.getenv('MCP_PORT', '8000'))

def test_mcp_server():
    """Test if the MCP server is running"""
    try:
        # Try to connect to the MCP server
        url = f"http://{MCP_HOST}:{MCP_PORT}/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ MCP Server is running at http://{MCP_HOST}:{MCP_PORT}")
            return True
        else:
            print(f"✗ MCP Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to MCP Server at http://{MCP_HOST}:{MCP_PORT}")
        print("  Make sure the server is running with: python src/mcp_server.py")
        return False
    except Exception as e:
        print(f"✗ Error testing MCP Server: {e}")
        return False

def test_mcp_tools():
    """Test if the MCP tools are available"""
    try:
        # Try to get the tools list
        url = f"http://{MCP_HOST}:{MCP_PORT}/tools"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print(f"✓ MCP Tools are available: {len(tools)} tools found")
            for tool in tools:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return True
        else:
            print(f"✗ MCP Tools endpoint returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing MCP Tools: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing BigQuery MCP Server (HTTP)\n")
    
    tests = [
        ("MCP Server Connection Test", test_mcp_server),
        ("MCP Tools Availability Test", test_mcp_tools),
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
    
    print(f"\n\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())