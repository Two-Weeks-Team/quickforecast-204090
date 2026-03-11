from fastapi import FastAPI, Depends, HTTPException, status
from models import Transaction, Forecast, Goal, DashboardOverview, SessionLocal, Base, engine
from pydantic import BaseModel
from datetime import datetime
from typing import List
from ai_service import call_forecast, allocate_goal

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request models
class TransactionCreate(BaseModel):
    amount: float
    type: str
    label: str
    date: str
    note: str

class ForecastRequest(BaseModel):
    start_date: str
    days: int

class GoalAllocationRequest(BaseModel):
    target_amount: float
    target_date: str

class DashboardOverviewResponse(BaseModel):
    net_balance: float
    total_goals: int
    upcoming_deadlines: str

class ForecastResponse(BaseModel):
    forecast: str
    confidence_interval: str

class GoalAllocationResponse(BaseModel):
    monthly_allocation: float
    allocation_schedule: str

router = FastAPI()

# Create transaction
@router.post("/transactions")
async def create_transaction(transaction: TransactionCreate, db: SessionLocal = Depends(get_db)):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

# Get all transactions
@router.get("/transactions", response_model=List[TransactionCreate])
async def get_transactions(db: SessionLocal = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions

# Get dashboard overview
@router.get("/dashboard/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(db: SessionLocal = Depends(get_db)):
    overview = db.query(DashboardOverview).first()
    if not overview:
        raise HTTPException(status_code=404, detail="Dashboard overview not found")
    return overview

# Generate forecast
@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(forecast_request: ForecastRequest, db: SessionLocal = Depends(get_db)):
    start_date = datetime.fromisoformat(forecast_request.start_date)
    forecast_data, confidence_interval = await call_forecast(start_date, forecast_request.days)
    db_forecast = Forecast(
        user_id="user_12345",
        start_date=start_date,
        forecast_data=forecast_data,
    )
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return {
        "forecast": forecast_data,
        "confidence_interval": confidence_interval
    }

# Allocate to goal
@router.post("/goals/{goal_id}/allocate", response_model=GoalAllocationResponse)
async def allocate_to_goal(goal_id: int, allocation_request: GoalAllocationRequest, db: SessionLocal = Depends(get_db)):
    target_date = datetime.fromisoformat(allocation_request.target_date)
    monthly_allocation, allocation_schedule = await allocate_goal(goal_id, allocation_request.target_amount, target_date)
    db_goal = Goal(
        user_id="user_12345",
        name="Sample Goal",
        target_amount=allocation_request.target_amount,
        target_date=target_date,
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return {
        "monthly_allocation": monthly_allocation,
        "allocation_schedule": allocation_schedule
    }