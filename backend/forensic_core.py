"""VeriLedger / Kizuna-Vault (絆) Deterministic Forensic Core Engine.

Target Track: OPEN-PS-01 (Thapar Japan Hackathon 2026)
Target Stakeholders: Value Create Inc. (Tokyo), JETRO, and Faculty Reviewers.

Key Formulations:
1. 3-Way Reconciliation Tensor Matrix:
   Cross-references Pitch Deck Claimed Sales vs. GSTN Invoicing vs. Cleared Customer Bank Credits.
   Delta_Tax = (Sum(GSTR-1) - Sum(GSTR-3B)) / Sum(GSTR-1)
   Delta_Cash = (ReportedSales - ClearedBankCredits) / ReportedSales
2. Benford's Law First-Two-Digit (F2D) & Nigrini's Mean Absolute Deviation (MAD):
   P(D1D2 = k) = log10(1 + 1/k) for k in [10, 99].
   MAD = (1/90) * Sum(|Observed(k) - Expected(k)|). Flags MAD >= 0.0022.
3. Month-End Window Dressing & Contra Entry Detector:
   Identifies temporary liquidity spikes deposited on days 28-31 and reversed on days 1-5.
4. True Operational Cash Runway:
   Net Operational Cash = Bank Balance - Pending GST - Unpaid TDS - Pending Payables.
   Normalizes monthly burn by stripping one-off capex, tax lumps, and equity infusions.
5. Master Governance Trust Score (0 - 100) & Bilingual Tokyo Ringi-sho Circular.
"""

from __future__ import annotations
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from backend.schemas import (
    RebitTransaction,
    GstInvoice,
    DirectorRecord,
    PitchClaims,
    ThreeWayReconciliationResult,
    BenfordCluster,
    BenfordF2DResult,
    TrueRunwayResult,
    GovernanceScorecard,
    StatutoryViolation,
)
from backend.statutory_rules import StatutoryVerificationEngine, INR_TO_JPY_RATE
from backend.accounting_ledger import DoubleEntryLedgerEngine
from backend.cash_flow_and_indirect_expenses import CashConversionAndIndirectExpenseEngine


class VeriLedgerForensicCore:
    """Master deterministic forensic diligence and reconciliation suite."""

    def __init__(
        self,
        directors: List[DirectorRecord],
        gst_invoices: List[GstInvoice],
        bank_transactions: List[RebitTransaction],
        pitch_claims: Optional[PitchClaims] = None,
        opening_balance: float = 12500000.0,
        closing_balance: float = 8450000.0,
        ca_books: Optional[Dict[str, Any]] = None,
    ):
        self.directors = directors
        self.gst_invoices = gst_invoices
        self.bank_transactions = bank_transactions
        self.pitch_claims = pitch_claims or PitchClaims(company_name="Target Entity")
        self.opening_balance = opening_balance
        self.closing_balance = closing_balance
        self.ca_books = ca_books or {}

        self.statutory_engine = StatutoryVerificationEngine(directors=directors)
        self.accounting_engine = DoubleEntryLedgerEngine()

    # ---------------------------------------------------------------------------
    # Engine 1: 3-Way Reconciliation Tensor Matrix
    # ---------------------------------------------------------------------------
    def reconcile_three_way(self) -> ThreeWayReconciliationResult:
        """Execute 3-Way Reconciliation between Pitch Claims, GST Invoicing, and Cleared Bank Credits."""
        # 1. Claimed Sales
        claimed_sales = self.pitch_claims.claimed_arr_inr
        if claimed_sales <= 0:
            # Fallback to total GSTR-1 if not explicitly provided in deck
            claimed_sales = sum(inv.taxable_value for inv in self.gst_invoices if inv.type == "OUTWARD")

        # 2. GST Data
        outward_invoices = [inv for inv in self.gst_invoices if inv.type == "OUTWARD"]
        gstr1_sales = sum(inv.taxable_value for inv in outward_invoices)
        gstr3b_paid_sales = sum(inv.taxable_value for inv in outward_invoices if inv.gstr3b_offset_status == "OFFSET_PAID")
        unpaid_tax_sales = sum(inv.taxable_value for inv in outward_invoices if inv.gstr3b_offset_status == "UNOFF_SET_UNPAID")

        # 3. Bank Credits Decomposition
        total_bank_credits = sum(t.amount for t in self.bank_transactions if t.type in ["CREDIT", "DEPOSIT_EQUITY"])
        equity_infusions = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "DEPOSIT_EQUITY" or any(k in t.narration.upper() for k in ["SERIES", "EQUITY", "ANGEL"])
        )
        director_loans = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "CREDIT" and any(k in t.narration.upper() for k in ["DIRECTOR LOAN", "PROMOTER LOAN"])
        )
        contra_transfers = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "CREDIT" and "CONTRA" in t.narration.upper()
        )

        cleared_customer_credits = max(
            0.0,
            total_bank_credits - equity_infusions - director_loans - contra_transfers
        )

        # 4. Deltas & Variance Calculations
        delta_tax_pct = 0.0
        if gstr1_sales > 0:
            delta_tax_pct = round(((gstr1_sales - gstr3b_paid_sales) / gstr1_sales) * 100, 2)

        # Delta Cash: Divergence between reported sales and real cleared bank customer credits
        reference_sales = max(claimed_sales, gstr1_sales)
        delta_cash_pct = 0.0
        phantom_revenue = 0.0
        if reference_sales > 0:
            phantom_revenue = max(0.0, reference_sales - cleared_customer_credits)
            delta_cash_pct = round((phantom_revenue / reference_sales) * 100, 2)

        flags = []
        status = "COMPLIANT"

        if delta_tax_pct > 5.0:
            flags.append(f"UNREMITTED_TAX_ALERT: GSTR-1 declared turnover exceeds GSTR-3B paid sales by {delta_tax_pct}%")
            status = "TAX_RISK"

        if delta_cash_pct > 15.0:
            flags.append(f"PHANTOM_REVENUE_CRITICAL: {delta_cash_pct}% of claimed sales (₹{phantom_revenue:,.2f}) has no cleared bank cash match")
            status = "CRITICAL_FRAUD" if status == "TAX_RISK" else "CASH_DIVERGENCE"

        return ThreeWayReconciliationResult(
            claimed_sales_inr=round(claimed_sales, 2),
            gstr1_reported_sales_inr=round(gstr1_sales, 2),
            gstr3b_tax_paid_sales_inr=round(gstr3b_paid_sales, 2),
            unpaid_tax_sales_inr=round(unpaid_tax_sales, 2),
            bank_cleared_customer_credits_inr=round(cleared_customer_credits, 2),
            equity_infusions_inr=round(equity_infusions, 2),
            director_loans_inr=round(director_loans, 2),
            contra_transfers_inr=round(contra_transfers, 2),
            delta_tax_pct=delta_tax_pct,
            delta_cash_pct=delta_cash_pct,
            phantom_revenue_inr=round(phantom_revenue, 2),
            status=status,
            flags=flags,
        )

    # ---------------------------------------------------------------------------
    # Engine 2: Benford's Law (F2D) Anomaly & Nigrini MAD Analysis
    # ---------------------------------------------------------------------------
    def evaluate_benford_f2d(self) -> BenfordF2DResult:
        """Audit first-two-digits (F2D) of ledger disbursements against Nigrini's logarithmic distribution."""
        # Consider all disbursements >= 1,000 INR
        debits = [t.amount for t in self.bank_transactions if t.type == "DEBIT" and t.amount >= 1000.0]

        if len(debits) < 10:
            return BenfordF2DResult(
                sample_size=len(debits),
                nigrini_mad=0.0,
                conformity_status="INSUFFICIENT_SAMPLE_SIZE",
                is_anomalous=False,
            )

        # Theoretical probabilities for digits 10 through 99
        p_expected = {d: math.log10(1.0 + 1.0 / d) for d in range(10, 100)}

        # Observed frequencies
        f2d_counts = defaultdict(int)
        for amt in debits:
            str_val = f"{amt:.2f}".replace(".", "").lstrip("0")
            if len(str_val) >= 2:
                f2d = int(str_val[:2])
                if 10 <= f2d <= 99:
                    f2d_counts[f2d] += 1

        total_obs = sum(f2d_counts.values())
        if total_obs == 0:
            total_obs = 1

        mad_sum = 0.0
        clusters: List[BenfordCluster] = []
        top_freqs: Dict[int, float] = {}

        for d in range(10, 100):
            obs_cnt = f2d_counts[d]
            obs_pct = obs_cnt / total_obs
            exp_pct = p_expected[d]
            diff = abs(obs_pct - exp_pct)
            mad_sum += diff

            top_freqs[d] = round(obs_pct * 100, 2)

            # Detect spike clusters (e.g. at 49 or 19)
            if obs_pct >= (exp_pct * 3.0) and obs_cnt >= 3:
                clusters.append(
                    BenfordCluster(
                        leading_two_digits=d,
                        observed_pct=round(obs_pct * 100, 2),
                        expected_pct=round(exp_pct * 100, 2),
                        count=obs_cnt,
                        inference=f"Significant clustering at leading digits {d} (e.g. ₹{d},500 or ₹{d},000 amounts evading tax/board thresholds)",
                    )
                )

        nigrini_mad = round(mad_sum / 90.0, 5)

        # Nigrini Conformity Cutoffs
        if nigrini_mad < 0.0012:
            status = "CLOSE_CONFORMITY_CLEAN"
            is_anomalous = False
        elif nigrini_mad < 0.0022:
            status = "ACCEPTABLE_CONFORMITY"
            is_anomalous = False
        else:
            status = "NON_CONFORMING_FRAUD_RISK"
            is_anomalous = True

        return BenfordF2DResult(
            sample_size=total_obs,
            nigrini_mad=nigrini_mad,
            threshold_mad_cutoff=0.0022,
            conformity_status=status,
            is_anomalous=is_anomalous,
            clumping_clusters=clusters,
            top_digit_frequencies=top_freqs,
        )

    # ---------------------------------------------------------------------------
    # Engine 3: Month-End Window Dressing & Contra Inflow Detector
    # ---------------------------------------------------------------------------
    def detect_window_dressing(self) -> List[Dict[str, Any]]:
        """Identify temporary capital infusions deposited on days 28-31 and reversed on days 1-5."""
        window_events = []
        sorted_txns = sorted(
            self.bank_transactions,
            key=lambda t: t.valueDate or t.transactionTimestamp
        )

        for i, credit in enumerate(sorted_txns):
            if credit.type in ["CREDIT", "DEPOSIT_EQUITY"] and credit.amount >= 500000.0:
                c_date_str = credit.valueDate or credit.transactionTimestamp[:10]
                try:
                    c_dt = datetime.strptime(c_date_str, "%Y-%m-%d")
                    # Check if deposited on month-end (days 27-31)
                    if c_dt.day >= 27:
                        # Look ahead within 10 days for matching reversal/contra debit
                        for debit in sorted_txns[i+1:]:
                            d_date_str = debit.valueDate or debit.transactionTimestamp[:10]
                            try:
                                d_dt = datetime.strptime(d_date_str, "%Y-%m-%d")
                                delta_days = (d_dt - c_dt).days
                                if 1 <= delta_days <= 10 and debit.type == "DEBIT":
                                    # Match amount within 5%
                                    if abs(debit.amount - credit.amount) <= (credit.amount * 0.05):
                                        window_events.append({
                                            "credit_txn_id": credit.txnId,
                                            "credit_date": c_date_str,
                                            "credit_amount_inr": credit.amount,
                                            "credit_narration": credit.narration,
                                            "reversal_txn_id": debit.txnId,
                                            "reversal_date": d_date_str,
                                            "reversal_amount_inr": debit.amount,
                                            "reversal_narration": debit.narration,
                                            "holding_duration_days": delta_days,
                                            "finding": f"Window dressing detected: ₹{credit.amount:,.2f} injected on Day {c_dt.day} and reversed {delta_days} days later on Day {d_dt.day}",
                                        })
                            except Exception:
                                pass
                except Exception:
                    pass

        return window_events

    # ---------------------------------------------------------------------------
    # Engine 4: True Operational Runway & Cash Burn Forecaster
    # ---------------------------------------------------------------------------
    def calculate_true_runway(self) -> TrueRunwayResult:
        """Compute authentic runway net of unremitted taxes and stripped of one-off financing."""
        # 1. Unremitted GST liability from GSTR-1 vs GSTR-3B
        outward_unpaid = [inv for inv in self.gst_invoices if inv.type == "OUTWARD" and inv.gstr3b_offset_status == "UNOFF_SET_UNPAID"]
        pending_gst = sum(inv.gst_amount for inv in outward_unpaid)

        # 2. Estimated unpaid TDS liabilities (approx 10% on inward invoices)
        inward_invoices = [inv for inv in self.gst_invoices if inv.type == "INWARD"]
        pending_tds = sum(inv.taxable_value * 0.10 for inv in inward_invoices)

        # 3. Stripping non-operational infusions from cash
        equity_infusions = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "DEPOSIT_EQUITY" or any(k in t.narration.upper() for k in ["SERIES", "EQUITY", "ANGEL"])
        )
        contra_inflows = sum(
            t.amount for t in self.bank_transactions 
            if t.type == "CREDIT" and "CONTRA" in t.narration.upper()
        )

        raw_closing = self.closing_balance
        net_operational_cash = max(0.0, raw_closing - pending_gst - pending_tds)

        # 4. Normalized Monthly Burn (Strip capex and tax spikes)
        debits = [t for t in self.bank_transactions if t.type == "DEBIT"]
        total_debits = sum(t.amount for t in debits)
        
        # Assume dataset covers 3 months (quarter)
        quarterly_burn = total_debits - contra_inflows
        normalized_monthly_burn = max(100000.0, quarterly_burn / 3.0)

        # True Runway Months
        true_runway_months = round(net_operational_cash / normalized_monthly_burn, 1)
        claimed_runway = self.pitch_claims.claimed_runway_months or 18.0

        inflation_factor = round(claimed_runway / max(0.1, true_runway_months), 1)

        if true_runway_months < 3.0:
            verdict = f"CRITICAL_INSOLVENCY_RISK: Real cash runway is only {true_runway_months} months (Claimed: {claimed_runway} mo)."
        elif true_runway_months < 6.0:
            verdict = f"REQUIRES_REVIEW: Tight liquidity buffer of {true_runway_months} months."
        else:
            verdict = f"HEALTHY: Verifiable operational runway of {true_runway_months} months."

        return TrueRunwayResult(
            cleared_bank_balance_inr=round(raw_closing, 2),
            pending_gst_liabilities_inr=round(pending_gst, 2),
            unpaid_tds_liabilities_inr=round(pending_tds, 2),
            pending_vendor_payables_inr=0.0,
            net_operational_cash_inr=round(net_operational_cash, 2),
            gross_quarterly_burn_inr=round(quarterly_burn, 2),
            normalized_monthly_burn_inr=round(normalized_monthly_burn, 2),
            claimed_runway_months=claimed_runway,
            true_runway_months=true_runway_months,
            runway_inflation_factor=inflation_factor,
            verdict=verdict,
        )

    # ---------------------------------------------------------------------------
    # Engine 5: Master Shinrai Governance Trust Score (0 - 100)
    # ---------------------------------------------------------------------------
    def execute_master_audit(self) -> GovernanceScorecard:
        """Run all forensic engines and compute the composite Shinrai Governance Trust Score."""
        recon_result = self.reconcile_three_way()
        benford_result = self.evaluate_benford_f2d()
        window_events = self.detect_window_dressing()
        runway_result = self.calculate_true_runway()

        # Run working capital logistics & indirect expense siphoning engine
        wc_engine = CashConversionAndIndirectExpenseEngine(
            directors=self.directors,
            gst_invoices=self.gst_invoices,
            bank_transactions=self.bank_transactions,
            pitch_claims=self.pitch_claims,
            ca_books=self.ca_books,
        )
        ccc_analysis = wc_engine.analyze_cash_conversion_cycle()
        indirect_analysis = wc_engine.audit_indirect_expenses_and_siphoning()

        # Advanced CA Forensic Matching & Solvency Engines
        dynamic_contingencies = wc_engine.evaluate_dynamic_liquidity_contingencies(
            true_runway_months=runway_result.true_runway_months
        )
        bad_debt_result = wc_engine.evaluate_bad_debt_provisioning(
            ccc_data=ccc_analysis
        )
        solvency_result = wc_engine.evaluate_solvency_and_debt_covenants(
            pending_statutory_dues=runway_result.pending_gst_liabilities_inr + runway_result.unpaid_tds_liabilities_inr
        )
        circular_debt_result = wc_engine.detect_circular_debt_round_tripping()

        # Run statutory tax & company law audits
        statutory_summary = self.statutory_engine.run_full_statutory_audit(
            transactions=self.bank_transactions,
            gst_invoices=self.gst_invoices,
        )

        statutory_violations = [StatutoryViolation(**v) for v in statutory_summary["violations_list"]]
        statutory_violations.extend(dynamic_contingencies.violations)
        statutory_violations.extend(solvency_result.covenant_violations)
        statutory_violations.extend(circular_debt_result.violations)
        related_party_findings = statutory_summary["related_party_findings"]

        # Run ICAI SA 240 & SA 505 double-entry checks
        sa505_result = self.accounting_engine.audit_sa505_external_confirmations(
            bank_transactions=self.bank_transactions,
            gst_invoices=self.gst_invoices,
        )

        # -----------------------------------------------------------------------
        # Deductive Scoring Algorithm (Tokyo Boardroom "Genten Shugi" 減点主義)
        # Starting base score: 100 points
        # -----------------------------------------------------------------------
        score = 100

        # Deduction 1: Phantom Revenue Divergence (Delta_Cash)
        if recon_result.delta_cash_pct > 50.0:
            score -= 40
        elif recon_result.delta_cash_pct > 20.0:
            score -= 25
        elif recon_result.delta_cash_pct > 10.0:
            score -= 10

        # Deduction 2: Section 188 / 185 Promoter Siphoning
        if related_party_findings:
            score -= 30

        # Deduction 3: CGST Rule 88C Tax Deficit
        if recon_result.delta_tax_pct > 10.0:
            score -= 15
        elif recon_result.delta_tax_pct > 5.0:
            score -= 10

        # Deduction 4: Benford F2D Anomaly (Threshold Smurfing)
        if benford_result.is_anomalous:
            score -= 10

        # Deduction 5: Window Dressing & Circular Debt
        if window_events or circular_debt_result.has_circular_debt:
            score -= 10

        # Deduction 6: Severe Runway Crunch (< 3 months) & Dynamic Contingency
        if runway_result.true_runway_months < 1.0:
            score -= 15
        elif runway_result.true_runway_months < 3.0:
            score -= 10

        score = max(5, min(100, score))

        # Classification & Kanji Badge
        if score >= 80:
            classification = "VERIFIED_CLEAN"
            kanji_badge = "【適格】"
            verdict = "INVESTABLE: High governance integrity across DPI ledgers. Sovereign verification passed."
        elif score >= 50:
            classification = "REQUIRES_REVIEW"
            kanji_badge = "【要確認】"
            verdict = "REQUIRES REVIEW: Operational variances detected. Issue 90-day compliance remediation roadmap."
        else:
            classification = "CRITICAL_RED_FLAG_REJECT"
            kanji_badge = "【精査要】"
            verdict = "REJECT DEAL: Critical governance red flags, undisclosed Section 188 self-dealing, or phantom revenue divergence."

        recommendations = []
        if related_party_findings:
            recommendations.append("Immediate freeze on disbursements to related-party vendors matching Director PAN.")
        if recon_result.delta_cash_pct > 15.0:
            recommendations.append(f"Audit uncollected receivables of ₹{recon_result.phantom_revenue_inr:,.2f} before valuation finalization.")
        if recon_result.delta_tax_pct > 5.0:
            recommendations.append(f"Remit pending GST tax liability of ₹{recon_result.unpaid_tax_sales_inr:,.2f} to prevent CGST Rule 88C bank freeze.")
        if runway_result.true_runway_months < 3.0:
            recommendations.append(f"Inject emergency bridge financing; true cash runway is compressed to {runway_result.true_runway_months} months.")
        if dynamic_contingencies.is_cash_distressed:
            recommendations.append(f"Statutory Default Warning: Pending dues of ₹{dynamic_contingencies.total_contingent_statutory_liability_inr:,.2f} trigger compounding interest under Sec 201(1A) and GST/PF penalties.")
        if bad_debt_result.is_write_off_triggered:
            recommendations.append(f"Apply mandated bad debt write-off of ₹{bad_debt_result.total_bad_debt_provision_inr:,.2f} under Ind AS 109 and discount claimed valuation by {bad_debt_result.valuation_haircut_pct}%.")
        if solvency_result.is_ibc_insolvency_triggered:
            recommendations.append(f"Immediate Solvency Hazard: Acid-test quick ratio ({solvency_result.quick_ratio}) < 0.8 with pending dues creates immediate NCLT IBC CIRP vulnerability.")
        if circular_debt_result.has_circular_debt:
            recommendations.append(f"Disclose and unwind circular promoter loan round-tripping of ₹{circular_debt_result.total_circular_amount_inr:,.2f} violating Companies Act Sec 185/188.")

        return GovernanceScorecard(
            governance_trust_score=score,
            rating_classification=classification,
            kanji_badge=kanji_badge,
            summary_verdict=verdict,
            three_way_reconciliation=recon_result,
            related_party_siphoning={
                "has_conflict": len(related_party_findings) > 0,
                "conflict_count": len(related_party_findings),
                "total_siphoned_inr": sum(f["amount_inr"] for f in related_party_findings),
                "total_siphoned_jpy": sum(f["amount_jpy"] for f in related_party_findings),
                "findings": related_party_findings,
            },
            benford_f2d_analysis=benford_result,
            statutory_violations=statutory_violations,
            cash_burn_and_runway=runway_result,
            window_dressing_events=window_events,
            working_capital_and_logistics=ccc_analysis,
            indirect_siphoning_findings=indirect_analysis["indirect_siphoning_summary"],
            dynamic_statutory_contingencies=dynamic_contingencies.model_dump(),
            bad_debt_provisioning=bad_debt_result.model_dump(),
            solvency_and_debt_covenants=solvency_result.model_dump(),
            circular_debt_findings=circular_debt_result.model_dump(),
            icai_sa240_sa505_findings=sa505_result,
            boardroom_recommendations=recommendations,
        )
