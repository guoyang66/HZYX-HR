"""E2E test: Upload PDF + Match all positions"""
import time, requests, sys

BASE = "http://localhost:8080"

# Login
r = requests.post(f"{BASE}/api/auth/login", json={"username": "hr_admin", "password": "password"})
token = r.json()["data"]["accessToken"]
print("Login OK")

# Upload PDF
pdf_path = r"C:\Users\guoya\Desktop\呙钖-.pdf"
print(f"Uploading PDF ({pdf_path})...")
start = time.time()
with open(pdf_path, "rb") as f:
    r = requests.post(
        f"{BASE}/api/hr/resumes/upload",
        files={"file": ("呙钖-.pdf", f, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
elapsed = time.time() - start
data = r.json()["data"]
resume_id = data["resumeId"]
print(f"Upload: {elapsed:.1f}s, id={resume_id}, skills={len(data['extractedSkills'])}")
print(f"  Sample skills: {data['extractedSkills'][:10]}")

# Match against all positions
print(f"\nMatching resume {resume_id} against all positions...")
start = time.time()
r = requests.post(
    f"{BASE}/api/hr/match/resume/{resume_id}/positions",
    headers={"Authorization": f"Bearer {token}"},
    timeout=300,
)
elapsed = time.time() - start
results = r.json()["data"]
print(f"Match: {elapsed:.1f}s, {len(results)} positions matched")

# Top 5 results
sorted_results = sorted(results, key=lambda x: x.get("finalScore", 0), reverse=True)
print("\nTop 5 Matches:")
for i, m in enumerate(sorted_results[:5]):
    print(f"  #{i+1}: {m['positionTitle']} | Score: {m['finalScore']} | Grade: {m['matchGrade']} | Recommend: {m['recommendLevel']}")
    print(f"    Matched: {m.get('matchedSkills', [])[:5]}")
    print(f"    Missing: {m.get('missingSkills', [])[:5]}")
    print()

print("FULL FLOW COMPLETE: Upload -> Parse -> Match -> Results")
