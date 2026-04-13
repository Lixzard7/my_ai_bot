from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Replace with your API key
genai.configure(api_key="AIzaSyADMvScSAzw2YW_St69QCQl4JarPJSX7Tw")

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