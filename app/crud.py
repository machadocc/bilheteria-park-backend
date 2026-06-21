from datetime import datetime, date
from typing import List, Optional
import uuid

from sqlalchemy import func, extract, desc
from sqlalchemy.orm import Session

from . import models, schemas


def log_event_history(db: Session, event_id: int, action: str, notes: Optional[str] = None) -> models.EventHistory:
    history = models.EventHistory(event_id=event_id, action=action, notes=notes)
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def list_events(db: Session) -> List[models.Event]:
    return db.query(models.Event).order_by(models.Event.date.asc(), models.Event.time.asc()).all()


def list_public_events(db: Session) -> List[dict]:
    events = (
        db.query(models.Event)
        .filter(models.Event.status == models.EventStatus.ACTIVE)
        .order_by(models.Event.date.asc(), models.Event.time.asc())
        .all()
    )
    response = []
    for event in events:
        active_batches = [
            batch
            for batch in event.ticket_batches
            if batch.status == models.BatchStatus.ACTIVE and batch.quantity_available > 0
        ]
        available_tickets = sum(batch.quantity_available for batch in active_batches)
        min_price = min((batch.unit_price for batch in active_batches), default=0.0)
        response.append(
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "time": event.time,
                "location": event.location,
                "banner_url": event.banner_url,
                "min_price": float(min_price),
                "available_tickets": int(available_tickets),
                "status": event.status,
                "category": event.category,
            }
        )
    return response


def create_event(db: Session, event_in: schemas.EventCreate) -> models.Event:
    event = models.Event(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    log_event_history(db, event.id, "CREATED", f"Evento criado: {event.name}")
    return event


def update_event(db: Session, event_id: int, event_in: schemas.EventUpdate) -> Optional[models.Event]:
    event = get_event(db, event_id)
    if not event:
        return None

    for field, value in event_in.dict(exclude_unset=True).items():
        setattr(event, field, value)

    db.add(event)
    db.commit()
    db.refresh(event)
    log_event_history(db, event.id, "UPDATED", f"Evento atualizado: {event.name}")
    return event


def delete_event(db: Session, event_id: int) -> bool:
    event = get_event(db, event_id)
    if not event:
        return False
    db.delete(event)
    db.commit()
    return True


def cancel_event(db: Session, event_id: int) -> Optional[models.Event]:
    event = get_event(db, event_id)
    if not event:
        return None
    event.status = models.EventStatus.CANCELED
    db.add(event)
    db.commit()
    db.refresh(event)
    log_event_history(db, event.id, "CANCELED", "Evento cancelado")
    return event


def duplicate_event(db: Session, event_id: int) -> Optional[models.Event]:
    event = get_event(db, event_id)
    if not event:
        return None
    duplicate = models.Event(
        name=f"{event.name} - Cópia",
        description=event.description,
        category=event.category,
        date=event.date,
        time=event.time,
        location=event.location,
        capacity=event.capacity,
        banner_url=event.banner_url,
        status=models.EventStatus.ACTIVE,
    )
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    log_event_history(db, duplicate.id, "DUPLICATED", f"Evento duplicado a partir de {event.id}")
    return duplicate


def get_event_history(db: Session, event_id: int) -> List[models.EventHistory]:
    return (
        db.query(models.EventHistory)
        .filter(models.EventHistory.event_id == event_id)
        .order_by(models.EventHistory.created_at.desc())
        .all()
    )


def create_ticket_batch(db: Session, batch_in: schemas.TicketBatchCreate) -> models.TicketBatch:
    batch = models.TicketBatch(**batch_in.dict())
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def update_ticket_batch(db: Session, batch_id: int, batch_in: schemas.TicketBatchUpdate) -> Optional[models.TicketBatch]:
    batch = db.query(models.TicketBatch).filter(models.TicketBatch.id == batch_id).first()
    if not batch:
        return None
    for field, value in batch_in.dict(exclude_unset=True).items():
        setattr(batch, field, value)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def close_ticket_batch(db: Session, batch_id: int) -> Optional[models.TicketBatch]:
    batch = db.query(models.TicketBatch).filter(models.TicketBatch.id == batch_id).first()
    if not batch:
        return None
    batch.status = models.BatchStatus.CLOSED
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


def get_ticket_batches(db: Session) -> List[models.TicketBatch]:
    return db.query(models.TicketBatch).order_by(models.TicketBatch.valid_until.asc()).all()


def create_customer(db: Session, customer_in: schemas.CustomerCreate) -> models.Customer:
    customer = models.Customer(**customer_in.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer_id: int, customer_in: schemas.CustomerUpdate) -> Optional[models.Customer]:
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        return None
    for field, value in customer_in.dict(exclude_unset=True).items():
        setattr(customer, field, value)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_cpf(db: Session, cpf: str) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.cpf == cpf).first()


def get_or_create_customer(db: Session, name: str, cpf: str, email: str) -> models.Customer:
    customer = get_customer_by_cpf(db, cpf)
    if customer:
        return customer
    new_customer = models.Customer(name=name, cpf=cpf, email=email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def generate_purchase_code() -> str:
    return uuid.uuid4().hex.upper()[:12]


def create_purchase(db: Session, purchase_in: schemas.PurchaseCreate) -> models.Sale:
    event = get_event(db, purchase_in.evento_id)
    if not event or event.status != models.EventStatus.ACTIVE:
        raise ValueError("Evento não encontrado ou inativo")

    batches = (
        db.query(models.TicketBatch)
        .filter(
            models.TicketBatch.event_id == event.id,
            models.TicketBatch.status == models.BatchStatus.ACTIVE,
            models.TicketBatch.quantity_available > 0,
        )
        .order_by(models.TicketBatch.unit_price.asc(), models.TicketBatch.valid_until.asc())
        .with_for_update()
        .all()
    )

    total_available = sum(batch.quantity_available for batch in batches)
    if total_available < purchase_in.quantidade:
        raise ValueError("Estoque insuficiente")

    customer = get_or_create_customer(
        db,
        name=purchase_in.nome_comprador,
        cpf=purchase_in.cpf_comprador,
        email=purchase_in.email_comprador,
    )

    sale = models.Sale(
        customer_id=customer.id,
        payment_method="PUBLIC",
        purchase_code=generate_purchase_code(),
    )
    db.add(sale)
    db.flush()

    total_amount = 0.0
    remaining = purchase_in.quantidade

    for batch in batches:
        if remaining <= 0:
            break

        allocate = min(batch.quantity_available, remaining)
        batch.quantity_available -= allocate
        if batch.quantity_available <= 0:
            batch.quantity_available = 0
            batch.status = models.BatchStatus.CLOSED

        sale_item = models.SaleItem(
            sale_id=sale.id,
            ticket_batch_id=batch.id,
            quantity=allocate,
            unit_price=batch.unit_price,
        )
        db.add(sale_item)
        total_amount += allocate * batch.unit_price
        remaining -= allocate

    sale.total_amount = total_amount
    db.commit()
    db.refresh(sale)
    return sale


def get_customer_history(db: Session, customer_id: int) -> List[models.Sale]:
    return (
        db.query(models.Sale)
        .filter(models.Sale.customer_id == customer_id)
        .order_by(models.Sale.created_at.desc())
        .all()
    )


def create_sale(db: Session, sale_in: schemas.SaleCreate) -> models.Sale:
    customer = get_customer(db, sale_in.customer_id)
    if not customer:
        raise ValueError("Cliente não encontrado")

    sale = models.Sale(customer_id=customer.id, payment_method=sale_in.payment_method, purchase_code=generate_purchase_code())
    db.add(sale)
    db.flush()

    total_amount = 0.0
    for item in sale_in.items:
        batch = (
            db.query(models.TicketBatch)
            .filter(models.TicketBatch.id == item.ticket_batch_id)
            .with_for_update()
            .first()
        )
        if not batch or batch.status != models.BatchStatus.ACTIVE:
            raise ValueError(f"Lote de ingresso inválido ou inativo: {item.ticket_batch_id}")
        if batch.quantity_available < item.quantity:
            raise ValueError(f"Estoque insuficiente para o lote {batch.id}")

        batch.quantity_available -= item.quantity
        if batch.quantity_available <= 0:
            batch.quantity_available = 0
            batch.status = models.BatchStatus.CLOSED

        total_amount += batch.unit_price * item.quantity
        sale_item = models.SaleItem(
            sale_id=sale.id,
            ticket_batch_id=batch.id,
            quantity=item.quantity,
            unit_price=batch.unit_price,
        )
        db.add(sale_item)

    sale.total_amount = total_amount
    db.commit()
    db.refresh(sale)
    return sale


def get_dashboard_summary(db: Session) -> schemas.DashboardSummary:
    today = date.today()
    total_tickets_sold_today = (
        db.query(func.sum(models.SaleItem.quantity))
        .join(models.Sale)
        .filter(func.date(models.Sale.created_at) == today)
        .scalar() or 0
    )
    daily_revenue = (
        db.query(func.sum(models.Sale.total_amount))
        .filter(func.date(models.Sale.created_at) == today)
        .scalar() or 0.0
    )
    monthly_revenue = (
        db.query(func.sum(models.Sale.total_amount))
        .filter(extract("year", models.Sale.created_at) == today.year)
        .filter(extract("month", models.Sale.created_at) == today.month)
        .scalar() or 0.0
    )
    active_events = db.query(models.Event).filter(models.Event.status == models.EventStatus.ACTIVE).count()
    finished_events = db.query(models.Event).filter(models.Event.status == models.EventStatus.FINALIZED).count()
    tickets_available = db.query(func.sum(models.TicketBatch.quantity_available)).scalar() or 0

    return schemas.DashboardSummary(
        total_tickets_sold_today=int(total_tickets_sold_today),
        daily_revenue=float(daily_revenue),
        monthly_revenue=float(monthly_revenue),
        active_events=int(active_events),
        finished_events=int(finished_events),
        tickets_available=int(tickets_available),
    )


def get_top_events(db: Session, limit: int = 5) -> List[schemas.TopEventOut]:
    rows = (
        db.query(
            models.Event.id,
            models.Event.name,
            func.sum(models.SaleItem.quantity).label("tickets_sold"),
            func.sum(models.SaleItem.quantity * models.SaleItem.unit_price).label("revenue"),
        )
        .join(models.TicketBatch, models.TicketBatch.event_id == models.Event.id)
        .join(models.SaleItem, models.SaleItem.ticket_batch_id == models.TicketBatch.id)
        .group_by(models.Event.id)
        .order_by(desc("tickets_sold"))
        .limit(limit)
        .all()
    )
    return [
        schemas.TopEventOut(
            event_id=row.id,
            name=row.name,
            tickets_sold=int(row.tickets_sold or 0),
            revenue=float(row.revenue or 0.0),
        )
        for row in rows
    ]


def get_sales_report(db: Session) -> List[schemas.AdminSaleReportOut]:
    rows = (
        db.query(
            models.Event.id.label("event_id"),
            models.Event.name,
            func.sum(models.SaleItem.quantity).label("tickets_sold"),
            func.sum(models.SaleItem.quantity * models.SaleItem.unit_price).label("revenue"),
            models.Event.capacity,
        )
        .join(models.TicketBatch, models.TicketBatch.event_id == models.Event.id)
        .join(models.SaleItem, models.SaleItem.ticket_batch_id == models.TicketBatch.id)
        .group_by(models.Event.id)
        .order_by(desc("tickets_sold"))
        .all()
    )
    return [
        schemas.AdminSaleReportOut(
            event_id=row.event_id,
            name=row.name,
            tickets_sold=int(row.tickets_sold or 0),
            revenue=float(row.revenue or 0.0),
            capacity=int(row.capacity or 0),
        )
        for row in rows
    ]


def get_capacity_alerts(db: Session, threshold_percentage: float = 0.9) -> List[schemas.AlertOut]:
    events = db.query(models.Event).filter(models.Event.status == models.EventStatus.ACTIVE).all()
    alerts = []
    for event in events:
        tickets_sold = (
            db.query(func.sum(models.SaleItem.quantity))
            .join(models.TicketBatch, models.TicketBatch.id == models.SaleItem.ticket_batch_id)
            .filter(models.TicketBatch.event_id == event.id)
            .scalar() or 0
        )
        remaining = event.capacity - int(tickets_sold)
        if event.capacity > 0 and remaining / event.capacity <= (1 - threshold_percentage):
            alerts.append(
                schemas.AlertOut(
                    event_id=event.id,
                    name=event.name,
                    remaining_tickets=remaining,
                    capacity=event.capacity,
                )
            )
    return alerts


def get_last_sales(db: Session, limit: int = 10) -> List[models.Sale]:
    return db.query(models.Sale).order_by(models.Sale.created_at.desc()).limit(limit).all()
