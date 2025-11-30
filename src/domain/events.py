"""
Domain Events - Base classes for event-driven architecture

⚠️ DEMONSTRATION SYSTEM - NOT FOR PRODUCTION USE
This is an educational demonstration system. See DISCLAIMERS.md for details.

In DDD, Domain Events represent something important that happened in the domain
(Vernon, 2013). They are immutable facts that occurred at a specific point in time.
Events are used to communicate between bounded contexts and trigger workflows
(Hohpe & Woolf, 2003).

DDD Pattern: Domain Events enable loose coupling between bounded contexts and
support event-driven architecture patterns.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DomainEvent(BaseModel, ABC):
    """
    Base class for all domain events.
    
    Domain Events are Value Objects that represent something significant
    that happened in the domain. They are immutable and carry all the
    information needed to understand what occurred.
    
    Key DDD Principles:
    - Immutability: Events cannot be changed after creation
    - Timestamp: Every event knows when it occurred
    - Event ID: Unique identifier for event tracking
    """
    
    event_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this event")
    occurred_at: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")
    event_type: str = Field(description="Type of event (set by subclass)")
    
    class Config:
        frozen = True  # Pydantic frozen=True enforces immutability (DDD Value Object principle)
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    
    def __init__(self, **data):
        # Set event_type to the class name if not provided
        if 'event_type' not in data:
            data['event_type'] = self.__class__.__name__
        super().__init__(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return self.model_dump()


class EventHandler(ABC):
    """
    Abstract base class for event handlers.
    
    In event-driven architecture, handlers respond to domain events.
    This follows the Observer pattern and allows loose coupling between
    event publishers and subscribers.
    """
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle a domain event.
        
        Args:
            event: The domain event to handle
        """
        pass


class EventBus:
    """
    Simple in-memory event bus for domain events.
    
    In a production system, this would be replaced with a message broker
    like RabbitMQ, Kafka, or Redis Streams. This implementation is for
    educational purposes and demonstrates the event-driven pattern.
    
    DDD Pattern: Domain Events are published to notify other parts of the
    system about important domain occurrences without tight coupling.
    """
    
    def __init__(self):
        self._handlers: Dict[str, list[EventHandler]] = {}
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The handler that will process the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all subscribed handlers.
        
        Args:
            event: The domain event to publish
        """
        event_type = event.event_type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler.handle(event)
    
    def clear(self) -> None:
        """Clear all handlers (useful for testing)"""
        self._handlers.clear()


# Global event bus instance (in production, use dependency injection)
event_bus = EventBus()

