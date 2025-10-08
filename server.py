#!/usr/bin/env python3
"""
MCP Server for Indra Variants API
"""

import asyncio
import json
import sys
from typing import Any, Sequence
import requests

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    NotificationOptions,
    ExperimentalCapabilities,
)

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

async def main():
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="indra-variants",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities=ExperimentalCapabilities(),
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
