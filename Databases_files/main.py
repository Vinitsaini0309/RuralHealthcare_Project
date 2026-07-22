from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime

from .database import engine, Base, get_db
from . import models, schemas

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

@app.get("/transfers", response_model=List[schemas.StockTransferResponse])
def get_transfers(db: Session = Depends(get_db)):
    return db.query(models.StockTransfer).all()

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


# --- Objections CRUD Routes ---

@app.post("/objections", response_model=schemas.ObjectionResponse, status_code=201)
def create_objection(objection: schemas.ObjectionCreate, db: Session = Depends(get_db)):
    transfer = db.query(models.StockTransfer).filter(models.StockTransfer.id == objection.transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail=f"Stock transfer with ID {objection.transfer_id} not found")
    
    db_objection = models.Objection(
        transfer_id=objection.transfer_id,
        reason=objection.reason,
        submitted_by=objection.submitted_by
    )
    db.add(db_objection)
    db.commit()
    db.refresh(db_objection)
    return db_objection

@app.get("/objections", response_model=List[schemas.ObjectionResponse])
def read_objections(db: Session = Depends(get_db)):
    return db.query(models.Objection).all()

@app.get("/objections/{id}", response_model=schemas.ObjectionResponse)
def read_objection(id: int, db: Session = Depends(get_db)):
    objection = db.query(models.Objection).filter(models.Objection.id == id).first()
    if not objection:
        raise HTTPException(status_code=404, detail=f"Objection with ID {id} not found")
    return objection

@app.put("/objections/{id}", response_model=schemas.ObjectionResponse)
def update_objection(id: int, objection_update: schemas.ObjectionUpdate, db: Session = Depends(get_db)):
    db_objection = db.query(models.Objection).filter(models.Objection.id == id).first()
    if not db_objection:
        raise HTTPException(status_code=404, detail=f"Objection with ID {id} not found")
    
    if objection_update.reason is not None:
        db_objection.reason = objection_update.reason
    if objection_update.status is not None:
        db_objection.status = objection_update.status
        
    db.commit()
    db.refresh(db_objection)
    return db_objection

@app.delete("/objections/{id}", status_code=204)
def delete_objection(id: int, db: Session = Depends(get_db)):
    db_objection = db.query(models.Objection).filter(models.Objection.id == id).first()
    if not db_objection:
        raise HTTPException(status_code=404, detail=f"Objection with ID {id} not found")
    
    db.delete(db_objection)
    db.commit()
    return


# --- Emergency Alerts CRUD Routes ---

@app.post("/emergency-alerts", response_model=schemas.EmergencyAlertResponse, status_code=201)
def create_emergency_alert(alert: schemas.EmergencyAlertCreate, db: Session = Depends(get_db)):
    facility = db.query(models.Facility).filter(models.Facility.id == alert.facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility with ID {alert.facility_id} not found")
    
    db_alert = models.EmergencyAlert(
        facility_id=alert.facility_id,
        alert_type=alert.alert_type,
        description=alert.description,
        severity=alert.severity,
        status=alert.status
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/emergency-alerts", response_model=List[schemas.EmergencyAlertResponse])
def read_emergency_alerts(db: Session = Depends(get_db)):
    return db.query(models.EmergencyAlert).all()

@app.get("/emergency-alerts/{id}", response_model=schemas.EmergencyAlertResponse)
def read_emergency_alert(id: int, db: Session = Depends(get_db)):
    alert = db.query(models.EmergencyAlert).filter(models.EmergencyAlert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Emergency alert with ID {id} not found")
    return alert

@app.put("/emergency-alerts/{id}", response_model=schemas.EmergencyAlertResponse)
def update_emergency_alert(id: int, alert_update: schemas.EmergencyAlertUpdate, db: Session = Depends(get_db)):
    db_alert = db.query(models.EmergencyAlert).filter(models.EmergencyAlert.id == id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail=f"Emergency alert with ID {id} not found")
    
    if alert_update.description is not None:
        db_alert.description = alert_update.description
    if alert_update.severity is not None:
        db_alert.severity = alert_update.severity
    if alert_update.status is not None:
        db_alert.status = alert_update.status
        
    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.delete("/emergency-alerts/{id}", status_code=204)
def delete_emergency_alert(id: int, db: Session = Depends(get_db)):
    db_alert = db.query(models.EmergencyAlert).filter(models.EmergencyAlert.id == id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail=f"Emergency alert with ID {id} not found")
    
    db.delete(db_alert)
    db.commit()
    return


# --- Stock Transfer Request Route ---

@app.post("/api/transfer/request", response_model=schemas.StockTransferResponse, status_code=201)
def request_stock_transfer(req: schemas.StockTransferRequest, db: Session = Depends(get_db)):
    # 1. Verify facilities exist
    sender = db.query(models.Facility).filter(models.Facility.id == req.sender_facility_id).first()
    receiver = db.query(models.Facility).filter(models.Facility.id == req.receiver_facility_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail=f"Sender facility with ID {req.sender_facility_id} not found")
    if not receiver:
        raise HTTPException(status_code=404, detail=f"Receiver facility with ID {req.receiver_facility_id} not found")
    
    # 2. Verify medicine exists
    med = db.query(models.Medicine).filter(models.Medicine.id == req.medicine_id).first()
    if not med:
        raise HTTPException(status_code=404, detail=f"Medicine with ID {req.medicine_id} not found")
        
    # 3. Check stock at sender facility
    if req.batch_number:
        # Check specific batch
        inventory = db.query(models.Inventory).filter(
            models.Inventory.facility_id == req.sender_facility_id,
            models.Inventory.medicine_id == req.medicine_id,
            models.Inventory.batch_number == req.batch_number
        ).first()
        if not inventory or inventory.quantity < req.quantity:
            available = inventory.quantity if inventory else 0
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock in batch {req.batch_number}. Requested {req.quantity}, available {available}."
            )
        # Deduct
        inventory.quantity -= req.quantity
    else:
        # Check total stock across all batches
        inventories = db.query(models.Inventory).filter(
            models.Inventory.facility_id == req.sender_facility_id,
            models.Inventory.medicine_id == req.medicine_id
        ).all()
        
        total_qty = sum(inv.quantity for inv in inventories)
        if total_qty < req.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient total stock at sender facility. Requested {req.quantity}, total available {total_qty}."
            )
            
        # Deduct prioritizing soonest expiry (FIFO/FEFO)
        # Sort inventories by expiry date. If expiry_date is None, put it last.
        sorted_inventories = sorted(
            inventories, 
            key=lambda x: x.expiry_date if x.expiry_date is not None else datetime.date.max
        )
        
        remaining_to_deduct = req.quantity
        for inv in sorted_inventories:
            if inv.quantity <= 0:
                continue
            if inv.quantity >= remaining_to_deduct:
                inv.quantity -= remaining_to_deduct
                remaining_to_deduct = 0
                break
            else:
                remaining_to_deduct -= inv.quantity
                inv.quantity = 0
                
        if remaining_to_deduct > 0:
            # Fallback guard
            raise HTTPException(
                status_code=400,
                detail="An unexpected error occurred during stock allocation."
            )
            
    # Create StockTransfer record
    transfer = models.StockTransfer(
        sender_facility_id=req.sender_facility_id,
        receiver_facility_id=req.receiver_facility_id,
        medicine_id=req.medicine_id,
        quantity=req.quantity,
        status="Requested"
    )
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer

