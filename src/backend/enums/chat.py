from enum import Enum


class MessageRole(str, Enum):
    """
    Represents the role of a message in a conversation.
    Values match the Anthropic messages API role field.
    """
    USER = "user"
    ASSISTANT = "assistant"
