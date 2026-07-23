
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    role: str = Field(..., description="User role, e.g. WAREHOUSE_ADMIN, HEALTHCARE_WORKER, DOCTOR, PHARMACY, PATIENT")
    username: str = Field(..., description="Facility ID or username")
    password: str = Field(..., description="Password credential")

class LoginResponse(BaseModel):
    status: str
    message: str
    role: str
    username: str
    facility_id: Optional[int] = None
    redirect_url: str


# --- Stock Transfer Schemas ---
class StockTransferRequest(BaseModel):
    sender_facility_id: int
    receiver_facility_id: int
    medicine_id: int
    quantity: int = Field(..., gt=0, description="Quantity to transfer must be greater than zero")
    batch_number: Optional[str] = Field(None, description="Optional batch number to transfer from. If omitted, stock is deducted prioritizing soonest expiry.")

class TransferStatusUpdate(BaseModel):
    status: str = Field(..., description="New status, e.g., Transit, Completed, Cancelled")

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


# --- Dispense Schemas ---
class DispenseItem(BaseModel):
    medicine_id: Optional[int] = None
    medicine_name: Optional[str] = None
    quantity: int = Field(..., gt=0)

class DispenseRequest(BaseModel):
    facility_id: int
    patient_name: str
    rx_number: str
    items: List[DispenseItem]

class DispenseResponse(BaseModel):
    status: str
    message: str
    rx_number: str
    patient_name: str
    items_dispensed: List[dict]


# --- Objection Schemas ---
class ObjectionCreate(BaseModel):
    transfer_id: int
    reason: str = Field(..., min_length=3, description="Reason for objection")
    submitted_by: str = Field(..., min_length=2, description="Name/role of person submitting objection")

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
