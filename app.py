from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
api_key=os.getenv("GEMINI_API_KEY")# Replace with your API key
print("API Key:", api_key)  # Debugging line to check if the API key is being read correctly
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-lite")
 
@app.get("/")
def home():
    return {"message": "Chatbot is running"}


@app.post("/chat/{prompt}")
async def chat(prompt: str):
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}