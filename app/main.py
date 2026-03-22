from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import make_asgi_app

import time
import hashlib
import random

from app.metrics import (
    REQUEST_COUNT, REQUEST_LATENCY,
    CACHE_HITS, CACHE_MISSES,
    TOKENS_USED, ACTIVE_REQUESTS
)

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
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    cache_key = hashlib.md5(request.prompt.encode()).hexdigest()

    if cache_key in cache:
        CACHE_HITS.inc()
        latency = (time.time() - start_time) * 1000
        REQUEST_LATENCY.labels(endpoint="/api/chat").observe(latency / 1000)
        REQUEST_COUNT.labels(method="POST", endpoint="/api/chat", status="200").inc()
        record = {"prompt": request.prompt, "response": cache[cache_key], "cached": True, "latency_ms": round(latency, 2), "tokens_used": 0, "timestamp": time.time()}
        request_history.append(record)
        ACTIVE_REQUESTS.dec()
        return ChatResponse(**record)

    CACHE_MISSES.inc()
    time.sleep(random.uniform(0.3, 1.5))
    ai_response = f"AI response to: {request.prompt[:50]}"
    tokens = len(request.prompt.split()) * 3
    latency = (time.time() - start_time) * 1000

    TOKENS_USED.inc(tokens)
    REQUEST_LATENCY.labels(endpoint="/api/chat").observe(latency / 1000)
    REQUEST_COUNT.labels(method="POST", endpoint="/api/chat", status="200").inc()

    cache[cache_key] = ai_response
    record = {"prompt": request.prompt, "response": ai_response, "cached": False, "latency_ms": round(latency, 2), "tokens_used": tokens, "timestamp": time.time()}
    request_history.append(record)
    ACTIVE_REQUESTS.dec()
    return ChatResponse(**record)


@app.get("/api/history")
def get_history():
    REQUEST_COUNT.labels(method="GET", endpoint="/api/history", status="200").inc()
    return {"total": len(request_history), "requests": request_history[-20:]}


@app.get("/api/stats")
def get_stats():
    REQUEST_COUNT.labels(method="GET", endpoint="/api/stats", status="200").inc()
    total = len(request_history)
    cached = sum(1 for r in request_history if r["cached"])
    total_tokens = sum(r["tokens_used"] for r in request_history)
    avg_latency = sum(r["latency_ms"] for r in request_history) / total if total > 0 else 0
    return {"total_requests": total, "cached_requests": cached, "cache_hit_ratio": round(cached / total * 100, 1) if total > 0 else 0, "total_tokens": total_tokens, "avg_latency_ms": round(avg_latency, 2)}
