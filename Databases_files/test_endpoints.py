import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_request(url, method="GET", payload=None):
    headers = {}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            response_body = response.read().decode('utf-8')
            return status_code, json.loads(response_body) if response_body else None
    except urllib.error.HTTPError as e:
        response_body = e.read().decode('utf-8')
        try:
            body_json = json.loads(response_body)
        except:
            body_json = response_body
        return e.code, body_json
    except Exception as e:
        print(f"Connection error: {e}")
        return None, str(e)


def run_tests():
    print("=== Testing Healthcare Services API endpoints ===")

    # Test 1: Get basic inventory level of Paracetamol (id 1) at Warehouse (id 1)
    print("\n[Test 1] Checking initial Warehouse Paracetamol stock...")
    status, inventory = make_request(f"{BASE_URL}/inventory")
    if status != 200:
        print(f"Failed to fetch inventory. Status: {status}")
        sys.exit(1)
        
    warehouse_para = next((item for item in inventory if item['facility_id'] == 1 and item['medicine_id'] == 1), None)
    if not warehouse_para:
        print("Warehouse Paracetamol stock not found in inventory!")
        sys.exit(1)
    
    initial_qty = warehouse_para['quantity']
    print(f"Initial quantity of Paracetamol at Warehouse: {initial_qty}")

    # Test 2: Request inter-facility transfer (Warehouse -> PHC Khedbrahma)
    print("\n[Test 2] Requesting inter-facility transfer...")
    transfer_payload = {
        "sender_facility_id": 1,
        "receiver_facility_id": 2,
        "medicine_id": 1,
        "quantity": 150
    }
    status, transfer = make_request(f"{BASE_URL}/api/transfer/request", method="POST", payload=transfer_payload)
    if status != 201:
        print(f"Failed to request transfer. Status: {status}, Detail: {transfer}")
        sys.exit(1)
    
    transfer_id = transfer['id']
    print(f"Transfer request created successfully! ID: {transfer_id}, Status: {transfer['status']}")

    # Test 3: Verify stock deduction at Warehouse
    print("\n[Test 3] Verifying stock deduction...")
    status, inventory = make_request(f"{BASE_URL}/inventory")
    warehouse_para = next((item for item in inventory if item['facility_id'] == 1 and item['medicine_id'] == 1), None)
    new_qty = warehouse_para['quantity']
    print(f"New quantity of Paracetamol at Warehouse: {new_qty}")
    if initial_qty - new_qty == 150:
        print("Stock successfully deducted (decreased by 150 units).")
    else:
        print(f"Stock mismatch! Expected deduction of 150, but got {initial_qty - new_qty}")
        sys.exit(1)

    # Test 4: Request transfer exceeding stock (expect failure)
    print("\n[Test 4] Requesting transfer exceeding available stock...")
    over_payload = {
        "sender_facility_id": 1,
        "receiver_facility_id": 2,
        "medicine_id": 1,
        "quantity": 50000
    }
    status, detail = make_request(f"{BASE_URL}/api/transfer/request", method="POST", payload=over_payload)
    if status == 400:
        print(f"Transfer rejected as expected: HTTP {status}, Detail: {detail.get('detail')}")
    else:
        print(f"Expected HTTP 400, but got HTTP {status}. Detail: {detail}")
        sys.exit(1)

    # Test 5: CRUD Objections
    print("\n[Test 5] Creating an Objection...")
    objection_payload = {
        "transfer_id": transfer_id,
        "reason": "Cold chain verification required for transportation route.",
        "submitted_by": "Dr. Ramesh Patel (PHC Officer)"
    }
    status, objection = make_request(f"{BASE_URL}/objections", method="POST", payload=objection_payload)
    if status != 201:
        print(f"Failed to submit objection. Status: {status}, Detail: {objection}")
        sys.exit(1)
    
    objection_id = objection['id']
    print(f"Objection created with ID: {objection_id}, Status: {objection['status']}")

    print("\n[Test 5.1] Reading the Objection...")
    status, fetched_objection = make_request(f"{BASE_URL}/objections/{objection_id}")
    if status != 200:
        print(f"Failed to read objection. Status: {status}")
        sys.exit(1)
    print(f"Objection details: Submitted by: {fetched_objection['submitted_by']}, Reason: {fetched_objection['reason']}")

    print("\n[Test 5.2] Updating the Objection status...")
    update_payload = {
        "status": "Reviewed",
        "reason": "Cold chain verified. Route approved."
    }
    status, updated_objection = make_request(f"{BASE_URL}/objections/{objection_id}", method="PUT", payload=update_payload)
    if status != 200:
        print(f"Failed to update objection. Status: {status}")
        sys.exit(1)
    print(f"Objection status updated to: {updated_objection['status']}, New Reason: {updated_objection['reason']}")

    print("\n[Test 5.3] Deleting the Objection...")
    status, response = make_request(f"{BASE_URL}/objections/{objection_id}", method="DELETE")
    if status != 204:
        print(f"Failed to delete objection. Status: {status}")
        sys.exit(1)
    print("Objection deleted successfully.")

    # Test 6: CRUD Emergency Alerts (Epidemic Alerts)
    print("\n[Test 6] Creating an Emergency Alert (Epidemic Outbreak)...")
    alert_payload = {
        "facility_id": 4, # Bhiloda CHC
        "alert_type": "Epidemic Outbreak - Dengue Fever",
        "description": "Sudden spike of 20 Dengue cases recorded in Bhiloda Taluka within 48 hours. URGENT supply of paracetamol and IV fluids required.",
        "severity": "Critical"
    }
    status, alert = make_request(f"{BASE_URL}/emergency-alerts", method="POST", payload=alert_payload)
    if status != 201:
        print(f"Failed to trigger emergency alert. Status: {status}, Detail: {alert}")
        sys.exit(1)
    
    alert_id = alert['id']
    print(f"Emergency alert triggered! ID: {alert_id}, Alert: {alert['alert_type']}, Severity: {alert['severity']}")

    print("\n[Test 6.1] Reading the Emergency Alert...")
    status, fetched_alert = make_request(f"{BASE_URL}/emergency-alerts/{alert_id}")
    if status != 200:
        print(f"Failed to read alert. Status: {status}")
        sys.exit(1)
    print(f"Fetched alert: {fetched_alert['alert_type']} - Status: {fetched_alert['status']}")

    print("\n[Test 6.2] Updating Emergency Alert status...")
    alert_update_payload = {
        "status": "Resolved",
        "description": "Stock supplied. Dengue outbreak controlled. Patient count stabilized."
    }
    status, updated_alert = make_request(f"{BASE_URL}/emergency-alerts/{alert_id}", method="PUT", payload=alert_update_payload)
    if status != 200:
        print(f"Failed to update alert. Status: {status}")
        sys.exit(1)
    print(f"Alert updated! Status: {updated_alert['status']}, Description: {updated_alert['description']}")

    print("\n[Test 6.3] Deleting Emergency Alert...")
    status, response = make_request(f"{BASE_URL}/emergency-alerts/{alert_id}", method="DELETE")
    if status != 204:
        print(f"Failed to delete alert. Status: {status}")
        sys.exit(1)
    print("Emergency alert deleted successfully.")

    print("\n==============================================")
    print("ALL API ENDPOINT AND CRUD TESTS PASSED SUCCESSFULLY!")
    print("==============================================")

if __name__ == "__main__":
    run_tests()
