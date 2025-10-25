#!/usr/bin/env python3
"""
Direct test of the analysis functionality
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
    print("Direct Test of Analysis Query")
    print("=" * 50)
    
    # Test the specific query that's not working
    test_query = "can you analyse the indianapi table and explain your understanding of it"
    print(f"Test Query: {test_query}")
    print()
    
    # Run the agent
    try:
        response = await run_agent(test_query)
        print("SUCCESS: Agent Response:")
        print("-" * 30)
        print(response)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())