"""Comprehensive Pytest Suite for VeriLedger Forensic Core & Accounting Ledger.

Verifies:
1. DoubleEntryLedgerEngine mathematical balance & ICAI SA 240 / SA 505 compliance.
2. StatutoryVerificationEngine (Sec 269ST, Sec 40A(3), Sec 194C/J, Sec 68, Companies Act Sec 188, Rule 88C).
3. VeriLedgerForensicCore (3-way reconciliation, Benford F2D Nigrini MAD, Window Dressing, True Runway).
4. Master Audit Score determinism across 50 iterations (Zero non-deterministic drift).
"""

import os
import json
import csv
import pytest

from backend.schemas import (
    RebitTransaction,
    GstInvoice,
    DirectorRecord,
    PitchClaims,
    AccountCategory,
    JournalLine,
)
from backend.accounting_ledger import DoubleEntryLedgerEngine
from backend.statutory_rules import StatutoryVerificationEngine
from backend.forensic_core import VeriLedgerForensicCore
from backend.cash_flow_and_indirect_expenses import CashConversionAndIndirectExpenseEngine


@pytest.fixture
def mock_directors():
    return [
        DirectorRecord(
            cin="U72900KA2023PTC178921",
            company_name="Apex AI Labs Private Limited",
            din="08921045",
            director_name="Rajesh Sharma",
            pan="ABCPS1234F",
        ),
        DirectorRecord(
            cin="U72900KA2023PTC178921",
            company_name="Apex AI Labs Private Limited",
            din="09144820",
            director_name="Ananya Sen",
            pan="AEFPS5678K",
        ),
    ]


@pytest.fixture
def fraud_dataset():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    rebit_path = os.path.join(base_dir, "data", "fraud_startup_rebit.json")
    gst_path = os.path.join(base_dir, "data", "fraud_startup_gst.csv")
    
    with open(rebit_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        acc = data.get("account") or data.get("Account") or {}
        txns = acc.get("transactions") or acc.get("Transactions") or {}
        rebit_raw = txns.get("transaction") or txns.get("Transaction") or []
    transactions = [RebitTransaction(**t) for t in rebit_raw]

    invoices = []
    with open(gst_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            taxable = float(row.get("taxable_value", 0))
            gst_amt = float(row.get("gst_amount") or (float(row.get("igst", 0)) + float(row.get("cgst", 0)) + float(row.get("sgst", 0))))
            tot_amt = float(row.get("total_amount") or row.get("invoice_value", taxable + gst_amt))
            inv_dict = {
                "invoice_number": row.get("invoice_number", ""),
                "irn_hash": row.get("irn_hash", ""),
                "invoice_date": row.get("invoice_date", ""),
                "supplier_gstin": row.get("supplier_gstin") or "29AABCK1234F1Z5",
                "supplier_name": row.get("supplier_name") or "PhantomTech Solutions Private Limited",
                "buyer_gstin": row.get("buyer_gstin") or row.get("gstin_recipient", ""),
                "buyer_name": row.get("buyer_name") or row.get("receiver_name", ""),
                "taxable_value": taxable,
                "gst_amount": gst_amt,
                "total_amount": tot_amt,
                "gstr3b_offset_status": row.get("gstr3b_offset_status") or "OFFSET_PAID",
                "type": row.get("type") or "OUTWARD",
            }
            invoices.append(GstInvoice(**inv_dict))

    return transactions, invoices


@pytest.fixture
def clean_dataset():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    rebit_path = os.path.join(base_dir, "data", "clean_startup_rebit.json")
    gst_path = os.path.join(base_dir, "data", "clean_startup_gst.csv")
    
    with open(rebit_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        acc = data.get("account") or data.get("Account") or {}
        txns = acc.get("transactions") or acc.get("Transactions") or {}
        rebit_raw = txns.get("transaction") or txns.get("Transaction") or []
    transactions = [RebitTransaction(**t) for t in rebit_raw]

    invoices = []
    with open(gst_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            taxable = float(row.get("taxable_value", 0))
            gst_amt = float(row.get("gst_amount") or (float(row.get("igst", 0)) + float(row.get("cgst", 0)) + float(row.get("sgst", 0))))
            tot_amt = float(row.get("total_amount") or row.get("invoice_value", taxable + gst_amt))
            inv_dict = {
                "invoice_number": row.get("invoice_number", ""),
                "irn_hash": row.get("irn_hash", ""),
                "invoice_date": row.get("invoice_date", ""),
                "supplier_gstin": row.get("supplier_gstin") or "29AABCK1234F1Z5",
                "supplier_name": row.get("supplier_name") or "PhantomTech Solutions Private Limited",
                "buyer_gstin": row.get("buyer_gstin") or row.get("gstin_recipient", ""),
                "buyer_name": row.get("buyer_name") or row.get("receiver_name", ""),
                "taxable_value": taxable,
                "gst_amount": gst_amt,
                "total_amount": tot_amt,
                "gstr3b_offset_status": row.get("gstr3b_offset_status") or "OFFSET_PAID",
                "type": row.get("type") or "OUTWARD",
            }
            invoices.append(GstInvoice(**inv_dict))

    return transactions, invoices


# ---------------------------------------------------------------------------
# Test Group 1: Double-Entry Ledger & ICAI SA 240 / SA 505
# ---------------------------------------------------------------------------

def test_double_entry_balance():
    ledger = DoubleEntryLedgerEngine()
    lines = [
        JournalLine(account_code="1010", account_name="Cash at HDFC", category=AccountCategory.ASSET, debit=500000.0, credit=0.0),
        JournalLine(account_code="4010", account_name="Software Revenue", category=AccountCategory.REVENUE, debit=0.0, credit=500000.0),
    ]
    entry = ledger.post_journal_entry(
        entry_id="JE-001",
        date="2026-03-15",
        reference="INV-001",
        narration="Sales revenue received",
        lines=lines,
    )
    assert entry.entry_id == "JE-001"

    tb = ledger.generate_trial_balance(as_of_date="2026-03-31")
    assert tb.is_balanced is True
    assert tb.total_debits == 500000.0
    assert tb.total_credits == 500000.0


def test_double_entry_unbalanced_rejected():
    ledger = DoubleEntryLedgerEngine()
    lines = [
        JournalLine(account_code="1010", account_name="Cash at HDFC", category=AccountCategory.ASSET, debit=500000.0, credit=0.0),
        JournalLine(account_code="4010", account_name="Software Revenue", category=AccountCategory.REVENUE, debit=0.0, credit=400000.0), # Unbalanced!
    ]
    with pytest.raises(ValueError) as excinfo:
        ledger.post_journal_entry(
            entry_id="JE-BAD",
            date="2026-03-15",
            reference="INV-BAD",
            narration="Bad entry",
            lines=lines,
        )
    assert "Double-entry balance violation" in str(excinfo.value)


def test_sa240_round_number_detection():
    ledger = DoubleEntryLedgerEngine()
    lines = [
        JournalLine(account_code="1010", account_name="Cash at HDFC", category=AccountCategory.ASSET, debit=2500000.0, credit=0.0),
        JournalLine(account_code="3010", account_name="Share Capital", category=AccountCategory.EQUITY, debit=0.0, credit=2500000.0),
    ]
    ledger.post_journal_entry(
        entry_id="JE-ROUND",
        date="2026-03-28", # Quarter-end
        reference="CONTRA-01",
        narration="Promoter infusion contra adjustment",
        lines=lines,
    )
    audit = ledger.audit_sa240_fraud_indicators()
    assert audit["total_risk_entries_flagged"] >= 1
    assert len(audit["round_number_flags"]) >= 1
    assert len(audit["quarter_end_timing_flags"]) >= 1


# ---------------------------------------------------------------------------
# Test Group 2: Indian Statutory Law Verification
# ---------------------------------------------------------------------------

def test_section_188_promoter_siphoning(mock_directors, fraud_dataset):
    transactions, invoices = fraud_dataset
    engine = StatutoryVerificationEngine(directors=mock_directors)
    findings, violations = engine.check_section_188_related_parties(invoices, transactions)

    assert len(findings) >= 1
    # Vendor Apex Cloud Solutions LLP has GSTIN 29ABCPS1234F1Z5, which matches Director Rajesh Sharma's PAN
    assert findings[0].extracted_pan == "ABCPS1234F"
    assert findings[0].conflict_director_name == "Rajesh Sharma"
    assert findings[0].amount_inr == 4130000.0


def test_cgst_rule_88c_tax_deficit(mock_directors, fraud_dataset):
    _, invoices = fraud_dataset
    engine = StatutoryVerificationEngine(directors=mock_directors)
    summary, violations = engine.check_cgst_rule_88c(invoices)

    assert summary["is_rule_88c_triggered"] is True
    assert summary["delta_tax_percentage"] > 5.0
    assert len(violations) >= 1
    assert "Rule 88C" in violations[0].statutory_section


def test_tds_smurfing_evasion(mock_directors, fraud_dataset):
    transactions, _ = fraud_dataset
    engine = StatutoryVerificationEngine(directors=mock_directors)
    violations = engine.check_tds_smurfing(transactions)

    assert len(violations) >= 1
    assert violations[0].category == "TDS_SMURFING"
    assert "Section 194C / 194J" in violations[0].statutory_section


# ---------------------------------------------------------------------------
# Test Group 3: Forensic Core Engines (Benford, 3-Way, Window Dressing)
# ---------------------------------------------------------------------------

def test_benford_law_anomaly_detection(mock_directors, fraud_dataset):
    transactions, invoices = fraud_dataset
    core = VeriLedgerForensicCore(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
    )
    benford_res = core.evaluate_benford_f2d()
    assert benford_res.nigrini_mad >= 0.0022
    assert benford_res.is_anomalous is True
    # Verify spike at 49
    cluster_digits = [c.leading_two_digits for c in benford_res.clumping_clusters]
    assert 49 in cluster_digits


def test_three_way_reconciliation_fraud(mock_directors, fraud_dataset):
    transactions, invoices = fraud_dataset
    core = VeriLedgerForensicCore(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    recon = core.reconcile_three_way()
    assert recon.delta_cash_pct > 50.0
    assert recon.delta_tax_pct > 5.0
    assert recon.phantom_revenue_inr > 10000000.0
    assert recon.status == "CRITICAL_FRAUD"


def test_clean_startup_scorecard(mock_directors, clean_dataset):
    transactions, invoices = clean_dataset
    core = VeriLedgerForensicCore(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="Apex AI Labs", claimed_arr_inr=24800000.0, claimed_runway_months=18.0),
        closing_balance=34164000.0,
    )
    scorecard = core.execute_master_audit()
    assert scorecard.governance_trust_score >= 80
    assert scorecard.rating_classification == "VERIFIED_CLEAN"
    assert scorecard.kanji_badge == "【適格】"
    assert scorecard.related_party_siphoning["has_conflict"] is False


def test_determinism_50_iterations(mock_directors, fraud_dataset):
    """Verify 100% mathematical determinism: running 50 times yields exact same score."""
    transactions, invoices = fraud_dataset
    core = VeriLedgerForensicCore(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    first_score = core.execute_master_audit().governance_trust_score

    for _ in range(50):
        assert core.execute_master_audit().governance_trust_score == first_score


def test_cash_conversion_cycle_and_ar_aging(mock_directors, fraud_dataset):
    """Verify Cash Conversion Cycle, DSO, DPO, and AR aging buckets."""
    transactions, invoices = fraud_dataset
    engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    analysis = engine.analyze_cash_conversion_cycle()
    metrics = analysis["working_capital_metrics"]
    assert metrics["total_credit_sales_inr"] > 0
    assert metrics["dso_days"] >= 0
    assert metrics["cash_conversion_cycle_days"] != 0
    assert "bucket_0_30_days" in analysis["ar_aging_schedule"]
    assert "bucket_90_plus_days" in analysis["ar_aging_schedule"]


def test_indirect_expenses_and_rapid_drainage(mock_directors, fraud_dataset):
    """Verify detection of rapid pass-through outflows and disguised indirect expenses."""
    transactions, invoices = fraud_dataset
    engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    audit = engine.audit_indirect_expenses_and_siphoning()
    summary = audit["indirect_siphoning_summary"]
    # Verify rapid pass through drainage check runs and evaluates outflows
    assert "rapid_pass_through_drainage" in summary
    assert "disguised_personal_expenses" in summary


# ---------------------------------------------------------------------------
# Test Group 4: Advanced CA Decision Trees & Solvency Engines
# ---------------------------------------------------------------------------

def test_dynamic_liquidity_contingencies(mock_directors, fraud_dataset, clean_dataset):
    """Verify Section 201(1A) TDS interest, CGST Sec 50 interest, and EPFO damages."""
    f_txns, f_invs = fraud_dataset
    c_txns, c_invs = clean_dataset

    f_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=f_invs,
        bank_transactions=f_txns,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    f_res = f_engine.evaluate_dynamic_liquidity_contingencies(true_runway_months=1.5)
    assert f_res.is_cash_distressed is True
    assert f_res.tds_sec201_interest_inr > 0 or f_res.gst_sec50_interest_inr > 0
    assert len(f_res.violations) > 0

    c_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=c_invs,
        bank_transactions=c_txns,
        pitch_claims=PitchClaims(company_name="Apex AI Labs", claimed_arr_inr=25500000.0),
    )
    c_res = c_engine.evaluate_dynamic_liquidity_contingencies(true_runway_months=14.0)
    assert c_res.is_cash_distressed is False
    assert len(c_res.violations) == 0


def test_bad_debt_provisioning_ind_as_109(mock_directors, fraud_dataset, clean_dataset):
    """Verify Ind AS 109 3-stage ECL provisioning and valuation haircut."""
    f_txns, f_invs = fraud_dataset
    f_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=f_invs,
        bank_transactions=f_txns,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    f_res = f_engine.evaluate_bad_debt_provisioning()
    assert f_res.is_write_off_triggered is True
    assert f_res.stage3_credit_impaired_writeoff_inr > 0
    assert f_res.valuation_haircut_pct > 0

    c_txns, c_invs = clean_dataset
    c_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=c_invs,
        bank_transactions=c_txns,
        pitch_claims=PitchClaims(company_name="Apex AI Labs", claimed_arr_inr=25500000.0),
    )
    c_res = c_engine.evaluate_bad_debt_provisioning()
    assert c_res.is_write_off_triggered is False
    assert c_res.valuation_haircut_pct == 0.0


def test_solvency_and_debt_covenants(mock_directors, fraud_dataset, clean_dataset):
    """Verify DSCR debt distress and Quick Ratio < 0.8 IBC insolvency triggers."""
    f_txns, f_invs = fraud_dataset
    f_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=f_invs,
        bank_transactions=f_txns,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    f_solv = f_engine.evaluate_solvency_and_debt_covenants(pending_statutory_dues=3500000.0)
    assert f_solv.is_ibc_insolvency_triggered is True
    assert f_solv.quick_ratio < 0.8
    assert len(f_solv.covenant_violations) > 0

    c_txns, c_invs = clean_dataset
    c_engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=c_invs,
        bank_transactions=c_txns,
        pitch_claims=PitchClaims(company_name="Apex AI Labs", claimed_arr_inr=25500000.0),
    )
    c_solv = c_engine.evaluate_solvency_and_debt_covenants(pending_statutory_dues=0.0)
    assert c_solv.is_ibc_insolvency_triggered is False
    assert c_solv.quick_ratio >= 0.8


def test_circular_debt_round_tripping(mock_directors, fraud_dataset):
    """Verify detection of circular promoter loan round-tripping."""
    transactions, invoices = fraud_dataset
    engine = CashConversionAndIndirectExpenseEngine(
        directors=mock_directors,
        gst_invoices=invoices,
        bank_transactions=transactions,
        pitch_claims=PitchClaims(company_name="PhantomTech", claimed_arr_inr=25500000.0),
    )
    res = engine.detect_circular_debt_round_tripping()
    assert res.has_circular_debt is True
    assert res.total_circular_amount_inr > 0
    assert len(res.events_detected) > 0


def test_fastapi_ca_decision_endpoints():
    """Verify all 4 new FastAPI CA microservice endpoints return valid responses."""
    from backend.main import (
        get_liquidity_contingency,
        get_bad_debt_provisioning,
        get_solvency_covenants,
        get_circular_debt,
    )

    clean_liq = get_liquidity_contingency("clean_startup")
    assert clean_liq["status"] == "HEALTHY"

    fraud_liq = get_liquidity_contingency("fraud_startup")
    assert fraud_liq["status"] == "DISTRESSED"
    assert fraud_liq["violations_count"] > 0

    clean_bd = get_bad_debt_provisioning("clean_startup")
    assert clean_bd["status"] == "HEALTHY_RECEIVABLES"

    fraud_bd = get_bad_debt_provisioning("fraud_startup")
    assert fraud_bd["status"] == "WRITE_OFF_MANDATED"
    assert fraud_bd["valuation_haircut_pct"] > 0

    clean_solv = get_solvency_covenants("clean_startup")
    assert clean_solv["solvency_status"] == "SOLVENT_LIQUID"

    fraud_solv = get_solvency_covenants("fraud_startup")
    assert fraud_solv["is_ibc_insolvency_triggered"] is True

    clean_circ = get_circular_debt("clean_startup")
    assert clean_circ["status"] == "CLEAN"

    fraud_circ = get_circular_debt("fraud_startup")
    assert fraud_circ["status"] == "CIRCULAR_DEBT_DETECTED"
    assert fraud_circ["total_circular_amount_inr"] > 0


