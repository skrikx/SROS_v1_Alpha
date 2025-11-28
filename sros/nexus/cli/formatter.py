"""
CLI Output Formatter

Handles formatting of CLI output (text, JSON, tables).
"""
import json
from typing import Any, Dict, List


class Formatter:
    """Output formatter for CLI."""
    
    def __init__(self):
        self.json_mode = False
    
    def output(self, data: Any):
        """Output data in appropriate format."""
        if self.json_mode:
            print(json.dumps(data, indent=2))
        else:
            self._print_text(data)
    
    def _print_text(self, data: Any):
        """Print data as formatted text."""
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print(f"- {item}")
        else:
            print(data)
    
    def success(self, message: str):
        """Print success message."""
        if self.json_mode:
            print(json.dumps({"status": "success", "message": message}))
        else:
            print(f"✓ {message}")
    
    def error(self, message: str):
        """Print error message."""
        if self.json_mode:
            print(json.dumps({"status": "error", "message": message}))
        else:
            print(f"✗ {message}")
    
    def table(self, headers: List[str], rows: List[List[Any]]):
        """Print data as table."""
        if self.json_mode:
            data = [dict(zip(headers, row)) for row in rows]
            print(json.dumps(data, indent=2))
        else:
            # Simple table formatting
            col_widths = [max(len(str(h)), max(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
            
            # Header
            header_row = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
            print(header_row)
            print("-" * len(header_row))
            
            # Rows
            for row in rows:
                print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
