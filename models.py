from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

# Auto-fix database URL scheme
DB_URL = os.getenv("DATABASE_URL", os.getenv("POSTGRES_URL", "sqlite:///./app.db"))

if DB_URL.startswith("postgresql+asyncpg://"):
    DB_URL = DB_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+psycopg://")

# Add SSL if not localhost and not SQLite
if DB_URL.startswith("postgresql"):
    from urllib.parse import urlparse
    parsed = urlparse(DB_URL)
    if parsed.hostname != "localhost":
        DB_URL += "?sslmode=require"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Transaction model with app-specific prefix
class Transaction(Base):
    __tablename__ = "qb_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    label = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    note = Column(String)

# Forecast model with app-specific prefix
class Forecast(Base):
    __tablename__ = "qb_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    forecast_data = Column(String)

# Goal model with app-specific prefix
class Goal(Base):
    __tablename__ = "qb_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String, index=True)
    target_amount = Column(Float, nullable=False)
    target_date = Column(DateTime)

# Dashboard overview model with app-specific prefix
class DashboardOverview(Base):
    __tablename__ = "qb_dashboard_overviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    net_balance = Column(Float)
    total_goals = Column(Integer)
    upcoming_deadlines = Column(String)