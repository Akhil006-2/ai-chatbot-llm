from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from pydantic import BaseModel
from lmstudio import llm  # or appropriate import for your LLM
import httpx

import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

def build_prompt(history, latest_msg):
    prompt = ""
    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        prompt += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
    prompt += f"User: {latest_msg}\nAssistant: "
    print(prompt)
    return prompt

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def stream_generator() -> AsyncGenerator[str, None]:
        try:
            prompt = build_prompt(req.history or [], req.message)

            headers = {"Content-Type": "application/json"}
            payload = {
                "model": "llama-3.2-3b-instruct",  # or whatever your model name is
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": True,
            }

            async with httpx.AsyncClient() as client:
                async with client.stream("POST", "http://localhost:1234/v1/chat/completions", headers=headers, json=payload) as response:
                    async for line in response.aiter_lines():
                        if line.strip().startswith("data:"):
                            yield line.lstrip("data: ")
                        await asyncio.sleep(0.01)

        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    return StreamingResponse(stream_generator(), media_type="text/plain")