#!/usr/bin/env python3
"""
簡單的 FastAPI 應用 - 用於測試 Heartbeat
"""

from fastapi import FastAPI
from datetime import datetime
import time

app = FastAPI()

@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Jarvis is alive!"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_id": "test",
        "model": "test",
        "uptime": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
