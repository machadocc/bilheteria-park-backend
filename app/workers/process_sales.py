# worker.py (roda em ECS/Lambda/EC2 separado)
import json
import logging
import time

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import crud, schemas
from app.config import AWS_SQS_QUEUE_URL
from app.aws_clients import get_sqs_client

logger = logging.getLogger(__name__)

sqs = get_sqs_client()
QUEUE_URL = AWS_SQS_QUEUE_URL


def process_message(payload: dict, db: Session) -> bool:
    """
    Processa uma mensagem de compra vinda do SQS.
    Reaproveita crud.create_purchase, que já cuida de:
    - gerar o purchase_code
    - validar se o evento existe e está ACTIVE
    - reservar/alocar os lotes (com lock) por preço/validade
    - fechar o lote quando o estoque chega a zero
    - calcular o total_amount e dar commit

    Retorno:
        True  -> mensagem deve ser removida da fila (processada ou descartável)
        False -> mensagem deve voltar à fila para nova tentativa
    """
    try:
        purchase_in = schemas.PurchaseCreate(
            evento_id=payload["event_id"],
            quantidade=payload["quantity"],
            nome_comprador=payload["customer_name"],
            email_comprador=payload["customer_email"],
            cpf_comprador=payload["customer_cpf"],
        )
    except (KeyError, ValidationError) as e:
        logger.error(f"❌ Mensagem malformada, descartando da fila: {e} | payload={payload}")
        return True

    try:
        sale = crud.create_purchase(db, purchase_in)
        logger.info(f"✅ Venda {sale.id} (código {sale.purchase_code}) processada com sucesso")
        return True

    except ValueError as e:
        db.rollback()
        logger.warning(f"⚠️ Não foi possível processar a compra, voltará à fila: {e}")
        return False

    except Exception as e:
        # Erro inesperado (ex: banco indisponível). Retry faz sentido.
        db.rollback()
        logger.error(f"❌ Erro inesperado ao processar mensagem: {e}")
        return False


def worker():
    """
    Worker que consome mensagens da SQS continuamente.
    """
    while True:
        try:
            # Puxa até 10 mensagens
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,  # Long polling
            )

            messages = response.get("Messages", [])
            if not messages:
                logger.debug("Nenhuma mensagem na fila")
                continue

            for message in messages:
                receipt_handle = message["ReceiptHandle"]

                try:
                    payload = json.loads(message["Body"])
                    logger.info(f"Processando: {payload}")

                    db = SessionLocal()
                    try:
                        success = process_message(payload, db)
                    finally:
                        db.close()

                    if success:
                        sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
                        logger.info("Mensagem deletada da fila")                    
                except json.JSONDecodeError as e:                    
                    logger.error(f"❌ Mensagem com body inválido (não é JSON), descartando: {e}")
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)

                except Exception as e:
                    logger.error(f"Erro ao processar mensagem individual: {e}")                    

        except Exception as e:
            logger.error(f"Erro no worker: {e}")
            time.sleep(5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    if not QUEUE_URL:
        raise RuntimeError(
            "AWS_SQS_QUEUE_URL não está configurada. Defina essa variável de ambiente "
            "(no .env ou no docker-compose.yml) antes de iniciar o worker."
        )
    logger.info("Worker iniciado")
    worker()