import datetime
from database import engine, SessionLocal, Base
import models

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data to allow re-seeding
        db.query(models.SystemAlert).delete()
        db.query(models.StockTransfer).delete()
        db.query(models.Inventory).delete()
        db.query(models.Medicine).delete()
        db.query(models.Facility).delete()
        db.commit()
        print("Cleared existing database tables.")

        # 1. Seed Facilities (1 Central Warehouse, 4 Rural PHCs)
        facilities = [
            models.Facility(
                name="Central Pharmaceutical Warehouse",
                type="Warehouse",
                address="Distributor Zone, Sector 4, Regional Capital",
                lat=23.0225,
                lng=72.5714,
                contact="+91 99999 11111"
            ),
            models.Facility(
                name="Khedbrahma Primary Health Centre",
                type="PHC",
                address="Main Road, Khedbrahma, Sabarkantha District",
                lat=24.0298,
                lng=73.0463,
                contact="+91 99999 22222"
            ),
            models.Facility(
                name="Vijaynagar Rural Clinic",
                type="PHC",
                address="Near Market Yard, Vijaynagar",
                lat=23.9782,
                lng=73.2704,
                contact="+91 99999 33333"
            ),
            models.Facility(
                name="Bhiloda Community Health Centre",
                type="PHC",
                address="Opposite Taluka Office, Bhiloda",
                lat=23.8872,
                lng=73.2558,
                contact="+91 99999 44444"
            ),
            models.Facility(
                name="Poshina Health Centre",
                type="PHC",
                address="Vakhatpura Road, Poshina",
                lat=24.3820,
                lng=73.0182,
                contact="+91 99999 55555"
            ),
        ]
        db.add_all(facilities)
        db.commit()
        # Refresh to get IDs
        for f in facilities:
            db.refresh(f)
        print(f"Seeded {len(facilities)} facilities.")

        warehouse = facilities[0]
        phc_khedbrahma = facilities[1]
        phc_vijaynagar = facilities[2]
        phc_bhiloda = facilities[3]
        phc_poshina = facilities[4]

        # 2. Seed Medicines (8 items)
        medicines = [
            models.Medicine(name="Paracetamol 650mg", category="Analgesic", unit_type="Tablet", default_threshold=500),
            models.Medicine(name="Amoxicillin 500mg", category="Antibiotic", unit_type="Capsule", default_threshold=300),
            models.Medicine(name="ORS (Oral Rehydration Salts)", category="Rehydration", unit_type="Sachet", default_threshold=400),
            models.Medicine(name="Insulin Glargine", category="Antidiabetic", unit_type="Vial", default_threshold=50),
            models.Medicine(name="Metformin 500mg", category="Antidiabetic", unit_type="Tablet", default_threshold=600),
            models.Medicine(name="Artesunate 60mg Injection", category="Antimalarial", unit_type="Vial", default_threshold=30),
            models.Medicine(name="Albendazole 400mg", category="Antiparasitic", unit_type="Tablet", default_threshold=200),
            models.Medicine(name="Atenolol 50mg", category="Antihypertensive", unit_type="Tablet", default_threshold=400),
        ]
        db.add_all(medicines)
        db.commit()
        for m in medicines:
            db.refresh(m)
        print(f"Seeded {len(medicines)} medicines.")

        med_para = medicines[0]
        med_amox = medicines[1]
        med_ors = medicines[2]
        med_insulin = medicines[3]
        med_metformin = medicines[4]
        med_artesunate = medicines[5]
        med_alben = medicines[6]
        med_atenolol = medicines[7]

        # 3. Seed Inventory
        # Central Warehouse has massive stocks of everything
        today = datetime.date.today()
        inventories = [
            # Warehouse Inventory (High Stocks, multiple batches)
            models.Inventory(facility_id=warehouse.id, medicine_id=med_para.id, batch_number="WH-PARA-01", quantity=10000, expiry_date=today + datetime.timedelta(days=730)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_amox.id, batch_number="WH-AMOX-01", quantity=8000, expiry_date=today + datetime.timedelta(days=365)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_ors.id, batch_number="WH-ORS-01", quantity=15000, expiry_date=today + datetime.timedelta(days=540)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_insulin.id, batch_number="WH-INS-01", quantity=1200, expiry_date=today + datetime.timedelta(days=180)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_metformin.id, batch_number="WH-MET-01", quantity=20000, expiry_date=today + datetime.timedelta(days=730)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_artesunate.id, batch_number="WH-ART-01", quantity=500, expiry_date=today + datetime.timedelta(days=240)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_alben.id, batch_number="WH-ALB-01", quantity=6000, expiry_date=today + datetime.timedelta(days=365)),
            models.Inventory(facility_id=warehouse.id, medicine_id=med_atenolol.id, batch_number="WH-ATE-01", quantity=8000, expiry_date=today + datetime.timedelta(days=540)),

            # PHC 1: Khedbrahma (Healthy stock, but expiring batch of Amoxicillin)
            models.Inventory(facility_id=phc_khedbrahma.id, medicine_id=med_para.id, batch_number="KB-PARA-02", quantity=800, expiry_date=today + datetime.timedelta(days=400)),
            models.Inventory(facility_id=phc_khedbrahma.id, medicine_id=med_amox.id, batch_number="KB-AMOX-02", quantity=400, expiry_date=today + datetime.timedelta(days=15)),  # Expiring soon!
            models.Inventory(facility_id=phc_khedbrahma.id, medicine_id=med_ors.id, batch_number="KB-ORS-02", quantity=600, expiry_date=today + datetime.timedelta(days=300)),

            # PHC 2: Vijaynagar (Low stock of Paracetamol, Normal Metformin)
            models.Inventory(facility_id=phc_vijaynagar.id, medicine_id=med_para.id, batch_number="VN-PARA-03", quantity=200, expiry_date=today + datetime.timedelta(days=350)),  # Low stock (threshold 500)
            models.Inventory(facility_id=phc_vijaynagar.id, medicine_id=med_metformin.id, batch_number="VN-MET-02", quantity=800, expiry_date=today + datetime.timedelta(days=500)),
            models.Inventory(facility_id=phc_vijaynagar.id, medicine_id=med_ors.id, batch_number="VN-ORS-03", quantity=900, expiry_date=today + datetime.timedelta(days=200)),

            # PHC 3: Bhiloda (Critically low on Insulin, completely out of Artesunate)
            models.Inventory(facility_id=phc_bhiloda.id, medicine_id=med_insulin.id, batch_number="BH-INS-02", quantity=5, expiry_date=today + datetime.timedelta(days=90)),  # Low stock (threshold 50)
            models.Inventory(facility_id=phc_bhiloda.id, medicine_id=med_atenolol.id, batch_number="BH-ATE-02", quantity=500, expiry_date=today + datetime.timedelta(days=400)),

            # PHC 4: Poshina (Normal levels, but stock expiring)
            models.Inventory(facility_id=phc_poshina.id, medicine_id=med_para.id, batch_number="PO-PARA-04", quantity=600, expiry_date=today + datetime.timedelta(days=600)),
            models.Inventory(facility_id=phc_poshina.id, medicine_id=med_alben.id, batch_number="PO-ALB-02", quantity=10, expiry_date=today + datetime.timedelta(days=120)),  # Low stock (threshold 200)
        ]
        db.add_all(inventories)
        db.commit()
        print(f"Seeded {len(inventories)} inventory records.")

        # 4. Seed Stock Transfers
        transfers = [
            models.StockTransfer(
                sender_facility_id=warehouse.id,
                receiver_facility_id=phc_khedbrahma.id,
                medicine_id=med_para.id,
                quantity=1000,
                status="Completed",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=5)
            ),
            models.StockTransfer(
                sender_facility_id=warehouse.id,
                receiver_facility_id=phc_vijaynagar.id,
                medicine_id=med_para.id,
                quantity=500,
                status="Transit",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            models.StockTransfer(
                sender_facility_id=warehouse.id,
                receiver_facility_id=phc_bhiloda.id,
                medicine_id=med_insulin.id,
                quantity=100,
                status="Pending",
                timestamp=datetime.datetime.utcnow()
            )
        ]
        db.add_all(transfers)
        db.commit()
        print(f"Seeded {len(transfers)} stock transfer records.")

        # 5. Seed System Alerts (System logs/alerts)
        alerts = [
            # Low stock alerts based on inventory levels above
            models.SystemAlert(
                facility_id=phc_vijaynagar.id,
                medicine_id=med_para.id,
                alert_type="Low Stock Warning",
                status="Active",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=12)
            ),
            models.SystemAlert(
                facility_id=phc_bhiloda.id,
                medicine_id=med_insulin.id,
                alert_type="Critical Low Stock",
                status="Active",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            ),
            # Expiry warnings
            models.SystemAlert(
                facility_id=phc_khedbrahma.id,
                medicine_id=med_amox.id,
                alert_type="Near Expiry Alert",
                status="Active",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            models.SystemAlert(
                facility_id=phc_poshina.id,
                medicine_id=med_alben.id,
                alert_type="Low Stock Warning",
                status="Resolved",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            )
        ]
        db.add_all(alerts)
        db.commit()
        print(f"Seeded {len(alerts)} system alert records.")
        print("\nDatabase Seeding Completed Successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
