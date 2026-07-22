from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'Warehouse' or 'PHC'
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    contact = Column(String)

    # Relationships
    inventories = relationship("Inventory", back_populates="facility")
    sent_transfers = relationship("StockTransfer", foreign_keys="[StockTransfer.sender_facility_id]", back_populates="sender")
    received_transfers = relationship("StockTransfer", foreign_keys="[StockTransfer.receiver_facility_id]", back_populates="receiver")
    alerts = relationship("SystemAlert", back_populates="facility")
    emergency_alerts = relationship("EmergencyAlert", back_populates="facility")


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    unit_type = Column(String)
    default_threshold = Column(Integer, default=100)

    # Relationships
    inventories = relationship("Inventory", back_populates="medicine")
    transfers = relationship("StockTransfer", back_populates="medicine")
    alerts = relationship("SystemAlert", back_populates="medicine")


class Inventory(Base):
    __tablename__ = "inventories"

    facility_id = Column(Integer, ForeignKey("facilities.id"), primary_key=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), primary_key=True)
    batch_number = Column(String, primary_key=True)
    quantity = Column(Integer, default=0)
    expiry_date = Column(Date)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="inventories")
    medicine = relationship("Medicine", back_populates="inventories")


class StockTransfer(Base):
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True, index=True)
    sender_facility_id = Column(Integer, ForeignKey("facilities.id"))
    receiver_facility_id = Column(Integer, ForeignKey("facilities.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="Pending")  # e.g., Pending, Transit, Completed, Cancelled
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    sender = relationship("Facility", foreign_keys=[sender_facility_id], back_populates="sent_transfers")
    receiver = relationship("Facility", foreign_keys=[receiver_facility_id], back_populates="received_transfers")
    medicine = relationship("Medicine", back_populates="transfers")
    objections = relationship("Objection", back_populates="transfer", cascade="all, delete-orphan")


class SystemAlert(Base):
    __tablename__ = "system_alerts"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=True)
    alert_type = Column(String, nullable=False)  # e.g., Low Stock, Expiring Soon, Expired
    status = Column(String, default="Active")  # e.g., Active, Resolved
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="alerts")
    medicine = relationship("Medicine", back_populates="alerts")


class Objection(Base):
    __tablename__ = "objections"

    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("stock_transfers.id"), nullable=False)
    reason = Column(String, nullable=False)
    submitted_by = Column(String, nullable=False)
    status = Column(String, default="Pending")  # e.g., Pending, Reviewed, Resolved
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    transfer = relationship("StockTransfer", back_populates="objections")


class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facilities.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # e.g., Epidemic Outbreak, Acute Shortage
    description = Column(String)
    severity = Column(String, default="Critical")  # e.g., Critical, High, Medium, Low
    status = Column(String, default="Active")  # e.g., Active, Resolved
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    facility = relationship("Facility", back_populates="emergency_alerts")
