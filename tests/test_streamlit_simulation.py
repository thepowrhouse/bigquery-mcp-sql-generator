#!/usr/bin/env python3
"""
Test script to simulate what the Streamlit UI does
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
    print("Simulating Streamlit UI interaction")
    print("=" * 40)
    
    # Test query
    test_query = "show me the first 10 rows of the IndianAPI table"
    print(f"Test Query: {test_query}")
    print()
    
    # Run the agent (this is what Streamlit does)
    response = await run_agent(test_query)
    print("Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())