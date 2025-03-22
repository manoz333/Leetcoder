import logging
import inspect
from enum import Enum, auto

class Events(Enum):
    """Enumeration of event types for the event bus."""
    QUESTION_DETECTED = auto()
    RESPONSE_READY = auto()
    RESPONSE_CHUNK = auto()  # New event for streaming response chunks
    SETTINGS_CHANGED = auto()
    TOGGLE_ACTIVE = auto()
    CONTEXT_UPDATED = auto()
    SHUTDOWN = auto()

class EventBus:
    """Simple pub/sub event bus for decoupled communication."""
    def __init__(self):
        self.subscribers = {}
        self.logger = logging.getLogger(__name__)
        
    def subscribe(self, event_type, callback):
        """Subscribe to an event type with a callback."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type, callback):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            
    def publish(self, event_type, data=None):
        """Publish an event with optional data."""
        if event_type not in self.subscribers:
            print(f"DEBUG: Event {event_type.name} published but no subscribers found")
            return
            
        # Log events (except frequent ones to avoid spam)
        if event_type not in [Events.RESPONSE_CHUNK]:
            self.logger.debug(f"Event published: {event_type.name}")
            print(f"DEBUG: Publishing event {event_type.name} with {len(self.subscribers[event_type])} subscribers")
        elif event_type == Events.RESPONSE_CHUNK:
            # Minimal logging for chunks to avoid spam
            print(f"DEBUG: Publishing response chunk, length: {len(data.get('text', '')) if isinstance(data, dict) and 'text' in data else 'unknown'}")
            
        # Call subscribers
        for callback in self.subscribers[event_type]:
            try:
                # Check if callback accepts a parameter
                sig = inspect.signature(callback)
                if len(sig.parameters) > 0:
                    print(f"DEBUG: Calling subscriber {callback.__qualname__} with data")
                    callback(data)
                else:
                    print(f"DEBUG: Calling subscriber {callback.__qualname__} without data")
                    callback()
            except Exception as e:
                self.logger.error(f"Error in event callback: {e}")
                print(f"DEBUG: Error in event callback {callback.__qualname__}: {e}")