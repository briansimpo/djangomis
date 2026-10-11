
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(slots=True)
class Message:
    """A single in-memory chat message."""

    role: str
    content: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Message:
        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            created_at=data["created_at"],
        )


@dataclass(slots=True)
class Conversation:
    """
    A temporary conversation.

    This object itself has no database persistence.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_message(self, role: str, content: str) -> Message:
        if role not in {"user", "assistant", "system"}:
            raise ValueError(f"Unsupported message role: {role}")

        message = Message(role=role, content=content)
        self.messages.append(message)
        return message

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "messages": [
                message.to_dict() for message in self.messages
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Conversation:
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            messages=[
                Message.from_dict(item)
                for item in data.get("messages", [])
            ],
        )

    def clear(self) -> None:
        self.messages.clear()
