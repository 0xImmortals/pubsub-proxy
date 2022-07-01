import logging
import os
import sys

from fastapi import FastAPI

from .webhook import router as webhook_router

level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(stream=sys.stdout, level=level)
log = logging.getLogger(__name__)

app = FastAPI(
    title="Pubsub Proxy",
    description="Thin REST API to catch webhooks and write them to GCP PubSub",
    version="0.1.0"
)

app.include_router(webhook_router)


@app.get("/")
async def main():
    return {"message": "Hello World"}


@app.get("/healthz")
async def healthz():
    return {"message": "ok"}
