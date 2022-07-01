import logging

from fastapi import APIRouter, Request

from .dependencies import GooglePubSubTopic

log = logging.getLogger(__name__)
router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)


@router.post("/{obj}/{action}")
async def handle_webhook(obj: str, action: str, request: Request):
    data = await request.json()
    topic = GooglePubSubTopic(f"{obj}-{action}")
    topic.publish(data)
    return {"message": "ok"}
