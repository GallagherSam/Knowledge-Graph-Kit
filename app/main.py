import argparse

from fastmcp import FastMCP

from app.config import load_config
from app.tools.tool import Tools

# This is the central FastMCP application instance.
mcp = FastMCP(
    name="Knowledge Graph Kit",
    instructions=(
        "You are an agent managing a knowledge graph. Use the available tools to create, "
        "retrieve, update, and connect nodes to fulfill user requests."
    ),
)


def main():
    """
    Main function to run the MCP server.
    """
    parser = argparse.ArgumentParser(description="Run the Notes Graph MCP server.")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to the configuration file (optional, uses env vars/defaults otherwise).",
    )
    args = parser.parse_args()

    # Load the configuration (returns immutable AppConfig)
    config = load_config(args.config)

    # Initialize tools with config
    Tools(mcp, config)

    # Run the MCP server
    mcp.run(transport="http", host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
