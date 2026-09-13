from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="A single user question")

    @field_validator("message")
    @classmethod
    def message_must_contain_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must contain non-whitespace text")
        return cleaned


class ChatResponse(BaseModel):
    answer: str
    safety_notice: str
    escalation_required: bool
    blocked: bool
    flags: list[str]
    request_id: str