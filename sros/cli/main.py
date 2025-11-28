"""
SROS CLI Entry Point Shim.
Redirects to the actual CLI implementation in sros.nexus.cli.main.
"""
from sros.nexus.cli.main import main as app

if __name__ == "__main__":
    app()
