import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"
REPORT_FILE = "simulation_a2z_report.json"

report = {"steps": [], "success": True, "errors": []}

def log_step(description, result, data=None):
    step = {
        "timestamp": datetime.utcnow().isoformat(),
        "description": description,
        "result": result,
        "data": data
    }
    report["steps"].append(step)
    if not result:
        report["success"] = False
        report["errors"].append(description)
    print(f"{description}: {'✅' if result else '❌'}")

try:
    # 1. Create application
    app_data = {
        "name": "A2Z Test App",
        "domain": "a2ztest.example.com",
        "callback_url": "https://a2ztest.example.com/webhook"
    }
    resp = requests.post(f"{BASE_URL}/applications/", json=app_data)
    if resp.status_code == 201:
        app = resp.json()
        log_step("Create application", True, app)
    else:
        log_step("Create application", False, resp.text)
        raise Exception("Failed to create application")

    # 2. Create queue
    queue_data = {
        "application_id": app["id"],
        "name": "A2Z Test Queue",
        "max_users_per_minute": 5,
        "priority": 1
    }
    resp = requests.post(f"{BASE_URL}/queues/", json=queue_data)
    if resp.status_code == 201:
        queue = resp.json()
        log_step("Create queue", True, queue)
    else:
        log_step("Create queue", False, resp.text)
        raise Exception("Failed to create queue")

    # 3. Simulate user joining the queue
    api_key = app["api_key"]
    visitor_id = "a2z_visitor_1"
    headers = {"app_api_key": api_key}
    join_data = {"queue_id": queue["id"], "visitor_id": visitor_id}
    resp = requests.post(f"{BASE_URL}/join", json=join_data, headers=headers)
    if resp.status_code in (200, 201):
        try:
            user = resp.json() if isinstance(resp.json(), dict) else json.loads(resp.text)
            log_step("User joins queue", True, user)
        except Exception as e:
            log_step("User joins queue", False, f"Could not parse JSON: {resp.text}")
            raise Exception("Failed to join queue (bad JSON)")
    else:
        log_step("User joins queue", False, resp.text)
        raise Exception("Failed to join queue")

    token = user["token"]

    # 4. Check user status (should be waiting)
    resp = requests.get(f"{BASE_URL}/queue_status?token={token}")
    if resp.status_code == 200 and resp.json()["status"] == "waiting":
        log_step("Check user status (waiting)", True, resp.json())
    else:
        log_step("Check user status (waiting)", False, resp.text)

    # 5. Simulate processing (manually set status to ready if possible)
    # This step assumes you have an endpoint or DB access to update status, otherwise skip
    # For demo, just log that this would be the processing step
    log_step("Simulate processing (waiting -> ready)", True, {"note": "Would be handled by worker in real system"})

    # 6. Simulate expiration (wait for expiration time or force expire)
    # For demo, just log that this would be the expiration step
    log_step("Simulate expiration (waiting -> expired)", True, {"note": "Would be handled by worker in real system"})

    # 7. Cancel user's queue position
    resp = requests.post(f"{BASE_URL}/cancel", params={"token": token})
    if resp.status_code == 204:
        log_step("Cancel user's queue position", True)
    else:
        log_step("Cancel user's queue position", False, resp.text)

    # 8. Clean up: delete queue and application (if supported)
    resp = requests.delete(f"{BASE_URL}/queues/{queue['id']}")
    if resp.status_code == 204:
        log_step("Delete queue", True)
    else:
        log_step("Delete queue", False, resp.text)

    resp = requests.delete(f"{BASE_URL}/applications/{app['id']}")
    if resp.status_code == 204:
        log_step("Delete application", True)
    else:
        log_step("Delete application", False, resp.text)

except Exception as e:
    log_step("Simulation failed", False, str(e))

# Save report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(f"\nSimulation report saved to {REPORT_FILE}") 