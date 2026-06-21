import os

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    IPS_VALIDS = [                
        "http://localhost:80",        
        "http://127.0.0.1",        
        "http://127.0.0.1:80"
    ]
else:
    raw = os.getenv("IP_FRONT", "")
    IPS_VALIDS = [u.strip() for u in raw.split(",") if u.strip()]

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ticketing.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "")
AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
