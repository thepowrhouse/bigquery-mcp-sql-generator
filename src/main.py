#!/usr/bin/env python3
"""
Main entry point for the BigQuery MCP application
"""

import os
import sys
import argparse
import subprocess

# Add the parent directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def start_mcp_server():
    """Start the MCP server"""
    print("Starting BigQuery MCP Server...")
    # Import and run the MCP server directly
    from src.mcp_server import mcp
    from src.config import MCP_HOST, MCP_PORT
    print(f"Starting BigQuery MCP Server on http://{MCP_HOST}:{MCP_PORT}")
    mcp.run(transport='streamable-http', host=MCP_HOST, port=MCP_PORT)

def start_streamlit_ui():
    """Start the Streamlit UI"""
    print("Starting Streamlit UI...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/streamlit_ui.py"])

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="BigQuery MCP Application")
    parser.add_argument(
        "command", 
        choices=["server", "ui", "all"], 
        help="Command to run: server (MCP server), ui (Streamlit UI), all (both)"
    )
    
    args = parser.parse_args()
    
    if args.command == "server":
        start_mcp_server()
    elif args.command == "ui":
        start_streamlit_ui()
    elif args.command == "all":
        print("Starting both MCP server and Streamlit UI...")
        print("Please run 'python src/main.py ui' in a separate terminal for the UI")
        start_mcp_server()

if __name__ == "__main__":
    main()