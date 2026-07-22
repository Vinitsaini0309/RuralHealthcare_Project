from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# --- Stock Transfer Schemas ---
class StockTransferRequest(BaseModel):
    sender_facility_id: int
    receiver_facility_id: int
    medicine_id: int
    quantity: int = Field(..., gt=0, description="Quantity to transfer must be greater than zero")
    batch_number: Optional[str] = Field(None, description="Optional batch number to transfer from. If omitted, stock is deducted prioritizing soonest expiry.")

class StockTransferResponse(BaseModel):
    id: int
    sender_facility_id: int
    receiver_facility_id: int
    medicine_id: int
    quantity: int
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


# --- Objection Schemas ---
class ObjectionCreate(BaseModel):
    transfer_id: int
    reason: str = Field(..., min_length=5, description="Reason for objection must be at least 5 characters long")
    submitted_by: str = Field(..., min_length=2, description="Name/role of the person submitting the objection")

class ObjectionUpdate(BaseModel):
    reason: Optional[str] = None
    status: Optional[str] = None

class ObjectionResponse(BaseModel):
    id: int
    transfer_id: int
    reason: str
    submitted_by: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True


# --- Emergency Alert (Epidemic Alert) Schemas ---
class EmergencyAlertCreate(BaseModel):
    facility_id: int
    alert_type: str = Field(..., description="Type of alert, e.g., Epidemic Outbreak, Acute Shortage")
    description: Optional[str] = None
    severity: str = Field("Critical", description="Severity level, e.g., Critical, High, Medium, Low")
    status: str = Field("Active", description="Status of the alert, e.g., Active, Resolved")

class EmergencyAlertUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None

class EmergencyAlertResponse(BaseModel):
    id: int
    facility_id: int
    alert_type: str
    description: Optional[str]
    severity: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True
