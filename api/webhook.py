import logging
import os
import hmac
from hashlib import sha256
import base64

from fastapi import APIRouter, Request, Header, HTTPException, status

from .dependencies import GooglePubSubTopic, verify_hmac

log = logging.getLogger(__name__)
router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)


@router.post("/{obj}/{action}")
async def handle_webhook(obj: str, action: str, request: Request,
                         x_shopify_hmac_sha256: bytes = Header(None)):
    data = await request.json()
    await verify_hmac(request, x_shopify_hmac_sha256)
    topic = GooglePubSubTopic(f"{obj}-{action}")
    topic.publish({
        "body": data,
        "headers": dict(request.headers.items())
    })
    return {"message": "ok"}
