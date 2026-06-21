from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..auth import get_current_admin
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


# ── Eventos ──────────────────────────────────────────────────────────────────

@router.get("/eventos", response_model=List[schemas.EventOut])
def list_events_admin(db: Session = Depends(get_db)):
    """Lista todos os eventos (incluindo rascunhos) para o painel admin."""
    return crud.list_events(db)


@router.post("/eventos", response_model=schemas.EventOut)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db, event_in)


@router.put("/eventos/{event_id}", response_model=schemas.EventOut)
def update_event(event_id: int, event_in: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = crud.update_event(db, event_id, event_in)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.delete("/eventos/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    if not crud.delete_event(db, event_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return None


@router.post("/eventos/{event_id}/cancel", response_model=schemas.EventOut)
def cancel_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.cancel_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/eventos/{event_id}/duplicate", response_model=schemas.EventOut)
def duplicate_event(event_id: int, db: Session = Depends(get_db)):
    event = crud.duplicate_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.get("/eventos/{event_id}/history", response_model=List[schemas.EventHistoryOut])
def event_history(event_id: int, db: Session = Depends(get_db)):
    if not crud.get_event(db, event_id):
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return crud.get_event_history(db, event_id)


# ── Lotes (Batches) ───────────────────────────────────────────────────────────

@router.get("/lotes", response_model=List[schemas.TicketBatchOut])
def list_batches(db: Session = Depends(get_db)):
    return crud.get_ticket_batches(db)


@router.post("/lotes", response_model=schemas.TicketBatchOut)
def create_batch(batch_in: schemas.TicketBatchCreate, db: Session = Depends(get_db)):
    return crud.create_ticket_batch(db, batch_in)


@router.put("/lotes/{batch_id}", response_model=schemas.TicketBatchOut)
def update_batch(batch_id: int, batch_in: schemas.TicketBatchUpdate, db: Session = Depends(get_db)):
    batch = crud.update_ticket_batch(db, batch_id, batch_in)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return batch


@router.post("/lotes/{batch_id}/close", response_model=schemas.TicketBatchOut)
def close_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = crud.close_ticket_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return batch


# ── Clientes ──────────────────────────────────────────────────────────────────

@router.get("/clientes", response_model=List[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@router.post("/clientes", response_model=schemas.CustomerOut)
def create_customer(customer_in: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db, customer_in)


@router.put("/clientes/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(customer_id: int, customer_in: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    customer = crud.update_customer(db, customer_id, customer_in)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.get("/clientes/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.get("/clientes/{customer_id}/history", response_model=List[schemas.SaleOut])
def customer_history(customer_id: int, db: Session = Depends(get_db)):
    if not crud.get_customer(db, customer_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return crud.get_customer_history(db, customer_id)


# ── Vendas / PDV ─────────────────────────────────────────────────────────────

@router.get("/vendas", response_model=List[schemas.AdminSaleReportOut])
def get_sales_report(db: Session = Depends(get_db)):
    return crud.get_sales_report(db)


@router.post("/vendas/checkout", response_model=schemas.SaleOut)
def pdv_checkout(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    """Ponto de venda: registra venda com customer_id e lista de lotes."""
    try:
        sale = crud.create_sale(db, sale_in)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return sale


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)


@router.get("/dashboard/top-events", response_model=List[schemas.TopEventOut])
def top_events(db: Session = Depends(get_db)):
    return crud.get_top_events(db)


@router.get("/dashboard/alerts", response_model=List[schemas.AlertOut])
def capacity_alerts(db: Session = Depends(get_db)):
    return crud.get_capacity_alerts(db)


@router.get("/dashboard/last-sales", response_model=List[schemas.SaleOut])
def last_sales(db: Session = Depends(get_db)):
    return crud.get_last_sales(db)
