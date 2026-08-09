from utils.logger import logging
from utils.exception import CustomException

from langchain_mcp_adapters.client import MultiServerMCPClient

import sys
import os 
from dotenv import load_dotenv
from configs.config import api
load_dotenv()

import asyncio

class MCPService:

    def __init__(self):
        self.DB_URL = api.DB_URL
        self.TOOLS = None
        self.EXECUTE_TOOL = None

    async def initialize_mcp(self):

        client = MultiServerMCPClient(
            {
                "postgres": {
                    "command": "postgres-mcp",
                    "args": ["--access-mode=restricted"],
                    "env": {
                        "DATABASE_URI": self.DB_URL
                    },
                    "transport": "stdio",
                }
            }
        )

        self.TOOLS = await client.get_tools()

        for tool in self.TOOLS:
            if "execute" in tool.name.lower():
                self.EXECUTE_TOOL = tool
                break

        if self.EXECUTE_TOOL is None:
            raise RuntimeError("Could not find SQL execution tool")
        
mcp = MCPService()