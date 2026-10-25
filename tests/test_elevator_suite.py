"""
Elevated Verification Test Suite for VeriLedger / Kizuna-Vault (絆)
Validates:
1. Discrepancy Waterfall data integrity and cascade progression
2. Dynamic What-If simulation and anomaly injection overrides
3. Light & Dark theme Plotly rendering for Discrepancy Waterfall
4. Strict zero-emoji compliance across all i18n translation tokens
"""

import pytest
import plotly.graph_objects as go
from backend.main import load_startup_bundle, full_audit
from backend.schemas import AuditRequest
from backend.forensic_rules import ForensicAuditEngine
from frontend.components import render_discrepancy_waterfall, render_reconciliation_chart, render_benford_chart
from frontend.i18n import TRANSLATIONS, t, format_currency, FX_INR_TO_JPY
from frontend.styles import get_custom_css


def test_discrepancy_waterfall_metrics():
    """Verify waterfall cascade matches mathematical flow from claims to bank cash."""
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, g_d, d_d, c_d, ca_d = load_startup_bundle("clean_startup")
    clean_res = engine.evaluate(r_d, g_d, d_d, ca_d, c_d)

    assert "waterfall" in clean_res
    wf_clean = clean_res["waterfall"]
    assert wf_clean["pitch_claimed_arr_inr"] == 25500000.0
    assert wf_clean["promoter_siphoned_inr"] == 0.0
    assert wf_clean["cleared_bank_cash_inr"] > 20000000.0

    r_f, g_f, d_f, c_f, ca_f = load_startup_bundle("fraud_startup")
    fraud_res = engine.evaluate(r_f, g_f, d_f, ca_f, c_f)
    wf_fraud = fraud_res["waterfall"]
    assert wf_fraud["promoter_siphoned_inr"] == 4130000.0
    assert wf_fraud["uncollected_bank_gap_inr"] > 0.0
    assert wf_fraud["true_unencumbered_cash_inr"] < wf_fraud["cleared_bank_cash_inr"]


def test_what_if_simulation_overrides():
    """Verify live what-if simulation dynamically toggles anomalies and recalculates score."""
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, g_d, d_d, c_d, ca_d = load_startup_bundle("clean_startup")

    # Baseline clean audit
    clean_base = engine.evaluate(r_d, g_d, d_d, ca_d, c_d)
    score_clean = clean_base["kpis"]["governance_trust_score"]
    assert score_clean >= 80

    # Inject Section 188 conflict into clean startup
    sim_injected = engine.evaluate(
        r_d, g_d, d_d, ca_d, c_d,
        anomaly_injections={'siphoning': True}
    )
    score_injected = sim_injected["kpis"]["governance_trust_score"]
    assert score_injected < score_clean
    assert sim_injected["kpis"]["siphoned_funds_inr"] == 4130000.0

    # Test fraud startup with anomaly cleared
    r_f, g_f, d_f, c_f, ca_f = load_startup_bundle("fraud_startup")
    fraud_base = engine.evaluate(r_f, g_f, d_f, ca_f, c_f)
    assert fraud_base["kpis"]["siphoned_funds_inr"] == 4130000.0

    sim_repaired = engine.evaluate(
        r_f, g_f, d_f, ca_f, c_f,
        anomaly_injections={'siphoning': False}
    )
    assert sim_repaired["kpis"]["siphoned_funds_inr"] == 0.0


def test_what_if_claimed_arr_scaling():
    """Verify adjusting claimed ARR widens cash divergence percentage."""
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, g_d, d_d, c_d, ca_d = load_startup_bundle("clean_startup")

    res_1 = engine.evaluate(r_d, g_d, d_d, ca_d, c_d, override_claimed_arr=25500000.0)
    res_2 = engine.evaluate(r_d, g_d, d_d, ca_d, c_d, override_claimed_arr=60000000.0)

    assert res_1["waterfall"]["pitch_claimed_arr_inr"] == 25500000.0
    assert res_2["waterfall"]["pitch_claimed_arr_inr"] == 60000000.0
    assert res_2["waterfall"]["unbilled_pitch_gap_inr"] > res_1["waterfall"]["unbilled_pitch_gap_inr"]


def test_waterfall_figure_rendering():
    """Verify Plotly waterfall figure generates valid traces in light and dark modes."""
    sample_audit = {
        "kpis": {
            "claimed_arr_inr": 25500000.0,
            "real_bank_credits_inr": 10100000.0,
            "siphoned_funds_inr": 4130000.0,
            "unremitted_tax_dues_inr": 1840000.0,
        },
        "waterfall": {
            "pitch_claimed_arr_inr": 25500000.0,
            "unbilled_pitch_gap_inr": 6000000.0,
            "gst_declared_turnover_inr": 19500000.0,
            "uncollected_bank_gap_inr": 9400000.0,
            "cleared_bank_cash_inr": 10100000.0,
            "promoter_siphoned_inr": 4130000.0,
            "unremitted_tax_dues_inr": 1840000.0,
            "true_unencumbered_cash_inr": 4130000.0
        }
    }

    fig_light = render_discrepancy_waterfall(sample_audit, currency_mode="INR", lang="en", theme="light")
    assert isinstance(fig_light, go.Figure)
    assert fig_light.layout.paper_bgcolor == "#FFFFFF"
    assert fig_light.layout.plot_bgcolor == "#FFFFFF"

    fig_dark = render_discrepancy_waterfall(sample_audit, currency_mode="JPY", lang="jp", theme="dark")
    assert isinstance(fig_dark, go.Figure)
    assert fig_dark.layout.paper_bgcolor == "#111827"
    assert fig_dark.layout.plot_bgcolor == "#111827"


def test_zero_emojis_in_translations():
    """Ensure zero emojis exist across all English and Japanese translation entries."""
    emojis = ["⚡", "🔐", "🚨", "⚠️", "🛡️", "📝", "📄", "🔍", "✓", "🔴", "🔓", "📥"]
    for key, lang_dict in TRANSLATIONS.items():
        for lang, text in lang_dict.items():
            for emoji in emojis:
                assert emoji not in text, f"Emoji '{emoji}' found in translation key '{key}' ({lang}): {text}"


def test_pure_white_theme_css():
    """Ensure pure white theme CSS produces crisp slate borders and white background."""
    css_light = get_custom_css(theme="light")
    assert "#FFFFFF" in css_light
    assert "#0F172A" in css_light
    assert "#E2E8F0" in css_light
    assert "JetBrains Mono" in css_light
    assert "tabular-nums" in css_light


def test_edge_cases_boundary_values():
    """Test boundary values: zero claimed ARR, massive ARR, all anomalies simultaneously."""
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, g_d, d_d, c_d, ca_d = load_startup_bundle("clean_startup")

    # Boundary 1: Zero claimed ARR
    res_zero = engine.evaluate(r_d, g_d, d_d, ca_d, c_d, override_claimed_arr=0.0)
    assert res_zero["status"] == "AUDIT_COMPLETE"
    assert res_zero["kpis"]["claimed_arr_inr"] == 0.0

    # Boundary 2: 10,000 Crore claimed ARR vs 2.55 Cr GSTN
    res_huge = engine.evaluate(r_d, g_d, d_d, ca_d, c_d, override_claimed_arr=1e11)
    assert res_huge["status"] == "AUDIT_COMPLETE"
    assert res_huge["waterfall"]["unbilled_pitch_gap_inr"] > 9.9e10

    # Boundary 3: All 5 anomalies injected at once
    res_all_anomalies = engine.evaluate(
        r_d, g_d, d_d, ca_d, c_d,
        anomaly_injections={
            'siphoning': True,
            'window_dressing': True,
            'tax_evasion': True,
            'benford_anomaly': True,
            'zombie_debtors': True
        }
    )
    assert res_all_anomalies["kpis"]["governance_trust_score"] < 50
    assert res_all_anomalies["kpis"]["kanji_badge"] == "[精査要]"


def test_edge_cases_empty_and_missing_inputs():
    """Test resilience against empty transactions, empty GST, and missing ca books."""
    import pandas as pd
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    empty_rebit = {"account": {"transactions": {"transaction": []}}}
    empty_gst = pd.DataFrame()
    empty_mca = pd.DataFrame()

    res = engine.evaluate(empty_rebit, empty_gst, empty_mca, ca_books={}, claimed_profile={})
    assert res["status"] == "AUDIT_COMPLETE"
    assert res["kpis"]["real_bank_credits_inr"] == 0.0
    assert "waterfall" in res
    assert res["waterfall"]["cleared_bank_cash_inr"] == 0.0


def test_gst_df_robustness_without_type_column():
    """Verify GST DataFrame with gstr3b_offset_status but no 'type' column executes safely."""
    import pandas as pd
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, _, d_d, c_d, ca_d = load_startup_bundle("clean_startup")

    # CSV with offset status but NO 'type' column
    gst_no_type = pd.DataFrame({
        "invoice_number": ["INV-CUSTOM-01", "INV-CUSTOM-02"],
        "taxable_value": [500000.0, 750000.0],
        "gstr3b_offset_status": ["UNOFF_SET_UNPAID", "OFFSET_PAID"],
        "buyer_name": ["Alpha Corp", "Beta Corp"]
    })

    res = engine.evaluate(r_d, gst_no_type, d_d, ca_d, c_d)
    assert res["status"] == "AUDIT_COMPLETE"
    # Should flag the unpaid invoice without KeyError
    phantom_discs = [d for d in res["discrepancies_detail"] if d.get("category") == "PHANTOM_REVENUE"]
    assert len(phantom_discs) >= 1


def test_directors_df_robustness_arbitrary_columns():
    """Verify directors DataFrame with non-standard column naming executes safely."""
    import pandas as pd
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    r_d, g_d, _, c_d, ca_d = load_startup_bundle("clean_startup")

    # Directors with missing or non-standard columns
    directors_nonstandard = pd.DataFrame({
        "Director PAN": ["ABCDE1234F"],
        "Director Name": ["Dr. K. Sharma"],
        "DIN": ["00123456"]
    })

    res = engine.evaluate(r_d, g_d, directors_nonstandard, ca_d, c_d)
    assert res["status"] == "AUDIT_COMPLETE"


def test_rebit_single_dict_and_none_transactions():
    """Verify ReBIT AA JSON where 'transaction' is a single dict or None executes safely."""
    import pandas as pd
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    _, g_d, d_d, c_d, ca_d = load_startup_bundle("clean_startup")

    # Single transaction as a dict
    rebit_single = {
        "account": {
            "transactions": {
                "transaction": {
                    "txnId": "SINGLE_TXN_01",
                    "type": "CREDIT",
                    "amount": 2500000.0,
                    "narration": "CUSTOMER_INFLOW",
                    "valueDate": "2026-10-15"
                }
            }
        }
    }
    res_single = engine.evaluate(rebit_single, g_d, d_d, ca_d, c_d)
    assert res_single["status"] == "AUDIT_COMPLETE"
    assert res_single["kpis"]["real_bank_credits_inr"] == 2500000.0

    # Null transactions
    rebit_null = {"account": {"transactions": {"transaction": None}}}
    res_null = engine.evaluate(rebit_null, g_d, d_d, ca_d, c_d)
    assert res_null["status"] == "AUDIT_COMPLETE"
    assert res_null["kpis"]["real_bank_credits_inr"] == 0.0


def test_normalize_gst_dataframe():
    """Verify normalize_gst_dataframe correctly maps common third-party column headers."""
    import pandas as pd
    from backend.forensic_rules import normalize_gst_dataframe

    raw_df = pd.DataFrame({
        "Inv No": ["INV-001"],
        "Bill Date": ["2026-10-10"],
        "Party GSTIN": ["29ABCDE1234F1Z5"],
        "Party Name": ["Acme Corp"],
        "Taxable Val": [150000.0],
        "Total Value": [177000.0],
        "Offset Status": ["OFFSET_PAID"]
    })

    norm = normalize_gst_dataframe(raw_df)
    assert "invoice_number" in norm.columns
    assert "invoice_date" in norm.columns
    assert "buyer_gstin" in norm.columns
    assert "buyer_name" in norm.columns
    assert "taxable_value" in norm.columns
    assert "total_amount" in norm.columns
    assert "gstr3b_offset_status" in norm.columns
    assert "type" in norm.columns


def test_diligence_sankey_flow_figure():
    """Verify Diligence Sankey Flow renders valid plotly figures across themes."""
    from frontend.components import render_diligence_sankey_flow

    r_f, g_f, d_f, c_f, ca_f = load_startup_bundle("fraud_startup")
    engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
    fraud_res = engine.evaluate(r_f, g_f, d_f, ca_f, c_f)

    fig_light = render_diligence_sankey_flow(fraud_res, currency_mode="INR", lang="en", theme="light")
    assert isinstance(fig_light, go.Figure)
    assert len(fig_light.data[0].link.value) >= 4
    assert fig_light.layout.paper_bgcolor == "#FFFFFF"

    fig_dark = render_diligence_sankey_flow(fraud_res, currency_mode="JPY", lang="jp", theme="dark")
    assert isinstance(fig_dark, go.Figure)
    assert len(fig_dark.data[0].link.value) >= 4
    assert fig_dark.layout.paper_bgcolor == "#111827"


def test_zero_emojis_across_frontend_source_files():
    """Ensure zero emojis exist across all frontend python source code and components."""
    import os
    banned_emojis = ['⚡', '🚨', '⚠️', '🛡️', '📝', '📄', '🔍', '✓', '🔴', '🔓', '📥', '↺', '✕']
    frontend_files = [
        os.path.join("frontend", "app.py"),
        os.path.join("frontend", "components.py"),
        os.path.join("frontend", "styles.py"),
        os.path.join("frontend", "i18n.py"),
        os.path.join("export", "memo_generator.py")
    ]
    for fn in frontend_files:
        with open(fn, "r", encoding="utf-8") as f:
            content = f.read()
            for em in banned_emojis:
                assert em not in content, f"Banned emoji '{em}' found in file '{fn}'"

