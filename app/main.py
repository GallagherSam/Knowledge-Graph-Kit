from fastmcp import FastMCP
import argparse

from app.config import load_config, config
from app.tools.tool import Tools


# This is the central FastMCP application instance.
mcp = FastMCP(
    name="Knowledge Graph Kit",
    instructions="You are an agent managing a knowledge graph. Use the available tools to create, retrieve, update, and connect nodes (tasks, notes, people, projects) to fulfill user requests."
)

tools = Tools(mcp)

def main():
    """
    Main function to run the MCP server.
    """
    parser = argparse.ArgumentParser(description="Run the Notes Graph MCP server.")
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to the configuration file.'
    )
    args = parser.parse_args()

    # Load the configuration
    load_config(args.config)

    # Get host and port from config
    host = config["HOST"]
    port = config["PORT"]

    # Run the MCP server
    mcp.run(transport='http', host=host, port=port)

if __name__ == "__main__":
    main()
