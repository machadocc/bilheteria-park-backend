# app/api/sales.py
from fastapi import APIRouter, Depends, HTTPException
import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..config import AWS_SQS_QUEUE_URL
from ..aws_clients import get_sqs_client
from ..database import SessionLocal
from .. import schemas, models

router = APIRouter(tags=["Purchases"])
sqs = get_sqs_client()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/compras")
def purchase_ticket(purchase_in: schemas.PurchaseCreate):
    """
    Não insere no banco! Apenas enfileira na SQS.
    """
    payload = {
        "event_type": "purchase_requested",
        "customer_name": purchase_in.nome_comprador,
        "customer_cpf": purchase_in.cpf_comprador,
        "customer_email": purchase_in.email_comprador,
        "event_id": purchase_in.evento_id,
        "quantity": purchase_in.quantidade,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        response = sqs.send_message(
            QueueUrl=AWS_SQS_QUEUE_URL,
            MessageBody=json.dumps(payload),
            DelaySeconds=0,
        )
        return {
            "status": "processing",
            "message": "Compra enfileirada. Você receberá confirmação por email.",
            "message_id": response["MessageId"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compras/status")
def check_purchase_status(cpf: str, evento_id: int, db: Session = Depends(get_db)):
    # Normaliza CPF para só dígitos
    cpf_normalizado = "".join(filter(str.isdigit, cpf))

    print(f"[STATUS] cpf_recebido={cpf!r} cpf_normalizado={cpf_normalizado!r} evento_id={evento_id!r}", flush=True)

    # Busca o customer pelo CPF
    customer = (
        db.query(models.Customer)
        .filter(models.Customer.cpf == cpf_normalizado)
        .first()
    )

    print(f"[STATUS] customer={customer}", flush=True)

    if not customer:
        return {"status": "pending"}

    # Lista todas as vendas do customer para debug
    todas_vendas = db.query(models.Sale).filter(models.Sale.customer_id == customer.id).all()
    print(f"[STATUS] vendas do customer: {[(s.id, s.purchase_code) for s in todas_vendas]}", flush=True)

    # Busca a venda mais recente desse customer que tenha item do evento solicitado
    sale = (
        db.query(models.Sale)
        .join(models.SaleItem, models.Sale.id == models.SaleItem.sale_id)
        .join(models.TicketBatch, models.SaleItem.ticket_batch_id == models.TicketBatch.id)
        .filter(
            models.Sale.customer_id == customer.id,
            models.TicketBatch.event_id == evento_id,
        )
        .order_by(models.Sale.created_at.desc())
        .first()
    )

    print(f"[STATUS] sale encontrada={sale}", flush=True)

    if not sale:
        return {"status": "pending"}

    return {
        "status": "confirmed",
        "purchase_code": sale.purchase_code,
        "total_amount": sale.total_amount,
        "created_at": sale.created_at.isoformat(),
    }