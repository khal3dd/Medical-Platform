from pydantic import BaseModel, Field
from enums.chat import MessageRole


class ConversationMessage(BaseModel):
    """
    A single message in a conversation history.
    Used internally when passing history to the LLM provider.
    """
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    """
    Incoming request body for the /api/chat endpoint.
    """
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Unique identifier for the conversation session.",
        examples=["user-abc-123"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message to the chatbot.",
        examples=["What foods are good for liver health?"],
    )


class ChatResponse(BaseModel):
    """
    Response body returned from the /api/chat endpoint.
    """
    session_id: str = Field(..., description="Echo of the session ID.")
    reply: str = Field(..., description="The assistant's response.")
    turn_count: int = Field(
        ...,
        description="Number of complete turns (user + assistant pairs) in this session so far.",
    )


class ClearSessionResponse(BaseModel):
    """
    Response body returned after clearing a session's history.
    """
    session_id: str
    cleared: bool
    message: str


class HealthResponse(BaseModel):
    """
    Response body for the /health endpoint.
    """
    status: str
    service: str
