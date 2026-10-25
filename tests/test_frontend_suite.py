"""
Frontend Verification Test Suite for VeriLedger / Kizuna-Vault (絆)
Tests i18n translation, dual-currency formatting, custom CSS, Plotly charts, and preset bundles.
"""

import pytest
import plotly.graph_objects as go
from frontend.i18n import t, format_currency, format_dual_currency_pair, FX_INR_TO_JPY
from frontend.styles import get_custom_css
from frontend.components import render_reconciliation_chart, render_benford_chart
from backend.main import full_audit
from backend.schemas import AuditRequest


def test_i18n_translation():
    """Verify bilingual translation lookup and fallback behavior."""
    assert "VERILEDGER" in t("app_title", "en")
    assert "VERILEDGER" in t("app_title", "jp")
    assert "TRUST SCORE" in t("kpi_shinrai", "en")
    assert "信頼" in t("kpi_shinrai", "jp")
    assert "GATEKEEPER" in t("gatekeeper_title", "en")
    assert "ゲートキーパー" in t("gatekeeper_title", "jp")
    
    # Test fallback on unknown key
    assert t("non_existent_key", "en") == "non_existent_key"


def test_format_currency_inr_and_jpy():
    """Verify dual currency formatting across INR and JPY denominations."""
    # INR Crores and Lakhs
    assert "Cr" in format_currency(25000000, currency_mode="INR", lang_mode="EN")
    assert "Lakhs" in format_currency(450000, currency_mode="INR", lang_mode="EN")
    
    # JPY 億円 and 万円
    jpy_large = format_currency(100000000, currency_mode="JPY", lang_mode="JP")
    assert "¥" in jpy_large and "億円" in jpy_large
    
    jpy_small = format_currency(500000, currency_mode="JPY", lang_mode="JP")
    assert "¥" in jpy_small and "万円" in jpy_small

    # Dual currency pair
    dual = format_dual_currency_pair(10000000, lang_mode="EN")
    assert "₹" in dual and "¥" in dual


def test_custom_css_compliance():
    """Ensure non-ai-slop-ui-design specifications are enforced in CSS."""
    css = get_custom_css()
    assert "#090D16" in css  # Dark obsidian canvas
    assert "#B33927" in css  # Cinnabar Vermilion for Hanko seals
    assert "JetBrains Mono" in css  # Monospace tabular numbers
    assert "tabular-nums" in css
    assert "hanko-seal" in css
    assert "telemetry-terminal" in css


def test_plotly_reconciliation_chart():
    """Verify 4-Way Reconciliation chart renders 4 traces with obsidian background."""
    sample_monthly = [
        {
            "month": "July 2026",
            "claimed_pitch_sales_inr": 4200000.0,
            "ca_booked_sales_inr": 4150000.0,
            "gstr1_declared_sales_inr": 4100000.0,
            "bank_cleared_cash_inr": 4180000.0,
        },
        {
            "month": "August 2026",
            "claimed_pitch_sales_inr": 4200000.0,
            "ca_booked_sales_inr": 4150000.0,
            "gstr1_declared_sales_inr": 4100000.0,
            "bank_cleared_cash_inr": 4250000.0,
        }
    ]
    fig = render_reconciliation_chart(sample_monthly, currency_mode="INR", lang="en")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 4
    assert fig.layout.paper_bgcolor == "#111827"
    assert fig.layout.plot_bgcolor == "#111827"


def test_plotly_benford_chart():
    """Verify Benford F2D Anomaly chart renders continuous curve and observed bars."""
    sample_benford = {
        "digits": list(range(10, 100)),
        "expected_pct": [3.0] * 90,
        "observed_pct": [3.1] * 90,
        "nigrini_mad": 0.0028
    }
    fig = render_benford_chart(sample_benford, lang="en")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.layout.paper_bgcolor == "#111827"


def test_all_presets_audit_pipeline():
    """Verify all 8 startup presets audit cleanly and return complete data contracts."""
    presets = [
        "clean_startup",
        "fraud_startup",
        "logipulse_startup",
        "mirai_startup",
        "edutrek_startup",
        "kwikpay_startup",
        "autocare_startup",
        "zenith_startup"
    ]
    for p in presets:
        req = AuditRequest(preset_key=p)
        res = full_audit(req)
        assert res["status"] in ["AUDIT_COMPLETE", "COMPLETED"]
        assert "kpis" in res
        assert "governance_trust_score" in res["kpis"]
        assert "hanko_stages" in res
        assert len(res["hanko_stages"]) == 5
        assert "monthly_reconciliation" in res
        assert "benford_curve" in res
        assert "merkle_root" in res["kpis"]


def test_negative_currency_formatting():
    """Verify negative monetary values format with prefix minus sign (-₹ / -¥), never ₹- or ¥-."""
    neg_inr_cr = format_currency(-25000000, currency_mode="INR", lang_mode="EN")
    assert neg_inr_cr.startswith("-₹")
    assert "₹-" not in neg_inr_cr
    assert "Cr" in neg_inr_cr

    neg_inr_lakh = format_currency(-450000, currency_mode="INR", lang_mode="EN")
    assert neg_inr_lakh.startswith("-₹")
    assert "₹-" not in neg_inr_lakh
    assert "Lakhs" in neg_inr_lakh

    neg_jpy_oku = format_currency(-100000000, currency_mode="JPY", lang_mode="JP")
    assert neg_jpy_oku.startswith("-¥")
    assert "¥-" not in neg_jpy_oku
    assert "億円" in neg_jpy_oku

    neg_jpy_man = format_currency(-500000, currency_mode="JPY", lang_mode="JP")
    assert neg_jpy_man.startswith("-¥")
    assert "¥-" not in neg_jpy_man
    assert "万円" in neg_jpy_man


def test_discrepancy_waterfall_chart():
    """Verify Discrepancy Waterfall Cascade renders with correct 8 steps across themes and currencies."""
    from frontend.components import render_discrepancy_waterfall
    req = AuditRequest(preset_key="fraud_startup")
    res = full_audit(req)

    # Dark mode INR
    fig_dark = render_discrepancy_waterfall(res, currency_mode="INR", lang="en", theme="dark")
    assert isinstance(fig_dark, go.Figure)
    assert len(fig_dark.data) == 1
    assert fig_dark.layout.paper_bgcolor == "#111827"
    assert len(fig_dark.data[0].x) == 8

    # Light mode JPY
    fig_light = render_discrepancy_waterfall(res, currency_mode="JPY", lang="jp", theme="light")
    assert isinstance(fig_light, go.Figure)
    assert fig_light.layout.paper_bgcolor == "#FFFFFF"
    assert len(fig_light.data[0].x) == 8


def test_hanko_stages_and_hydration():
    """Verify 5-stage Hanko seal structure and simulate committee stamp hydration."""
    req = AuditRequest(preset_key="clean_startup")
    res = full_audit(req)
    stages = res["hanko_stages"]
    assert len(stages) == 5

    expected_roles_jp = ["起　案", "審　査", "精　査", "合　議", "決　裁"]
    for i, stg in enumerate(stages):
        assert stg["role_jp"] == expected_roles_jp[i]
        assert "stage_id" in stg
        assert "role_en" in stg
        assert "status" in stg

    # Test state persistence hydration simulation
    stamps_session = {"stage_1": "APPROVED", "stage_2": "FLAGGED"}
    for stg in stages:
        s_id = stg["stage_id"]
        if s_id in stamps_session:
            stg["status"] = stamps_session[s_id]

    assert stages[0]["status"] == "APPROVED"
    assert stages[1]["status"] == "FLAGGED"


def test_css_root_tokens():
    """Ensure :root CSS custom properties are properly emitted for dark and light themes."""
    css_dark = get_custom_css("dark")
    assert ":root" in css_dark
    assert "--bg-canvas: #090D16" in css_dark
    assert "--text-primary: #F8FAFC" in css_dark

    css_light = get_custom_css("light")
    assert ":root" in css_light
    assert "--bg-canvas: #FFFFFF" in css_light
    assert "--text-primary: #0F172A" in css_light


def test_mca_registry_preset_alignment():
    """Verify that all 8 quick-fill options in registry_lookup resolve cleanly to their intended preset."""
    from backend.registry_lookup import lookup_mca_entity, get_all_quick_fill_options
    options = get_all_quick_fill_options()
    assert len(options) == 8
    for opt in options:
        res = lookup_mca_entity(opt["cin"])
        assert res["preset_key"] == opt["preset_key"]
        assert res["cin"] == opt["cin"]
        assert len(res["directors"]) >= 1
        assert res["gstin"].startswith(("29", "07", "27", "33", "06", "36"))


def test_founder_dashboard_onboarding_and_linkage_flow():
    """Verify end-to-end AppTest execution of founder dashboard, approval, and sovereign rail linkage."""
    import os
    from streamlit.testing.v1 import AppTest
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "app.py"))
    at = AppTest.from_file(app_path)
    at.session_state["page_state"] = "founder_dashboard"
    at.run()
    assert not at.exception

    # Select PhantomTech from quick-fill buttons
    qf_buttons = [b for b in at.button if "gate_qf" not in b.key and "qf_btn" in b.key]
    assert len(qf_buttons) == 8
    # Click option 1 (PhantomTech)
    qf_buttons[1].click().run()
    assert not at.exception
    assert at.session_state["active_preset"] == "fraud_startup"
    assert at.session_state["active_cin"] == "U74999DL2024PTC389102"
    assert at.session_state["aa_bank_linked"] is False

    # Approve diligence request
    appr_btns = [b for b in at.button if b.key == "btn_fnd_approve"]
    assert len(appr_btns) == 1
    appr_btns[0].click().run()
    assert not at.exception
    assert at.session_state["consent_request"]["status"] == "APPROVED"

    # Link Bank Account
    bank_btns = [b for b in at.button if b.key == "btn_connect_bank"]
    assert len(bank_btns) == 1
    bank_btns[0].click().run()
    assert not at.exception
    assert at.session_state["aa_bank_linked"] is True

    # Link GSTIN
    gst_btns = [b for b in at.button if b.key == "btn_connect_gst"]
    assert len(gst_btns) == 1
    gst_btns[0].click().run()
    assert not at.exception
    assert at.session_state["gstin_tax_linked"] is True

    # Link MCA & CA Books
    mca_btns = [b for b in at.button if b.key == "btn_connect_mca"]
    assert len(mca_btns) == 1
    mca_btns[0].click().run()
    assert not at.exception
    assert at.session_state["mca_books_linked"] is True

    # Launch Cockpit button is now active
    cockpit_btns = [b for b in at.button if b.key == "btn_fnd_cockpit"]
    assert len(cockpit_btns) == 1
    cockpit_btns[0].click().run()
    assert not at.exception
    assert at.session_state["page_state"] in ["cockpit", "telemetry"]


def test_apex_ai_labs_15_char_corporate_gstin():
    """Verify that Apex AI Labs Private Limited has a 10-char Corporate PAN (4th char 'C') and exactly 15-char GSTIN."""
    from backend.registry_lookup import lookup_mca_entity
    res = lookup_mca_entity("clean_startup")
    assert res["company_name"] == "Apex AI Labs Private Limited"
    assert res["pan"] == "AABCA1234C"
    assert len(res["pan"]) == 10
    assert res["pan"][3] == "C"
    assert res["gstin"] == "29AABCA1234C1Z5"
    assert len(res["gstin"]) == 15
    assert res["gstin"][2:12] == res["pan"]


def test_founder_fast_track_link_all_instantly():
    """Verify clicking [FAST-TRACK] Link All Sovereign Rails Instantly immediately links all rails and unlocks Step 4."""
    import os
    from streamlit.testing.v1 import AppTest
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "app.py"))
    at = AppTest.from_file(app_path)
    at.session_state["page_state"] = "founder_dashboard"
    at.session_state["active_preset"] = "clean_startup"
    at.session_state["aa_bank_linked"] = False
    at.session_state["gstin_tax_linked"] = False
    at.session_state["mca_books_linked"] = False
    at.session_state["consent_request"] = {"status": "DISPATCHED", "handle": "REQ-KIZUNA-2026-CLEA-0914"}
    at.run()
    assert not at.exception

    ft_btns = [b for b in at.button if b.key == "btn_link_all_fast"]
    assert len(ft_btns) == 1
    ft_btns[0].click().run()
    assert not at.exception

    assert at.session_state["aa_bank_linked"] is True
    assert at.session_state["gstin_tax_linked"] is True
    assert at.session_state["mca_books_linked"] is True
    assert at.session_state["consent_request"]["status"] == "APPROVED"

    cockpit_btns = [b for b in at.button if b.key == "btn_fnd_cockpit"]
    assert len(cockpit_btns) == 1
    cockpit_btns[0].click().run()
    assert not at.exception
    assert at.session_state["page_state"] in ["cockpit", "telemetry"]


