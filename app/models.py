from enum import Enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from .database import Base


class EventStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FINALIZED = "FINALIZED"


class BatchStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(220), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(120), nullable=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    location = Column(String(220), nullable=True)
    capacity = Column(Integer, nullable=False, default=0)
    banner_url = Column(String(400), nullable=True)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    ticket_batches = relationship("TicketBatch", back_populates="event", cascade="all, delete-orphan")
    history = relationship("EventHistory", back_populates="event", cascade="all, delete-orphan")


class TicketBatch(Base):
    __tablename__ = "ticket_batches"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(180), nullable=False)
    ticket_type = Column(String(80), nullable=False)
    quantity_available = Column(Integer, nullable=False, default=0)
    unit_price = Column(Float, nullable=False)
    valid_until = Column(Date, nullable=False)
    status = Column(SQLEnum(BatchStatus), nullable=False, default=BatchStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    event = relationship("Event", back_populates="ticket_batches")
    sale_items = relationship("SaleItem", back_populates="ticket_batch")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(180), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(40), nullable=True)
    email = Column(String(180), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales = relationship("Sale", back_populates="customer")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(80), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    ticket_batch_id = Column(Integer, ForeignKey("ticket_batches.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    ticket_batch = relationship("TicketBatch", back_populates="sale_items")


class EventHistory(Base):
    __tablename__ = "event_history"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(160), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    event = relationship("Event", back_populates="history")
