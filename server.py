#!/usr/bin/env python3
"""
MCP Server for Indra Variants API
"""

import asyncio
import json
import os
from typing import Any
import requests

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# HTTP/SSE transport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import uvicorn

# Create server instance
server = Server("indra-variants")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    """
    return [
        Tool(
            name="get_variants_for_gene",
            description="Get DBSNP variants associated with a gene using the Indra Discovery API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "gene": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tuple [namespace, id], e.g. ['HGNC', '9896']"
                    }
                },
                "required": ["gene"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handle tool calls.
    """
    if name == "get_variants_for_gene":
        gene = arguments.get("gene", [])
        
        if not gene:
            return [TextContent(type="text", text="Error: gene parameter is required")]
        
        try:
            # Call Indra API
            url = "https://discovery.indra.bio/api/get_variants_for_gene"
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            response = requests.post(url, json={"gene": gene}, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"Indra API returned {response.status_code}: {response.text}"
                return [TextContent(type="text", text=error_msg)]
            
            result = response.json()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            error_msg = f"Error calling Indra API: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main_stdio():
    # Run the server using stdio (useful locally)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


# --- HTTP/SSE app for Railway ---
sse_transport = SseServerTransport("/messages/")


async def handle_sse(request):
    # Establish SSE connection and run the MCP server over it
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
    # Return empty response after SSE finishes to satisfy Starlette
    return Response()


async def healthcheck(request):
    return Response("ok", media_type="text/plain")


starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Route("/health", endpoint=healthcheck, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
)

if __name__ == "__main__":
    # If running on Railway, expose HTTP server on $PORT; else use stdio
    port = os.environ.get("PORT")
    if port:
        uvicorn.run(starlette_app, host="0.0.0.0", port=int(port))
    else:
        asyncio.run(main_stdio())
