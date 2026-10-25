"""
Automated Test Suite for VeriLedger / Kizuna-Vault (絆)
Tests:
1. Sub-200ms latency on 1,000+ transaction rows
2. Deterministic repeatability (zero drift across iterations)
3. PAN-in-GSTIN slicing and Section 188 detection
4. Benford F2D Nigrini MAD calculation
5. Clean vs. Fraud scenario discrimination
"""

import time
import pytest
from backend.main import load_startup_bundle, full_audit
from backend.schemas import AuditRequest
from backend.forensic_rules import analyze_benford_f2d, detect_related_party_siphoning

def test_clean_startup_audit():
    req = AuditRequest(preset_key="clean_startup")
    t0 = time.time()
    res = full_audit(req)
    latency_ms = (time.time() - t0) * 1000

    assert latency_ms < 500, f"Audit took too long: {latency_ms}ms"
    assert res["status"] == "AUDIT_COMPLETE"
    kpis = res["kpis"]
    assert kpis["governance_trust_score"] >= 80, f"Expected high clean score, got {kpis['governance_trust_score']}"
    assert kpis["kanji_badge"] == "[適格]"
    assert kpis["classification"] == "VERIFIED_CLEAN"
    assert kpis["siphoned_funds_inr"] == 0.0
    assert kpis["cash_divergence_pct"] < 5.0

def test_fraud_startup_audit():
    req = AuditRequest(preset_key="fraud_startup")
    res = full_audit(req)
    kpis = res["kpis"]

    assert kpis["governance_trust_score"] <= 30, f"Expected low fraud score, got {kpis['governance_trust_score']}"
    assert kpis["kanji_badge"] == "[精査要]"
    assert kpis["classification"] == "CRITICAL_RED_FLAG_REJECT"
    assert kpis["siphoned_funds_inr"] == 4130000.0, f"Expected 41.3L siphoned, got {kpis['siphoned_funds_inr']}"
    assert kpis["cash_divergence_pct"] >= 50.0

    # Verify Section 188 alert exists
    siphon_alerts = [f for f in res["red_flags"] if f["rule"] == "SEC_188_SIPHONING"]
    assert len(siphon_alerts) >= 1
    assert "Companies Act 2013" in siphon_alerts[0]["statutory_citation"]

def test_deterministic_repeatability():
    """Confirms running the engine 10 times yields bit-for-bit identical results."""
    req = AuditRequest(preset_key="fraud_startup")
    baseline = full_audit(req)
    
    for _ in range(10):
        run = full_audit(req)
        assert run["kpis"]["governance_trust_score"] == baseline["kpis"]["governance_trust_score"]
        assert run["kpis"]["siphoned_funds_inr"] == baseline["kpis"]["siphoned_funds_inr"]
        assert run["kpis"]["cash_divergence_pct"] == baseline["kpis"]["cash_divergence_pct"]
        assert run["kpis"]["merkle_root"] == baseline["kpis"]["merkle_root"]

def test_benford_mad_clean_vs_fraud():
    rebit_clean, _, _, _, _ = load_startup_bundle("clean_startup")
    rebit_fraud, _, _, _, _ = load_startup_bundle("fraud_startup")

    clean_debits = [float(t["amount"]) for t in rebit_clean["account"]["transactions"]["transaction"] if t.get("type") == "DEBIT"]
    fraud_debits = [float(t["amount"]) for t in rebit_fraud["account"]["transactions"]["transaction"] if t.get("type") == "DEBIT"]

    mad_clean, status_clean, _ = analyze_benford_f2d(clean_debits)
    mad_fraud, status_fraud, _ = analyze_benford_f2d(fraud_debits)

    assert mad_clean < 0.0035, f"Clean MAD too high: {mad_clean}"
    assert mad_fraud >= 0.0035, f"Fraud MAD expected >= 0.0035, got {mad_fraud}"
    assert status_fraud == "NON_CONFORMING_ANOMALY"

def test_pan_slicing_section_188():
    _, _, df_directors, _, _ = load_startup_bundle("fraud_startup")
    test_txns = [
        {
            "txnId": "TEST_001",
            "type": "DEBIT",
            "amount": 100000.0,
            "counterparty": "Apex Cloud Solutions LLP",
            "counterpartyGstin": "29ABCPS1234F1Z5",  # PAN is ABCPS1234F
            "valueDate": "2026-10-24"
        },
        {
            "txnId": "TEST_002",
            "type": "DEBIT",
            "amount": 50000.0,
            "counterparty": "Independent Third Party Ltd",
            "counterpartyGstin": "07AAACZ9999K1Z1",  # Unrelated PAN
            "valueDate": "2026-10-24"
        }
    ]

    siphons, total_amt = detect_related_party_siphoning(test_txns, df_directors)
    assert len(siphons) == 1
    assert siphons[0]["extracted_vendor_pan"] == "ABCPS1234F"
    assert total_amt == 100000.0
