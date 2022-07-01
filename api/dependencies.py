import json
import logging
import os
from typing import Callable

from google.cloud import pubsub_v1

log = logging.getLogger(__name__)


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
