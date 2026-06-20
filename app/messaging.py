import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import AWS_REGION, AWS_SNS_TOPIC_ARN, AWS_SQS_QUEUE_URL

logger = logging.getLogger(__name__)


class MessageBus:
    def publish_sale_event(self, payload: dict) -> None:
        raise NotImplementedError

    def publish_event_update(self, payload: dict) -> None:
        raise NotImplementedError


class AWSMessageBus(MessageBus):
    def __init__(self):
        self.sqs_url = AWS_SQS_QUEUE_URL
        self.sns_topic_arn = AWS_SNS_TOPIC_ARN
        self.sqs = boto3.client("sqs", region_name=AWS_REGION)
        self.sns = boto3.client("sns", region_name=AWS_REGION)

    def publish_sale_event(self, payload: dict) -> None:
        message = json.dumps(payload, default=str)
        if self.sqs_url:
            try:
                self.sqs.send_message(QueueUrl=self.sqs_url, MessageBody=message)
            except (BotoCoreError, ClientError) as error:
                logger.warning("Falha ao enviar mensagem para SQS: %s", error)
        if self.sns_topic_arn:
            try:
                self.sns.publish(TopicArn=self.sns_topic_arn, Message=message)
            except (BotoCoreError, ClientError) as error:
                logger.warning("Falha ao publicar SNS: %s", error)

    def publish_event_update(self, payload: dict) -> None:
        payload = {**payload, "type": "event_update"}
        self.publish_sale_event(payload)


def build_message_bus() -> MessageBus:
    if AWS_SQS_QUEUE_URL or AWS_SNS_TOPIC_ARN:
        return AWSMessageBus()
    return MessageBus()


def lambda_sale_handler(event, context):
    logger.info("Lambda handler recebido: %s", event)
    record = event.get("Records", [])[0] if event.get("Records") else None
    if not record:
        logger.warning("Lambda sem registro de evento")
        return {"statusCode": 400, "body": "No records"}

    body = record.get("body") or record.get("Sns", {}).get("Message")
    logger.info("Evento de venda recebido: %s", body)
    return {"statusCode": 200, "body": "Processed"}
