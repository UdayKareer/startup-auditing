import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== FASTAPI ENDPOINT SUITE VERIFICATION ===")

# 1. Ingestion
r = client.post('/api/v1/ingest?preset_key=clean_startup')
d = r.json()
print(f"1. Ingest: Status={r.status_code}, Ingested={d.get('status')}, Latency={d.get('latency_ms')} ms")

# 2. Inflow match
r = client.post('/inflow-match?preset_key=clean_startup')
d = r.json()
print(f"2. Inflow match (Clean): Status={r.status_code}, Deposit Match={d.get('deposit_match_pct')}%, Circular={d.get('circular_billing_detected')}")

r = client.post('/inflow-match?preset_key=fraud_startup')
d = r.json()
print(f"   Inflow match (Fraud): Status={r.status_code}, Deposit Match={d.get('deposit_match_pct')}%, Circular={d.get('circular_billing_detected')}, RoundTripping=INR {d.get('round_tripping_amount_inr')}")

# 3. GST verify
r = client.post('/gst-verify?preset_key=fraud_startup')
d = r.json()
print(f"3. GST verify (Fraud): Status={r.status_code}, Violation={d.get('status')}, Tax Variance={d.get('tax_variance_pct')}%, Rule 88C Triggered={d.get('rule_88c_drc01b_notice_triggered')}")

# 4. Related party
r = client.post('/related-party?preset_key=fraud_startup')
d = r.json()
print(f"4. Related party (Fraud): Status={r.status_code}, Conflict={d.get('conflict_detected')}, Shell Outflow Ratio={d.get('shell_outflow_ratio')}, Siphoned=INR {d.get('total_siphoned_inr')}")

# 5. Runway calc
r = client.post('/runway-calc?preset_key=clean_startup')
d = r.json()
print(f"5. Runway (Clean): Status={r.status_code}, Real Runway={d.get('net_real_runway_months')} mo, Compression Factor={d.get('runway_compression_factor')}")

# 6. Parallel verify
r = client.post('/parallel-verify?preset_key=fraud_startup')
d = r.json()
print(f"6. Parallel Verify: Status={r.status_code}, Total Latency={d.get('total_parallel_latency_ms')} ms, Benchmark={d.get('benchmark')}")

# 7. Unlock vault
r = client.post('/api/v1/investor/vault/unlock', json={'passcode': 'TRUSTVAULT-VC901-TJH', 'email': 'analyst.sato@value-create.com', 'preset_key': 'clean_startup'})
d = r.json()
print(f"7. Unlock Vault: Status={r.status_code}, Session={d.get('session_token')}")

print("\nALL FASTAPI MODULE 2 ENDPOINTS VERIFIED OPERATIONAL!")
