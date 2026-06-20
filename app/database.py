from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from .models import Event, TicketBatch, Customer, Sale, SaleItem, EventHistory

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database schema created successfully.")
