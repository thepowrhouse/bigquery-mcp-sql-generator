# Dockerizing the BigQuery MCP Server

This document explains how to dockerize and run just the MCP server component of the BigQuery MCP SQL Generator application.

## Docker Files

The following files are located in the docker directory:

1. `Dockerfile.mcp` - Dockerfile for the MCP server
2. `docker-compose.mcp.yml` - Docker Compose file for easy deployment
3. `start_mcp_docker.sh` - Shell script to build and run the container

## Building the Docker Image

To build the Docker image for the MCP server:

```bash
cd docker
docker build -f Dockerfile.mcp -t bigquery-mcp-server .
```

## Running the Container

### Using Docker Run

```bash
cd docker
docker run -p 8000:8000 \
  -e PROJECT_ID=your-project-id \
  -e DATASET_ID=your-dataset-id \
  -e TABLE_ID=your-table-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v /path/to/your/credentials.json:/app/credentials.json:ro \
  bigquery-mcp-server
```

### Using Docker Compose

```bash
cd docker
docker-compose -f docker-compose.mcp.yml up
```

### Using the Shell Script

```bash
cd docker
./start_mcp_docker.sh
```

## Environment Variables

The MCP server requires the following environment variables:

- `PROJECT_ID`: Your Google Cloud Project ID
- `DATASET_ID`: Your BigQuery dataset name
- `TABLE_ID`: Your BigQuery table name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account key file
- `MCP_HOST`: Host for the MCP server (default: 0.0.0.0 for Docker)
- `MCP_PORT`: Port for the MCP server (default: 8000)

## Configuration

To configure the MCP server, you can either:

1. Use environment variables as shown above
2. Create a `.env` file with your configuration
3. Mount a credentials file for Google Cloud authentication

## Accessing the Server

Once running, the MCP server will be available at:
```
http://localhost:8000/mcp
```

## Notes

1. The MCP server uses HTTP streaming protocol with Server-Sent Events
2. The server generates a unique session ID for each connection
3. Make sure your Google Cloud credentials have BigQuery permissions
4. The container exposes port 8000 by default

## Troubleshooting

If you encounter issues:

1. Ensure Docker is running
2. Verify your Google Cloud credentials are properly configured
3. Check that the required environment variables are set
4. Ensure the port 8000 is not already in use