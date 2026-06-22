# app/api/sales.py
from fastapi import APIRouter, Depends, HTTPException
import json
from ..config import AWS_SQS_QUEUE_URL
from ..aws_clients import get_sqs_client
from .. import schemas
from datetime import datetime

router = APIRouter(tags=["Purchases"])
sqs = get_sqs_client()

@router.post("/compras")
def purchase_ticket(purchase_in: schemas.PurchaseCreate):
    """
    Não insere no banco! Apenas enfileira na SQS.
    """
    
    # Validação BÁSICA (se evento existe, capacidade, etc)
    # MAS NÃO insere nada ainda
    
    payload = {
        "event_type": "purchase_requested",
        "customer_name": purchase_in.nome_comprador,
        "customer_cpf": purchase_in.cpf_comprador,
        "customer_email": purchase_in.email_comprador,
        "event_id": purchase_in.evento_id,
        "quantity": purchase_in.quantidade,
        "timestamp": datetime.utcnow().isoformat()
    }
        
    try:
        response = sqs.send_message(
            QueueUrl=AWS_SQS_QUEUE_URL,
            MessageBody=json.dumps(payload),
            DelaySeconds=0
        )

        return {
            "status": "processing",
            "message": "Compra enfileirada. Você receberá confirmação por email.",
            "message_id": response['MessageId']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))