from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import make_asgi_app
import time, hashlib, random

app = FastAPI(title="AI Proxy Gateway", version="0.1.0")
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

request_history = []
cache = {}

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    cached: bool
    latency_ms: float
    tokens_used: int

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start_time = time.time()
    cache_key = hashlib.md5(request.prompt.encode()).hexdigest()
    if cache_key in cache:
        latency = (time.time() - start_time) * 1000
        record = {"prompt": request.prompt, "response": cache[cache_key], "cached": True, "latency_ms": round(latency, 2), "tokens_used": 0, "timestamp": time.time()}
        request_history.append(record)
        return ChatResponse(**record)
    time.sleep(random.uniform(0.3, 1.5))
    ai_response = f"AI response to: {request.prompt[:50]}"
    tokens = len(request.prompt.split()) * 3
    latency = (time.time() - start_time) * 1000
    cache[cache_key] = ai_response
    record = {"prompt": request.prompt, "response": ai_response, "cached": False, "latency_ms": round(latency, 2), "tokens_used": tokens, "timestamp": time.time()}
    request_history.append(record)
    return ChatResponse(**record)

@app.get("/api/history")
def get_history():
    return {"total": len(request_history), "requests": request_history[-20:]}

@app.get("/api/stats")
def get_stats():
    total = len(request_history)
    cached = sum(1 for r in request_history if r["cached"])
    total_tokens = sum(r["tokens_used"] for r in request_history)
    avg_latency = sum(r["latency_ms"] for r in request_history) / total if total > 0 else 0
    return {"total_requests": total, "cached_requests": cached, "cache_hit_ratio": round(cached / total * 100, 1) if total > 0 else 0, "total_tokens": total_tokens, "avg_latency_ms": round(avg_latency, 2)}
