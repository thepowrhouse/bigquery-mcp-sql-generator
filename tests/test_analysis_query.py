#!/usr/bin/env python3
"""
Test script to debug the analysis query
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
    print("Testing Analysis Query")
    print("=" * 40)
    
    # Test query
    test_query = "can you analyse the indianapi table and explain your understanding of it"
    print(f"Test Query: {test_query}")
    print()
    
    # Run the agent
    response = await run_agent(test_query)
    print("Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())