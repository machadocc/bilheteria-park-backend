from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, constr


class EventStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    FINALIZED = "FINALIZED"


class BatchStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class EventBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=3)
    description: Optional[str] = None
    category: Optional[str] = None
    date: date
    time: time
    location: Optional[str] = None
    capacity: int = Field(..., gt=0)
    banner_url: Optional[str] = None
    status: Optional[EventStatus] = EventStatus.ACTIVE


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    banner_url: Optional[str] = None
    status: Optional[EventStatus] = None


class EventHistoryOut(BaseModel):
    action: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TicketBatchBase(BaseModel):
    event_id: int
    name: constr(strip_whitespace=True, min_length=3)
    ticket_type: constr(strip_whitespace=True, min_length=3)
    quantity_available: int = Field(..., ge=0)
    unit_price: float = Field(..., gt=0)
    valid_until: date


class TicketBatchCreate(TicketBatchBase):
    pass


class TicketBatchUpdate(BaseModel):
    name: Optional[str] = None
    ticket_type: Optional[str] = None
    quantity_available: Optional[int] = None
    unit_price: Optional[float] = None
    valid_until: Optional[date] = None
    status: Optional[BatchStatus] = None


class TicketBatchOut(TicketBatchBase):
    id: int
    status: BatchStatus
    created_at: datetime

    class Config:
        from_attributes = True


class EventCatalogOut(BaseModel):
    id: int
    name: str
    date: date
    time: time
    location: Optional[str] = None
    banner_url: Optional[str] = None
    min_price: float
    available_tickets: int
    status: EventStatus
    category: Optional[str] = None

    class Config:
        from_attributes = True


class EventOut(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ticket_batches: List[TicketBatchOut] = []
    history: List[EventHistoryOut] = []

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=3)
    cpf: constr(strip_whitespace=True, min_length=11, max_length=14)
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None


class CustomerOut(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    ticket_batch_id: int
    quantity: int = Field(..., gt=0)


class SaleCreate(BaseModel):
    customer_id: int
    payment_method: str
    items: List[SaleItemCreate]


class PurchaseCreate(BaseModel):
    evento_id: int
    quantidade: int = Field(..., gt=0)
    nome_comprador: constr(strip_whitespace=True, min_length=3)
    email_comprador: constr(strip_whitespace=True, min_length=5)
    cpf_comprador: constr(strip_whitespace=True, min_length=11, max_length=14)


class SaleItemOut(BaseModel):
    ticket_batch_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    id: int
    customer_id: Optional[int]
    total_amount: float
    purchase_code: str
    payment_method: Optional[str]
    created_at: datetime
    items: List[SaleItemOut] = []

    class Config:
        from_attributes = True


class AuthLogin(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str


class AdminSaleReportOut(BaseModel):
    event_id: int
    name: str
    tickets_sold: int
    revenue: float
    capacity: int

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_tickets_sold_today: int
    daily_revenue: float
    monthly_revenue: float
    active_events: int
    finished_events: int
    tickets_available: int


class TopEventOut(BaseModel):
    event_id: int
    name: str
    tickets_sold: int
    revenue: float


class AlertOut(BaseModel):
    event_id: int
    name: str
    remaining_tickets: int
    capacity: int
