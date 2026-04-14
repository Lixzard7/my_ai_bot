from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
from pathlib import Path

app = FastAPI()
frontend_path = Path(__file__).parent / "frontend" / "index.html"


def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-lite")


model = get_model()


class ChatRequest(BaseModel):
    prompt: str
 
@app.get("/")
def home():
    return HTMLResponse(frontend_path.read_text(encoding="utf-8"))


@app.post("/api/chat")
async def chat_api(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}


@app.post("/chat/{prompt}")
async def chat(prompt: str):
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}