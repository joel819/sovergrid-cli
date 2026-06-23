import asyncio
import os
from mcp.server.fastmcp import FastMCP
from sovergrid.config import SoverGridConfig, CONFIG_FILENAME
from sovergrid.orchestrator import run_deployment
from sovergrid.cli import DEFAULT_CONFIG, detect_project_type, generate_dockerfile

# Create the MCP Server
mcp = FastMCP(
    "SoverGrid",
    dependencies=["sovergrid", "mcp"]
)

@mcp.tool()
async def sovergrid_init(directory: str) -> str:
    """
    Initialize a new SoverGrid project in the target directory.
    This creates the sovergrid.yaml file and a Dockerfile.
    """
    os.chdir(directory)
    project_name = os.path.basename(directory)

    config_path = os.path.join(directory, CONFIG_FILENAME)
    
    if os.path.exists(config_path):
        return f"Warning: {CONFIG_FILENAME} already exists in {directory}."
        
    # Generate the yaml file
    config_content = DEFAULT_CONFIG.format(app_name=project_name)
    with open(config_path, "w") as f:
        f.write(config_content)
        
    # Attempt to generate a Dockerfile
    project_type = detect_project_type(directory)
    if project_type:
        generate_dockerfile(directory, port=8080)
        return f"Success: Initialized SoverGrid project and generated Dockerfile for {project_type} in {directory}."
        
    return f"Success: Initialized SoverGrid project in {directory}. Please create a Dockerfile manually."

@mcp.tool()
async def sovergrid_deploy(directory: str) -> str:
    """
    Deploy the application in the target directory to the SoverGrid decentralized network.
    Requires a sovergrid.yaml file to exist in the directory.
    """
    os.chdir(directory)
    config_path = os.path.join(directory, CONFIG_FILENAME)
    
    if not os.path.exists(config_path):
        return f"Error: No {CONFIG_FILENAME} found in {directory}. Please run sovergrid_init first."
        
    try:
        cfg = SoverGridConfig.load(config_path)
        result = await run_deployment(cfg)
        
        if result:
            return f"Deployment Successful!\n{result}"
        else:
            return "Deployment Failed. Please check the logs."
    except Exception as e:
        return f"Error during deployment: {str(e)}"

def main():
    """Entry point for the sovergrid-mcp script"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
