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
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme123")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

AWS_SQS_QUEUE_VENDAS_URL = os.getenv("AWS_SQS_QUEUE_VENDAS_URL", "")