from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import openai
import os

# Initialize FastAPI app
app = FastAPI()

# Connect to MongoDB (Ensure MongoDB is running)
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client.chatbot
db_chats = db.chats

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chat request model
class ChatRequest(BaseModel):
    message: str

# Chat response model
class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Call OpenAI GPT-3.5
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.message}]
        )
        response_text = openai_response["choices"][0]["message"]["content"]

        # Store chat in MongoDB (Temporary storage)
        db_chats.insert_one({"user": request.message, "bot": response_text})

        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_chat_history():
    chats = list(db_chats.find({}, {"_id": 0}))  # Exclude MongoDB _id
    return {"history": chats}
