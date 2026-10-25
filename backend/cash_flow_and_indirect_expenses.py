"""Cash Conversion Cycle (CCC), Logistics Working Capital, and Indirectly Directed Expenses Engine.

Target: Track OPEN-PS-01 (Thapar Japan Hackathon 2026)
Focus Areas:
1. Logistics & Working Capital Dynamics:
   - Days Sales Outstanding (DSO) and Days Payable Outstanding (DPO).
   - Cash Conversion Cycle (CCC = DSO + DIO - DPO).
   - Accounts Receivable (AR) Aging Buckets (0-30, 31-60, 61-90, 90+ days).
   - Operating Cash Flow to EBITDA Conversion Efficiency (OCF / EBITDA).
   - Fictitious Revenue / Expected Credit Loss (ECL) under Ind AS 109 & ICAI SA 240.

2. Indirectly Directed Expenses & Disguised Promoter Siphoning:
   - Income Tax Act Section 40A(2)(b): Unreasonable payments to relatives / specified persons.
   - Address Co-location Matching: Vendor registered address matching Director residential address (MCA-21 vs GSTN).
   - Ghost Payroll / Headcount Inflation: Reconciling bank salary batch debits against claimed pitch headcount and EPFO ECR filings.
   - Disguised Personal / Lifestyle Expenses: Corporate bank debits for personal travel, luxury hospitality, and non-business items.
   - Intermediary Layering: Rapid pass-through outflows where funds are routed through an intermediate consulting/marketing shell within 48 hours.
"""

from __future__ import annotations
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict

from backend.schemas import (
    RebitTransaction,
    GstInvoice,
    DirectorRecord,
    PitchClaims,
    StatutoryViolation,
    StatutoryDefaultEscalation,
    BadDebtProvisioningResult,
    SolvencyAndDebtCovenantsResult,
    CircularDebtEvent,
    CircularDebtAnalysisResult,
)

INR_TO_JPY_RATE = 1.80


class CashConversionAndIndirectExpenseEngine:
    """Forensic engine for working capital logistics, cash conversion velocity, and indirect expense siphoning."""

    def __init__(
        self,
        directors: List[DirectorRecord],
        gst_invoices: List[GstInvoice],
        bank_transactions: List[RebitTransaction],
        pitch_claims: Optional[PitchClaims] = None,
        ca_books: Optional[Dict[str, Any]] = None,
    ):
        self.directors = directors
        self.gst_invoices = gst_invoices
        self.bank_transactions = bank_transactions
        self.pitch_claims = pitch_claims or PitchClaims(company_name="Target Entity")
        self.ca_books = ca_books or {}
        self.director_pan_map: Dict[str, DirectorRecord] = {d.pan.strip().upper(): d for d in directors if d.pan}

    # ---------------------------------------------------------------------------
    # 1. Cash Conversion Cycle (CCC) & AR Aging Schedule
    # ---------------------------------------------------------------------------
    def analyze_cash_conversion_cycle(self) -> Dict[str, Any]:
        """Compute Days Sales Outstanding (DSO), Days Payable Outstanding (DPO), and Aging Buckets."""
        outward_invoices = [inv for inv in self.gst_invoices if inv.type == "OUTWARD"]
        inward_invoices = [inv for inv in self.gst_invoices if inv.type == "INWARD"]

        total_credit_sales = sum(inv.total_amount for inv in outward_invoices)
        total_inward_purchases = sum(inv.total_amount for inv in inward_invoices)

        # Bank collections from customers
        customer_collections = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "CREDIT" and "contra" not in t.narration.lower() and "equity" not in t.narration.lower()
        )

        # Bank payments to vendors
        vendor_payments = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "DEBIT" and "salary" not in t.narration.lower() and "contra" not in t.narration.lower()
        )

        # Outstanding Trade Receivables (Uncollected)
        trade_receivables = max(0.0, total_credit_sales - customer_collections)
        # Outstanding Trade Payables
        trade_payables = max(0.0, total_inward_purchases - vendor_payments)

        # Compute DSO & DPO (dynamically calculating statement period, minimum 90 days)
        txn_dates = []
        for t in self.bank_transactions:
            d_str = t.valueDate or t.transactionTimestamp[:10]
            try:
                txn_dates.append(datetime.strptime(d_str, "%Y-%m-%d"))
            except Exception:
                pass
        if txn_dates:
            span_days = (max(txn_dates) - min(txn_dates)).days
            days_in_period = max(90, span_days)
        else:
            days_in_period = 90

        dso = round((trade_receivables / max(1.0, total_credit_sales)) * days_in_period, 1) if total_credit_sales > 0 else 0.0
        dpo = round((trade_payables / max(1.0, total_inward_purchases)) * days_in_period, 1) if total_inward_purchases > 0 else 0.0
        dio = 15.0  # Assumed standard tech inventory / WIP days
        ccc = round(dso + dio - dpo, 1)

        # AR Aging Breakdown based on invoice date relative to latest statement or invoice date
        all_dates = txn_dates.copy()
        for inv in self.gst_invoices:
            if getattr(inv, "invoice_date", None):
                try:
                    all_dates.append(datetime.strptime(inv.invoice_date, "%Y-%m-%d"))
                except Exception:
                    pass
        as_of_date = max(all_dates) if all_dates else datetime(2026, 12, 31)
        aging_buckets = {
            "bucket_0_30_days": {"amount_inr": 0.0, "count": 0, "status": "CURRENT_HEALTHY"},
            "bucket_31_60_days": {"amount_inr": 0.0, "count": 0, "status": "NORMAL_COLLECTION"},
            "bucket_61_90_days": {"amount_inr": 0.0, "count": 0, "status": "STRETCHED_WORKING_CAPITAL"},
            "bucket_90_plus_days": {"amount_inr": 0.0, "count": 0, "status": "HIGH_RISK_FICTITIOUS_REVENUE"},
        }

        stale_invoices = []
        for inv in outward_invoices:
            # Check if this invoice was marked unpaid in GSTR-3B or has no bank match
            if inv.gstr3b_offset_status == "UNOFF_SET_UNPAID" or trade_receivables > 0:
                try:
                    inv_dt = datetime.strptime(inv.invoice_date, "%Y-%m-%d")
                    age_days = (as_of_date - inv_dt).days
                    amt = inv.total_amount

                    if age_days <= 30:
                        aging_buckets["bucket_0_30_days"]["amount_inr"] += amt
                        aging_buckets["bucket_0_30_days"]["count"] += 1
                    elif age_days <= 60:
                        aging_buckets["bucket_31_60_days"]["amount_inr"] += amt
                        aging_buckets["bucket_31_60_days"]["count"] += 1
                    elif age_days <= 90:
                        aging_buckets["bucket_61_90_days"]["amount_inr"] += amt
                        aging_buckets["bucket_61_90_days"]["count"] += 1
                    else:
                        aging_buckets["bucket_90_plus_days"]["amount_inr"] += amt
                        aging_buckets["bucket_90_plus_days"]["count"] += 1
                        stale_invoices.append({
                            "invoice_number": inv.invoice_number,
                            "buyer_name": inv.buyer_name,
                            "amount_inr": amt,
                            "age_days": age_days,
                            "risk": "Receivable aged >90 days without cash realization. High probability of fictitious invoice under ICAI SA 240.",
                        })
                except Exception:
                    pass

        # OCF to EBITDA Conversion Efficiency
        # Approximate EBITDA = Total Sales - Total Operational Vendor Debits - Payroll
        claimed_revenue = max(total_credit_sales, self.pitch_claims.claimed_arr_inr / 4.0)
        total_opex = sum(t.amount for t in self.bank_transactions if t.type == "DEBIT" and "contra" not in t.narration.lower())
        operating_cash_inflow = customer_collections - total_opex
        estimated_accounting_ebitda = claimed_revenue - (total_inward_purchases + 20000000.0) # approx costs

        ocf_to_ebitda_pct = 0.0
        if estimated_accounting_ebitda > 0:
            ocf_to_ebitda_pct = round((operating_cash_inflow / estimated_accounting_ebitda) * 100, 2)

        return {
            "working_capital_metrics": {
                "total_credit_sales_inr": round(total_credit_sales, 2),
                "actual_customer_collections_inr": round(customer_collections, 2),
                "outstanding_receivables_inr": round(trade_receivables, 2),
                "outstanding_payables_inr": round(trade_payables, 2),
                "dso_days": dso,
                "dpo_days": dpo,
                "dio_days": dio,
                "cash_conversion_cycle_days": ccc,
                "cash_conversion_efficiency_status": (
                    "EXCELLENT" if ccc < 30 else ("ACCEPTABLE" if ccc < 60 else "CRITICAL_LIQUIDITY_DRAG")
                ),
            },
            "ar_aging_schedule": aging_buckets,
            "stale_receivables_flags": stale_invoices,
            "ocf_to_ebitda_conversion": {
                "operating_cash_inflow_inr": round(operating_cash_inflow, 2),
                "estimated_ebitda_inr": round(estimated_accounting_ebitda, 2),
                "conversion_rate_pct": ocf_to_ebitda_pct,
                "verdict": (
                    "HEALTHY_CASH_CONVERSION" if ocf_to_ebitda_pct >= 75.0 else "EARNINGS_QUALITY_RED_FLAG_DISCONNECTED"
                ),
            },
        }

    # ---------------------------------------------------------------------------
    # 2. Indirectly Directed Expenses & Disguised Siphoning
    # ---------------------------------------------------------------------------
    def audit_indirect_expenses_and_siphoning(self) -> Dict[str, Any]:
        """Identify indirect siphoning, Section 40A(2)(b) relative expenses, ghost payroll, and address co-locations."""
        violations: List[StatutoryViolation] = []
        address_conflicts = []
        disguised_personal_expenses = []
        ghost_payroll_alerts = []

        director_addresses = [d.address.upper() for d in self.directors if d.address]
        director_surnames = set()
        for d in self.directors:
            parts = d.director_name.strip().split()
            if len(parts) >= 2:
                director_surnames.add(parts[-1].upper())

        # 1. Address Co-location matching (Vendor address matches Director home)
        # Check if vendor has matching locality or address token with director
        for inv in self.gst_invoices:
            if inv.type == "INWARD":
                vendor_name_clean = inv.supplier_name.upper()
                for d in self.directors:
                    if d.address:
                        # Extract core locality tokens (e.g. "Koramangala", "Whitefield", "Lotus Towers")
                        locality_tokens = [tok for tok in re.split(r"[, \s-]+", d.address.upper()) if len(tok) >= 5 and tok not in ["FLAT", "VILLA", "ROAD", "STREET", "TOWERS"]]
                        for loc in locality_tokens:
                            if loc in vendor_name_clean:
                                address_conflicts.append({
                                    "vendor_name": inv.supplier_name,
                                    "vendor_gstin": inv.supplier_gstin,
                                    "matched_director": d.director_name,
                                    "director_locality": loc,
                                    "amount_inr": inv.total_amount,
                                    "finding": f"Vendor '{inv.supplier_name}' shares residential locality '{loc}' with Director {d.director_name}. Potential undisclosed related entity.",
                                })

        # 2. Income Tax Act Sec 40A(2)(b) & Disguised Lifestyle Expenses
        # Check bank transaction narrations for luxury/lifestyle indicators booked on corporate card
        lifestyle_keywords = [
            "HOTEL", "RESORT", "JEWEL", "CLUB", "SPA", "LUXURY", "AIRBNB", "FLIGHT PERSONAL",
            "RETAIL MALL", "FASHION", "TAJ", "MARRIOTT", "OBEROI"
        ]

        for txn in self.bank_transactions:
            if txn.type == "DEBIT":
                narr_upper = txn.narration.upper()
                for kw in lifestyle_keywords:
                    if kw in narr_upper and txn.amount >= 25000.0:
                        disguised_personal_expenses.append({
                            "txn_id": txn.txnId,
                            "date": txn.valueDate or txn.transactionTimestamp[:10],
                            "amount_inr": txn.amount,
                            "narration": txn.narration,
                            "flagged_keyword": kw,
                            "regulatory_risk": "Income Tax Sec 40A(2)(b) & Sec 37(1) - Personal lifestyle expense improperly booked as business expenditure.",
                        })
                        violations.append(
                            StatutoryViolation(
                                statutory_section="Income Tax Act, 1961 - Section 40A(2)(b) / Section 37(1)",
                                category="DISGUISED_PERSONAL_EXPENSE",
                                severity="HIGH",
                                rule_description=f"Personal lifestyle expenditure booked under corporate debit: '{txn.narration}'.",
                                evidence_txn_id=txn.txnId,
                                date=txn.valueDate or txn.transactionTimestamp[:10],
                                counterparty=txn.narration,
                                amount_inr=txn.amount,
                                penalty_provision="Disallowed from business expenses + added to taxable corporate profit + 100% penalty under Section 270A.",
                                penalty_estimate_inr=round(txn.amount * 0.60, 2),
                                details={"keyword_matched": kw},
                            )
                        )
                        break

        # 3. Ghost Payroll / Salary Headcount Analysis
        # Extract payroll batch debits and verify consistency
        salary_txns = [t for t in self.bank_transactions if t.type == "DEBIT" and "SALARY" in t.narration.upper()]
        total_salary_disbursed = sum(t.amount for t in salary_txns)
        claimed_team_size = self.pitch_claims.claimed_team_size or 25

        # Check average compensation per claimed employee
        if claimed_team_size > 0 and total_salary_disbursed > 0:
            # Assume quarterly period (3 months)
            avg_monthly_salary_per_head = (total_salary_disbursed / 3.0) / claimed_team_size
            if avg_monthly_salary_per_head > 500000.0:
                ghost_payroll_alerts.append({
                    "claimed_team_size": claimed_team_size,
                    "quarterly_salary_payout_inr": total_salary_disbursed,
                    "implied_monthly_salary_per_head": round(avg_monthly_salary_per_head, 2),
                    "finding": f"Implied average monthly salary of ₹{avg_monthly_salary_per_head:,.2f}/head is extraordinarily inflated. Potential ghost payroll siphoning.",
                })

        # 4. Rapid Pass-Through Intermediary Outflows (<48 hours)
        # Check if large equity/investor credits are immediately drained within 48 hours to non-payroll vendors
        sorted_txns = sorted(self.bank_transactions, key=lambda t: t.valueDate or t.transactionTimestamp)
        pass_through_events = []

        for i, credit in enumerate(sorted_txns):
            if credit.type in ["CREDIT", "DEPOSIT_EQUITY"] and credit.amount >= 5000000.0:
                c_dt_str = credit.valueDate or credit.transactionTimestamp[:10]
                try:
                    c_dt = datetime.strptime(c_dt_str, "%Y-%m-%d")
                    for debit in sorted_txns[i+1:]:
                        d_dt_str = debit.valueDate or debit.transactionTimestamp[:10]
                        try:
                            d_dt = datetime.strptime(d_dt_str, "%Y-%m-%d")
                            delta_hours = (d_dt - c_dt).total_seconds() / 3600.0
                            if 0 < delta_hours <= 48 and debit.type == "DEBIT" and debit.amount >= 2000000.0:
                                if "salary" not in debit.narration.lower():
                                    pass_through_events.append({
                                        "infusion_txn_id": credit.txnId,
                                        "infusion_amount_inr": credit.amount,
                                        "infusion_date": c_dt_str,
                                        "outflow_txn_id": debit.txnId,
                                        "outflow_amount_inr": debit.amount,
                                        "outflow_date": d_dt_str,
                                        "vendor_narration": debit.narration,
                                        "drain_time_hours": round(delta_hours, 1),
                                        "finding": f"Rapid capital drainage: ₹{debit.amount:,.2f} siphoned to '{debit.narration}' within {round(delta_hours, 1)} hours of ₹{credit.amount:,.2f} equity infusion.",
                                    })
                        except Exception:
                            pass
                except Exception:
                    pass

        return {
            "indirect_siphoning_summary": {
                "total_disguised_personal_expenses_inr": sum(e["amount_inr"] for e in disguised_personal_expenses),
                "total_disguised_personal_expenses_jpy": sum(e["amount_inr"] for e in disguised_personal_expenses) * INR_TO_JPY_RATE,
                "disguised_personal_expenses": disguised_personal_expenses,
                "address_co_location_conflicts": address_conflicts,
                "ghost_payroll_alerts": ghost_payroll_alerts,
                "rapid_pass_through_drainage": pass_through_events,
            },
            "statutory_violations": [(v.model_dump() if hasattr(v, 'model_dump') else v.dict()) for v in violations],
        }

    # ---------------------------------------------------------------------------
    # 3. Dynamic Liquidity & Cash Flow Contingencies Engine
    # ---------------------------------------------------------------------------
    def evaluate_dynamic_liquidity_contingencies(
        self,
        ca_books: Optional[Dict[str, Any]] = None,
        true_runway_months: Optional[float] = None,
    ) -> StatutoryDefaultEscalation:
        """Dynamic Liquidity & Cash Flow Contingencies Engine.
        
        Trigger Condition: If Operating Cash Flow < 0 OR True Runway < 3.0 months:
        Escalates statutory defaults:
        1. Income Tax Sec 201(1A) TDS Default Interest (1.5% per month).
        2. CGST Sec 50 Interest (18% p.a.) & Sec 47 Late Fees (₹50/day).
        3. EPFO Sec 14B Penal Damages (up to 25% p.a.) & Sec 7Q Interest (12% p.a.).
        """
        books = ca_books or self.ca_books
        
        # 1. Compute Operating Cash Flow (OCF)
        customer_collections = sum(
            t.amount for t in self.bank_transactions
            if t.type == "CREDIT" and "contra" not in t.narration.lower() and "equity" not in t.narration.lower()
        )
        operational_debits = sum(
            t.amount for t in self.bank_transactions
            if t.type == "DEBIT" and "contra" not in t.narration.lower()
        )
        operating_cash_flow = round(customer_collections - operational_debits, 2)
        
        # 2. Runway
        if true_runway_months is None:
            closing = 0.0
            if self.bank_transactions:
                closing = self.bank_transactions[-1].currentBalance
            monthly_burn = max(100000.0, operational_debits / 3.0)
            true_runway = max(0.0, round(closing / monthly_burn, 1))
        else:
            true_runway = round(true_runway_months, 1)

        # Contingency Trigger
        is_cash_distressed = (operating_cash_flow < 0.0) or (true_runway < 3.0)
        
        violations: List[StatutoryViolation] = []
        tds_interest = 0.0
        gst_interest = 0.0
        gst_late_fees = 0.0
        epfo_damages = 0.0
        epfo_interest = 0.0
        
        # Extract pending dues from CA books or GST/invoices
        stat_dues = books.get("trial_balance_inr", {}).get("statutory_dues_payable", {})
        pending_tds = float(stat_dues.get("tds_payable", 0.0))
        if pending_tds == 0.0:
            inward_invs = [inv for inv in self.gst_invoices if inv.type == "INWARD"]
            pending_tds = sum(inv.taxable_value * 0.10 for inv in inward_invs)
            
        pending_gst = float(stat_dues.get("gst_output_liability", 0.0))
        if pending_gst == 0.0:
            unpaid_gst = [inv for inv in self.gst_invoices if inv.type == "OUTWARD" and inv.gstr3b_offset_status == "UNOFF_SET_UNPAID"]
            pending_gst = sum(inv.gst_amount for inv in unpaid_gst)
            
        pending_pf = float(stat_dues.get("pf_esi_payable", 0.0))
        if pending_pf == 0.0:
            salary_debits = sum(t.amount for t in self.bank_transactions if t.type == "DEBIT" and "SALARY" in t.narration.upper())
            pending_pf = round(salary_debits * 0.12, 2)

        if is_cash_distressed:
            # 1. Section 201(1A) TDS Default Interest (1.5% per month, 3-month default period)
            if pending_tds > 0:
                tds_interest = round(pending_tds * 0.015 * 3.0, 2)
                violations.append(
                    StatutoryViolation(
                        statutory_section="Income Tax Act, 1961 - Section 201(1A)",
                        category="TDS_DEFAULT_INTEREST",
                        severity="CRITICAL",
                        rule_description=(
                            f"Dynamic Liquidity Trigger: Cash distress (OCF: ₹{operating_cash_flow:,.2f}, Runway: {true_runway} mo) "
                            f"escalates unpaid TDS of ₹{pending_tds:,.2f} into Section 201(1A) penal interest @ 1.5%/month (₹{tds_interest:,.2f})."
                        ),
                        amount_inr=pending_tds,
                        penalty_provision="Mandatory interest under Sec 201(1A) @ 1.5% per month + penalty under Sec 271C (100% of tax).",
                        penalty_estimate_inr=tds_interest,
                        details={"pending_tds_principal_inr": pending_tds, "interest_rate_monthly_pct": 1.5, "months_default": 3},
                    )
                )
                
            # 2. CGST Section 50 Interest (18% p.a.) & Section 47 Late Fees (₹50/day)
            if pending_gst > 0:
                gst_interest = round(pending_gst * 0.18 * (90.0 / 365.0), 2)
                gst_late_fees = round(min(10000.0, 50.0 * 90.0), 2)
                violations.append(
                    StatutoryViolation(
                        statutory_section="CGST Act, 2017 - Section 50 / Section 47",
                        category="GST_DEFAULT_ESCALATION",
                        severity="CRITICAL",
                        rule_description=(
                            f"Dynamic Liquidity Trigger: Unremitted GST liability of ₹{pending_gst:,.2f} incurred mandatory "
                            f"18% p.a. interest under Section 50 (₹{gst_interest:,.2f}) and Section 47 late fees (₹{gst_late_fees:,.2f})."
                        ),
                        amount_inr=pending_gst,
                        penalty_provision="Mandatory 18% p.a. interest under Section 50(1) + late filing fees under Section 47 + automated DRC-01B notice.",
                        penalty_estimate_inr=round(gst_interest + gst_late_fees, 2),
                        details={"pending_gst_liability_inr": pending_gst, "sec50_interest_inr": gst_interest, "sec47_late_fee_inr": gst_late_fees},
                    )
                )
                
            # 3. EPFO Section 14B Penal Damages & Section 7Q Interest (12% p.a.)
            if pending_pf > 0:
                epfo_damages = round(pending_pf * 0.15, 2)
                epfo_interest = round(pending_pf * 0.12 * (90.0 / 365.0), 2)
                violations.append(
                    StatutoryViolation(
                        statutory_section="EPF Act, 1952 - Section 14B / Section 7Q",
                        category="EPFO_DEFAULT_ESCALATION",
                        severity="CRITICAL",
                        rule_description=(
                            f"Dynamic Liquidity Trigger: Delay in remitting employee PF/ESI contributions of ₹{pending_pf:,.2f} "
                            f"incurs Section 14B penal damages (₹{epfo_damages:,.2f}) and Section 7Q interest (₹{epfo_interest:,.2f})."
                        ),
                        amount_inr=pending_pf,
                        penalty_provision="Section 14B damages up to 25% p.a. + Section 7Q interest @ 12% p.a. + Section 406/409 IPC prosecution.",
                        penalty_estimate_inr=round(epfo_damages + epfo_interest, 2),
                        details={"pending_pf_principal_inr": pending_pf, "sec14b_damages_inr": epfo_damages, "sec7q_interest_inr": epfo_interest},
                    )
                )

        total_statutory_liability = round(
            (pending_tds + tds_interest) +
            (pending_gst + gst_interest + gst_late_fees) +
            (pending_pf + epfo_damages + epfo_interest),
            2
        )
        total_statutory_liability_jpy = round(total_statutory_liability * INR_TO_JPY_RATE, 2)

        return StatutoryDefaultEscalation(
            is_cash_distressed=is_cash_distressed,
            operating_cash_flow_inr=operating_cash_flow,
            true_runway_months=true_runway,
            tds_sec201_interest_inr=tds_interest,
            gst_sec50_interest_inr=gst_interest,
            gst_sec47_late_fee_inr=gst_late_fees,
            epfo_sec14b_damages_inr=epfo_damages,
            epfo_sec7q_interest_inr=epfo_interest,
            total_contingent_statutory_liability_inr=total_statutory_liability,
            total_contingent_statutory_liability_jpy=total_statutory_liability_jpy,
            violations=violations,
        )

    # ---------------------------------------------------------------------------
    # 4. Automated Bad Debt Write-Off Provisioning & Claimed Valuation Haircut
    # ---------------------------------------------------------------------------
    def evaluate_bad_debt_provisioning(
        self,
        ca_books: Optional[Dict[str, Any]] = None,
        ccc_data: Optional[Dict[str, Any]] = None,
    ) -> BadDebtProvisioningResult:
        """Automated Bad Debt Write-Off Provisioning & Claimed Valuation Discounting.
        
        Condition: If Cash Conversion Cycle (CCC) > 60 days AND Debtor Days (DSO) > 75 days:
        Triggers Ind AS 109 / ICAI SA 240 Expected Credit Loss (ECL) 3-stage schedule:
        - Stage 1 (0-30 days): 2% ECL provision
        - Stage 2 (31-90 days): 20% ECL provision
        - Stage 3 (>90 days / over 180 days doubtful): 100% write-off mandated
        
        Discounts claimed valuation by haircut percentage proportional to uncollectible receivables.
        """
        books = ca_books or self.ca_books
        
        if ccc_data is None:
            ccc_data = self.analyze_cash_conversion_cycle()

        metrics = ccc_data.get("working_capital_metrics", {})
        ccc_days = float(metrics.get("cash_conversion_cycle_days", 0.0))
        dso_days = float(metrics.get("dso_days", 0.0))
        
        # Aging schedule
        ca_trial = books.get("trial_balance_inr", {})
        ca_receivables = float(ca_trial.get("trade_receivables_total", 0.0))
        ca_doubtful = float(ca_trial.get("receivables_aging", {}).get("over_180_days_doubtful", 0.0))
        ca_under_30 = float(ca_trial.get("receivables_aging", {}).get("under_30_days", 0.0))
        ca_31_90 = float(ca_trial.get("receivables_aging", {}).get("31_to_90_days", 0.0))
        
        ar_aging = ccc_data.get("ar_aging_schedule", {})
        b0_30 = ca_under_30 if ca_under_30 > 0 else float(ar_aging.get("bucket_0_30_days", {}).get("amount_inr", 0.0))
        b31_90 = ca_31_90 if ca_31_90 > 0 else (
            float(ar_aging.get("bucket_31_60_days", {}).get("amount_inr", 0.0)) +
            float(ar_aging.get("bucket_61_90_days", {}).get("amount_inr", 0.0))
        )
        b90_plus = ca_doubtful if ca_doubtful > 0 else float(ar_aging.get("bucket_90_plus_days", {}).get("amount_inr", 0.0))
        
        total_receivables = ca_receivables if ca_receivables > 0 else (b0_30 + b31_90 + b90_plus)
        if total_receivables == 0.0:
            total_receivables = float(metrics.get("outstanding_receivables_inr", 0.0))

        # Condition: CCC > 60 days AND DSO > 75 days
        is_write_off_triggered = (ccc_days > 60.0) and (dso_days > 75.0)

        # Ind AS 109 / ICAI 3-Stage ECL Provisioning
        stage1_provision = round(b0_30 * 0.02, 2)
        stage2_provision = round(b31_90 * 0.20, 2)
        if is_write_off_triggered:
            stage3_provision = round(b90_plus * 1.0, 2)  # 100% mandated write-off
        else:
            stage3_provision = round(b90_plus * 0.50, 2) # Standard conservative 50% provision
            
        total_bad_debt_provision = round(stage1_provision + stage2_provision + stage3_provision, 2)
        
        # Valuation Haircut
        claimed_arr = float(self.pitch_claims.claimed_arr_inr or 25500000.0)
        valuation_multiple = 5.0
        claimed_valuation = round(claimed_arr * valuation_multiple, 2)

        if is_write_off_triggered:
            haircut_pct = min(90.0, max(20.0, round((total_bad_debt_provision / max(1.0, claimed_arr)) * 100.0, 2)))
            discounted_val = round(max(0.0, claimed_valuation * (1.0 - (haircut_pct / 100.0))), 2)
            verdict = (
                f"MANDATORY_BAD_DEBT_WRITEOFF: CCC of {ccc_days:.1f} days (>60d) and DSO of {dso_days:.1f} days (>75d) "
                f"indicate critical collection failure. Mandated write-off of ₹{total_bad_debt_provision:,.2f} "
                f"imposes a {haircut_pct}% valuation discount (Valuation reduced from ₹{claimed_valuation/1e7:.2f} Cr to ₹{discounted_val/1e7:.2f} Cr)."
            )
        else:
            haircut_pct = 0.0
            discounted_val = claimed_valuation
            verdict = (
                f"HEALTHY_WORKING_CAPITAL: CCC ({ccc_days:.1f} days) and DSO ({dso_days:.1f} days) are within normal operational limits. "
                f"Standard baseline ECL provision of ₹{total_bad_debt_provision:,.2f} requires zero valuation haircut."
            )

        return BadDebtProvisioningResult(
            is_write_off_triggered=is_write_off_triggered,
            ccc_days=ccc_days,
            dso_days=dso_days,
            total_receivables_inr=round(total_receivables, 2),
            stage1_healthy_provision_inr=stage1_provision,
            stage2_stressed_provision_inr=stage2_provision,
            stage3_credit_impaired_writeoff_inr=stage3_provision,
            total_bad_debt_provision_inr=total_bad_debt_provision,
            claimed_arr_inr=claimed_arr,
            discounted_valuation_inr=discounted_val,
            valuation_haircut_pct=haircut_pct,
            mandated_write_off_verdict=verdict,
        )

    # ---------------------------------------------------------------------------
    # 5. Debt Covenants (DSCR) & Solvency (Current / Quick Ratio / IBC Trigger)
    # ---------------------------------------------------------------------------
    def evaluate_solvency_and_debt_covenants(
        self,
        ca_books: Optional[Dict[str, Any]] = None,
        pending_statutory_dues: float = 0.0,
        total_debt_service: Optional[float] = None,
    ) -> SolvencyAndDebtCovenantsResult:
        """Debt Covenants (DSCR) & Solvency (Current / Quick Ratio / IBC Trigger) Engine.
        
        Rules:
        1. Debt Service Coverage Ratio (DSCR = Operating Profit / Total Debt Service):
           If DSCR < 1.25, flag debt distress / covenant breach.
        2. Quick Ratio (Acid-Test = Quick Assets / Current Liabilities):
           If Quick Ratio < 0.8 while pending GST/TDS statutory dues exist,
           flag immediate insolvency risk under Insolvency & Bankruptcy Code (IBC 2016).
        """
        books = ca_books or self.ca_books
        violations: List[StatutoryViolation] = []
        
        # 1. Operating Profit (EBITDA / Operating Cash Flow)
        customer_collections = sum(
            t.amount for t in self.bank_transactions
            if t.type == "CREDIT" and "contra" not in t.narration.lower() and "equity" not in t.narration.lower()
        )
        operational_debits = sum(
            t.amount for t in self.bank_transactions
            if t.type == "DEBIT" and "contra" not in t.narration.lower()
        )
        operating_profit = max(0.0, customer_collections - operational_debits)
        if operating_profit == 0.0:
            outward_sales = sum(inv.total_amount for inv in self.gst_invoices if inv.type == "OUTWARD")
            operating_profit = max(0.0, outward_sales - operational_debits)

        # 2. Total Debt Service
        if total_debt_service is None:
            debt_txns = [
                t.amount for t in self.bank_transactions
                if t.type == "DEBIT" and any(k in t.narration.upper() for k in ["EMI", "LOAN", "INTEREST", "DEBT", "FINANCE COST", "BORROWING"])
            ]
            total_debt_service_val = sum(debt_txns)
        else:
            total_debt_service_val = float(total_debt_service)

        # Compute DSCR
        if total_debt_service_val > 0:
            dscr = round(operating_profit / total_debt_service_val, 2)
            if dscr < 1.0:
                dscr_status = "CRITICAL_DEFAULT"
                violations.append(
                    StatutoryViolation(
                        statutory_section="RBI Prudential Framework / Commercial Loan Covenants",
                        category="DSCR_COVENANT_BREACH",
                        severity="CRITICAL",
                        rule_description=(
                            f"Debt Service Coverage Ratio (DSCR) is {dscr:.2f} (Threshold: 1.25). Operating profit of "
                            f"₹{operating_profit:,.2f} is insufficient to service total debt commitments of ₹{total_debt_service_val:,.2f}."
                        ),
                        amount_inr=total_debt_service_val,
                        penalty_provision="Recall of credit facilities under Section 13(2) SARFAESI Act + penal interest levy.",
                        penalty_estimate_inr=round(total_debt_service_val * 0.05, 2),
                        details={"operating_profit_inr": operating_profit, "total_debt_service_inr": total_debt_service_val, "dscr": dscr},
                    )
                )
            elif dscr < 1.25:
                dscr_status = "DEBT_DISTRESS_BREACH"
                violations.append(
                    StatutoryViolation(
                        statutory_section="RBI Prudential Framework / Commercial Loan Covenants",
                        category="DSCR_COVENANT_BREACH",
                        severity="HIGH",
                        rule_description=(
                            f"Debt Service Coverage Ratio (DSCR) is {dscr:.2f}, below mandatory banking covenant threshold of 1.25. "
                            f"Tight cash flow leaves zero margin of safety for interest and principal repayment."
                        ),
                        amount_inr=total_debt_service_val,
                        penalty_provision="Mandated debt restructuring and restriction on promoter distributions.",
                        penalty_estimate_inr=round(total_debt_service_val * 0.02, 2),
                        details={"operating_profit_inr": operating_profit, "total_debt_service_inr": total_debt_service_val, "dscr": dscr},
                    )
                )
            else:
                dscr_status = "COVENANT_COMPLIANT"
        else:
            dscr = 999.0
            dscr_status = "UNLEVERAGED_ZERO_DEBT"

        # 3. Current & Quick Ratios
        ca_trial = books.get("trial_balance_inr", {})
        bank_balance = 0.0
        if self.bank_transactions:
            bank_balance = max(0.0, self.bank_transactions[-1].currentBalance)
            
        trade_rec = float(ca_trial.get("trade_receivables_total", 0.0))
        trade_pay = float(ca_trial.get("trade_payables", 0.0))
        
        stat_dues = float(pending_statutory_dues)
        if stat_dues == 0.0:
            stat_dict = ca_trial.get("statutory_dues_payable", {})
            stat_dues = float(stat_dict.get("gst_output_liability", 0.0)) + float(stat_dict.get("tds_payable", 0.0)) + float(stat_dict.get("pf_esi_payable", 0.0))
            if stat_dues == 0.0:
                unpaid_gst = sum(inv.gst_amount for inv in self.gst_invoices if inv.type == "OUTWARD" and inv.gstr3b_offset_status == "UNOFF_SET_UNPAID")
                stat_dues = round(unpaid_gst, 2)

        current_assets = round(bank_balance + trade_rec, 2)
        current_liabilities = round(trade_pay + stat_dues + total_debt_service_val, 2)
        
        current_ratio = round(current_assets / max(1.0, current_liabilities), 2)
        doubtful = float(ca_trial.get("receivables_aging", {}).get("over_180_days_doubtful", 0.0))
        clean_receivables = max(0.0, trade_rec - doubtful)
        quick_assets = round(bank_balance + clean_receivables, 2)
        quick_ratio = round(quick_assets / max(1.0, current_liabilities), 2)

        # Insolvency Trigger: Quick Ratio < 0.8 WHILE pending statutory dues exist
        is_ibc_triggered = (quick_ratio < 0.8) and (stat_dues > 0.0)

        if is_ibc_triggered:
            solvency_status = "CRITICAL_INSOLVENCY_RISK_IBC_DEFAULT"
            violations.append(
                StatutoryViolation(
                    statutory_section="Insolvency and Bankruptcy Code, 2016 - Section 7 / Section 9",
                    category="IBC_INSOLVENCY_TRIGGER",
                    severity="CRITICAL",
                    rule_description=(
                        f"Immediate Insolvency Trigger: Acid-Test Quick Ratio of {quick_ratio:.2f} (< 0.8) while carrying "
                        f"₹{stat_dues:,.2f} in pending statutory liabilities. Company is vulnerable to Section 9 operational creditor "
                        f"insolvency petition before the National Company Law Tribunal (NCLT)."
                    ),
                    amount_inr=stat_dues,
                    penalty_provision="Admission into Corporate Insolvency Resolution Process (CIRP), suspension of Board of Directors, and appointment of IRP.",
                    penalty_estimate_inr=stat_dues,
                    details={"quick_ratio": quick_ratio, "current_ratio": current_ratio, "statutory_dues_inr": stat_dues},
                )
            )
        elif current_ratio < 1.0:
            solvency_status = "WORKING_CAPITAL_DEFICIT"
        else:
            solvency_status = "SOLVENT_LIQUID"

        return SolvencyAndDebtCovenantsResult(
            operating_profit_inr=operating_profit,
            total_debt_service_inr=total_debt_service_val,
            dscr=dscr,
            dscr_status=dscr_status,
            current_assets_inr=current_assets,
            current_liabilities_inr=current_liabilities,
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            pending_statutory_dues_inr=stat_dues,
            is_ibc_insolvency_triggered=is_ibc_triggered,
            solvency_status=solvency_status,
            covenant_violations=violations,
        )

    # ---------------------------------------------------------------------------
    # 6. Circular Debt & Loan Round-Tripping Detection Engine
    # ---------------------------------------------------------------------------
    def detect_circular_debt_round_tripping(self) -> CircularDebtAnalysisResult:
        """Circular Debt & Loan Round-Tripping Detection Engine.
        
        Identifies multi-legged round-trip financing loops:
        Leg 1: Promoter loan / contra infusion credited to company.
        Leg 2: Inflow used to show simulated/fake sales customer deposits.
        Leg 3: Repaid or siphoned out as vendor expense or contra reversal.
        
        Statutory Violations:
        - Companies Act 2013 Section 185 / 188 (Prohibited Loans & Self-Dealing)
        - Income Tax Act 1961 Section 68 (Unexplained Cash Credits taxed @ 78% under Sec 115BBE)
        - Prevention of Money Laundering Act (PMLA 2002) Round-Tripping Provisions
        """
        events: List[CircularDebtEvent] = []
        violations: List[StatutoryViolation] = []
        
        sorted_txns = sorted(self.bank_transactions, key=lambda t: t.valueDate or t.transactionTimestamp)
        
        # 1. Identify Candidate Promoter / Director Loan Credits
        promoter_keywords = ["PROMOTER", "DIRECTOR", "HOLDINGS", "CONTRA_INFUSION", "UNSECURED LOAN", "SHAREHOLDER LOAN", "FOUNDER INFUSION", "LOAN INFLOW"]
        candidate_loans: List[RebitTransaction] = []
        for t in sorted_txns:
            if t.type in ["CREDIT", "DEPOSIT_EQUITY"] and t.amount >= 300000.0:
                narr_upper = t.narration.upper()
                cparty_upper = (getattr(t, "counterparty", "") or "").upper()
                is_promoter_match = any(kw in narr_upper or kw in cparty_upper for kw in promoter_keywords)
                for pan, d in self.director_pan_map.items():
                    if pan in narr_upper or pan in cparty_upper or d.director_name.upper() in narr_upper or d.director_name.upper() in cparty_upper:
                        is_promoter_match = True
                        break
                if is_promoter_match:
                    candidate_loans.append(t)

        event_counter = 0
        used_txns: Set[str] = set()

        for c1 in candidate_loans:
            if c1.txnId in used_txns:
                continue
            c1_dt_str = c1.valueDate or c1.transactionTimestamp[:10]
            try:
                c1_dt = datetime.strptime(c1_dt_str, "%Y-%m-%d")
            except Exception:
                continue

            # Leg 2: Search for Customer Inflow / Fake Sales Inflow within +/- 14 days
            matched_c2: Optional[RebitTransaction] = None
            for c2 in sorted_txns:
                if c2.type == "CREDIT" and c2.txnId != c1.txnId and c2.txnId not in used_txns:
                    c2_dt_str = c2.valueDate or c2.transactionTimestamp[:10]
                    try:
                        c2_dt = datetime.strptime(c2_dt_str, "%Y-%m-%d")
                        diff_days = abs((c2_dt - c1_dt).days)
                        if diff_days <= 14:
                            narr2 = c2.narration.upper()
                            cparty2 = (getattr(c2, "counterparty", "") or "").upper()
                            if any(k in narr2 or k in cparty2 for k in ["CUSTOMER", "DEP", "SALES", "RECEIPT", "RAZORPAY", "CLIENT"]):
                                matched_c2 = c2
                                break
                    except Exception:
                        pass

            # Leg 3: Search for Outflow (Vendor expense or Contra reversal) within 14 days of C1
            matched_d3: Optional[RebitTransaction] = None
            for d3 in sorted_txns:
                if d3.type == "DEBIT" and d3.txnId not in used_txns:
                    d3_dt_str = d3.valueDate or d3.transactionTimestamp[:10]
                    try:
                        d3_dt = datetime.strptime(d3_dt_str, "%Y-%m-%d")
                        diff_days = (d3_dt - c1_dt).days
                        if 0 <= diff_days <= 14:
                            if abs(d3.amount - c1.amount) <= (c1.amount * 0.25):
                                matched_d3 = d3
                                break
                    except Exception:
                        pass

            if matched_d3:
                event_counter += 1
                loop_duration = max(1, abs((datetime.strptime(matched_d3.valueDate or matched_d3.transactionTimestamp[:10], "%Y-%m-%d") - c1_dt).days))
                round_tripped_amt = min(c1.amount, matched_d3.amount)
                
                fake_sales_id = matched_c2.txnId if matched_c2 else f"SIM-SALE-{event_counter:03d}"
                fake_sales_amt = matched_c2.amount if matched_c2 else round(round_tripped_amt * 0.98, 2)
                fake_sales_dt = (matched_c2.valueDate or matched_c2.transactionTimestamp[:10]) if matched_c2 else c1_dt_str
                cust_counterparty = (getattr(matched_c2, "counterparty", "") or matched_c2.narration) if matched_c2 else "Simulated Trade Customer Ledger"

                event = CircularDebtEvent(
                    round_trip_id=f"CD-RT-{event_counter:03d}",
                    promoter_loan_txn_id=c1.txnId,
                    promoter_loan_amount_inr=c1.amount,
                    promoter_loan_date=c1_dt_str,
                    promoter_counterparty=getattr(c1, "counterparty", "") or c1.narration,
                    fake_sales_txn_id=fake_sales_id,
                    fake_sales_amount_inr=fake_sales_amt,
                    fake_sales_date=fake_sales_dt,
                    customer_counterparty=cust_counterparty,
                    siphoning_outflow_txn_id=matched_d3.txnId,
                    siphoning_outflow_amount_inr=matched_d3.amount,
                    siphoning_outflow_date=matched_d3.valueDate or matched_d3.transactionTimestamp[:10],
                    vendor_counterparty=getattr(matched_d3, "counterparty", "") or matched_d3.narration,
                    loop_duration_days=loop_duration,
                    total_round_tripped_inr=round_tripped_amt,
                    total_round_tripped_jpy=round(round_tripped_amt * INR_TO_JPY_RATE, 2),
                    statutory_citation="Companies Act 2013 Sec 185/188 & Income Tax Act Sec 68 / PMLA (Circular Loan Round-Tripping)",
                    severity="CRITICAL",
                )
                events.append(event)
                used_txns.add(c1.txnId)
                used_txns.add(matched_d3.txnId)
                if matched_c2:
                    used_txns.add(matched_c2.txnId)

                violations.append(
                    StatutoryViolation(
                        statutory_section="Companies Act, 2013 Sec 185 / 188 & Income Tax Sec 68",
                        category="CIRCULAR_LOAN_ROUND_TRIP",
                        severity="CRITICAL",
                        rule_description=(
                            f"Circular Loan Round-Tripping Detected: Promoter loan of ₹{c1.amount:,.2f} on {c1_dt_str} "
                            f"was routed through company accounts to simulate fake sales revenue of ₹{fake_sales_amt:,.2f} and "
                            f"repaid out to vendor/promoter entity '{getattr(matched_d3, 'counterparty', '') or matched_d3.narration}' "
                            f"(₹{matched_d3.amount:,.2f}) within {loop_duration} days."
                        ),
                        evidence_txn_id=f"{c1.txnId} -> {fake_sales_id} -> {matched_d3.txnId}",
                        date=c1_dt_str,
                        counterparty=getattr(c1, "counterparty", "") or c1.narration,
                        amount_inr=round_tripped_amt,
                        penalty_provision="Taxation under Section 115BBE at effective 78% rate + Director disqualification under Section 164 + PMLA investigation.",
                        penalty_estimate_inr=round(round_tripped_amt * 0.78, 2),
                        details={
                            "promoter_loan_txn": c1.txnId,
                            "fake_sales_txn": fake_sales_id,
                            "siphoning_outflow_txn": matched_d3.txnId,
                            "duration_days": loop_duration,
                        },
                    )
                )

        total_circular_inr = sum(e.total_round_tripped_inr for e in events)
        total_circular_jpy = sum(e.total_round_tripped_jpy for e in events)

        return CircularDebtAnalysisResult(
            has_circular_debt=len(events) > 0,
            total_circular_amount_inr=round(total_circular_inr, 2),
            total_circular_amount_jpy=round(total_circular_jpy, 2),
            events_detected=events,
            violations=violations,
        )
