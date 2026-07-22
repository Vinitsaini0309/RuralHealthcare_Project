from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, get_db
from .import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Services API",
    description="Rural Healthcare Medicine Supply Chain & Logistics API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Healthcare Services API!",
        "docs_url": "/docs",
        "status": "healthy"
    }

@app.get("/facilities")
def get_facilities(db: Session = Depends(get_db)):
    facilities = db.query(models.Facility).all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "type": f.type,
            "address": f.address,
            "coordinates": {"lat": f.lat, "lng": f.lng},
            "contact": f.contact
        }
        for f in facilities
    ]

@app.get("/medicines")
def get_medicines(db: Session = Depends(get_db)):
    medicines = db.query(models.Medicine).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "unit_type": m.unit_type,
            "default_threshold": m.default_threshold
        }
        for m in medicines
    ]

@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    inventory_items = db.query(models.Inventory).all()
    return [
        {
            "facility_id": i.facility_id,
            "facility_name": i.facility.name if i.facility else None,
            "medicine_id": i.medicine_id,
            "medicine_name": i.medicine.name if i.medicine else None,
            "batch_number": i.batch_number,
            "quantity": i.quantity,
            "expiry_date": str(i.expiry_date) if i.expiry_date else None,
            "last_updated": i.last_updated.isoformat() if i.last_updated else None
        }
        for i in inventory_items
    ]

@app.get("/transfers")
def get_transfers(db: Session = Depends(get_db)):
    transfers = db.query(models.StockTransfer).all()
    return [
        {
            "id": t.id,
            "sender_facility": t.sender.name if t.sender else None,
            "receiver_facility": t.receiver.name if t.receiver else None,
            "medicine_name": t.medicine.name if t.medicine else None,
            "quantity": t.quantity,
            "status": t.status,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None
        }
        for t in transfers
    ]

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.SystemAlert).all()
    return [
        {
            "id": a.id,
            "facility_name": a.facility.name if a.facility else None,
            "medicine_name": a.medicine.name if a.medicine else None,
            "alert_type": a.alert_type,
            "status": a.status,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None
        }
        for a in alerts
    ]
