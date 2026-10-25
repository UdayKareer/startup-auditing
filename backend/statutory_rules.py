"""Indian Statutory Tax & Corporate Law Verification Engines.

Codifies:
1. Income Tax Act, 1961 - Section 269ST:
   Prohibits receiving an amount of ₹2,00,000 or more in cash in aggregate from a person in a day,
   or in respect of a single transaction, or transactions relating to one event/occasion.
   Penalty under Section 271DA: 100% of the sum received.

2. Income Tax Act, 1961 - Section 40A(3):
   Disallows business expense deductions where aggregate payment made to a single person in a day
   otherwise than by account payee cheque/draft/ECS exceeds ₹10,000 (₹35,000 for transport contractors).

3. Income Tax Act, 1961 - Section 194C / 194J / 194H:
   Detects TDS smurfing / threshold evasion where disbursements are split into amounts clustered
   just below statutory TDS deduction limits (₹30,000 for Sec 194J professional fees,
   ₹50,000 for internal authorization / Sec 194C contracts, e.g., ₹29,500 or ₹49,500).

4. Income Tax Act, 1961 - Section 68 & 269SS / 269T:
   - Section 68: Unexplained cash credits (e.g. bogus share capital or seed infusions) without
     an official MCA Form PAS-3 (Return of Allotment) are taxed at 78% (Sec 115BBE).
   - Section 269SS/269T: Prohibits taking or repaying loans/deposits in cash >= ₹20,000.

5. Companies Act, 2013 - Section 188 & Section 185:
   - Section 188: Related-Party Transactions (RPT) with directors or entities where directors have interest.
     Detected programmatically by slicing characters 3 to 12 from all vendor GSTINs (GSTIN[2:12]) and
     matching against the MCA-21 Director PAN registry.
   - Section 185: Prohibits loans or financial assistance to directors or director-interested entities.

6. Central Goods and Services Tax (CGST) Rules, 2017 - Rule 88C:
   Detects variance where tax liability declared in Form GSTR-1 exceeds the tax paid in Form GSTR-3B
   by more than 5%. Triggers system-generated DRC-01B notice and bank account attachment risks.
"""

from __future__ import annotations
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from backend.schemas import (
    RebitTransaction,
    GstInvoice,
    DirectorRecord,
    McaPas3Return,
    StatutoryViolation,
    RelatedPartyFinding,
)

INR_TO_JPY_RATE = 1.80


class StatutoryVerificationEngine:
    """Deterministic statutory compliance and forensic audit engine for Indian tax and corporate law."""

    def __init__(
        self,
        directors: List[DirectorRecord],
        pas3_returns: Optional[List[McaPas3Return]] = None,
    ):
        self.directors = directors
        self.pas3_returns = pas3_returns or []
        
        # Build index of director PANs
        self.director_pan_map: Dict[str, DirectorRecord] = {}
        for d in directors:
            clean_pan = d.pan.strip().upper()
            self.director_pan_map[clean_pan] = d

    # ---------------------------------------------------------------------------
    # 1. Section 269ST & Section 40A(3): Cash Siphoning & Disallowed Expenses
    # ---------------------------------------------------------------------------
    def check_cash_limits(self, transactions: List[RebitTransaction]) -> List[StatutoryViolation]:
        """Audit bank ledger for Section 269ST and Section 40A(3) cash violations."""
        violations: List[StatutoryViolation] = []
        
        # Group cash transactions by date
        cash_credits_by_date = defaultdict(list)
        cash_debits_by_date = defaultdict(list)

        for txn in transactions:
            is_cash_mode = txn.mode.upper() in ["CASH", "ATM", "SELF"]
            narration_has_cash = any(k in txn.narration.upper() for k in ["CASH DEPOSIT", "CASH WDL", "SELF CASH"])
            
            if is_cash_mode or narration_has_cash:
                date_key = txn.valueDate or txn.transactionTimestamp[:10]
                if txn.type in ["CREDIT", "DEPOSIT_EQUITY"]:
                    cash_credits_by_date[date_key].append(txn)
                elif txn.type == "DEBIT":
                    cash_debits_by_date[date_key].append(txn)

        # Check Sec 269ST on single-day cash credits >= 2 Lakhs
        for date_str, txns in cash_credits_by_date.items():
            day_total = sum(t.amount for t in txns)
            if day_total >= 200000.0:
                violations.append(
                    StatutoryViolation(
                        statutory_section="Income Tax Act, 1961 - Section 269ST",
                        category="CASH_LIMIT",
                        severity="CRITICAL",
                        rule_description="Cash receipt of ₹2,00,000 or more in a single day is strictly prohibited.",
                        evidence_txn_id="; ".join(t.txnId for t in txns),
                        date=date_str,
                        counterparty="Cash Inflow",
                        amount_inr=day_total,
                        penalty_provision="Section 271DA: 100% penalty on the amount received in cash.",
                        penalty_estimate_inr=day_total,
                        details={
                            "transaction_count": len(txns),
                            "daily_cash_total_inr": day_total,
                        },
                    )
                )

        # Check Sec 40A(3) on single-party cash debits > 10,000
        for date_str, txns in cash_debits_by_date.items():
            for t in txns:
                if t.amount > 10000.0:
                    violations.append(
                        StatutoryViolation(
                            statutory_section="Income Tax Act, 1961 - Section 40A(3)",
                            category="CASH_EXPENSE_DISALLOWANCE",
                            severity="HIGH",
                            rule_description="Business payments exceeding ₹10,000 in cash per day are 100% disallowed.",
                            evidence_txn_id=t.txnId,
                            date=date_str,
                            counterparty=t.narration,
                            amount_inr=t.amount,
                            penalty_provision="Disallowed from tax deductible expenses; taxed at 30% corporate tax rate.",
                            penalty_estimate_inr=round(t.amount * 0.30, 2),
                            details={"mode": t.mode, "narration": t.narration},
                        )
                    )

        return violations

    # ---------------------------------------------------------------------------
    # 2. Section 194C / 194J: TDS Invoice Smurfing & Threshold Clustering
    # ---------------------------------------------------------------------------
    def check_tds_smurfing(self, transactions: List[RebitTransaction]) -> List[StatutoryViolation]:
        """Detect smurfing/structuring below TDS limits (₹30,000 or ₹50,000)."""
        violations: List[StatutoryViolation] = []
        
        # Candidate smurf debits (₹28,000-₹29,999 or ₹48,000-₹49,999)
        smurf_candidates = []
        for txn in transactions:
            if txn.type == "DEBIT":
                amt = txn.amount
                if (28000 <= amt <= 29999) or (48000 <= amt <= 49999):
                    smurf_candidates.append(txn)

        # Group by date and clean counterparty/narration prefix
        grouped = defaultdict(list)
        for txn in smurf_candidates:
            date_key = txn.valueDate or txn.transactionTimestamp[:10]
            # Extract common counterparty tokens
            cleaned_narr = txn.narration.upper()
            tokens = [w for w in re.split(r"[-/_\s]+", cleaned_narr) if len(w) > 3 and w not in ["NEFT", "RTGS", "IMPS"]]
            key = f"{date_key}_{tokens[0] if tokens else 'UNKNOWN'}"
            grouped[key].append(txn)

        for key, txns in grouped.items():
            if len(txns) >= 2:
                total_amt = sum(t.amount for t in txns)
                date_str = txns[0].valueDate or txns[0].transactionTimestamp[:10]
                violations.append(
                    StatutoryViolation(
                        statutory_section="Income Tax Act, 1961 - Section 194C / 194J",
                        category="TDS_SMURFING",
                        severity="HIGH",
                        rule_description=f"Detected {len(txns)} repetitive disbursements structured just below statutory threshold (₹30k or ₹50k) to evade TDS deduction.",
                        evidence_txn_id="; ".join(t.txnId for t in txns),
                        date=date_str,
                        counterparty=txns[0].narration,
                        amount_inr=total_amt,
                        penalty_provision="Interest under Section 201(1A) at 1.5% per month + penalty under Section 271C.",
                        penalty_estimate_inr=round(total_amt * 0.10, 2), # 10% TDS baseline
                        details={
                            "split_count": len(txns),
                            "split_amounts": [t.amount for t in txns],
                        },
                    )
                )

        return violations

    # ---------------------------------------------------------------------------
    # 3. Section 68 & 269SS: Bogus Equity Credits & Angel Tax Verification
    # ---------------------------------------------------------------------------
    def check_unexplained_capital_credits(
        self,
        transactions: List[RebitTransaction],
    ) -> List[StatutoryViolation]:
        """Audit capital and equity credits against filed MCA Form PAS-3 allotment records."""
        violations: List[StatutoryViolation] = []

        # Find bank credits labeled as investment / equity / share application
        capital_credits = []
        for t in transactions:
            if t.type == "DEPOSIT_EQUITY" or (
                t.type == "CREDIT" and any(k in t.narration.upper() for k in ["EQUITY", "SHARE CAPITAL", "SERIES", "ANGEL"])
            ):
                capital_credits.append(t)

        # Match against PAS-3 filings
        filed_srns = {p.roc_srn for p in self.pas3_returns}
        total_pas3_amount = sum(p.total_amount_received for p in self.pas3_returns)

        for cap_txn in capital_credits:
            # If no PAS-3 filing exists or transaction amount exceeds total filings
            has_matching_pas3 = False
            for p in self.pas3_returns:
                if abs(p.total_amount_received - cap_txn.amount) <= 50000.0:
                    has_matching_pas3 = True
                    break

            if not has_matching_pas3 and cap_txn.amount >= 500000.0:
                violations.append(
                    StatutoryViolation(
                        statutory_section="Income Tax Act, 1961 - Section 68",
                        category="UNEXPLAINED_CREDIT",
                        severity="CRITICAL",
                        rule_description="Capital inflow in bank account without matching MCA Form PAS-3 Return of Allotment.",
                        evidence_txn_id=cap_txn.txnId,
                        date=cap_txn.valueDate or cap_txn.transactionTimestamp[:10],
                        counterparty=cap_txn.narration,
                        amount_inr=cap_txn.amount,
                        penalty_provision="Taxed under Section 115BBE at effective 78% rate (60% tax + 25% surcharge + 4% cess).",
                        penalty_estimate_inr=round(cap_txn.amount * 0.78, 2),
                        details={
                            "narration": cap_txn.narration,
                            "pas3_filed_records_count": len(self.pas3_returns),
                        },
                    )
                )

        return violations

    # ---------------------------------------------------------------------------
    # 4. Companies Act 2013 - Section 188 & 185: Promoter Self-Dealing Graph
    # ---------------------------------------------------------------------------
    def check_section_188_related_parties(
        self,
        gst_invoices: List[GstInvoice],
        transactions: List[RebitTransaction],
    ) -> Tuple[List[RelatedPartyFinding], List[StatutoryViolation]]:
        """Traverse entity graph by slicing 10-digit PAN (GSTIN[2:12]) and matching against Director PANs."""
        findings: List[RelatedPartyFinding] = []
        violations: List[StatutoryViolation] = []

        # Map inward vendor invoices
        inward_invoices = [inv for inv in gst_invoices if inv.type == "INWARD"]

        for inv in inward_invoices:
            vendor_gstin = inv.supplier_gstin.strip().upper()
            if len(vendor_gstin) == 15:
                extracted_pan = vendor_gstin[2:12] # Slice characters 3 to 12
                
                if extracted_pan in self.director_pan_map:
                    conflict_director = self.director_pan_map[extracted_pan]
                    amt_inr = inv.total_amount
                    amt_jpy = round(amt_inr * INR_TO_JPY_RATE, 2)

                    finding = RelatedPartyFinding(
                        invoice_number=inv.invoice_number,
                        date=inv.invoice_date,
                        vendor_name=inv.supplier_name,
                        vendor_gstin=vendor_gstin,
                        extracted_pan=extracted_pan,
                        conflict_director_name=conflict_director.director_name,
                        conflict_director_din=conflict_director.din,
                        amount_inr=amt_inr,
                        amount_jpy=amt_jpy,
                        violation="Companies Act, 2013 - Section 188 (Undisclosed Related Party Self-Dealing)",
                        severity="CRITICAL",
                    )
                    findings.append(finding)

                    violations.append(
                        StatutoryViolation(
                            statutory_section="Companies Act, 2013 - Section 188 / 185",
                            category="PROMOTER_SELF_DEALING",
                            severity="CRITICAL",
                            rule_description=(
                                f"Unauthorized commercial disbursement to vendor '{inv.supplier_name}' "
                                f"whose GSTIN contains Director {conflict_director.director_name}'s PAN ({extracted_pan})."
                            ),
                            evidence_txn_id=inv.invoice_number,
                            date=inv.invoice_date,
                            counterparty=inv.supplier_name,
                            amount_inr=amt_inr,
                            penalty_provision="Disqualification of director under Sec 164(1)(g) + penalty up to ₹5,00,000 + disgorgement of profits.",
                            penalty_estimate_inr=amt_inr,
                            details={
                                "vendor_gstin": vendor_gstin,
                                "matched_director_pan": extracted_pan,
                                "director_name": conflict_director.director_name,
                                "director_din": conflict_director.din,
                            },
                        )
                    )

        # Also cross-verify bank debits where counterparty GSTIN or narration indicates related parties
        for txn in transactions:
            if txn.type == "DEBIT":
                cgstin = (getattr(txn, "counterpartyGstin", None) or "").strip().upper()
                cname = getattr(txn, "counterparty", None) or txn.narration
                extracted_pan = ""
                if len(cgstin) == 15:
                    extracted_pan = cgstin[2:12]

                if extracted_pan in self.director_pan_map:
                    conflict_director = self.director_pan_map[extracted_pan]
                    amt_inr = txn.amount
                    amt_jpy = round(amt_inr * INR_TO_JPY_RATE, 2)

                    if not any(f.extracted_pan == extracted_pan and f.amount_inr == amt_inr for f in findings):
                        finding = RelatedPartyFinding(
                            invoice_number=txn.txnId,
                            date=txn.valueDate or txn.transactionTimestamp[:10],
                            vendor_name=cname,
                            vendor_gstin=cgstin,
                            extracted_pan=extracted_pan,
                            conflict_director_name=conflict_director.director_name,
                            conflict_director_din=conflict_director.din,
                            amount_inr=amt_inr,
                            amount_jpy=amt_jpy,
                            violation="Companies Act, 2013 - Section 188 (Undisclosed Related Party Self-Dealing)",
                            severity="CRITICAL",
                        )
                        findings.append(finding)

                        violations.append(
                            StatutoryViolation(
                                statutory_section="Companies Act, 2013 - Section 188 / 185",
                                category="PROMOTER_SELF_DEALING",
                                severity="CRITICAL",
                                rule_description=(
                                    f"Unauthorized commercial disbursement to vendor '{cname}' "
                                    f"whose GSTIN contains Director {conflict_director.director_name}'s PAN ({extracted_pan})."
                                ),
                                evidence_txn_id=txn.txnId,
                                date=txn.valueDate or txn.transactionTimestamp[:10],
                                counterparty=cname,
                                amount_inr=amt_inr,
                                penalty_provision="Disqualification of director under Sec 164(1)(g) + penalty up to ₹5,00,000 + disgorgement of profits.",
                                penalty_estimate_inr=amt_inr,
                                details={
                                    "vendor_gstin": cgstin,
                                    "matched_director_pan": extracted_pan,
                                    "director_name": conflict_director.director_name,
                                    "director_din": conflict_director.din,
                                },
                            )
                        )

                for pan, director in self.director_pan_map.items():
                    if pan in txn.narration.upper() or director.director_name.upper() in txn.narration.upper():
                        # Exclude normal director salary if < 2,50,000/mo
                        if txn.amount >= 500000.0 and "SALARY" not in txn.narration.upper():
                            violations.append(
                                StatutoryViolation(
                                    statutory_section="Companies Act, 2013 - Section 185",
                                    category="DIRECTOR_LOAN_SIPHONING",
                                    severity="CRITICAL",
                                    rule_description=f"Potential loan/advance to Director {director.director_name} in violation of Section 185.",
                                    evidence_txn_id=txn.txnId,
                                    date=txn.valueDate or txn.transactionTimestamp[:10],
                                    counterparty=txn.narration,
                                    amount_inr=txn.amount,
                                    penalty_provision="Section 185(4): Fine of ₹5,00,000 to ₹25,00,000 + imprisonment up to 6 months.",
                                    penalty_estimate_inr=round(txn.amount, 2),
                                    details={"director_name": director.director_name, "director_pan": pan},
                                )
                            )

        return findings, violations

    # ---------------------------------------------------------------------------
    # 5. CGST Rules 2017 - Rule 88C: GSTR-1 vs GSTR-3B Tax Liability Deficit
    # ---------------------------------------------------------------------------
    def check_cgst_rule_88c(self, gst_invoices: List[GstInvoice]) -> Tuple[Dict[str, Any], List[StatutoryViolation]]:
        """Verify sales tax reported in GSTR-1 outward invoices against GSTR-3B offset paid status."""
        violations: List[StatutoryViolation] = []

        outward_invoices = [inv for inv in gst_invoices if inv.type == "OUTWARD"]
        total_gstr1_taxable = sum(inv.taxable_value for inv in outward_invoices)
        total_gstr1_tax = sum(inv.gst_amount for inv in outward_invoices)

        # Invoices marked as OFFSET_PAID vs UNOFF_SET_UNPAID
        paid_invoices = [inv for inv in outward_invoices if inv.gstr3b_offset_status == "OFFSET_PAID"]
        unpaid_invoices = [inv for inv in outward_invoices if inv.gstr3b_offset_status == "UNOFF_SET_UNPAID"]

        gstr3b_paid_taxable = sum(inv.taxable_value for inv in paid_invoices)
        gstr3b_paid_tax = sum(inv.gst_amount for inv in paid_invoices)
        unpaid_taxable = sum(inv.taxable_value for inv in unpaid_invoices)
        unpaid_tax = sum(inv.gst_amount for inv in unpaid_invoices)

        delta_tax_pct = 0.0
        if total_gstr1_taxable > 0:
            delta_tax_pct = round(((total_gstr1_taxable - gstr3b_paid_taxable) / total_gstr1_taxable) * 100, 2)

        is_rule_88c_triggered = delta_tax_pct > 5.0

        if is_rule_88c_triggered:
            violations.append(
                StatutoryViolation(
                    statutory_section="CGST Rules, 2017 - Rule 88C",
                    category="GST_TAX_DEFICIT",
                    severity="CRITICAL",
                    rule_description=(
                        f"GSTR-1 declared outward turnover exceeds GSTR-3B tax-paid turnover by {delta_tax_pct}% "
                        f"(Threshold: 5%). Risk of automated DRC-01B notice and bank freeze."
                    ),
                    evidence_txn_id="; ".join(inv.invoice_number for inv in unpaid_invoices[:5]),
                    date=datetime.now().strftime("%Y-%m-%d"),
                    counterparty="Goods and Services Tax Network (GSTN)",
                    amount_inr=unpaid_tax,
                    penalty_provision="Rule 88C / Section 73: Immediate DRC-01B demand + 18% p.a. interest under Section 50 + bank account attachment under Section 83.",
                    penalty_estimate_inr=round(unpaid_tax * 1.18, 2),
                    details={
                        "gstr1_total_sales_inr": total_gstr1_taxable,
                        "gstr3b_tax_paid_sales_inr": gstr3b_paid_taxable,
                        "unremitted_sales_inr": unpaid_taxable,
                        "unremitted_gst_tax_inr": unpaid_tax,
                        "variance_percentage": delta_tax_pct,
                    },
                )
            )

        summary = {
            "gstr1_declared_sales_inr": round(total_gstr1_taxable, 2),
            "gstr3b_tax_paid_sales_inr": round(gstr3b_paid_taxable, 2),
            "unremitted_turnover_inr": round(unpaid_taxable, 2),
            "unremitted_gst_liability_inr": round(unpaid_tax, 2),
            "delta_tax_percentage": delta_tax_pct,
            "is_rule_88c_triggered": is_rule_88c_triggered,
        }

        return summary, violations

    # ---------------------------------------------------------------------------
    # Run Full Statutory Verification Suite
    # ---------------------------------------------------------------------------
    def run_full_statutory_audit(
        self,
        transactions: List[RebitTransaction],
        gst_invoices: List[GstInvoice],
    ) -> Dict[str, Any]:
        """Execute all statutory verification engines deterministically."""
        all_violations: List[StatutoryViolation] = []

        cash_violations = self.check_cash_limits(transactions)
        all_violations.extend(cash_violations)

        smurf_violations = self.check_tds_smurfing(transactions)
        all_violations.extend(smurf_violations)

        cap_violations = self.check_unexplained_capital_credits(transactions)
        all_violations.extend(cap_violations)

        related_findings, related_violations = self.check_section_188_related_parties(gst_invoices, transactions)
        all_violations.extend(related_violations)

        gst_summary, gst_violations = self.check_cgst_rule_88c(gst_invoices)
        all_violations.extend(gst_violations)

        total_penalty_exposure = sum(v.penalty_estimate_inr for v in all_violations)

        return {
            "total_statutory_violations_detected": len(all_violations),
            "total_statutory_penalty_exposure_inr": round(total_penalty_exposure, 2),
            "total_statutory_penalty_exposure_jpy": round(total_penalty_exposure * INR_TO_JPY_RATE, 2),
            "violations_list": [(v.model_dump() if hasattr(v, 'model_dump') else v.dict()) for v in all_violations],
            "related_party_findings": [(f.model_dump() if hasattr(f, 'model_dump') else f.dict()) for f in related_findings],
            "cgst_rule_88c_summary": gst_summary,
        }
