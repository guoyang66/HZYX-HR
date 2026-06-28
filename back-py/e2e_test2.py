"""E2E test with verbose logging"""
import time, requests

BASE = "http://localhost:8080"

r = requests.post(f"{BASE}/api/auth/login", json={"username": "hr_admin", "password": "password"})
token = r.json()["data"]["accessToken"]

# Get position count
r = requests.get(f"{BASE}/api/hr/positions/all", headers={"Authorization": f"Bearer {token}"})
positions = r.json()["data"]
print(f"Positions: {len(positions)}")

# Upload
print("Uploading...")
start = time.time()
with open(r"C:\Users\guoya\Desktop\呙钖-.pdf", "rb") as f:
    r = requests.post(
        f"{BASE}/api/hr/resumes/upload",
        files={"file": ("resume.pdf", f, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
rid = r.json()["data"]["resumeId"]
print(f"Upload ID={rid} in {time.time()-start:.1f}s")

# Match ONE position first to verify
print("\nMatching single position (id=1)...")
start = time.time()
r = requests.post(
    f"{BASE}/api/hr/match",
    json={"resumeId": rid, "positionId": 1},
    headers={"Authorization": f"Bearer {token}"},
    timeout=60,
)
print(f"Single match OK: score={r.json()['data']['finalScore']} grade={r.json()['data']['matchGrade']}")

# Match ALL positions
print(f"\nMatching all {len(positions)} positions...")
start = time.time()
r = requests.post(
    f"{BASE}/api/hr/match/resume/{rid}/positions",
    headers={"Authorization": f"Bearer {token}"},
    timeout=300,
)
elapsed = time.time() - start
results = r.json()["data"]
print(f"Batch match: {elapsed:.1f}s, {len(results)}/{len(positions)} matched")

if results:
    top = sorted(results, key=lambda x: x.get("finalScore", 0), reverse=True)[:5]
    for i, m in enumerate(top):
        print(f"  #{i+1}: {m['positionTitle']} | {m['finalScore']} | {m['matchGrade']}")
