#!/bin/bash

# Script to build and run the MCP server in Docker

# Change to parent directory where the source files are located
cd ..

# Build the Docker image
echo "Building MCP server Docker image..."
docker build -f docker/Dockerfile.mcp -t bigquery-mcp-server .

# Run the container
echo "Starting MCP server container..."
docker run -p 8000:8000 \
  -e PROJECT_ID=${PROJECT_ID:-vertical-hook-453217-j9} \
  -e DATASET_ID=${DATASET_ID:-IndianAPI} \
  -e TABLE_ID=${TABLE_ID:-IndianAPI} \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  --env-file .env \
  bigquery-mcp-server

echo "MCP server is now running at http://localhost:8000/mcp"