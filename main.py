from fastapi import FastAPI, Request, HTMLResponse
from routes import router
from models import Base, engine
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routes

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return HTMLResponse(
        """
        <html>
            <head>
                <title>QuickForecast API</title>
                <style>
                    body {
                        background-color: #1a1a1a;
                        color: #ffffff;
                        font-family: Arial, sans-serif;
                        padding: 2rem;
                    }
                    h1 {
                        color: #006d77;
                    }
                    a {
                        color: #ff9f1c;
                    }
                    .endpoint {
                        margin: 1rem 0;
                    }
                </style>
            </head>
            <body>
                <h1>QuickForecast API</h1>
                <p>Instant budgeting starts with a single transaction</p>
                <h2>Endpoints</h2>
                <div class='endpoint'>GET <a href='/health'>/health</a> - Health check</div>
                <div class='endpoint'>GET <a href='/api/transactions'>/api/transactions</a> - List transactions</div>
                <div class='endpoint'>POST <a href='/api/transactions'>/api/transactions</a> - Create transaction</div>
                <div class='endpoint'>GET <a href='/api/dashboard/overview'>/api/dashboard/overview</a> - Dashboard overview</div>
                <div class='endpoint'>POST <a href='/api/forecast'>/api/forecast</a> - Generate forecast</div>
                <div class='endpoint'>POST <a href='/api/goals/{goal_id}/allocate'>/api/goals/{goal_id}/allocate</a> - Allocate to goal</div>
                <h2>Documentation</h2>
                <div class='endpoint'><a href='/docs'>Swagger Docs</a></div>
                <div class='endpoint'><a href='/redoc'>ReDoc</a></div>
            </body>
        </html>
        """
    )