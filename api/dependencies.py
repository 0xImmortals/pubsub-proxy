import json
import logging
import os
from typing import Callable
import base64
import hmac
from hashlib import sha256

from google.cloud import pubsub_v1
from fastapi import Request, HTTPException, status

log = logging.getLogger(__name__)

API_SECRET = os.environ.get("SHOPIFY_API_SECRET")


class Topic(object):

    def __init__(self, topic_name):
        self.topic_name = topic_name

    def publish(self, message: dict):
        raise NotImplementedError

    def subscribe(self, subscription: str, callback: Callable):
        raise NotImplementedError


class GooglePubSubTopic(Topic):

    def __init__(self, topic_name: str):
        super(GooglePubSubTopic, self).__init__(topic_name)
        self._publish_client = pubsub_v1.PublisherClient()
        self._subscribe_client = pubsub_v1.SubscriberClient()
        self._project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', None)
        self.topic_name = self._publish_client.topic_path(self._project_id, topic_name)

    def publish(self, message: dict):
        byte_string = json.dumps(message).encode('utf-8')
        future = self._publish_client.publish(self.topic_name, byte_string)
        future.add_done_callback(self._publish_future_callback)

    def _publish_future_callback(self, future):
        log.debug(future)

    def subscribe(self, subscription: str, callback: Callable):
        sub_path = self._subscribe_client.subscription_path(self._project_id, subscription)
        future = self._subscribe_client.subscribe(sub_path, callback)
        future.result()


async def verify_hmac(request: Request, hmac_header: bytes):
    raw_body = await request.body()
    sig = base64.b64encode(hmac.new(bytes(API_SECRET, 'latin-1'), msg=raw_body, digestmod=sha256).digest())
    if not hmac.compare_digest(sig, hmac_header):
        log.info(f"Computed hmac: {sig} != received {hmac_header}")
        log.info(request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
