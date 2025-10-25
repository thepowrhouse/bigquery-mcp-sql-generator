#!/usr/bin/env python3
"""
Debug script to test the ADK agent directly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables
load_dotenv()

# Import the ADK agent
from src.adk_agent import run_agent

async def main():
    print("Testing ADK Agent Directly")
    print("=" * 40)
    
    # Test query
    test_query = "show me the first 10 rows of the IndianAPI table"
    print(f"Test Query: {test_query}")
    print()
    
    # Run the agent
    try:
        response = await run_agent(test_query)
        print("Response:")
        print(response)
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())