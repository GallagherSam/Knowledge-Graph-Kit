# app/test.py

from fastmcp import FastMCP

# 1. Instantiate the server
mcp = FastMCP(
    name="Test Server",
    instructions="A minimal server for testing connectivity."
)

# 2. Create a simple tool
@mcp.tool
def ping() -> str:
    """A simple tool that returns 'pong'. Used to verify the server is running and responsive."""
    return "pong"

# 3. Make it runnable (optional, but good practice)
if __name__ == "__main__":
    print("Starting minimal test server...")
    mcp.run()
