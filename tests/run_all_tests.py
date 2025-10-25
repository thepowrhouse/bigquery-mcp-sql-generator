#!/usr/bin/env python3
"""
Main test runner for BigQuery MCP Server
This script runs all essential tests for the BigQuery MCP server.
"""

import os
import sys
import subprocess

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

def run_test_script(script_name):
    """Run a test script and return the result"""
    try:
        print(f"\n{'='*60}")
        print(f"Running {script_name}")
        print(f"{'='*60}")
        
        # Run the test script
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run {script_name}: {e}")
        return False

def main():
    """Run all tests"""
    print("Running All BigQuery MCP Server Tests\n")
    
    test_scripts = [
        "test_mcp.py",
        "integration_test.py", 
        "demo_mcp.py",
        "test_mcp_http.py"
    ]
    
    passed = 0
    total = len(test_scripts)
    
    for script in test_scripts:
        try:
            result = run_test_script(script)
            if result:
                passed += 1
                print(f"✅ {script} PASSED")
            else:
                print(f"❌ {script} FAILED")
        except Exception as e:
            print(f"❌ {script} FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} test scripts passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())