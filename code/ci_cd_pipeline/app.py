from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Enterprise Payment Gateway Service", version="2.4.0")

class PaymentRequest(BaseModel):
    account_id: str
    amount: float
    currency: str = "USD"

@app.get("/health")
def health_check():
    db_connected = os.getenv("DB_CONNECTED", "true").lower() == "true"
    if not db_connected:
        raise HTTPException(status_code=503, detail="Database connection degraded")
    return {
        "status": "HEALTHY",
        "version": os.getenv("APP_VERSION", "2.4.0"),
        "environment": os.getenv("APP_ENV", "production")
    }

@app.get("/api/v1/version")
def get_version():
    return {
        "version": os.getenv("APP_VERSION", "2.4.0"),
        "color": os.getenv("APP_COLOR", "blue"),
        "features": {
            "fraud_detection_v2": os.getenv("FEATURE_FRAUD_V2", "false") == "true",
            "instant_settlement": True
        }
    }

@app.post("/api/v1/process-payment")
def process_payment(req: PaymentRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Transaction amount must be strictly positive")
    
    # Simulate processing logic
    tx_id = f"tx_{req.account_id}_{int(req.amount * 100)}"
    return {
        "status": "APPROVED",
        "transaction_id": tx_id,
        "amount": req.amount,
        "currency": req.currency,
        "processed_by_cluster": os.getenv("HOSTNAME", "primary-gateway-node-01")
    }

