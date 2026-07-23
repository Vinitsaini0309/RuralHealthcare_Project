
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

try:
    from . import models, schemas
except ImportError:
    import models, schemas

# --- Custom Exceptions for Clean Business Logic ---
class EntityNotFoundError(Exception):
    """Raised when a requested database entity does not exist."""
    pass

class InsufficientStockError(Exception):
    """Raised when a stock transfer or dispense is requested but insufficient stock is available."""
    pass


# --- Facility Services ---
def get_facilities(db: Session) -> List[models.Facility]:
    return db.query(models.Facility).all()


# --- Medicine Services ---
def get_medicines(db: Session) -> List[models.Medicine]:
    return db.query(models.Medicine).all()


# --- Inventory Services ---
def get_inventories(db: Session) -> List[models.Inventory]:
    return db.query(models.Inventory).all()

def dispense_medicine(db: Session, req: schemas.DispenseRequest) -> dict:
    facility = db.query(models.Facility).filter(models.Facility.id == req.facility_id).first()
    if not facility:
        # Fall back to first PHC facility if not found
        facility = db.query(models.Facility).filter(models.Facility.type == 'PHC').first()
        if not facility:
            raise EntityNotFoundError(f"Facility with ID {req.facility_id} not found")
        req.facility_id = facility.id

    dispensed_summary = []

    for item in req.items:
        # Find medicine by ID or name
        med = None
        if item.medicine_id:
            med = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        elif item.medicine_name:
            med = db.query(models.Medicine).filter(models.Medicine.name.ilike(f"%{item.medicine_name}%")).first()

        if not med:
            continue

        # Find inventory at facility
        inventories = db.query(models.Inventory).filter(
            models.Inventory.facility_id == req.facility_id,
            models.Inventory.medicine_id == med.id
        ).all()

        total_avail = sum(inv.quantity for inv in inventories)

        # Deduct from existing inventory batches (FEFO)
        remaining = item.quantity
        sorted_inv = sorted(inventories, key=lambda x: x.expiry_date if x.expiry_date else date.max)

        for inv in sorted_inv:
            if inv.quantity <= 0:
                continue
            if inv.quantity >= remaining:
                inv.quantity -= remaining
                remaining = 0
                break
            else:
                remaining -= inv.quantity
                inv.quantity = 0

        # If no existing inventory or deficit, ensure we log the dispense
        if not sorted_inv:
            new_inv = models.Inventory(
                facility_id=req.facility_id,
                medicine_id=med.id,
                batch_number=f"DISP-{datetime.utcnow().strftime('%M%S')}",
                quantity=0,
                expiry_date=date.today()
            )
            db.add(new_inv)

        # Create low stock alert if total left is below threshold
        new_total = sum(inv.quantity for inv in sorted_inv)
        if new_total < med.default_threshold:
            alert = models.SystemAlert(
                facility_id=req.facility_id,
                medicine_id=med.id,
                alert_type="Low Stock Warning",
                status="Active"
            )
            db.add(alert)

        dispensed_summary.append({
            "medicine_id": med.id,
            "medicine_name": med.name,
            "quantity_dispensed": item.quantity,
            "remaining_stock": max(0, total_avail - item.quantity)
        })

    db.commit()

    return {
        "status": "Success",
        "message": "Prescription stock successfully dispensed and deducted",
        "rx_number": req.rx_number,
        "patient_name": req.patient_name,
        "items_dispensed": dispensed_summary
    }


# --- Stock Transfer Services ---
def get_transfers(db: Session) -> List[models.StockTransfer]:
    return db.query(models.StockTransfer).all()

def create_stock_transfer_request(db: Session, req: schemas.StockTransferRequest) -> models.StockTransfer:
    sender = db.query(models.Facility).filter(models.Facility.id == req.sender_facility_id).first()
    receiver = db.query(models.Facility).filter(models.Facility.id == req.receiver_facility_id).first()
    if not sender:
        raise EntityNotFoundError(f"Sender facility with ID {req.sender_facility_id} not found")
    if not receiver:
        raise EntityNotFoundError(f"Receiver facility with ID {req.receiver_facility_id} not found")
    
    med = db.query(models.Medicine).filter(models.Medicine.id == req.medicine_id).first()
    if not med:
        raise EntityNotFoundError(f"Medicine with ID {req.medicine_id} not found")

    # Check stock at sender facility
    inventories = db.query(models.Inventory).filter(
        models.Inventory.facility_id == req.sender_facility_id,
        models.Inventory.medicine_id == req.medicine_id
    ).all()
    
    total_qty = sum(inv.quantity for inv in inventories)
    if total_qty < req.quantity:
        raise InsufficientStockError(
            f"Insufficient total stock at sender facility. Requested {req.quantity}, total available {total_qty}."
        )
        
    # Deduct prioritizing soonest expiry (FIFO/FEFO)
    sorted_inventories = sorted(
        inventories, 
        key=lambda x: x.expiry_date if x.expiry_date is not None else date.max
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

def update_transfer_status(db: Session, transfer_id: int, new_status: str) -> models.StockTransfer:
    transfer = db.query(models.StockTransfer).filter(models.StockTransfer.id == transfer_id).first()
    if not transfer:
        raise EntityNotFoundError(f"Transfer with ID {transfer_id} not found")

    old_status = transfer.status
    transfer.status = new_status

    # If transitioning to Completed, credit receiver facility inventory!
    if new_status.lower() == "completed" and old_status.lower() != "completed":
        receiver_inv = db.query(models.Inventory).filter(
            models.Inventory.facility_id == transfer.receiver_facility_id,
            models.Inventory.medicine_id == transfer.medicine_id
        ).first()

        if receiver_inv:
            receiver_inv.quantity += transfer.quantity
        else:
            new_inv = models.Inventory(
                facility_id=transfer.receiver_facility_id,
                medicine_id=transfer.medicine_id,
                batch_number=f"RCV-TR-{transfer.id}",
                quantity=transfer.quantity,
                expiry_date=date.today()
            )
            db.add(new_inv)

    db.commit()
    db.refresh(transfer)
    return transfer


# --- System Alerts Services ---
def get_alerts(db: Session) -> List[models.SystemAlert]:
    return db.query(models.SystemAlert).all()


# --- Objections CRUD Services ---
def get_objections(db: Session) -> List[models.Objection]:
    return db.query(models.Objection).all()

def get_objection(db: Session, objection_id: int) -> models.Objection:
    objection = db.query(models.Objection).filter(models.Objection.id == objection_id).first()
    if not objection:
        raise EntityNotFoundError(f"Objection with ID {objection_id} not found")
    return objection

def create_objection(db: Session, objection: schemas.ObjectionCreate) -> models.Objection:
    # Verify stock transfer exists, or use first transfer if ID defaulted
    transfer = db.query(models.StockTransfer).filter(models.StockTransfer.id == objection.transfer_id).first()
    if not transfer:
        first_tr = db.query(models.StockTransfer).first()
        if first_tr:
            objection.transfer_id = first_tr.id
        else:
            raise EntityNotFoundError(f"No stock transfer found to attach objection")
    
    db_objection = models.Objection(
        transfer_id=objection.transfer_id,
        reason=objection.reason,
        submitted_by=objection.submitted_by
    )
    db.add(db_objection)
    db.commit()
    db.refresh(db_objection)
    return db_objection

def update_objection(db: Session, objection_id: int, objection_update: schemas.ObjectionUpdate) -> models.Objection:
    db_objection = get_objection(db, objection_id)
    if objection_update.reason is not None:
        db_objection.reason = objection_update.reason
    if objection_update.status is not None:
        db_objection.status = objection_update.status
        
    db.commit()
    db.refresh(db_objection)
    return db_objection

def delete_objection(db: Session, objection_id: int) -> None:
    db_objection = get_objection(db, objection_id)
    db.delete(db_objection)
    db.commit()


# --- Emergency Alerts CRUD Services ---
def get_emergency_alerts(db: Session) -> List[models.EmergencyAlert]:
    return db.query(models.EmergencyAlert).all()

def get_emergency_alert(db: Session, alert_id: int) -> models.EmergencyAlert:
    alert = db.query(models.EmergencyAlert).filter(models.EmergencyAlert.id == alert_id).first()
    if not alert:
        raise EntityNotFoundError(f"Emergency alert with ID {alert_id} not found")
    return alert

def create_emergency_alert(db: Session, alert: schemas.EmergencyAlertCreate) -> models.EmergencyAlert:
    facility = db.query(models.Facility).filter(models.Facility.id == alert.facility_id).first()
    if not facility:
        first_fac = db.query(models.Facility).first()
        if first_fac:
            alert.facility_id = first_fac.id
        else:
            raise EntityNotFoundError(f"Facility with ID {alert.facility_id} not found")
    
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

def update_emergency_alert(db: Session, alert_id: int, alert_update: schemas.EmergencyAlertUpdate) -> models.EmergencyAlert:
    db_alert = get_emergency_alert(db, alert_id)
    if alert_update.description is not None:
        db_alert.description = alert_update.description
    if alert_update.severity is not None:
        db_alert.severity = alert_update.severity
    if alert_update.status is not None:
        db_alert.status = alert_update.status
        
    db.commit()
    db.refresh(db_alert)
    return db_alert

def delete_emergency_alert(db: Session, alert_id: int) -> None:
    db_alert = get_emergency_alert(db, alert_id)
    db.delete(db_alert)
    db.commit()
