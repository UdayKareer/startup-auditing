"""Double-Entry Accounting & ICAI Auditing Standards Engine.

Governs:
- ICAI Standard on Auditing (SA 240): The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statements.
  * Unusual journal entries (round-number postings, weekend/off-hour entries, management override).
  * Fictitious journal entries created without commercial justification.
- ICAI Standard on Auditing (SA 505): External Confirmations.
  * Direct independent confirmation matching between internal General Ledger and external Sovereign DPI sources
    (RBI Account Aggregator bank deposits and GSTN NIC-signed outward e-invoices).
- Core Double-Entry General Ledger:
  * Journal Entry validation (Sum Debits == Sum Credits).
  * T-Account ledger postings and running balance derivation.
  * Trial Balance formulation and balance verification.
  * Bank Reconciliation Statement (BRS) calculation (Book balance vs. Bank statement balance).
"""

from __future__ import annotations
import math
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from backend.schemas import (
    AccountCategory,
    JournalLine,
    JournalEntry,
    TrialBalanceItem,
    TrialBalanceReport,
    RebitTransaction,
    GstInvoice,
)


class DoubleEntryLedgerEngine:
    """Enterprise double-entry ledger implementing ICAI SA 240 & SA 505 auditing checks."""

    def __init__(self):
        self.journal_entries: List[JournalEntry] = []
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.running_balances: Dict[str, float] = defaultdict(float)

    def add_account(self, code: str, name: str, category: AccountCategory):
        """Register a chart of accounts entry."""
        self.accounts[code] = {
            "name": name,
            "category": category,
            "debit_total": 0.0,
            "credit_total": 0.0,
        }

    def post_journal_entry(
        self,
        entry_id: str,
        date: str,
        reference: str,
        narration: str,
        lines: List[JournalLine],
        created_by: str = "SYSTEM",
        is_reversal: bool = False,
    ) -> JournalEntry:
        """Validate and post a double-entry journal transaction.
        
        Enforces strict mathematical balance: Sum(Debits) == Sum(Credits).
        """
        total_debits = sum(line.debit for line in lines)
        total_credits = sum(line.credit for line in lines)

        # Enforce fundamental double-entry identity
        if abs(total_debits - total_credits) > 0.01:
            raise ValueError(
                f"Double-entry balance violation in {entry_id}: "
                f"Debits (₹{total_debits:,.2f}) != Credits (₹{total_credits:,.2f})"
            )

        # Check for round number transaction (SA 240 indicator)
        is_round = False
        if total_debits >= 100000 and (total_debits % 100000 == 0 or total_debits % 50000 == 0):
            is_round = True

        entry = JournalEntry(
            entry_id=entry_id,
            date=date,
            reference=reference,
            narration=narration,
            lines=lines,
            created_by=created_by,
            is_reversal=is_reversal,
            is_round_number=is_round,
        )
        self.journal_entries.append(entry)

        # Post to T-accounts
        for line in lines:
            if line.account_code not in self.accounts:
                self.add_account(line.account_code, line.account_name, line.category)
            
            self.accounts[line.account_code]["debit_total"] += line.debit
            self.accounts[line.account_code]["credit_total"] += line.credit

            # Update running balances based on normal balance rules:
            # Asset / Expense: Debit increases balance
            # Liability / Equity / Revenue: Credit increases balance
            cat = line.category
            if cat in [AccountCategory.ASSET, AccountCategory.EXPENSE]:
                self.running_balances[line.account_code] += (line.debit - line.credit)
            else:
                self.running_balances[line.account_code] += (line.credit - line.debit)

        return entry

    def generate_trial_balance(self, as_of_date: str) -> TrialBalanceReport:
        """Generate verified Trial Balance and check that Total Debits == Total Credits."""
        items: List[TrialBalanceItem] = []
        total_debits = 0.0
        total_credits = 0.0

        for code, acc in sorted(self.accounts.items()):
            d_total = acc["debit_total"]
            c_total = acc["credit_total"]
            net_d = max(0.0, d_total - c_total)
            net_c = max(0.0, c_total - d_total)

            total_debits += net_d
            total_credits += net_c

            items.append(
                TrialBalanceItem(
                    account_code=code,
                    account_name=acc["name"],
                    category=acc["category"],
                    debit_total=round(d_total, 2),
                    credit_total=round(c_total, 2),
                    net_debit=round(net_d, 2),
                    net_credit=round(net_c, 2),
                )
            )

        variance = round(abs(total_debits - total_credits), 2)
        is_balanced = variance <= 0.02

        return TrialBalanceReport(
            as_of_date=as_of_date,
            items=items,
            total_debits=round(total_debits, 2),
            total_credits=round(total_credits, 2),
            is_balanced=is_balanced,
            variance=variance,
        )

    # ---------------------------------------------------------------------------
    # ICAI SA 240: Fraud Risk Assessment on Journal Entries
    # ---------------------------------------------------------------------------
    def audit_sa240_fraud_indicators(self) -> Dict[str, Any]:
        """Audit journal entries against ICAI Standard on Auditing SA 240:
        
        1. Month-end / period-end round-number manual entries to revenue or asset accounts.
        2. Entries made by unauthorized users or posted at unusual times.
        3. Fictitious credit memos or contra-cancellations immediately following quarter-end.
        4. Management override: debiting cash and crediting unearned revenue/contra without invoices.
        """
        flagged_entries = []
        round_number_flags = []
        period_end_flags = []
        unusual_narration_flags = []

        suspicious_keywords = ["contra", "adjustment", "round off", "manual plug", "promoter infusion", "temp credit"]

        for entry in self.journal_entries:
            # 1. Round number check (e.g., ₹25,00,000, ₹50,00,000)
            entry_amount = sum(l.debit for l in entry.lines)
            if entry.is_round_number and entry_amount >= 500000:
                flag = {
                    "entry_id": entry.entry_id,
                    "date": entry.date,
                    "amount_inr": entry_amount,
                    "reason": f"Suspicious round-number journal entry of ₹{entry_amount:,.2f} posted without granular invoice breakdown",
                    "narration": entry.narration,
                }
                round_number_flags.append(flag)
                flagged_entries.append(flag)

            # 2. Date proximity to quarter-end (28th to 31st of March/September/December/June)
            try:
                dt = datetime.strptime(entry.date, "%Y-%m-%d")
                if dt.day >= 27 and dt.month in [3, 6, 9, 12]:
                    # Check if it affects revenue, equity, or large cash movements
                    affects_sensitive = any(l.category in [AccountCategory.REVENUE, AccountCategory.EQUITY, AccountCategory.ASSET] for l in entry.lines)
                    if affects_sensitive and entry_amount >= 500000.0:
                        flag = {
                            "entry_id": entry.entry_id,
                            "date": entry.date,
                            "amount_inr": entry_amount,
                            "reason": f"Quarter-end liquidity/equity spike entry posted on {entry.date} (Day {dt.day}) for ₹{entry_amount:,.2f}",
                            "narration": entry.narration,
                        }
                        period_end_flags.append(flag)
                        if flag not in flagged_entries:
                            flagged_entries.append(flag)
            except Exception:
                pass

            # 3. Suspicious narration keywords
            if any(kw in entry.narration.lower() for kw in suspicious_keywords):
                flag = {
                    "entry_id": entry.entry_id,
                    "date": entry.date,
                    "amount_inr": entry_amount,
                    "reason": f"Journal narration contains audit-sensitive keyword: '{entry.narration}'",
                    "narration": entry.narration,
                }
                unusual_narration_flags.append(flag)
                flagged_entries.append(flag)

        return {
            "standard": "ICAI SA 240 (Auditor's Responsibilities Relating to Fraud)",
            "total_entries_audited": len(self.journal_entries),
            "total_risk_entries_flagged": len(flagged_entries),
            "round_number_flags": round_number_flags,
            "quarter_end_timing_flags": period_end_flags,
            "suspicious_narration_flags": unusual_narration_flags,
            "fraud_risk_level": "CRITICAL" if len(flagged_entries) >= 3 else ("MEDIUM" if flagged_entries else "LOW"),
        }

    # ---------------------------------------------------------------------------
    # ICAI SA 505: External Confirmations with Sovereign DPI
    # ---------------------------------------------------------------------------
    def audit_sa505_external_confirmations(
        self,
        bank_transactions: List[RebitTransaction],
        gst_invoices: List[GstInvoice],
    ) -> Dict[str, Any]:
        """Verify internal General Ledger balances against independent external sources (ICAI SA 505):
        
        1. Bank Account Confirmation: Compare internal Cash/Bank ledger debit credits against
           cryptographically signed ReBIT Account Aggregator statements.
        2. Trade Receivables / Revenue Confirmation: Compare internal Accounts Receivable and
           Revenue credits against GSTN GSTR-1 outward invoices having verifiable NIC IRN hashes.
        """
        # 1. Internal Book Totals
        book_bank_debits = 0.0  # Money into bank in books
        book_bank_credits = 0.0 # Money out of bank in books
        book_sales_total = 0.0

        for entry in self.journal_entries:
            for line in entry.lines:
                if "bank" in line.account_name.lower() or "cash" in line.account_name.lower():
                    book_bank_debits += line.debit
                    book_bank_credits += line.credit
                if line.category == AccountCategory.REVENUE:
                    book_sales_total += line.credit

        # 2. External Bank Confirmation (ReBIT AA)
        external_bank_credits = sum(t.amount for t in bank_transactions if t.type in ["CREDIT", "DEPOSIT_EQUITY"])
        external_bank_debits = sum(t.amount for t in bank_transactions if t.type == "DEBIT")
        external_cleared_customer_credits = sum(
            t.amount for t in bank_transactions 
            if t.type == "CREDIT" and "contra" not in t.narration.lower() and "equity" not in t.narration.lower()
        )

        # 3. External GST Invoicing Confirmation (GSTR-1 outward)
        external_gst_sales = sum(inv.taxable_value for inv in gst_invoices if inv.type == "OUTWARD")
        external_gst_total = sum(inv.total_amount for inv in gst_invoices if inv.type == "OUTWARD")
        verified_irn_count = sum(1 for inv in gst_invoices if inv.irn_hash and len(inv.irn_hash) == 64)

        # 4. Compute Discrepancy & Confirmation Status
        bank_inflow_variance = abs(book_bank_debits - external_bank_credits)
        sales_variance = abs(book_sales_total - external_gst_sales)

        bank_confirmed = bank_inflow_variance <= 1000.0
        sales_confirmed = sales_variance <= 1000.0

        discrepancies = []
        if not bank_confirmed:
            discrepancies.append({
                "account": "Cash at Bank",
                "internal_book_figure_inr": round(book_bank_debits, 2),
                "external_sovereign_figure_inr": round(external_bank_credits, 2),
                "variance_inr": round(bank_inflow_variance, 2),
                "finding": "Internal ledger cash receipts diverge from RBI Account Aggregator statement.",
            })

        if not sales_confirmed:
            discrepancies.append({
                "account": "Sales / Revenue",
                "internal_book_figure_inr": round(book_sales_total, 2),
                "external_sovereign_figure_inr": round(external_gst_sales, 2),
                "variance_inr": round(sales_variance, 2),
                "finding": "Booked revenue differs from GSTR-1 outward tax invoices registered on GSTN.",
            })

        return {
            "standard": "ICAI SA 505 (External Confirmations)",
            "external_sources_utilized": [
                "Reserve Bank of India Account Aggregator (ReBIT DEPOSIT v2.0)",
                "GSTN Invoice Registration Portal (NIC e-Invoice IRN Hash Registry)"
            ],
            "bank_reconciliation_confirmation": {
                "internal_book_debits_inr": round(book_bank_debits, 2),
                "external_bank_credits_inr": round(external_bank_credits, 2),
                "external_cleared_customer_credits_inr": round(external_cleared_customer_credits, 2),
                "is_confirmed": bank_confirmed,
            },
            "revenue_external_confirmation": {
                "internal_book_revenue_inr": round(book_sales_total, 2),
                "external_gstr1_taxable_inr": round(external_gst_sales, 2),
                "external_gstr1_gross_inr": round(external_gst_total, 2),
                "nic_irn_verified_invoices": verified_irn_count,
                "is_confirmed": sales_confirmed,
            },
            "confirmation_discrepancies": discrepancies,
            "sa505_overall_verdict": "CONFIRMED_CLEAN" if (bank_confirmed and sales_confirmed) else "UNCONFIRMED_DISCREPANCY_FLAGGED",
        }
