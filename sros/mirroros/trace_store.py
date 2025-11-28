from typing import List, Dict, Any
import json
import os
import time

class TraceStore:
    """
    Stores execution traces.
    """
    def __init__(self, storage_path: str = "./data/traces"):
        self.storage_path = storage_path
        self.traces = []  # In-memory cache for test harness
        
        # Create directory if it's a file path
        if storage_path.endswith('.jsonl'):
            dir_path = os.path.dirname(storage_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
        elif not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)

    def append(self, trace_event: Dict[str, Any]):
        """
        Append a trace event.
        """
        self.traces.append(trace_event)
        
        # Also write to file if storage_path is a file
        if self.storage_path.endswith('.jsonl'):
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(trace_event) + "\n")
        else:
            # Simple JSONL appending
            filename = f"trace_{int(time.time() // 3600)}.jsonl"
            filepath = os.path.join(self.storage_path, filename)
            
            with open(filepath, "a") as f:
                f.write(json.dumps(trace_event) + "\n")
                
    def load_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Load the most recent traces.
        """
        return self.traces[-count:]
