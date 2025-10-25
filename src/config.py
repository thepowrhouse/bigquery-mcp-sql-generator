#!/usr/bin/env python3
"""
Configuration module for the BigQuery MCP application
Centralizes all environment variable loading and configuration management
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ADK Agent Configuration
ADK_MODEL = os.getenv('ADK_MODEL', 'gemini-2.5-flash')
ADK_AGENT_NAME = os.getenv('ADK_AGENT_NAME', 'bigquery_analytics_agent')

# MCP Server Configuration
MCP_HOST = os.getenv('MCP_HOST', 'localhost')
MCP_PORT = int(os.getenv('MCP_PORT', '8000'))
MCP_DEBUG = os.getenv('MCP_DEBUG', 'False').lower() == 'true'

# Google Cloud Configuration
PROJECT_ID = os.getenv('PROJECT_ID', 'vertical-hook-453217-j9')
DATASET_ID = os.getenv('DATASET_ID', 'IndianAPI')
TABLE_ID = os.getenv('TABLE_ID', 'IndianAPI')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
REGION = os.getenv('REGION', 'us-central1')

# API Keys and Authentication
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Streamlit UI Configuration
STREAMLIT_HOST = os.getenv('STREAMLIT_HOST', 'localhost')
STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', '8501'))

# Configuration validation
def validate_config():
    """Validate that required configuration values are present"""
    required_configs = {
        'PROJECT_ID': PROJECT_ID,
        'DATASET_ID': DATASET_ID,
        'TABLE_ID': TABLE_ID
    }
    
    missing_configs = [key for key, value in required_configs.items() if not value]
    if missing_configs:
        raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
    
    return True

# Validate configuration on import
validate_config()