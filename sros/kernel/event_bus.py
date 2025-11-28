import time
import uuid
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class EventEnvelope:
    id: str
    timestamp: float
    source: str
    topic: str
    payload: Any
    tenant: str = "system"

class EventBus:
    """
    Synchronous in-process event bus.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[EventEnvelope], None]]] = {}

    def subscribe(self, topic: str, handler: Callable[[EventEnvelope], None]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def publish(self, source: str, topic: str, payload: Any, tenant: str = "system"):
        event = EventEnvelope(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            source=source,
            topic=topic,
            payload=payload,
            tenant=tenant
        )
        
        # Exact match dispatch
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error handling event {topic}: {e}")
                    
        # Wildcard dispatch (simple implementation)
        # TODO: Implement proper wildcard matching (e.g. kernel.*)
