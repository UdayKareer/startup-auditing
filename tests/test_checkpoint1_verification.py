"""
Checkpoint 1 Master Verification Suite
Validates:
1. Module 1: SQLite Multi-Source Ingestion & Sub-0.5s Latency
2. Module 2: FastAPI Parallel Verification Router (<2.0s) & Endpoints (/inflow-match, /gst-verify, /related-party, /runway-calc)
3. Module 3: Deterministic Forensic Engine (Shinrai Health Score 0-100)
4. Module 4: 4-Sample Integrity (Clean, Fraud, LogiPulse, Mirai) & ReportLab Bilingual Memo Generation
"""

import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app, load_startup_bundle
from backend.ingestion import ingest_to_sqlite
from backend.forensic_rules import execute_forensic_audit
from export.memo_generator import generate_ringi_sho_pdf

client = TestClient(app)


def test_module1_sqlite_ingestion():
    """Verify SQLite ingestion executes in <500ms and loads all tables."""
    res = ingest_to_sqlite("clean_startup")
    assert res["status"] == "INGESTION_SUCCESS"
    assert res["latency_ms"] < 500.0
    assert res["rows_ingested"]["bank_transactions"] > 900
    assert res["rows_ingested"]["gst_invoices"] > 0
    assert res["rows_ingested"]["mca_directors"] > 0


def test_module2_inflow_match_clean_and_fraud():
    """Verify inflow match flags divergence and circular billing."""
    # Clean
    r_clean = client.post("/inflow-match?preset_key=clean_startup")
    assert r_clean.status_code == 200
    d_clean = r_clean.json()
    assert d_clean["status"] == "COMPLIANT"
    assert d_clean["deposit_match_pct"] > 95.0
    assert d_clean["circular_billing_detected"] is False

    # Fraud
    r_fraud = client.post("/inflow-match?preset_key=fraud_startup")
    assert r_fraud.status_code == 200
    d_fraud = r_fraud.json()
    assert d_fraud["status"] == "DIVERGENCE_DETECTED"
    assert d_fraud["deposit_match_pct"] < 50.0
    assert d_fraud["circular_billing_detected"] is True
    assert d_fraud["round_tripping_amount_inr"] > 0


def test_module2_gst_verify():
    """Verify GST Rule 88C DRC-01B notice detection."""
    r = client.post("/gst-verify?preset_key=fraud_startup")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "RULE_88C_VIOLATION_DRC01B"
    assert d["rule_88c_drc01b_notice_triggered"] is True
    assert d["unremitted_gst_dues_inr"] > 1000000.0


def test_module2_related_party():
    """Verify Section 188 Director PAN conflict and Shell Outflow Ratio."""
    r = client.post("/related-party?preset_key=fraud_startup")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "FLAGGED"
    assert d["conflict_detected"] is True
    assert d["total_siphoned_inr"] == 4130000.0
    assert d["shell_outflow_ratio"] > 0.05


def test_module2_runway_calc():
    """Verify Net Real Runway deductions."""
    r = client.post("/runway-calc?preset_key=clean_startup")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "HEALTHY"
    assert d["net_real_runway_months"] >= 10.0


def test_module2_parallel_verification_router():
    """Verify parallel execution runs in <2000ms."""
    r = client.post("/parallel-verify?preset_key=fraud_startup")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "PARALLEL_VERIFICATION_COMPLETE"
    assert d["total_parallel_latency_ms"] < 2000.0
    assert "inflow_match" in d["module_results"]
    assert "gst_verify" in d["module_results"]
    assert "related_party" in d["module_results"]
    assert "runway_calc" in d["module_results"]


def test_module3_all_four_presets_integrity():
    """Verify all 4 startup presets evaluate deterministically without errors."""
    expected = {
        "clean_startup": {"min_score": 85, "badge": "[適格]"},
        "fraud_startup": {"max_score": 35, "badge": "[精査要]"},
        "logipulse_startup": {"max_score": 65, "badge": "[精査要]"},
        "mirai_startup": {"min_score": 85, "badge": "[適格]"}
    }
    for preset, rules in expected.items():
        rebit, gst, mca, claims, ca = load_startup_bundle(preset)
        res = execute_forensic_audit(rebit, gst, mca, claims, ca)
        score = res["kpis"]["governance_trust_score"]
        if "min_score" in rules:
            assert score >= rules["min_score"], f"{preset} score {score} < {rules['min_score']}"
        if "max_score" in rules:
            assert score <= rules["max_score"], f"{preset} score {score} > {rules['max_score']}"
        assert res["kpis"]["kanji_badge"] == rules["badge"]


def test_module4_bilingual_ringi_sho_pdf_generation():
    """Verify 1-page Japanese/English Ringi-sho PDF renders properly."""
    rebit, gst, mca, claims, ca = load_startup_bundle("clean_startup")
    res = execute_forensic_audit(rebit, gst, mca, claims, ca)
    out_pdf = "export/test_checkpoint1_ringi_sho.pdf"
    pdf_path = generate_ringi_sho_pdf(res, out_pdf)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
