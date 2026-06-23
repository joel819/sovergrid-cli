"""
SoverGrid Dev Runner
Provides local dry-run testing capabilities using Docker.
"""

import os
import subprocess
import sys

from sovergrid.logger import get_logger, Colors
from sovergrid.dockerizer import detect_project_type, generate_dockerfile

log = get_logger(__name__)


def run_local_dev(port: int = 3000):
    """
    Builds the Docker container locally and runs it to simulate
    the exact environment the user will get on Akash.
    """
    cwd = os.getcwd()
    
    log.info(f"{Colors.BOLD}{Colors.CYAN}SoverGrid Local Preview{Colors.RESET}")
    log.info("Preparing local testing environment...\n")

    # Ensure a Dockerfile exists
    dockerfile_path = os.path.join(cwd, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        project_type = detect_project_type(cwd)
        if project_type:
            log.info(f"Detected {project_type}. Generating Dockerfile...")
            generate_dockerfile(cwd, port=port)
        else:
            log.error(
                "No Dockerfile found and could not auto-detect project type.\n"
                "Please run 'sovergrid init' or create a Dockerfile manually."
            )
            return False

    image_name = "sovergrid-local-preview"

    # Build the Docker image
    log.info(f"Building Docker image '{image_name}'...")
    build_cmd = ["docker", "build", "-t", image_name, "."]
    
    try:
        build_process = subprocess.run(build_cmd, capture_output=True, text=True)
        if build_process.returncode != 0:
            log.error("Docker build failed!")
            print(build_process.stderr, file=sys.stderr)
            return False
        log.info(f"{Colors.GREEN}✓ Build successful{Colors.RESET}")
    except FileNotFoundError:
        log.error("Docker is not installed or not running. Please install Docker to use 'sovergrid dev'.")
        return False

    # Run the container
    log.info(f"Starting local container on port {port}...")
    run_cmd = [
        "docker", "run", "--rm", "-p", f"{port}:{port}", "-e", f"PORT={port}", image_name
    ]

    log.info(f"\n{Colors.GREEN}🚀 App running locally!{Colors.RESET}")
    log.info(f"{Colors.BOLD}Preview URL:{Colors.RESET} http://localhost:{port}")
    log.info(f"{Colors.YELLOW}Press Ctrl+C to stop the preview{Colors.RESET}\n")

    try:
        subprocess.run(run_cmd)
    except KeyboardInterrupt:
        log.info(f"\n{Colors.YELLOW}Shutting down local preview...{Colors.RESET}")
    
    return True
