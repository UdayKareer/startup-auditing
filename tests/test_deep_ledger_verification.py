"""
Deep Verification Test Suite for VeriLedger High-Volume Datasets and Ledger APIs.
Validates:
1. Zero-rupee transaction and invoice elimination across all 8 presets
2. Schema robustness: bidirectional camelCase <-> snake_case interoperability
3. REST API query & body parameter handling (?preset=... vs ?preset_key=... and POST JSON)
4. Pagination (limit + offset) and multi-field search across Bank Ledger and GST Invoices
5. UI table safe string normalization (zero 'None' or 'nan' string artifacts)
"""

import os
import json
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app, load_startup_bundle
from backend.schemas import RebitTransaction, GstInvoice
from frontend.components import _safe_str, render_redline_table, render_audited_bank_ledger, render_audited_gst_register


client = TestClient(app)
PRESETS = ["clean_startup", "fraud_startup", "zenith", "autocare", "edutrek", "kwikpay", "logipulse", "mirai"]


def test_no_zero_or_negative_amounts_across_all_presets():
    """Ensure every transaction and invoice across all 8 presets has positive amounts."""
    for p in PRESETS:
        with open(f"data/{p}_rebit.json", "r", encoding="utf-8") as f:
            rebit = json.load(f)
        txns = rebit.get("account", {}).get("transactions", {}).get("transaction", [])
        assert len(txns) >= 1000, f"Preset {p} has fewer than 1,000 transactions ({len(txns)})"

        zero_txns = [t for t in txns if float(t.get("amount", 0.0) or 0.0) <= 0.0]
        assert len(zero_txns) == 0, f"Preset {p} contains {len(zero_txns)} zero/negative amount transactions"

        zero_jpy = [t for t in txns if float(t.get("amount_jpy", 0.0) or 0.0) <= 0.0]
        assert len(zero_jpy) == 0, f"Preset {p} contains {len(zero_jpy)} zero/negative amount_jpy transactions"

        # Check required narrative and temporal fields
        for t in txns[:20]:
            assert t.get("transactionTimestamp") and "T" in t["transactionTimestamp"]
            assert t.get("valueDate")
            assert t.get("accountHead")
            assert t.get("whatHappened")
            assert t.get("whyReason")

        # Invoices check
        gst_df = pd.read_csv(f"data/{p}_gst.csv")
        assert len(gst_df) > 0, f"Preset {p} has empty GST register"
        zero_invoices = gst_df[gst_df["invoice_value"] <= 0.0]
        assert len(zero_invoices) == 0, f"Preset {p} has {len(zero_invoices)} zero/negative invoice values"


def test_schema_bidirectional_case_compatibility():
    """Verify RebitTransaction and GstInvoice accept and expose both snake_case and camelCase."""
    # RebitTransaction from snake_case
    t_snake = RebitTransaction(
        txn_id="TXN-TEST-001",
        amount=50000.0,
        current_balance=1000000.0,
        transaction_timestamp="2026-08-10T14:30:00+05:30",
        narration="Advisory fee",
        account_head="Account 5020: Strategy Advisory",
        what_happened="Disbursement to vendor",
        why_reason="Bona fide business expense",
        statutory_citation="Sec 37(1)"
    )
    assert t_snake.txnId == "TXN-TEST-001"
    assert t_snake.accountHead == "Account 5020: Strategy Advisory"
    assert t_snake.account_head == "Account 5020: Strategy Advisory"
    assert t_snake.whatHappened == "Disbursement to vendor"
    assert t_snake.what_happened == "Disbursement to vendor"
    assert t_snake.whyReason == "Bona fide business expense"
    assert t_snake.why_reason == "Bona fide business expense"
    assert t_snake.statutoryCitation == "Sec 37(1)"
    assert t_snake.statutory_citation == "Sec 37(1)"

    # GstInvoice from camelCase
    inv_camel = GstInvoice(
        invoiceNumber="INV-TEST-001",
        invoiceDate="2026-08-10",
        buyerGstin="29AABCA1234A1Z5",
        buyerName="Test Enterprise",
        taxableValue=100000.0,
        gstAmount=18000.0,
        totalAmount=118000.0,
        accountHead="Account 4010: AI Subscriptions",
        whatHappened="Outward subscription bill",
        whyReason="100% matched IRN"
    )
    assert inv_camel.invoice_number == "INV-TEST-001"
    assert inv_camel.buyer_name == "Test Enterprise"
    assert inv_camel.account_head == "Account 4010: AI Subscriptions"
    assert inv_camel.accountHead == "Account 4010: AI Subscriptions"
    assert inv_camel.what_happened == "Outward subscription bill"
    assert inv_camel.whatHappened == "Outward subscription bill"
    assert inv_camel.why_reason == "100% matched IRN"
    assert inv_camel.whyReason == "100% matched IRN"


def test_api_preset_parameter_alias():
    """Verify GET and POST endpoints accept both ?preset= and ?preset_key=."""
    # Transactions via ?preset=
    r_txns_preset = client.get("/api/v1/ledger/transactions?preset=fraud_startup&limit=5")
    assert r_txns_preset.status_code == 200
    assert r_txns_preset.json()["preset_key"] == "fraud_startup"
    assert r_txns_preset.json()["company_name"] == "PhantomTech Solutions Private Limited"

    # Invoices via ?preset=
    r_inv_preset = client.get("/api/v1/ledger/invoices?preset=fraud_startup&limit=5")
    assert r_inv_preset.status_code == 200
    assert r_inv_preset.json()["preset_key"] == "fraud_startup"
    assert r_inv_preset.json()["company_name"] == "PhantomTech Solutions Private Limited"

    # Discrepancies via ?preset=
    r_disc_preset = client.get("/api/v1/forensic/discrepancies?preset=fraud_startup")
    assert r_disc_preset.status_code == 200
    assert r_disc_preset.json()["preset_key"] == "fraud_startup"
    assert r_disc_preset.json()["company_name"] == "PhantomTech Solutions Private Limited"
    assert r_disc_preset.json()["discrepancies_count"] > 1

    # POST with JSON body
    r_post_txns = client.post("/api/v1/ledger/transactions", json={"preset": "zenith", "limit": 10})
    assert r_post_txns.status_code == 200
    assert r_post_txns.json()["preset_key"] == "zenith"
    assert len(r_post_txns.json()["transactions"]) == 10

    r_post_inv = client.post("/api/v1/ledger/invoices", json={"preset_key": "autocare", "limit": 5})
    assert r_post_inv.status_code == 200
    assert r_post_inv.json()["preset_key"] == "autocare"
    assert len(r_post_inv.json()["invoices"]) == 5


def test_api_pagination_and_search():
    """Verify offset and limit pagination and search filtering work correctly."""
    # Test transactions pagination
    p0 = client.get("/api/v1/ledger/transactions?preset_key=clean_startup&limit=5&offset=0").json()["transactions"]
    p1 = client.get("/api/v1/ledger/transactions?preset_key=clean_startup&limit=5&offset=5").json()["transactions"]
    assert len(p0) == 5
    assert len(p1) == 5
    assert p0[0]["txnId"] != p1[0]["txnId"]

    # Test invoices pagination
    inv_p0 = client.get("/api/v1/ledger/invoices?preset_key=clean_startup&limit=3&offset=0").json()["invoices"]
    inv_p1 = client.get("/api/v1/ledger/invoices?preset_key=clean_startup&limit=3&offset=3").json()["invoices"]
    assert len(inv_p0) == 3
    assert len(inv_p1) == 3
    assert inv_p0[0]["invoice_number"] != inv_p1[0]["invoice_number"]

    # Test search across narration and whatHappened
    r_search = client.get("/api/v1/ledger/transactions?preset_key=fraud_startup&search=Apex%20Cloud")
    assert r_search.status_code == 200
    data = r_search.json()
    assert data["filtered_count"] > 0
    for t in data["transactions"]:
        corpus = f"{t.get('narration')} {t.get('counterparty')} {t.get('whatHappened')}".lower()
        assert "apex cloud" in corpus


def test_ui_safe_string_normalization():
    """Ensure _safe_str eliminates literal 'None' and 'nan' artifacts."""
    assert _safe_str(None, "fallback") == "fallback"
    assert _safe_str("None", "fallback") == "fallback"
    assert _safe_str("nan", "fallback") == "fallback"
    assert _safe_str("   ", "fallback") == "fallback"
    assert _safe_str("Valid Value", "fallback") == "Valid Value"
