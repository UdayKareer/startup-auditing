"""Pydantic schemas and data models for VeriLedger (Kizuna-Vault).

Covers:
- RBI Account Aggregator ReBIT DEPOSIT v2.0 schema
- GSTN GSTR-1, GSTR-3B, GSTR-2B data structures
- MCA-21 Director and Form PAS-3 (Return of Allotment) records
- Pitch deck claimed financials
- Double-entry ledger models (Journal entries, Ledger accounts, Trial balance)
- Statutory violation models (Income Tax Act & Companies Act)
- Forensic audit results & Shinrai Governance Scorecard
"""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# ReBIT Account Aggregator Schemas (DEPOSIT v2.0)
# ---------------------------------------------------------------------------

class TransactionMode(str, Enum):
    RTGS = "RTGS"
    NEFT = "NEFT"
    IMPS = "IMPS"
    UPI = "UPI"
    CASH = "CASH"
    ATM = "ATM"
    SELF = "SELF"
    CHEQUE = "CHEQUE"
    OTHER = "OTHER"


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    DEPOSIT_EQUITY = "DEPOSIT_EQUITY"


class RebitTransaction(BaseModel):
    txnId: str = Field(..., description="Unique transaction reference ID")
    type: str = Field(default="OUTWARD")
    mode: str = Field(default="RTGS", description="Payment rail: RTGS, NEFT, IMPS, CASH, ATM, etc.")
    amount: float = Field(..., ge=0, description="Transaction amount in INR")
    currentBalance: float = Field(..., description="Post-transaction bank ledger balance in INR")
    transactionTimestamp: str = Field(..., description="ISO 8601 transaction timestamp")
    valueDate: Optional[str] = Field(default=None, description="Value settlement date (YYYY-MM-DD)")
    narration: str = Field(..., description="Bank statement narration / remarks")
    reference: Optional[str] = Field(default=None, description="Core banking system reference number")
    counterparty: Optional[str] = Field(default=None, description="Counterparty entity name")
    counterpartyGstin: Optional[str] = Field(default=None, description="Counterparty GSTIN if known")
    amount_jpy: Optional[float] = Field(default=None, description="Transaction amount in JPY (canonical rate 1.80)")
    accountHead: Optional[str] = Field(default=None, description="Chart of accounts classification")
    whatHappened: Optional[str] = Field(default=None, description="Itemized forensic description of transaction flow")
    whyReason: Optional[str] = Field(default=None, description="Forensic and statutory justification")
    forensicStatus: Optional[str] = Field(default="VERIFIED_CLEAN", description="VERIFIED_CLEAN or FLAGGED_ANOMALY")
    statutoryCitation: Optional[str] = Field(default=None, description="Statutory legal citation or accounting standard")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {
                "account_head": "accountHead",
                "what_happened": "whatHappened",
                "why_reason": "whyReason",
                "forensic_status": "forensicStatus",
                "statutory_citation": "statutoryCitation",
                "txn_id": "txnId",
                "current_balance": "currentBalance",
                "transaction_timestamp": "transactionTimestamp",
                "value_date": "valueDate",
                "counterparty_gstin": "counterpartyGstin",
            }
            for snake, camel in mapping.items():
                if snake in data and camel not in data:
                    data[camel] = data[snake]
        return data

    @property
    def account_head(self) -> Optional[str]:
        return self.accountHead

    @property
    def what_happened(self) -> Optional[str]:
        return self.whatHappened

    @property
    def why_reason(self) -> Optional[str]:
        return self.whyReason

    @property
    def forensic_status(self) -> Optional[str]:
        return self.forensicStatus

    @property
    def statutory_citation(self) -> Optional[str]:
        return self.statutoryCitation



class RebitPeriod(BaseModel):
    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")


class RebitSummary(BaseModel):
    openingBalance: float
    closingBalance: float
    totalCredits: float
    totalDebits: float
    currency: str = "INR"
    period: Optional[RebitPeriod] = None


class RebitAccount(BaseModel):
    type: str = "DEPOSIT"
    fipId: str = Field(default="HDFC-IN-FIP-001", description="Financial Information Provider Bank Identifier")
    maskedAccNumber: str = Field(default="XXXXXX9821")
    currency: str = "INR"
    holder: str = Field(..., description="Entity / account holder name")
    pan: Optional[str] = Field(default=None, description="10-digit PAN of the company")
    summary: RebitSummary
    Transactions: Dict[str, List[RebitTransaction]]


class RebitStatement(BaseModel):
    Account: RebitAccount


# ---------------------------------------------------------------------------
# GSTN Invoicing Schemas (GSTR-1, GSTR-3B)
# ---------------------------------------------------------------------------

class GstInvoiceType(str, Enum):
    OUTWARD = "OUTWARD"
    INWARD = "INWARD"


class GstOffsetStatus(str, Enum):
    OFFSET_PAID = "OFFSET_PAID"
    UNOFF_SET_UNPAID = "UNOFF_SET_UNPAID"


class GstInvoice(BaseModel):
    invoice_number: str
    irn_hash: Optional[str] = Field(default=None, description="64-char SHA-256 Invoice Registration Number")
    invoice_date: str
    supplier_gstin: str = Field(default="29AABCA1234A1Z5")
    supplier_name: str = Field(default="Target Startup Pvt Ltd")
    buyer_gstin: str = Field(..., min_length=15, max_length=15, description="15-character Buyer GSTIN")
    buyer_name: str
    taxable_value: float = Field(..., ge=0)
    gst_amount: float = Field(..., ge=0)
    total_amount: float = Field(..., ge=0)
    gstr3b_offset_status: str = Field(default="OFFSET_PAID")
    type: str = Field(default="OUTWARD", description="OUTWARD or INWARD")
    amount_jpy: Optional[float] = Field(default=None, description="Invoice amount in JPY")
    account_head: Optional[str] = Field(default=None, description="Chart of accounts classification")
    what_happened: Optional[str] = Field(default=None, description="Itemized invoice description")
    why_reason: Optional[str] = Field(default=None, description="Verification or statutory compliance rationale")
    verification_status: Optional[str] = Field(default="NIC_CRYPTOGRAPHICALLY_VERIFIED", description="NIC cryptographic status")

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {
                "accountHead": "account_head",
                "whatHappened": "what_happened",
                "whyReason": "why_reason",
                "verificationStatus": "verification_status",
                "amountJpy": "amount_jpy",
                "totalAmount": "total_amount",
                "taxableValue": "taxable_value",
                "gstAmount": "gst_amount",
                "invoiceNumber": "invoice_number",
                "invoiceDate": "invoice_date",
                "buyerGstin": "buyer_gstin",
                "buyerName": "buyer_name",
                "receiver_name": "buyer_name",
                "gstin_recipient": "buyer_gstin",
                "invoice_value": "total_amount",
            }
            for source, target in mapping.items():
                if source in data and target not in data:
                    data[target] = data[source]
        return data

    @property
    def accountHead(self) -> Optional[str]:
        return self.account_head

    @property
    def whatHappened(self) -> Optional[str]:
        return self.what_happened

    @property
    def whyReason(self) -> Optional[str]:
        return self.why_reason


# ---------------------------------------------------------------------------
# MCA-21 Director & Form PAS-3 Schemas
# ---------------------------------------------------------------------------

class DirectorRecord(BaseModel):
    cin: str = Field(..., description="21-character Corporate Identification Number")
    company_name: str
    din: str = Field(..., description="8-digit Director Identification Number")
    director_name: str
    pan: str = Field(..., min_length=10, max_length=10, description="10-digit Permanent Account Number")
    address: Optional[str] = None
    appointment_date: Optional[str] = None


class McaPas3Return(BaseModel):
    return_id: str
    cin: str
    allotment_date: str
    allottee_name: str
    allottee_pan: Optional[str] = None
    shares_allotted: int
    nominal_value_per_share: float
    premium_per_share: float = 0.0
    total_amount_received: float
    mode_of_payment: str = "BANKING_CHANNEL"
    bank_reference: Optional[str] = None
    roc_srn: str = Field(..., description="ROC Service Request Number")


# ---------------------------------------------------------------------------
# Pitch Deck Claims
# ---------------------------------------------------------------------------

class PitchClaims(BaseModel):
    company_name: str
    claimed_arr_inr: float = Field(default=0.0, description="Annual Recurring Revenue claimed in pitch deck")
    claimed_mrr_inr: float = Field(default=0.0, description="Monthly Recurring Revenue claimed in pitch deck")
    claimed_burn_rate_inr: float = Field(default=0.0, description="Monthly net burn claimed")
    claimed_runway_months: float = Field(default=0.0, description="Runway months claimed to investors")
    claimed_team_size: Optional[int] = None


# ---------------------------------------------------------------------------
# Double-Entry Accounting Models (ICAI SA 240 / SA 505)
# ---------------------------------------------------------------------------

class AccountCategory(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class JournalLine(BaseModel):
    account_code: str
    account_name: str
    category: AccountCategory
    debit: float = Field(default=0.0, ge=0)
    credit: float = Field(default=0.0, ge=0)
    narration: Optional[str] = None


class JournalEntry(BaseModel):
    entry_id: str
    date: str
    reference: str
    narration: str
    lines: List[JournalLine]
    created_by: str = "SYSTEM"
    is_reversal: bool = False
    is_round_number: bool = False


class TrialBalanceItem(BaseModel):
    account_code: str
    account_name: str
    category: AccountCategory
    debit_total: float
    credit_total: float
    net_debit: float
    net_credit: float


class TrialBalanceReport(BaseModel):
    as_of_date: str
    items: List[TrialBalanceItem]
    total_debits: float
    total_credits: float
    is_balanced: bool
    variance: float = 0.0


# ---------------------------------------------------------------------------
# Forensic Engine Finding Models
# ---------------------------------------------------------------------------

class StatutoryViolation(BaseModel):
    statutory_section: str = Field(..., description="e.g., Income Tax Sec 269ST, Companies Act Sec 188")
    category: str = Field(..., description="CASH_LIMIT, TDS_SMURFING, UNEXPLAINED_CREDIT, SELF_DEALING, GST_DEFICIT")
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    rule_description: str
    evidence_txn_id: Optional[str] = None
    date: Optional[str] = None
    counterparty: Optional[str] = None
    amount_inr: float
    penalty_provision: Optional[str] = None
    penalty_estimate_inr: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class ThreeWayReconciliationResult(BaseModel):
    claimed_sales_inr: float
    gstr1_reported_sales_inr: float
    gstr3b_tax_paid_sales_inr: float
    unpaid_tax_sales_inr: float
    bank_cleared_customer_credits_inr: float
    equity_infusions_inr: float
    director_loans_inr: float
    contra_transfers_inr: float
    delta_tax_pct: float
    delta_cash_pct: float
    phantom_revenue_inr: float
    status: str
    flags: List[str] = Field(default_factory=list)


class RelatedPartyFinding(BaseModel):
    invoice_number: Optional[str] = None
    txn_id: Optional[str] = None
    date: Optional[str] = None
    vendor_name: str
    vendor_gstin: str
    extracted_pan: str
    conflict_director_name: str
    conflict_director_din: str
    amount_inr: float
    amount_jpy: float
    violation: str
    severity: str


class BenfordCluster(BaseModel):
    leading_two_digits: int
    observed_pct: float
    expected_pct: float
    count: int
    inference: str


class BenfordF2DResult(BaseModel):
    sample_size: int
    nigrini_mad: float
    threshold_mad_cutoff: float = 0.0022
    conformity_status: str
    is_anomalous: bool
    clumping_clusters: List[BenfordCluster] = Field(default_factory=list)
    top_digit_frequencies: Dict[int, float] = Field(default_factory=dict)


class TrueRunwayResult(BaseModel):
    cleared_bank_balance_inr: float
    pending_gst_liabilities_inr: float
    unpaid_tds_liabilities_inr: float
    pending_vendor_payables_inr: float
    net_operational_cash_inr: float
    gross_quarterly_burn_inr: float
    normalized_monthly_burn_inr: float
    claimed_runway_months: float
    true_runway_months: float
    runway_inflation_factor: float
    verdict: str


class GovernanceScorecard(BaseModel):
    governance_trust_score: int = Field(..., ge=0, le=100)
    rating_classification: str = Field(..., description="VERIFIED_CLEAN, REQUIRES_REVIEW, or CRITICAL_RED_FLAG_REJECT")
    kanji_badge: str = Field(..., description="【適格】, 【要確認】, or 【精査要】")
    summary_verdict: str
    three_way_reconciliation: ThreeWayReconciliationResult
    related_party_siphoning: Dict[str, Any]
    benford_f2d_analysis: BenfordF2DResult
    statutory_violations: List[StatutoryViolation]
    cash_burn_and_runway: TrueRunwayResult
    window_dressing_events: List[Dict[str, Any]] = Field(default_factory=list)
    working_capital_and_logistics: Optional[Dict[str, Any]] = Field(default_factory=dict)
    indirect_siphoning_findings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    dynamic_statutory_contingencies: Optional[Dict[str, Any]] = Field(default_factory=dict)
    bad_debt_provisioning: Optional[Dict[str, Any]] = Field(default_factory=dict)
    solvency_and_debt_covenants: Optional[Dict[str, Any]] = Field(default_factory=dict)
    circular_debt_findings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    icai_sa240_sa505_findings: Dict[str, Any] = Field(default_factory=dict)
    boardroom_recommendations: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Advanced CA Forensic Matching & Solvency Models
# ---------------------------------------------------------------------------

class StatutoryDefaultEscalation(BaseModel):
    is_cash_distressed: bool
    operating_cash_flow_inr: float
    true_runway_months: float
    tds_sec201_interest_inr: float = 0.0
    gst_sec50_interest_inr: float = 0.0
    gst_sec47_late_fee_inr: float = 0.0
    epfo_sec14b_damages_inr: float = 0.0
    epfo_sec7q_interest_inr: float = 0.0
    total_contingent_statutory_liability_inr: float = 0.0
    total_contingent_statutory_liability_jpy: float = 0.0
    violations: List[StatutoryViolation] = Field(default_factory=list)


class BadDebtProvisioningResult(BaseModel):
    is_write_off_triggered: bool
    ccc_days: float
    dso_days: float
    total_receivables_inr: float
    stage1_healthy_provision_inr: float = 0.0
    stage2_stressed_provision_inr: float = 0.0
    stage3_credit_impaired_writeoff_inr: float = 0.0
    total_bad_debt_provision_inr: float
    claimed_arr_inr: float
    discounted_valuation_inr: float
    valuation_haircut_pct: float
    mandated_write_off_verdict: str


class SolvencyAndDebtCovenantsResult(BaseModel):
    operating_profit_inr: float
    total_debt_service_inr: float
    dscr: float
    dscr_status: str
    current_assets_inr: float
    current_liabilities_inr: float
    current_ratio: float
    quick_ratio: float
    pending_statutory_dues_inr: float
    is_ibc_insolvency_triggered: bool
    solvency_status: str
    covenant_violations: List[StatutoryViolation] = Field(default_factory=list)


class CircularDebtEvent(BaseModel):
    round_trip_id: str
    promoter_loan_txn_id: str
    promoter_loan_amount_inr: float
    promoter_loan_date: str
    promoter_counterparty: str
    fake_sales_txn_id: str
    fake_sales_amount_inr: float
    fake_sales_date: str
    customer_counterparty: str
    siphoning_outflow_txn_id: str
    siphoning_outflow_amount_inr: float
    siphoning_outflow_date: str
    vendor_counterparty: str
    loop_duration_days: int
    total_round_tripped_inr: float
    total_round_tripped_jpy: float
    statutory_citation: str
    severity: str


class CircularDebtAnalysisResult(BaseModel):
    has_circular_debt: bool
    total_circular_amount_inr: float = 0.0
    total_circular_amount_jpy: float = 0.0
    events_detected: List[CircularDebtEvent] = Field(default_factory=list)
    violations: List[StatutoryViolation] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# High-Level Forensic Audit Request & Response Models
# ---------------------------------------------------------------------------

class AuditRequest(BaseModel):
    preset_key: Optional[str] = "clean_startup"  # clean_startup, fraud_startup, logipulse_startup, mirai_startup, edutrek_startup, kwikpay_startup, autocare_startup, zenith_startup
    vault_id: Optional[str] = "TJH-2026-VC01"
    passcode: Optional[str] = "TRUSTVAULT-VC901-TJH"
    investor_email: Optional[str] = "analyst.sato@value-create.com"


class AnomalyFlag(BaseModel):
    rule: str
    severity: str  # CRITICAL, WARNING, INFO
    title: str
    description: str
    amount_inr: Optional[float] = 0.0
    amount_jpy: Optional[float] = 0.0
    statutory_citation: str
    counterparty: Optional[str] = None
    gstin: Optional[str] = None
    date: Optional[str] = None


class ForensicKPIs(BaseModel):
    governance_trust_score: int
    kanji_badge: str
    classification: str
    verdict: str
    claimed_arr_inr: float
    ca_booked_revenue_inr: Optional[float] = 0.0
    gst_invoiced_turnover_inr: Optional[float] = 0.0
    real_bank_credits_inr: float
    phantom_revenue_inr: float
    cash_divergence_pct: float
    siphoned_funds_inr: float
    benford_nigrini_mad: float
    benford_status: str
    claimed_runway_months: float
    true_runway_months: float
    unremitted_tax_dues_inr: float
    doubtful_debtors_inr: Optional[float] = 0.0
    sec269st_cash_violations_inr: Optional[float] = 0.0
    merkle_root: str


class FullAuditResponse(BaseModel):
    status: str
    vault_id: str
    company_name: str
    cin: str
    kpis: ForensicKPIs
    red_flags: List[AnomalyFlag]
    monthly_reconciliation: List[Dict[str, Any]]
    benford_curve: Dict[str, Any]
    hanko_stages: List[Dict[str, Any]]
    watermark: str
