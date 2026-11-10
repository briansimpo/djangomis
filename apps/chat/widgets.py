from __future__ import annotations

from typing import ClassVar

from djangospice.widget import Widget
from djangospice.widget.decorators import widget
from djangospice.utils import get_template_name
from .notifications import FriendRequest
from .conversation import Conversation
from .apps import namespace


@widget
class ChatWidget(Widget):
    """Interactive, session-backed chat widget."""

    template_name: ClassVar[str] = get_template_name("widgets/chat.html", namespace)

    message_parameter: ClassVar[str] = "message"

    placeholder: ClassVar[str] = "Type a message..."
    submit_label: ClassVar[str] = "Send"
    empty_message: ClassVar[str] = "Start a conversation."

    max_message_length: ClassVar[int] = 10_000
    max_messages: ClassVar[int] = 200

    session_key_prefix: ClassVar[str] = "djangospice_chat"


    def get_session_key(self) -> str:
        """Return the session key for this widget instance."""
        widget_id = getattr(self, "id", None) or getattr(
            self, "html_id", None
        )

        if not widget_id:
            widget_id = self.__class__.__name__

        return f"{self.session_key_prefix}:{widget_id}"

    def get_conversation(self) -> Conversation:
        """Load the transient conversation from the current session."""
        if hasattr(self, "_conversation"):
            return self._conversation

        session = self.request.session
        key = self.get_session_key()
        data = session.get(key)

        if data:
            try:
                conversation = Conversation.from_dict(data)
            except (KeyError, TypeError, ValueError):
                conversation = Conversation()
        else:
            conversation = Conversation()

        self._conversation = conversation
        return conversation

    def save_conversation(self) -> None:
        """
        Store serialized state in the session, not in a database.

        Explicit assignment ensures Django notices the session change.
        """
        self.request.session[self.get_session_key()] = (
            self.get_conversation().to_dict()
        )

    def get_messages(self):
        return self.get_conversation().messages

    def create_message(self, message: str):
        """Append a user message to the transient conversation."""
        conversation = self.get_conversation()

        return conversation.add_message(
            role="user",
            content=message,
        )

    def get_assistant_response(self, message: str) -> str:
        """
        Produce an assistant response.

        Override this method to connect an AI model or another service.
        The default implementation makes the widget usable immediately.
        """
        return (
            f"You said: {message}\n\n"
            "This chat is working. Connect an assistant provider "
            "to generate intelligent responses."
        )

    def process_message(self, message: str) -> None:
        """Append the user message and its assistant response."""
        conversation = self.get_conversation()

        self.create_message(message)

        # Keep the transcript within the configured limit.
        while len(conversation.messages) > self.max_messages - 1:
            conversation.messages.pop(0)

        reply = self.get_assistant_response(message)

        if reply and reply.strip():
            conversation.add_message(
                role="assistant",
                content=reply.strip(),
            )

        # Save the latest state after both messages are added.
        self.save_conversation()

    def clear_conversation(self) -> None:
        """Clear the current conversation without database operations."""
        self._conversation = Conversation()
        self.save_conversation()

    def send_message(self) -> None:
        message = self.get_value(self.message_parameter)

        if not isinstance(message, str):
            return

        message = message.strip()

        if not message or len(message) > self.max_message_length:
            return

        self.process_message(message)

    def post(self):
        self.send_message()
        self.user.notify(FriendRequest)
        return self.response()

    def get_context(self):
        context = super().get_context()

        context.update(
            conversation=self.get_conversation(),
            messages=self.get_messages(),
            placeholder=self.placeholder,
            submit_label=self.submit_label,
            message_parameter=self.message_parameter,
            empty_message=self.empty_message,
            max_message_length=self.max_message_length,
        )

        return context
