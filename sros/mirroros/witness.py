from .trace_store import TraceStore

class Witness:
    """
    Observes the system and records traces.
    """
    def __init__(self, trace_store):
        self.trace_store = trace_store
        
    def record(self, event_type: str, payload: dict):
        """
        Record an event to the trace store.
        """
        import time
        trace = {
            "timestamp": time.time(),
            "event_type": event_type,
            "payload": payload
        }
        self.trace_store.append(trace)
        
    def log_event(self, envelope):
        """
        Convert envelope to dict and log.
        """
        trace = {
            "id": envelope.id,
            "timestamp": envelope.timestamp,
            "source": envelope.source,
            "topic": envelope.topic,
            "payload": envelope.payload
        }
        self.trace_store.append(trace)
