#!/usr/bin/env python3
"""
Final test to confirm the fix is working
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
    print("Final Test of Fixed Agent")
    print("=" * 40)
    
    # Test the specific query that was failing
    test_query = "can you analyse the indianapi table and explain your understanding of it"
    print(f"Test Query: {test_query}")
    print()
    
    # Run the agent
    try:
        response = await run_agent(test_query)
        print("SUCCESS: Agent is working correctly!")
        print(f"Response length: {len(response)} characters")
        print("First 800 characters of response:")
        print("-" * 40)
        print(response[:800])
        if len(response) > 800:
            print("...")
        print("-" * 40)
        print("Agent fix confirmed!")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())