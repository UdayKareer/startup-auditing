import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from backend.main import app, load_startup_bundle, execute_forensic_audit, full_audit
from backend.schemas import AuditRequest
from backend.ingestion import resolve_preset_files, ingest_to_sqlite
from backend.registry_lookup import get_all_quick_fill_options, lookup_mca_entity
from export.memo_generator import generate_ringi_sho_pdf
import pypdf

client = TestClient(app)

ALL_PRESETS = [
    "clean_startup",
    "fraud_startup",
    "logipulse_startup",
    "mirai_startup",
    "edutrek_startup",
    "kwikpay_startup",
    "autocare_startup",
    "zenith_startup"
]


def test_resolve_and_verify_files_exist_all_seven_presets():
    """Verify all 5 source file paths resolve and exist on disk for each of the 7 presets."""
    mock_claims_path = os.path.join("data", "mock_claims.json")
    assert os.path.exists(mock_claims_path), "mock_claims.json must exist"
    
    import json
    with open(mock_claims_path, "r", encoding="utf-8") as f:
        mock_claims_data = json.load(f)

    for preset in ALL_PRESETS:
        assert preset in mock_claims_data, f"{preset} must be present in mock_claims.json"
        rebit_p, gst_p, ca_p, dir_p = resolve_preset_files(preset)
        for p in (rebit_p, gst_p, ca_p, dir_p):
            assert os.path.exists(p), f"File {p} for {preset} does not exist on disk"


def test_sqlite_ingestion_latency_all_seven_presets():
    """Verify SQLite ingestion executes cleanly in <500ms for each of the 7 presets."""
    for preset in ALL_PRESETS:
        t0 = time.perf_counter()
        res = ingest_to_sqlite(preset)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        assert res["status"] == "INGESTION_SUCCESS"
        assert res["rows_ingested"]["bank_transactions"] > 0
        assert latency_ms < 500.0, f"{preset} SQLite ingestion took {latency_ms:.1f}ms (threshold 500ms)"


def test_parallel_verification_router_all_seven_presets():
    """Verify FastAPI /parallel-verify endpoint executes in <2000ms for each of the 7 presets."""
    for preset in ALL_PRESETS:
        r = client.post(f"/parallel-verify?preset_key={preset}")
        assert r.status_code == 200, f"/parallel-verify failed for {preset}: {r.text}"
        data = r.json()
        assert data["status"] == "PARALLEL_VERIFICATION_COMPLETE"
        assert data["total_parallel_latency_ms"] < 2000.0
        assert "inflow_match" in data["module_results"]
        assert "gst_verify" in data["module_results"]
        assert "related_party" in data["module_results"]
        assert "runway_calc" in data["module_results"]


def test_forensic_audit_score_calibration_all_seven_presets():
    """Verify deterministic scoring invariants and Kanji badge classifications for all 7 presets."""
    rules = {
        "clean_startup": {"min_score": 85, "badge": "[適格]"},
        "fraud_startup": {"max_score": 35, "badge": "[精査要]"},
        "logipulse_startup": {"max_score": 65, "badge": "[精査要]"},
        "mirai_startup": {"min_score": 85, "badge": "[適格]"},
        "edutrek_startup": {"max_score": 35, "badge": "[精査要]"},
        "kwikpay_startup": {"max_score": 35, "badge": "[精査要]"},
        "autocare_startup": {"max_score": 35, "badge": "[精査要]"},
        "zenith_startup": {"min_score": 75, "max_score": 80, "badge": "[要確認]"},
    }

    for preset, rule in rules.items():
        rebit, gst, mca, claims, ca = load_startup_bundle(preset)
        res = execute_forensic_audit(rebit, gst, mca, claims, ca)
        score = res["kpis"]["governance_trust_score"]

        if "min_score" in rule:
            assert score >= rule["min_score"], f"{preset} score {score} < {rule['min_score']}"
        if "max_score" in rule:
            assert score <= rule["max_score"], f"{preset} score {score} > {rule['max_score']}"
        assert res["kpis"]["kanji_badge"] == rule["badge"], f"{preset} badge mismatch: got {res['kpis']['kanji_badge']}"


def test_edutrek_archetype_specific_findings():
    """Verify Edutrek Learning detects aggressive revenue, >180d debtors > ₹20 Cr, and Rule 88C GST gap."""
    rebit, gst, mca, claims, ca = load_startup_bundle("edutrek_startup")
    res = execute_forensic_audit(rebit, gst, mca, claims, ca)
    
    # Check doubtful debtors > 180 days (SA 505 / 240) in AR aging
    doubtful_debtors = res["working_capital_logistics"]["ar_aging"]["bucket_90_plus_days"]["amount_inr"]
    assert doubtful_debtors >= 200_000_000, f"Edutrek should flag >= ₹20 Cr doubtful debtors, got {doubtful_debtors}"
    
    # Check massive uncollected phantom revenue (> ₹20 Cr) and unremitted tax dues (> ₹4 Cr)
    assert res["kpis"]["phantom_revenue_inr"] >= 200_000_000, "Expected > ₹20 Cr phantom revenue gap"
    assert res["kpis"]["unremitted_tax_dues_inr"] >= 40_000_000, "Expected > ₹4 Cr unremitted GST tax dues"

    # Check red flags include STALE_RECEIVABLES and PHANTOM_REVENUE
    red_flag_rules = [rf.get("rule", "") for rf in res.get("red_flags", [])]
    assert "STALE_RECEIVABLES" in red_flag_rules
    assert "PHANTOM_REVENUE" in red_flag_rules


def test_kwikpay_archetype_specific_findings():
    """Verify KwikPay Digital detects Section 188 promoter siphoning to Madhuri Mehra and TDS smurfing."""
    rebit, gst, mca, claims, ca = load_startup_bundle("kwikpay_startup")
    res = execute_forensic_audit(rebit, gst, mca, claims, ca)

    # Check promoter siphoning funds detected (> ₹50 Lakhs)
    assert res["kpis"]["siphoned_funds_inr"] >= 5_000_000, f"Expected > ₹50L siphoned, got {res['kpis']['siphoned_funds_inr']}"

    # Check Section 188 violation in red flags or statutory violations
    red_flag_titles = [rf["title"] for rf in res.get("red_flags", [])]
    red_flag_rules = [rf.get("rule", "") for rf in res.get("red_flags", [])]
    all_red_flags = " ".join(red_flag_titles + red_flag_rules)
    assert "188" in all_red_flags or "Promoter" in all_red_flags or "Siphoning" in all_red_flags

    # Check Benford Nigrini MAD indicates non-conformance (TDS smurfing)
    assert res["kpis"]["benford_nigrini_mad"] > 0.0035, "Expected non-conforming Nigrini MAD due to TDS split invoices"


def test_zenith_archetype_specific_findings():
    """Verify Zenith BioHealth maintains clean governance, zero siphoning, and qualified 76-day DSO."""
    rebit, gst, mca, claims, ca = load_startup_bundle("zenith_startup")
    res = execute_forensic_audit(rebit, gst, mca, claims, ca)

    # Clean governance invariants
    assert res["kpis"]["siphoned_funds_inr"] == 0.0, "Zenith should have 0 siphoned funds"
    assert res["kpis"]["kanji_badge"] == "[要確認]", f"Zenith should receive qualified [要確認] badge, got {res['kpis']['kanji_badge']}"
    assert res["kpis"]["governance_trust_score"] == 78, f"Zenith score should be calibrated to 78, got {res['kpis']['governance_trust_score']}"


def test_autocare_archetype_specific_findings():
    """Verify AutoCare Network (GoMechanic archetype) flags Section 269ST cash siphoning and parts diversion."""
    rebit, gst, mca, claims, ca = load_startup_bundle("autocare_startup")
    res = execute_forensic_audit(rebit, gst, mca, claims, ca)

    # Section 269ST cash violations >= ₹15 Lakhs
    assert res["kpis"]["sec269st_cash_violations_inr"] >= 1_500_000, f"Expected >= ₹15L cash violations, got {res['kpis']['sec269st_cash_violations_inr']}"

    # Category check in discrepancies_detail
    disc_cats = [d.get("category") for d in res.get("discrepancies_detail", [])]
    assert "CASH_SIPHONING_269ST" in disc_cats, f"CASH_SIPHONING_269ST missing from discrepancies: {disc_cats}"

    # Section 188 promoter siphoning to Oberoi Spares
    assert res["kpis"]["siphoned_funds_inr"] > 0, "Expected non-zero siphoned funds to Oberoi Spares"

    # Red flag scores
    assert res["kpis"]["governance_trust_score"] <= 35, f"Expected critical score <= 35, got {res['kpis']['governance_trust_score']}"
    assert res["kpis"]["kanji_badge"] == "[精査要]", f"Expected [精査要], got {res['kpis']['kanji_badge']}"


def test_registry_quick_fill_options_count():
    """Verify get_all_quick_fill_options returns all 8 presets."""
    options = get_all_quick_fill_options()
    assert len(options) == 8
    keys = [opt["preset_key"] for opt in options]
    for p in ALL_PRESETS:
        assert p in keys, f"Preset {p} missing from quick fill options"


def test_mca_entity_lookup_all_seven_presets():
    """Verify MCA registry lookup resolves exact CIN and entity details for each preset."""
    options = get_all_quick_fill_options()
    for opt in options:
        cin = opt["cin"]
        entity = lookup_mca_entity(cin)
        assert entity is not None
        assert entity["cin"] == cin
        assert entity["preset_key"] == opt["preset_key"], f"Preset mismatch for {cin}: {entity['preset_key']} != {opt['preset_key']}"
        assert len(entity["directors"]) > 0


def test_ringi_sho_pdf_new_presets():
    """Verify 1-page PDF generation works seamlessly for all new startup archetypes."""
    for preset in ["edutrek_startup", "kwikpay_startup", "autocare_startup", "zenith_startup"]:
        audit = full_audit(AuditRequest(preset_key=preset))
        out_pdf = f"export/test_{preset}.pdf"
        generate_ringi_sho_pdf(audit, out_pdf)
        assert os.path.exists(out_pdf)
        reader = pypdf.PdfReader(out_pdf)
        assert len(reader.pages) == 1, f"Expected 1 page for {preset}, got {len(reader.pages)}"
        text = reader.pages[0].extract_text()
        assert "■" not in text and "\u25a0" not in text


def test_public_domain_case_studies_registry():
    """Verify all 6 verified public domain case studies resolve with authentic MCA and investor data."""
    from backend.registry_lookup import get_public_case_studies, lookup_mca_entity
    cases = get_public_case_studies()
    assert len(cases) == 6

    expected_cins = {
        "U74999DL2016PTC300195": "GoMechanic",
        "U80903KA2011PTC061427": "BYJU'S",
        "U74999DL2018PTC331205": "BharatPe",
        "L51100PN2010PLC136340": "FirstCry",
        "L72200DL2000PLC108985": "Paytm",
        "U33100DL2008PLC185963": "Lenskart",
    }
    for cin, name_sub in expected_cins.items():
        res = lookup_mca_entity(cin)
        assert res is not None
        assert res["cin"] == cin
        assert name_sub in res["company_name"]
        assert len(res["directors"]) > 0
        assert "investor_context" in res
        assert "forensic_auditor" in res
        assert "primary_violation" in res

