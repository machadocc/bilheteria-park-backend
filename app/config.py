import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ticketing.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "")
AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
