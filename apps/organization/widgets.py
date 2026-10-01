from djangospice_widget.widget import Widget
from djangospice_widget.decorators import widget
from djangospice_framework.web.templates import get_template_name
from apps.organization.apps import namespace


@widget
class ChatWidget(Widget):
    """
    Reusable server-rendered chat widget.

    The widget is responsible for presenting and interacting with a
    conversation. Conversation storage and message generation can be
    provided by subclasses.
    """

    template_name = "organization/widgets/chat.html"

    message_parameter = "message"

    placeholder = "Type a message..."
    submit_label = "Send"

    empty_message = "Start a conversation."

    def get_messages(self):
        """
        Return the messages displayed by the widget.

        Override this method to connect the widget to a conversation
        or message model.
        """
        return ()

    def get_conversation(self):
        """
        Return the current conversation.

        Override this method when the widget is backed by a
        conversation model.
        """
        return None

    def get_context(self):
        context = super().get_context()

        context.update(
            conversation=self.get_conversation(),
            messages=self.get_messages(),
            placeholder=self.placeholder,
            submit_label=self.submit_label,
            message_parameter=self.message_parameter,
            empty_message=self.empty_message,
        )

        return context

    def send_message(self):
        """
        Handle a submitted message.

        Override this method to persist the message and/or invoke
        an AI/chat service.
        """
        message = self.request_value(
            self.message_parameter,
        )

        if not message:
            return

        self.create_message(message)

    def create_message(self, message: str):
        """
        Create or process a submitted message.

        Override in an application-specific implementation.
        """
        return message

    def post(self):
        self.send_message()

        return self.response()
