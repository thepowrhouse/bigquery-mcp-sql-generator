#!/usr/bin/env python3
"""
Streamlit UI for interacting with the BigQuery Planning Agent
"""

import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Load environment variables
load_dotenv()

# Import the Planning agent
from src.planning_agent import run_planning_agent

# Load configuration from centralized config module
from src.config import (
    ADK_AGENT_NAME,
    MCP_HOST,
    MCP_PORT,
    STREAMLIT_HOST,
    STREAMLIT_PORT,
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID
)

# Streamlit UI
st.set_page_config(
    page_title=f"BigQuery Analytics Agent",
    page_icon="📊",
    layout="wide"
)

st.title("Chat with your Database")
st.markdown(f"This agent connects to BigQuery data through an MCP server running at `http://{MCP_HOST}:{MCP_PORT}`")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your BigQuery data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add assistant response to chat history
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Run the Planning agent to get the response
        try:
            full_response = asyncio.run(run_planning_agent(prompt))
        except Exception as e:
            full_response = f"Error running agent: {str(e)}"
        
        # Display the response
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown(f"""
    **Agent Name:** Planning Agent
    **MCP Server:** http://{MCP_HOST}:{MCP_PORT}
    **Status:** Connected ✅
    
    ## Capabilities
    - List BigQuery datasets
    - Get dataset information
    - List tables in datasets
    - Get table information
    - Execute SQL queries
    - Enhanced analysis with reasoning
    
    ## How to Use
    Ask questions like:
    - "What datasets do I have?"
    - "Tell me about the {DATASET_ID} dataset"
    - "What tables are in the {DATASET_ID} dataset?"
    - "Show me the first 10 rows of the {TABLE_ID} table"
    - "Analyze the sector distribution in my data"
    - "Compare different industries in my dataset"
    """)
    
    st.divider()
    
    st.markdown("### Configuration")
    st.markdown(f"""
    - **Host:** {STREAMLIT_HOST}
    - **Port:** {STREAMLIT_PORT}
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()