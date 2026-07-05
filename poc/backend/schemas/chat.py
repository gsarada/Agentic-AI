from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    product_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    message_id: int


class ChatHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    product_id: int | None
    created_at: str
