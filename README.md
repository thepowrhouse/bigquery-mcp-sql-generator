# BigQuery MCP Server

This project implements a Model Context Protocol (MCP) server for Google BigQuery using Google ADK and FastMCP. It provides tools for AI agents to interact with BigQuery datasets.

## Features

- List BigQuery datasets in a project
- Get metadata about specific datasets
- List tables within a dataset
- Get metadata about specific tables
- Execute SQL queries against BigQuery
- HTTP-based streaming protocol instead of stdio
- Integration with Google ADK agents
- **Intelligent LLM-powered natural language processing** for automatic query generation
- Streamlit UI for natural language interaction

## Prerequisites

- Python 3.8+
- Google Cloud Project with BigQuery API enabled
- Service Account with BigQuery permissions

## Setup

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Copy the example configuration file and customize it for your environment:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file to set your specific configuration values:
   - Set your Google Cloud Project ID
   - Set your BigQuery dataset and table names
   - Set your Google API Key for LLM features (optional but recommended)
   - Configure other settings as needed

## Authentication

The BigQuery MCP server supports multiple authentication methods:

1. **Service Account Key File** (Recommended for production):
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to the path of your key file

2. **Application Default Credentials** (For development):
   - Install and initialize Google Cloud SDK
   - Run `gcloud auth application-default login`

3. **Workload Identity Federation** (For GCP environments):
   - Configure workload identity federation in Google Cloud

## Security

This project implements several security measures to protect sensitive information:

1. **Environment Variables**: All sensitive configuration is stored in environment variables rather than hardcoded
2. **Git Ignore**: Sensitive files like `.env` and Python cache files are excluded from version control
3. **API Key Protection**: The Google API Key is only used locally and never committed to the repository
4. **Credential Management**: Service account keys are referenced via file paths and not stored in the codebase

**Important**: Never commit sensitive files like `.env` containing API keys or credentials to version control. Always use the `.env.example` template instead.

## Environment Variables

The following environment variables can be configured in the `.env` file:

- `PROJECT_ID`: Your Google Cloud Project ID (default: vertical-hook-453217-j9)
- `DATASET_ID`: Your BigQuery dataset name (default: IndianAPI)
- `TABLE_ID`: Your BigQuery table name (default: IndianAPI)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file (optional)
- `REGION`: Google Cloud region (default: us-central1)
- `MCP_HOST`: MCP server host (default: localhost)
- `MCP_PORT`: MCP server port (default: 8000)
- `MCP_DEBUG`: Enable debug mode (default: False)
- `ADK_MODEL`: ADK agent model (default: gemini-2.5-flash)
- `ADK_AGENT_NAME`: ADK agent name (default: bigquery_analytics_agent)
- `STREAMLIT_HOST`: Streamlit UI host (default: localhost)
- `STREAMLIT_PORT`: Streamlit UI port (default: 8501)
- `GOOGLE_API_KEY`: Google API Key for LLM features (required for advanced AI capabilities)

## Usage

### Starting the MCP Server

Start the MCP server:
```bash
python src/main.py server
```

The server will start and listen for HTTP connections on `http://localhost:8000`.

### Running the ADK Agent

Run the ADK agent that connects to the MCP server:
```bash
python src/adk_agent.py "Your question here"
```

**Note**: For full LLM-powered capabilities, configure your `GOOGLE_API_KEY` in the `.env` file. 
Without this key, the agent will only support basic functionality. With the API key configured,
the LLM will automatically determine what tools to use and generate appropriate SQL queries
based on your natural language questions.

### Starting the Streamlit UI

Start the Streamlit UI for natural language interaction:
```bash
python src/main.py ui
```

The UI will be available at `http://localhost:8501`.

### Starting All Components

To start all components at once, use the startup script:
```bash
./start_system.sh
```

This will start the MCP server in the background and the Streamlit UI in the foreground.

Note: You can also start components individually:
```bash
python src/main.py server  # Start MCP server
python src/main.py ui      # Start Streamlit UI
```

## Testing

The project includes comprehensive testing capabilities organized in the `tests/` directory:

1. **Unit Tests** (`tests/test_mcp.py`): Tests all components individually
   - Import verification
   - Environment variable validation
   - BigQuery client initialization
   - MCP tool definitions
   - Error handling
   - FastMCP integration

2. **Integration Tests** (`tests/integration_test.py`): Tests actual BigQuery operations
   - Dataset listing
   - Dataset information retrieval
   - Table listing
   - SQL query execution
   - MCP tool verification

3. **Demo Script** (`tests/demo_mcp.py`): Demonstrates functionality with detailed output
   - Complete workflow demonstration
   - Detailed method output
   - Tool verification

4. **HTTP Tests** (`tests/test_mcp_http.py`): Tests HTTP-based MCP server
   - Server connectivity
   - Tool availability

Run all tests:
```bash
python tests/run_all_tests.py
```

Run individual test suites:
```bash
python tests/test_mcp.py
python tests/integration_test.py
python tests/demo_mcp.py
python tests/test_mcp_http.py
```

## Tools Provided

The MCP server exposes the following tools:

1. `list_dataset_ids`: Lists all BigQuery datasets in the project
2. `get_dataset_info`: Gets metadata about a specific dataset
3. `list_table_ids`: Lists all tables in a dataset
4. `get_table_info`: Gets metadata about a specific table
5. `execute_sql`: Executes a SQL query against BigQuery

## Integration with ADK Agents

To use this MCP server with Google ADK agents:

1. Start the MCP server in one terminal
2. In your ADK agent, add the MCPToolset to your agent's tools:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Add to your agent's tools
MCPToolset(
    connection_params=SseConnectionParams(
        url='http://localhost:8000'
    )
)
```

## Development

To modify the server:

1. Edit files in the `src/` directory to add new tools or modify existing ones
2. Run tests: `python tests/run_all_tests.py`
3. Start the server: `python src/main.py server`