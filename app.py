from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
from pathlib import Path
from typing import Dict, List

app = FastAPI(docs_url=None, redoc_url=None)
frontend_path = Path(__file__).parent / "frontend" / "index.html"
MAX_TURNS = 6
chat_sessions: Dict[str, List[dict]] = {}


def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-lite")


model = get_model()


class ChatRequest(BaseModel):
    prompt: str
    session_id: str


def build_context_prompt(history: List[dict], current_prompt: str) -> str:
    lines = [
        "You are a helpful assistant. Continue the conversation using prior context when relevant.",
        "Conversation so far:"
    ]

    for turn in history[-MAX_TURNS:]:
        lines.append(f"User: {turn['user']}")
        lines.append(f"Assistant: {turn['assistant']}")

    lines.append(f"User: {current_prompt}")
    lines.append("Assistant:")
    return "\n".join(lines)


def extract_response_text(response) -> str:
    text = (getattr(response, "text", "") or "").strip()
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = (getattr(part, "text", "") or "").strip()
            if part_text:
                return part_text

    return ""
 
@app.get("/")
def home():
    return HTMLResponse(frontend_path.read_text(encoding="utf-8"))


@app.get("/docs")
def docs_redirect():
    return RedirectResponse(url="/", status_code=307)


@app.post("/api/chat")
async def chat_api(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    session_id = request.session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    history = chat_sessions.setdefault(session_id, [])
    context_prompt = build_context_prompt(history, prompt)

    try:
        response = model.generate_content(context_prompt)
        answer = extract_response_text(response)
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="Model returned an empty response. Please retry your message."
            )
        history.append({"user": prompt, "assistant": answer})
        if len(history) > MAX_TURNS:
            del history[:-MAX_TURNS]
        return {"response": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")


@app.post("/chat/{prompt}")
async def chat(prompt: str):
    try:
        response = model.generate_content(prompt)
        answer = extract_response_text(response)
        if not answer:
            raise HTTPException(
                status_code=502,
                detail="Model returned an empty response. Please retry your message."
            )
        return {"response": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")