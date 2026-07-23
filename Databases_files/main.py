from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, get_db
from . import crud, schemas

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
    facilities = crud.get_facilities(db)
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
    medicines = crud.get_medicines(db)
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
    inventory_items = crud.get_inventories(db)
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

@app.get("/transfers", response_model=List[schemas.StockTransferResponse])
def get_transfers(db: Session = Depends(get_db)):
    return crud.get_transfers(db)

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = crud.get_alerts(db)
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


# --- Objections CRUD Routes ---

@app.post("/objections", response_model=schemas.ObjectionResponse, status_code=201)
def create_objection(objection: schemas.ObjectionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_objection(db, objection)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/objections", response_model=List[schemas.ObjectionResponse])
def read_objections(db: Session = Depends(get_db)):
    return crud.get_objections(db)

@app.get("/objections/{id}", response_model=schemas.ObjectionResponse)
def read_objection(id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_objection(db, id)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/objections/{id}", response_model=schemas.ObjectionResponse)
def update_objection(id: int, objection_update: schemas.ObjectionUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_objection(db, id, objection_update)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/objections/{id}", status_code=204)
def delete_objection(id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_objection(db, id)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Emergency Alerts CRUD Routes ---

@app.post("/emergency-alerts", response_model=schemas.EmergencyAlertResponse, status_code=201)
def create_emergency_alert(alert: schemas.EmergencyAlertCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_emergency_alert(db, alert)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/emergency-alerts", response_model=List[schemas.EmergencyAlertResponse])
def read_emergency_alerts(db: Session = Depends(get_db)):
    return crud.get_emergency_alerts(db)

@app.get("/emergency-alerts/{id}", response_model=schemas.EmergencyAlertResponse)
def read_emergency_alert(id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_emergency_alert(db, id)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.put("/emergency-alerts/{id}", response_model=schemas.EmergencyAlertResponse)
def update_emergency_alert(id: int, alert_update: schemas.EmergencyAlertUpdate, db: Session = Depends(get_db)):
    try:
        return crud.update_emergency_alert(db, id, alert_update)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/emergency-alerts/{id}", status_code=204)
def delete_emergency_alert(id: int, db: Session = Depends(get_db)):
    try:
        crud.delete_emergency_alert(db, id)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Stock Transfer Request Route ---

@app.post("/api/transfer/request", response_model=schemas.StockTransferResponse, status_code=201)
def request_stock_transfer(req: schemas.StockTransferRequest, db: Session = Depends(get_db)):
    try:
        return crud.create_stock_transfer_request(db, req)
    except crud.EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except crud.InsufficientStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
