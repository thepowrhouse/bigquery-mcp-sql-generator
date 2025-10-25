import os
import asyncio
from dotenv import load_dotenv
from google.cloud import bigquery
from fastmcp import FastMCP

# Load configuration from centralized config module
from src.config import (
    MCP_HOST,
    MCP_PORT,
    MCP_DEBUG,
    PROJECT_ID,
    DATASET_ID,
    TABLE_ID
)

# Initialize FastMCP server
mcp = FastMCP("BigQuery MCP Server 🚀")

# Initialize BigQuery client
class BigQueryClient:
    def __init__(self):
        self.project_id = PROJECT_ID
        self.default_dataset = DATASET_ID
        self.default_table = TABLE_ID
        self.client = None
        # Only initialize the client when credentials are available
        try:
            self.client = bigquery.Client(project=self.project_id)
        except Exception as e:
            print(f"Warning: BigQuery client not initialized: {e}")
            print("This is expected if you haven't set up authentication yet.")
    
    def list_datasets(self):
        """List all datasets in the project"""
        if not self.client:
            return ["Error: BigQuery client not authenticated"]
        try:
            datasets = list(self.client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def get_dataset_info(self, dataset_id: str):
        """Get information about a specific dataset"""
        if not self.client:
            return {"error": "BigQuery client not authenticated"}
        try:
            dataset_ref = self.client.dataset(dataset_id)
            dataset = self.client.get_dataset(dataset_ref)
            return {
                "dataset_id": dataset.dataset_id,
                "description": dataset.description,
                "location": dataset.location,
                "created": dataset.created.isoformat() if dataset.created else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_tables(self, dataset_id: str):
        """List all tables in a dataset"""
        if not self.client:
            return ["Error: BigQuery client not authenticated"]
        try:
            tables = list(self.client.list_tables(dataset_id))
            return [table.table_id for table in tables]
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def get_table_info(self, dataset_id: str, table_id: str):
        """Get information about a specific table"""
        if not self.client:
            return {"error": "BigQuery client not authenticated"}
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref)
            return {
                "table_id": table.table_id,
                "num_rows": table.num_rows,
                "num_columns": len(table.schema),
                "description": table.description
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_query(self, query: str):
        """Execute a SQL query and return results"""
        if not self.client:
            return [{"error": "BigQuery client not authenticated"}]
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            # Convert results to list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for key, value in row.items():
                    # Handle different data types properly
                    if value is None:
                        row_dict[key] = "NULL"
                    elif isinstance(value, (int, float, bool)):
                        row_dict[key] = value
                    else:
                        row_dict[key] = str(value)
                rows.append(row_dict)
            
            return rows
        except Exception as e:
            return [{"error": str(e)}]

# Initialize BigQuery client
bq_client = BigQueryClient()

@mcp.tool
def list_dataset_ids() -> list:
    """Fetches BigQuery dataset ids present in a GCP project."""
    return bq_client.list_datasets()

@mcp.tool
def get_dataset_info(dataset_id: str) -> dict:
    """Fetches metadata about a BigQuery dataset."""
    return bq_client.get_dataset_info(dataset_id)

@mcp.tool
def list_table_ids(dataset_id: str) -> list:
    """Fetches table ids present in a BigQuery dataset."""
    return bq_client.list_tables(dataset_id)

@mcp.tool
def get_table_info(dataset_id: str, table_id: str) -> dict:
    """Fetches metadata about a BigQuery table."""
    return bq_client.get_table_info(dataset_id, table_id)

@mcp.tool
def execute_sql(query: str) -> list:
    """Runs a SQL query in BigQuery and fetch the result."""
    return bq_client.execute_query(query)

if __name__ == "__main__":
    print(f"Starting BigQuery MCP Server on http://{MCP_HOST}:{MCP_PORT}")
    # Run with Streamable HTTP transport
    mcp.run(transport='streamable-http', host=MCP_HOST, port=MCP_PORT)