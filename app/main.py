from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.llm import LLMError, create_llm_client
from app.safety import EMERGENCY_RESPONSE, SAFETY_NOTICE, assess_message
from app.schemas import ChatRequest, ChatResponse

settings = get_settings()
llm_client = create_llm_client(settings)

app = FastAPI(
    title="LLM Integration Healthcare Chatbot",
    version="0.1.0",
    description="Safety-first educational healthcare conversation API.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env, "provider": settings.llm_provider}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    request_id = str(uuid4())
    assessment = assess_message(request.message)

    if assessment.emergency:
        return ChatResponse(
            answer=EMERGENCY_RESPONSE,
            safety_notice=SAFETY_NOTICE,
            escalation_required=True,
            blocked=True,
            flags=list(assessment.flags),
            request_id=request_id,
        )

    try:
        answer = await llm_client.complete(request.message)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        answer=answer,
        safety_notice=SAFETY_NOTICE,
        escalation_required=False,
        blocked=False,
        flags=list(assessment.flags),
        request_id=request_id,
    )