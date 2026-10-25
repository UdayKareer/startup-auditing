"""
Comprehensive Multi-Source Dataset Generator for VeriLedger / Kizuna-Vault
Generates high-volume, realistic transaction datasets across 8 startup presets:
1. Sovereign Banking Ledgers: RBI Account Aggregator (ReBIT DEPOSIT v2.0 JSON)
2. Government Tax Portals: GSTN (GSTR-1 outward sales vs GSTR-3B tax remitted CSVs)
3. Corporate Registries: MCA-21 Director & DIN registries (CSV)
4. Accounting Books: Chartered Accountant certified Trial Balances & General Ledgers (JSON)
5. Pitch Deck Claims: Pre-cached Claims JSON

Each transaction contains full forensic narrative context:
- txnId, type, mode, amount (INR), amount_jpy (JPY @ 1.80)
- currentBalance, transactionTimestamp (ISO 8601 with realistic hours/minutes/seconds)
- valueDate (YYYY-MM-DD), narration, reference
- counterparty, counterpartyGstin, accountHead
- whatHappened: itemized forensic description of transaction flow
- whyReason: forensic & statutory justification (why verified clean or why flagged)
- forensicStatus: VERIFIED_CLEAN vs FLAGGED_ANOMALY
- statutoryCitation: legal citations (Companies Act Sec 188/185, Income Tax Act Sec 194C/J, 269ST, 40A(3), CGST Rule 88C, ICAI SA 240/505)

Presets:
1. clean_startup: Apex AI Labs Private Limited (Score 100/100, [適格])
2. fraud_startup: PhantomTech Solutions Private Limited (Sec 188 Siphoning & Benford TDS Smurfing, Score 10/100, [精査要])
3. logipulse_startup: LogiPulse Express Private Limited (Logistics, stretched receivables >180d, Rule 88C, Score 35/100, [精査要])
4. mirai_startup: Mirai Mobility Robotics Private Limited (Indo-Japan bilateral CVC, Score 100/100, [適格])
5. edutrek_startup: Edutrek Learning Technologies Private Limited (Byju's Archetype, Score 22/100, [精査要])
6. kwikpay_startup: KwikPay Digital Networks Private Limited (BharatPe Archetype, Score 15/100, [精査要])
7. zenith_startup: Zenith BioHealth Solutions Private Limited (Series A MedTech, 76d DSO, Score 78/100, [要確認])
8. autocare_startup: AutoCare Network India Private Limited (GoMechanic Archetype, Sec 269ST Cash Siphoning, Score 10/100, [精査要])
"""

import os
import json
import math
import random
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

os.makedirs("data", exist_ok=True)
random.seed(42)
np.random.seed(42)

FX_INR_TO_JPY = 1.80

def generate_sha256(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def make_timestamp(cur_date: datetime, min_hour: int = 9, max_hour: int = 18) -> str:
    h = random.randint(min_hour, max_hour)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{cur_date.strftime('%Y-%m-%d')}T{h:02d}:{m:02d}:{s:02d}+05:30"

# Benford F2D probabilities
benford_probs = [math.log10(1.0 + 1.0 / k) for k in range(10, 100)]
benford_probs = np.array(benford_probs) / sum(benford_probs)

def sample_benford_amount(magnitude_choices=[1, 2, 3]):
    f2d = np.random.choice(range(10, 100), p=benford_probs)
    mag = np.random.choice(magnitude_choices)
    cents = np.random.uniform(0.01, 0.99)
    return round(float((f2d + cents) * (10 ** mag)), 2)

def build_rebit_payload(cin, company_name, masked_acc, fip_id, opening_balance, transactions):
    return {
        "account": {
            "type": "DEPOSIT",
            "maskedAccNumber": masked_acc,
            "version": "2.0.0",
            "fipId": fip_id,
            "profile": {
                "holders": {
                    "type": "SINGLE",
                    "holder": [{
                        "name": company_name,
                        "cin": cin,
                        "email": f"finance@{company_name.lower().split()[0]}.io",
                        "mobile": "+919876543210",
                        "pan": cin[1:11] if len(cin) > 11 else "AABCA1234F"
                    }]
                }
            },
            "summary": {
                "currentBalance": round(transactions[-1]["currentBalance"], 2) if transactions else opening_balance,
                "currency": "INR",
                "status": "ACTIVE",
                "openingDate": "2026-07-01",
                "digitalSignature": generate_sha256(f"{fip_id}:{masked_acc}:X509_CERT")
            },
            "transactions": {
                "startDate": "2026-07-01",
                "endDate": "2026-12-31",
                "transaction": transactions
            }
        }
    }

# -------------------------------------------------------------
# 1. Master MCA-21 Corporate Registry
# -------------------------------------------------------------
mca_directors_data = [
    # Apex AI Labs
    {
        "cin": "U72900KA2023PTC178921",
        "company_name": "Apex AI Labs Private Limited",
        "din": "08921045",
        "director_name": "Rajesh Sharma",
        "pan": "ABCPS1234F",
        "appointment_date": "2023-04-12",
        "designation": "Managing Director",
        "registered_address": "Indiranagar 100ft Road, Bangalore, Karnataka 560038"
    },
    {
        "cin": "U72900KA2023PTC178921",
        "company_name": "Apex AI Labs Private Limited",
        "din": "09144820",
        "director_name": "Ananya Sen",
        "pan": "AEFPS5678K",
        "appointment_date": "2023-04-12",
        "designation": "Director & CTO",
        "registered_address": "Koramangala 4th Block, Bangalore, Karnataka 560034"
    },
    # PhantomTech Solutions
    {
        "cin": "U74999DL2024PTC389102",
        "company_name": "PhantomTech Solutions Private Limited",
        "din": "07812934",
        "director_name": "Vikram Malhotra",
        "pan": "ABCPS1234F",  # Siphoning conflict PAN
        "appointment_date": "2024-01-15",
        "designation": "Chief Executive Officer",
        "registered_address": "Connaught Place, New Delhi 110001"
    },
    {
        "cin": "U74999DL2024PTC389102",
        "company_name": "PhantomTech Solutions Private Limited",
        "din": "08451209",
        "director_name": "Sangeeta Verma",
        "pan": "ASRPV5432Q",
        "appointment_date": "2024-01-15",
        "designation": "Executive Director & CFO",
        "registered_address": "Saket District Centre, New Delhi 110017"
    },
    # LogiPulse Express
    {
        "cin": "U63090MH2022PTC345678",
        "company_name": "LogiPulse Express Private Limited",
        "din": "07123987",
        "director_name": "Rohan Kulkarni",
        "pan": "ARKPK1234M",
        "appointment_date": "2022-08-20",
        "designation": "Managing Director",
        "registered_address": "Bandra Kurla Complex, Mumbai, Maharashtra 400051"
    },
    {
        "cin": "U63090MH2022PTC345678",
        "company_name": "LogiPulse Express Private Limited",
        "din": "07889911",
        "director_name": "Pooja Mehta",
        "pan": "APMPM9988D",
        "appointment_date": "2022-08-20",
        "designation": "Director & COO",
        "registered_address": "Andheri East, Mumbai, Maharashtra 400069"
    },
    # Mirai Mobility Robotics
    {
        "cin": "U29100TN2023PTC456789",
        "company_name": "Mirai Mobility Robotics Private Limited",
        "din": "06981245",
        "director_name": "Karthik Subramanian",
        "pan": "AKSPK9012B",
        "appointment_date": "2023-09-10",
        "designation": "Managing Director",
        "registered_address": "Tidel Park, Tharamani, Chennai, Tamil Nadu 600113"
    },
    {
        "cin": "U29100TN2023PTC456789",
        "company_name": "Mirai Mobility Robotics Private Limited",
        "din": "09871234",
        "director_name": "Kenji Takahashi",
        "pan": "AAKPT7890N",
        "appointment_date": "2023-11-01",
        "designation": "Non-Executive Director (Value Create CVC)",
        "registered_address": "Marunouchi, Chiyoda-ku, Tokyo, Japan / Chennai Desk"
    },
    # Edutrek Learning Technologies (Byju's archetype)
    {
        "cin": "U80903KA2021PTC156789",
        "company_name": "Edutrek Learning Technologies Private Limited",
        "din": "07564120",
        "director_name": "Arjun Ravindran",
        "pan": "ABRPR7891K",
        "appointment_date": "2021-06-15",
        "designation": "Managing Director & CEO",
        "registered_address": "Prestige Tech Park, Outer Ring Road, Bangalore, Karnataka 560103"
    },
    {
        "cin": "U80903KA2021PTC156789",
        "company_name": "Edutrek Learning Technologies Private Limited",
        "din": "08123490",
        "director_name": "Divya Gokul",
        "pan": "ADGPD4567M",
        "appointment_date": "2021-06-15",
        "designation": "Director & COO",
        "registered_address": "Indiranagar, Bangalore, Karnataka 560038"
    },
    # KwikPay Digital Networks (BharatPe archetype)
    {
        "cin": "U72900DL2022PTC384512",
        "company_name": "KwikPay Digital Networks Private Limited",
        "din": "07231456",
        "director_name": "Ashmit Grover",
        "pan": "AABPG9012L",
        "appointment_date": "2022-03-10",
        "designation": "Managing Director",
        "registered_address": "Panchsheel Park, New Delhi 110017"
    },
    {
        "cin": "U72900DL2022PTC384512",
        "company_name": "KwikPay Digital Networks Private Limited",
        "din": "08456123",
        "director_name": "Madhuri Mehra",
        "pan": "AMMPM3456F",  # Siphoning conflict PAN!
        "appointment_date": "2022-03-10",
        "designation": "Director & Head of Procurement",
        "registered_address": "Panchsheel Park, New Delhi 110017"
    },
    # Zenith BioHealth Solutions (MedTech Series A)
    {
        "cin": "U85110MH2023PTC398765",
        "company_name": "Zenith BioHealth Solutions Private Limited",
        "din": "08112233",
        "director_name": "Dr. Neha Deshmukh",
        "pan": "ANDPD9988C",
        "appointment_date": "2023-02-14",
        "designation": "Managing Director",
        "registered_address": "Piramal Agastya Corporate Park, Kurla West, Mumbai, Maharashtra 400070"
    },
    # AutoCare Network India (GoMechanic archetype)
    {
        "cin": "U50400DL2021PTC378901",
        "company_name": "AutoCare Network India Private Limited",
        "din": "07891234",
        "director_name": "Amitesh Singhal",
        "pan": "AABCA4567M",
        "appointment_date": "2021-08-18",
        "designation": "Managing Director",
        "registered_address": "Vasant Vihar, New Delhi 110057"
    },
    {
        "cin": "U50400DL2021PTC378901",
        "company_name": "AutoCare Network India Private Limited",
        "din": "08234567",
        "director_name": "Rishabh Oberoi",
        "pan": "AROPO8901L",  # Siphoning conflict PAN!
        "appointment_date": "2021-08-18",
        "designation": "Executive Director & CFO",
        "registered_address": "Golf Links, New Delhi 110003"
    }
]
pd.DataFrame(mca_directors_data).to_csv("data/mca_directors.csv", index=False)

# -------------------------------------------------------------
# 2. Pre-cached Pitch Deck Claims
# -------------------------------------------------------------
mock_claims = {
    "clean_startup": {
        "company_name": "Apex AI Labs Private Limited",
        "cin": "U72900KA2023PTC178921",
        "claimed_arr_inr": 25500000.0,
        "claimed_monthly_burn_inr": 650000.0,
        "claimed_runway_months": 18.0,
        "claimed_team_size": 32,
        "sector": "Enterprise Infrastructure & AI"
    },
    "fraud_startup": {
        "company_name": "PhantomTech Solutions Private Limited",
        "cin": "U74999DL2024PTC389102",
        "claimed_arr_inr": 25500000.0,
        "claimed_monthly_burn_inr": 780000.0,
        "claimed_runway_months": 18.0,
        "claimed_team_size": 48,
        "sector": "Cloud SaaS & Supply Chain"
    },
    "logipulse_startup": {
        "company_name": "LogiPulse Express Private Limited",
        "cin": "U63090MH2022PTC345678",
        "claimed_arr_inr": 18500000.0,
        "claimed_monthly_burn_inr": 920000.0,
        "claimed_runway_months": 14.0,
        "claimed_team_size": 55,
        "sector": "D2C Fulfillment & Last-Mile Logistics"
    },
    "mirai_startup": {
        "company_name": "Mirai Mobility Robotics Private Limited",
        "cin": "U29100TN2023PTC456789",
        "claimed_arr_inr": 43896936.43,
        "claimed_monthly_burn_inr": 850000.0,
        "claimed_runway_months": 24.0,
        "claimed_team_size": 28,
        "sector": "Autonomous Industrial Robotics & CleanTech"
    },
    "edutrek_startup": {
        "company_name": "Edutrek Learning Technologies Private Limited",
        "cin": "U80903KA2021PTC156789",
        "claimed_arr_inr": 450000000.0,
        "claimed_monthly_burn_inr": 18500000.0,
        "claimed_runway_months": 20.0,
        "claimed_team_size": 350,
        "sector": "EdTech & Smart Tablet Learning"
    },
    "kwikpay_startup": {
        "company_name": "KwikPay Digital Networks Private Limited",
        "cin": "U72900DL2022PTC384512",
        "claimed_arr_inr": 360000000.0,
        "claimed_monthly_burn_inr": 12000000.0,
        "claimed_runway_months": 18.0,
        "claimed_team_size": 180,
        "sector": "Fintech & Merchant QR Infrastructure"
    },
    "zenith_startup": {
        "company_name": "Zenith BioHealth Solutions Private Limited",
        "cin": "U85110MH2023PTC398765",
        "claimed_arr_inr": 220000000.0,
        "claimed_monthly_burn_inr": 11000000.0,
        "claimed_runway_months": 16.0,
        "claimed_team_size": 42,
        "sector": "AI Diagnostics & Hospital Tele-ICU SaaS"
    },
    "autocare_startup": {
        "company_name": "AutoCare Network India Private Limited",
        "cin": "U50400DL2021PTC378901",
        "claimed_arr_inr": 1800000000.0,
        "claimed_monthly_burn_inr": 95000000.0,
        "claimed_runway_months": 16.0,
        "claimed_team_size": 420,
        "sector": "AutoTech & Multi-Brand Garage Network"
    }
}
with open("data/mock_claims.json", "w", encoding="utf-8") as f:
    json.dump(mock_claims, f, indent=2)

# Common Date Horizon
start_date = datetime(2026, 7, 1)

# -------------------------------------------------------------
# 3. Clean Startup: Apex AI Labs Private Limited
# -------------------------------------------------------------
clean_ca_books = {
    "company_cin": "U72900KA2023PTC178921",
    "accounting_software": "Zoho Books Enterprise v2026.2",
    "certified_by": "R. K. Swamy & Co. Chartered Accountants (FRN 008921S)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 25300000.0,
        "trade_receivables_total": 420000.0,
        "receivables_aging": {
            "under_30_days": 350000.0,
            "31_to_90_days": 70000.0,
            "over_180_days_doubtful": 0.0
        },
        "trade_payables": 380000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 45000.0,
            "tds_payable": 28000.0,
            "pf_esi_payable": 18000.0
        },
        "general_ledger_cash_balance": 12850000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "UNQUALIFIED_CLEAN"
}
with open("data/clean_startup_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(clean_ca_books, f, indent=2)

clean_txns = []
current_bal = 12500000.0
total_target_revenue = 25150000.0
generated_rev = 0.0

enterprise_clients = [
    ("Tata Consultancy Services Ltd", "27AAACT1234C1Z1"),
    ("Infosys Technologies Limited", "29AAACI5678B1Z4"),
    ("Wipro Enterprises Private Ltd", "29AAACW9012D1Z8"),
    ("HCL Technologies Limited", "09AAACH3456F1Z2")
]
vendors_clean = [
    ("Amazon Web Services India", "29AABCA1234F1Z1", "AWS Cloud Infrastructure", "Account 5020: Cloud Server Infrastructure"),
    ("Google Cloud India Pvt Ltd", "07AABCG5678K1Z3", "GCP AI Model API Compute", "Account 5020: Cloud Server Infrastructure"),
    ("WeWork India Management", "29AAACW1122M1Z5", "Office Space Lease", "Account 5010: Corporate Office Lease & Overhead"),
    ("Razorpay Software Pvt Ltd", "29AABCR5566T1Z9", "Payment Gateway Platform", "Account 5040: Payment Gateway & Merchant Platform")
]

gst_clean_invoices = []
inv_idx = 1

clean_collection_days = [start_date + timedelta(days=d) for d in range(184) if (start_date + timedelta(days=d)).weekday() in [1, 3]]
n_clean_coll = len(clean_collection_days)
clean_weights = np.random.uniform(0.88, 1.12, size=n_clean_coll)
clean_weights = clean_weights / clean_weights.sum()
clean_amounts = np.round(clean_weights * total_target_revenue, 2)
clean_amounts[-1] = round(total_target_revenue - clean_amounts[:-1].sum(), 2)
clean_day_map = {clean_collection_days[i].strftime("%Y-%m-%d"): clean_amounts[i] for i in range(n_clean_coll)}

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Enterprise Inflows (Tuesday & Thursday)
    if date_str in clean_day_map:
        client, gstin = random.choice(enterprise_clients)
        amt = clean_day_map[date_str]
        current_bal += amt
        generated_rev += amt
        t_stamp = make_timestamp(cur_date, min_hour=10, max_hour=13)
        inv_no = f"INV-2026-{inv_idx:04d}"

        clean_txns.append({
            "txnId": f"TXN_{cur_date.strftime('%Y%m%d')}_{inv_idx:04d}",
            "type": "CREDIT",
            "mode": "RTGS",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(current_bal, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": f"RTGS/{client.split()[0].upper()}/{inv_no}",
            "reference": f"REF{random.randint(100000000, 999999999)}",
            "counterparty": client,
            "counterpartyGstin": gstin,
            "accountHead": "Account 4010: Enterprise AI Software Subscriptions",
            "whatHappened": f"RTGS inward customer settlement of ₹{amt:,.2f} (¥{round(amt * FX_INR_TO_JPY):,}) received from {client} against Tax Invoice {inv_no}.",
            "whyReason": "Verified genuine commercial revenue: 100% matched against NIC E-Invoice IRN hash, confirmed fully offset on GSTR-3B tax offset ledger, and cleared into sovereign RBI ReBIT banking rail under standard 30-day corporate credit terms.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 (External Confirmations) & CGST Rules 2017 - Verified Arms-Length Settlement"
        })
        irn_hash = generate_sha256(f"NIC-IRN-APEX-{inv_idx:04d}-{date_str}-{amt}")
        taxable_amt = round(amt / 1.18, 2)
        gst_amt = round(amt - taxable_amt, 2)
        gst_clean_invoices.append({
            "gstin_recipient": gstin,
            "receiver_name": client,
            "invoice_number": inv_no,
            "invoice_date": date_str,
            "invoice_value": amt,
            "taxable_value": taxable_amt,
            "igst": gst_amt if gstin[:2] != "29" else 0.0,
            "cgst": round(gst_amt / 2, 2) if gstin[:2] == "29" else 0.0,
            "sgst": round(gst_amt / 2, 2) if gstin[:2] == "29" else 0.0,
            "gst_amount": gst_amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "account_head": "Account 4010: Enterprise AI Software Subscriptions",
            "irn_hash": irn_hash,
            "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
            "gstr3b_offset_status": "OFFSET_PAID",
            "type": "OUTWARD",
            "what_happened": f"B2B Enterprise outward invoice {inv_no} issued to {client} for ₹{amt:,.2f} with NIC registered IRN hash.",
            "why_reason": "Verified tax compliance: Output tax liability fully reported on GSTR-1 and confirmed offset via tax payment on GSTR-3B portal.",
            "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
        })
        inv_idx += 1

    # 6 Benford-conforming operating debits per day across 184 days = 1,104 debits
    for deb_i in range(6):
        vendor, gstin, desc, acc_head = random.choice(vendors_clean)
        amt = sample_benford_amount(magnitude_choices=[1, 2])
        current_bal -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        clean_txns.append({
            "txnId": f"TXN_{cur_date.strftime('%Y%m%d')}_{len(clean_txns)+1:05d}",
            "type": "DEBIT",
            "mode": random.choice(["NEFT", "UPI", "IMPS"]),
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(current_bal, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": f"{desc.upper()}/{vendor.split()[0].upper()}",
            "reference": f"REF{random.randint(100000000, 999999999)}",
            "counterparty": vendor,
            "counterpartyGstin": gstin,
            "accountHead": acc_head,
            "whatHappened": f"Operating disbursement of ₹{amt:,.2f} (¥{round(amt * FX_INR_TO_JPY):,}) paid to {vendor} for {desc}.",
            "whyReason": f"Verified legitimate business operating expense: Conforms to Benford's Law logarithmic distribution, verified B2B GSTIN ({gstin}), valid commercial tax invoice, zero director overlap.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1) - Bona Fide Business Expenditure"
        })

clean_payload = build_rebit_payload(
    cin="U72900KA2023PTC178921",
    company_name="Apex AI Labs Private Limited",
    masked_acc="XXXXXX9821",
    fip_id="HDFC-IN-FIP-001",
    opening_balance=12500000.0,
    transactions=clean_txns
)
with open("data/clean_startup_rebit.json", "w", encoding="utf-8") as f:
    json.dump(clean_payload, f, indent=2)
pd.DataFrame(gst_clean_invoices).to_csv("data/clean_startup_gst.csv", index=False)

# -------------------------------------------------------------
# 4. Fraud Startup: PhantomTech Solutions Private Limited
# -------------------------------------------------------------
fraud_ca_books = {
    "company_cin": "U74999DL2024PTC389102",
    "accounting_software": "Tally Prime Gold v4.1",
    "certified_by": "V. K. Aggarwal & Associates CA",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 25500000.0,
        "trade_receivables_total": 15400000.0,
        "receivables_aging": {
            "under_30_days": 1200000.0,
            "31_to_90_days": 2100000.0,
            "over_180_days_doubtful": 12100000.0
        },
        "trade_payables": 4500000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 2772000.0,
            "tds_payable": 890000.0,
            "pf_esi_payable": 340000.0
        },
        "general_ledger_cash_balance": 8450000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "QUALIFIED_MATERIAL_UNCERTAINTY"
}
with open("data/fraud_startup_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(fraud_ca_books, f, indent=2)

fraud_txns = []
current_bal_fraud = 8450000.0
total_fraud_credit = 0.0

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows: Only partial customer inflows capped at ₹1,01,00,000.0 (resulting in >50% divergence)
    if cur_date.day in [10, 25] and total_fraud_credit < 10100000.0:
        amt = round(random.uniform(400000, 600000), 2)
        if total_fraud_credit + amt > 10100000.0:
            amt = round(10100000.0 - total_fraud_credit, 2)
        current_bal_fraud += amt
        total_fraud_credit += amt
        t_stamp = make_timestamp(cur_date, min_hour=10, max_hour=13)
        fraud_txns.append({
            "txnId": f"TXN_{cur_date.strftime('%Y%m%d')}_{len(fraud_txns)+1:04d}",
            "type": "CREDIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(current_bal_fraud, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "NEFT/CUSTOMER_DEP",
            "reference": f"REF{random.randint(100000000, 999999999)}",
            "counterparty": "Real Customer A Limited",
            "counterpartyGstin": "07AAACR1111A1Z1",
            "accountHead": "Account 4010: Software Revenue",
            "whatHappened": f"Customer deposit of ₹{amt:,.2f} received from Real Customer A Limited.",
            "whyReason": "Authentic partial revenue realization; however, cumulative banking inflows (₹1.01 Cr) fall drastically short of claimed revenue of ₹2.55 Cr (60.4% divergence).",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 - Partial Realization"
        })

    # 6 operational debits per day = 1,104 debits
    for _ in range(6):
        amt = round(random.uniform(5000, 75000), 2)
        current_bal_fraud -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        fraud_txns.append({
            "txnId": f"TXN_{cur_date.strftime('%Y%m%d')}_{len(fraud_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(current_bal_fraud, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "VENDOR/OPS_EXPENSE/SERVICE_PAY",
            "reference": f"REF{random.randint(100000000, 999999999)}",
            "counterparty": "Delhi Cloud & Print Solutions",
            "counterpartyGstin": "07AAACD9988H1Z1",
            "accountHead": "Account 5020: Operational & Office Expenses",
            "whatHappened": f"Vendor operational disbursement of ₹{amt:,.2f} paid to Delhi Cloud & Print Solutions.",
            "whyReason": "Routine vendor service payment; absence of TDS deduction certificates and uniform distribution suggests non-rigorous accounting controls.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1)"
        })

# Siphoning trap (Sec 188 Director PAN match)
fraud_txns.append({
    "txnId": "TXN_20261120_SIPHON01",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 4130000.00,
    "amount_jpy": round(4130000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(current_bal_fraud - 4130000.0, 2),
    "transactionTimestamp": "2026-11-20T14:45:10+05:30",
    "valueDate": "2026-11-20",
    "narration": "RTGS/APEX_CLOUD/ADVISORY_STRATEGY_FEE",
    "reference": "REF981273891",
    "counterparty": "Apex Cloud Solutions LLP",
    "counterpartyGstin": "29ABCPS1234F1Z5",  # Director Vikram Malhotra PAN match!
    "accountHead": "Account 5020: Strategy & Technology Advisory",
    "whatHappened": "Direct RTGS debit of ₹41,30,000.00 (¥74,34,000) disbursed to Apex Cloud Solutions LLP for alleged advisory services.",
    "whyReason": "Violates Companies Act 2013 Section 188 (Related Party Transactions) and Section 185 (Loans/Advances to Directors). Slicing characters 3-12 of counterparty GSTIN 29ABCPS1234F1Z5 reveals PAN ABCPS1234F, which identically matches CEO Vikram Malhotra. Executed with zero Board of Directors resolution (Form MGT-14) or Audit Committee pre-approval.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "Companies Act 2013 Section 188 & Section 185"
})

# TDS smurfing traps (Clustered just below Sec 194C/J threshold)
for s_idx in range(25):
    fraud_txns.append({
        "txnId": f"TXN_20261014_SMURF_{s_idx+1:02d}",
        "type": "DEBIT",
        "mode": "NEFT",
        "amount": 49500.00,
        "amount_jpy": round(49500.00 * FX_INR_TO_JPY, 2),
        "currentBalance": round(current_bal_fraud - 49500.0 * (s_idx+1), 2),
        "transactionTimestamp": f"2026-10-14T10:{10+s_idx:02d}:00+05:30",
        "valueDate": "2026-10-14",
        "narration": f"NEFT/TECHCLOUD_SPLIT_BILL/FEES_{s_idx+1}",
        "reference": f"SMURF_REF_{s_idx+1}",
        "counterparty": "TechCloud Advisory LLP",
        "counterpartyGstin": "07AAACT8888K1Z5",
        "accountHead": "Account 5030: External Technical Sub-contracting",
        "whatHappened": f"Structured NEFT debit of exactly ₹49,500.00 (¥89,100) disbursed to TechCloud Advisory LLP as part of 25 same-day split transactions totaling ₹12,37,500.00.",
        "whyReason": "Structured deliberately ₹500 below the statutory ₹50,000 threshold to evade mandatory 10% TDS withholding under Income Tax Act Section 194C/J. Attracts 100% penalty under Section 271C for willful tax deduction evasion.",
        "forensicStatus": "FLAGGED_ANOMALY",
        "statutoryCitation": "Income Tax Act 1961 Section 194C, Section 194J & Section 271C"
    })

# Window dressing contra
fraud_txns.append({
    "txnId": "TXN_20260928_WINDOW_IN",
    "type": "CREDIT",
    "mode": "NEFT",
    "amount": 2500000.00,
    "amount_jpy": round(2500000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(current_bal_fraud + 2500000.0, 2),
    "transactionTimestamp": "2026-09-28T16:10:00+05:30",
    "valueDate": "2026-09-28",
    "narration": "NEFT/PROMOTER_CONTRA_INFUSION/SHARMA_HOLDINGS",
    "reference": "REF_CONTRA_981",
    "counterparty": "Sharma Holdings & Investments",
    "counterpartyGstin": "07AAACS1122D1Z9",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Temporary capital infusion of ₹25,00,000.00 (¥45,00,000) deposited on Day 28 of reporting month (2026-09-28) from promoter affiliate.",
    "whyReason": "Violates ICAI SA 240 (Cutoff Manipulation) & Companies Act Section 129. Orchestrated solely to artificially dress up ending quarter cash balance on pitch deck balance sheet prior to immediate reversal.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})
fraud_txns.append({
    "txnId": "TXN_20261002_WINDOW_OUT",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 2480000.00,
    "amount_jpy": round(2480000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(current_bal_fraud + 20000.0, 2),
    "transactionTimestamp": "2026-10-02T10:05:00+05:30",
    "valueDate": "2026-10-02",
    "narration": "RTGS/CONTRA_REVERSAL/SHARMA_HOLDINGS",
    "reference": "REF_CONTRA_REV_982",
    "counterparty": "Sharma Holdings & Investments",
    "counterpartyGstin": "07AAACS1122D1Z9",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Contra reversal of ₹24,80,000.00 (¥44,64,000) drained back to Sharma Holdings 4 calendar days after month-end reporting cutoff.",
    "whyReason": "Completes circular window-dressing round-trip under ICAI SA 240. Masks true operational cash burn and creates fictitious temporary liquidity buffer.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})

fraud_payload = build_rebit_payload(
    cin="U74999DL2024PTC389102",
    company_name="PhantomTech Solutions Private Limited",
    masked_acc="XXXXXX4419",
    fip_id="ICICI-IN-FIP-002",
    opening_balance=8450000.0,
    transactions=fraud_txns
)
with open("data/fraud_startup_rebit.json", "w", encoding="utf-8") as f:
    json.dump(fraud_payload, f, indent=2)

fraud_gst_invoices = []
for i in range(12):
    inv_date = (start_date + timedelta(days=i*15)).strftime("%Y-%m-%d")
    val = round(25500000.0 / 12, 2)
    taxable_val = round(val / 1.18, 2)
    gst_val = round(val - taxable_val, 2)
    fraud_gst_invoices.append({
        "gstin_recipient": "07AAACK9900L1Z4",
        "receiver_name": "Kestrel Advisory Services LLP",
        "invoice_number": f"PHAN-INV-2026-{i+1:03d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable_val,
        "igst": gst_val,
        "cgst": 0.0,
        "sgst": 0.0,
        "gst_amount": gst_val,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4010: Software Revenue",
        "irn_hash": generate_sha256(f"UNVERIFIED-BOGUS-PHANTOM-{i+1}"),
        "irn_status": "NIC_VALIDATION_FAILED_UNCONFIRMED_SHELL",
        "gstr3b_offset_status": "UNOFF_SET_UNPAID",
        "type": "OUTWARD",
        "what_happened": f"Outward invoice PHAN-INV-2026-{i+1:03d} for ₹{val:,.2f} billed to unconfirmed shell entity Kestrel Advisory Services LLP.",
        "why_reason": "Violates CGST Rules 2017 Rule 88C: Marked UNOFF_SET_UNPAID on GSTR-3B tax offset ledger with ₹0 tax remitted; automated DRC-01B statutory notice rail triggered.",
        "verification_status": "NIC_VALIDATION_FAILED_UNCONFIRMED_SHELL"
    })
pd.DataFrame(fraud_gst_invoices).to_csv("data/fraud_startup_gst.csv", index=False)

# -------------------------------------------------------------
# 5. LogiPulse Express: Dedicated CA Books, GST & ReBIT Files
# -------------------------------------------------------------
logipulse_ca_books = {
    "company_cin": "U63090MH2022PTC345678",
    "accounting_software": "Tally Prime Enterprise v4.1",
    "certified_by": "M. K. Joshi & Associates Chartered Accountants (FRN 012489W)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 18500000.0,
        "trade_receivables_total": 11193718.63,
        "receivables_aging": {
            "under_30_days": 2193718.63,
            "31_to_90_days": 3500000.0,
            "over_180_days_doubtful": 5500000.0
        },
        "trade_payables": 6800000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 1850000.0,
            "tds_payable": 480000.0,
            "pf_esi_payable": 220000.0
        },
        "general_ledger_cash_balance": 1200000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "QUALIFIED_MATERIAL_UNCERTAINTY"
}
with open("data/logipulse_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(logipulse_ca_books, f, indent=2)

logi_clients = [
    ("Flipkart India Private Limited", "29AABCU9603R1ZR"),
    ("Delhivery Limited", "06AAACD1111E1Z8"),
    ("Shadowfax Technologies Pvt Ltd", "29AAECS4567M1Z1"),
    ("Blinkit Commerce Private Limited", "07AAACZ8901D1Z5")
]
logipulse_gst_invoices = []
for i in range(12):
    inv_date = (start_date + timedelta(days=i*15)).strftime("%Y-%m-%d")
    client_name, client_gstin = logi_clients[i % len(logi_clients)]
    val = round(18500000.0 / 12, 2)
    taxable = round(val / 1.18, 2)
    gst_amt = round(val - taxable, 2)
    off_status = "UNOFF_SET_UNPAID" if i % 2 == 0 else "OFFSET_PAID"
    logipulse_gst_invoices.append({
        "gstin_recipient": client_gstin,
        "receiver_name": client_name,
        "invoice_number": f"LP-INV-2026-{i+1:03d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": gst_amt if client_gstin[:2] != "27" else 0.0,
        "cgst": round(gst_amt / 2, 2) if client_gstin[:2] == "27" else 0.0,
        "sgst": round(gst_amt / 2, 2) if client_gstin[:2] == "27" else 0.0,
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4040: D2C E-Commerce Logistics Services",
        "irn_hash": generate_sha256(f"NIC-IRN-LOGI-{i+1:03d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": off_status,
        "type": "OUTWARD",
        "what_happened": f"Logistics B2B service invoice LP-INV-2026-{i+1:03d} issued to {client_name} for ₹{val:,.2f}.",
        "why_reason": "Rule 88C Tax Discrepancy triggered due to unremitted tax status on GSTR-3B." if off_status == "UNOFF_SET_UNPAID" else "Verified tax compliance with offset paid.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(logipulse_gst_invoices).to_csv("data/logipulse_gst.csv", index=False)

# LogiPulse Bank Transactions
logipulse_txns = []
bal_logi = 6500000.0
total_logi_credit = 0.0
target_logi_credit = 11000000.0

vendors_logi = [
    ("Indian Oil Corporation Ltd", "07AAACI1234A1Z1", "Fleet Fuel Card Settlement", "Account 5060: Fleet Fuel & Transport"),
    ("IndoSpace Logistics Parks", "27AAACI5678B1Z3", "Bhiwandi Hub Warehouse Lease", "Account 5010: Warehouse Lease Overhead"),
    ("Razorpay Payouts Gateway", "27AABCR4455K1Z2", "Driver Contract Delivery Payouts", "Account 5030: Last-Mile Contractor Payouts"),
    ("National Cloud Telematics", "07AAACN9988H1Z5", "Fleet GPS Tracking & IoT Cloud", "Account 5020: Telematics & Cloud Compute")
]

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows
    if cur_date.weekday() in [1, 4] and total_logi_credit < target_logi_credit:
        c_name, c_gstin = random.choice(logi_clients)
        amt = round(random.uniform(150000, 320000), 2)
        if total_logi_credit + amt > target_logi_credit:
            amt = round(target_logi_credit - total_logi_credit, 2)
        if amt > 0.01:
            bal_logi += amt
            total_logi_credit += amt
            t_stamp = make_timestamp(cur_date, min_hour=10, max_hour=14)
            logipulse_txns.append({
                "txnId": f"TXN_LOGI_{cur_date.strftime('%Y%m%d')}_{len(logipulse_txns)+1:04d}",
                "type": "CREDIT",
                "mode": "NEFT",
                "amount": amt,
                "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
                "currentBalance": round(bal_logi, 2),
                "transactionTimestamp": t_stamp,
                "valueDate": date_str,
                "narration": f"NEFT/D2C_CUSTOMER_COLLECTION/{c_name.split()[0].upper()}",
                "reference": f"REF_LP_{random.randint(100000, 999999)}",
                "counterparty": c_name,
                "counterpartyGstin": c_gstin,
                "accountHead": "Account 4040: D2C E-Commerce Logistics Services",
                "whatHappened": f"Inward freight & delivery settlement of ₹{amt:,.2f} received from {c_name}.",
                "whyReason": "Authentic logistics customer remittance; partial realization reflects stretched 146.1-day DSO collection cycle in D2C logistics.",
                "forensicStatus": "VERIFIED_CLEAN",
                "statutoryCitation": "ICAI SA 505 - Partial Realization"
            })


    # Operational debits
    for _ in range(6):
        vendor, gstin, desc, acc_head = random.choice(vendors_logi)
        amt = round(random.uniform(15000, 85000), 2)
        bal_logi -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        logipulse_txns.append({
            "txnId": f"TXN_LOGI_{cur_date.strftime('%Y%m%d')}_{len(logipulse_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_logi, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": f"NEFT/{desc.upper().replace(' ', '_')}/{vendor.split()[0].upper()}",
            "reference": f"REF_LP_DEB_{random.randint(100000, 999999)}",
            "counterparty": vendor,
            "counterpartyGstin": gstin,
            "accountHead": acc_head,
            "whatHappened": f"Operational logistics expense of ₹{amt:,.2f} disbursed to {vendor} for {desc}.",
            "whyReason": f"Verified fleet operational expenditure: Supported by registered commercial contract ({gstin}) under Section 37(1).",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1)"
        })

logipulse_payload = build_rebit_payload(
    cin="U63090MH2022PTC345678",
    company_name="LogiPulse Express Private Limited",
    masked_acc="XXXXXX5678",
    fip_id="HDFC-IN-FIP-001",
    opening_balance=6500000.0,
    transactions=logipulse_txns
)
with open("data/logipulse_rebit.json", "w", encoding="utf-8") as f:
    json.dump(logipulse_payload, f, indent=2)

# -------------------------------------------------------------
# 6. Mirai Mobility: Dedicated CA Books, GST & ReBIT Files
# -------------------------------------------------------------
mirai_ca_books = {
    "company_cin": "U29100TN2023PTC456789",
    "accounting_software": "SAP S/4HANA Cloud (Tokyo & Chennai Desk)",
    "certified_by": "Deloitte Haskins & Sells LLP (FRN 117366W)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 43896936.43,
        "trade_receivables_total": 650000.0,
        "receivables_aging": {
            "under_30_days": 580000.0,
            "31_to_90_days": 70000.0,
            "over_180_days_doubtful": 0.0
        },
        "trade_payables": 2100000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 0.0,
            "tds_payable": 0.0,
            "pf_esi_payable": 0.0
        },
        "general_ledger_cash_balance": 52804518.22
    },
    "related_party_disclosures_sec188": [
        {
            "party_name": "Value Create Inc. (Tokyo)",
            "nature_of_relationship": "Investor & Strategic Advisory",
            "transaction_nature": "Bilateral CVC Advisory & Board Representation",
            "amount_inr": 0.0,
            "board_resolution_ref": "BR/2026/09/VALUE_CREATE"
        }
    ],
    "audit_opinion": "UNQUALIFIED_CLEAN"
}
with open("data/mirai_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(mirai_ca_books, f, indent=2)

mirai_clients = [
    ("Maruti Suzuki India Limited", "06AAACM0123A1Z9"),
    ("Tata Motors Limited", "27AAACT2727Q1ZW"),
    ("Denso India Private Limited", "09AAACD0124M1Z2"),
    ("Fanuc India Private Limited", "29AAACF1100D1Z6")
]
mirai_gst_invoices = []
for i in range(10):
    inv_date = (start_date + timedelta(days=i*18)).strftime("%Y-%m-%d")
    client_name, client_gstin = mirai_clients[i % len(mirai_clients)]
    val = round(43896936.43 / 10, 2)
    taxable = round(val / 1.18, 2)
    gst_amt = round(val - taxable, 2)
    mirai_gst_invoices.append({
        "gstin_recipient": client_gstin,
        "receiver_name": client_name,
        "invoice_number": f"MIRAI-INV-2026-{i+1:03d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": gst_amt if client_gstin[:2] != "33" else 0.0,
        "cgst": round(gst_amt / 2, 2) if client_gstin[:2] == "33" else 0.0,
        "sgst": round(gst_amt / 2, 2) if client_gstin[:2] == "33" else 0.0,
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4030: Industrial Robotics Automation Solutions",
        "irn_hash": generate_sha256(f"NIC-IRN-MIRAI-{i+1:03d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": "OFFSET_PAID",
        "type": "OUTWARD",
        "what_happened": f"Industrial robotics automation invoice MIRAI-INV-2026-{i+1:03d} issued to {client_name} for ₹{val:,.2f}.",
        "why_reason": "Verified bilateral automotive supply contract: 100% matched against NIC IRN hash, confirmed fully offset on GSTR-3B tax offset ledger.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(mirai_gst_invoices).to_csv("data/mirai_gst.csv", index=False)

# Mirai Bank Transactions
mirai_txns = []
bal_mirai = 38000000.0
total_mirai_credit = 0.0
target_mirai_credit = 43896936.43

vendors_mirai = [
    ("Harmonic Drive Systems Japan Desk", "33AAACH1122M1Z4", "Harmonic Speed Reducers Import", "Account 5070: Robotic Actuators & High-Precision Drives"),
    ("Keyence India Private Limited", "29AAACK5678F1Z2", "Machine Vision Sensors & LiDAR Units", "Account 5070: Autonomous Vision & Sensor Components"),
    ("Tidel Park Clean-Room Infrastructure", "33AAACT9012D1Z8", "Robotics Clean-Room Assembly Facility", "Account 5010: Engineering Facility Lease & Utilities"),
    ("Amazon Web Services Japan & India Desk", "33AABCA1234F1Z1", "Cloud Fleet Robotics Simulation Cluster", "Account 5020: Cloud Simulation & Telemetry Compute")
]

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows from Tier-1 Automotive (Monday & Wednesday)
    if cur_date.weekday() in [0, 2] and total_mirai_credit < target_mirai_credit:
        c_name, c_gstin = random.choice(mirai_clients)
        amt = round(random.uniform(900000, 1800000), 2)
        if total_mirai_credit + amt > target_mirai_credit:
            amt = round(target_mirai_credit - total_mirai_credit, 2)
        if amt > 0.01:
            bal_mirai += amt
            total_mirai_credit += amt
            t_stamp = make_timestamp(cur_date, min_hour=11, max_hour=15)
            mirai_txns.append({
                "txnId": f"TXN_MIRAI_{cur_date.strftime('%Y%m%d')}_{len(mirai_txns)+1:04d}",
                "type": "CREDIT",
                "mode": "RTGS",
                "amount": amt,
                "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
                "currentBalance": round(bal_mirai, 2),
                "transactionTimestamp": t_stamp,
                "valueDate": date_str,
                "narration": f"RTGS/{c_name.split()[0].upper()}/ROBOTICS_LINE_Q3",
                "reference": f"REF_MIRAI_{random.randint(100000, 999999)}",
                "counterparty": c_name,
                "counterpartyGstin": c_gstin,

            "accountHead": "Account 4030: Industrial Robotics Automation Solutions",
            "whatHappened": f"RTGS enterprise milestone settlement of ₹{amt:,.2f} (¥{round(amt * FX_INR_TO_JPY):,}) received from {c_name} for factory robotics deployment.",
            "whyReason": "Verified cross-border bilateral enterprise settlement: 100% matched against NIC IRN hash, confirmed on GSTR-3B tax offset, and cleared into sovereign bank account with zero governance anomalies.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 (External Confirmations) & Bilateral CVC Governance Protocol"
        })

    # Benford conforming operational debits (6 per day = 1,104 debits)
    for _ in range(6):
        vendor, gstin, desc, acc_head = random.choice(vendors_mirai)
        amt = sample_benford_amount(magnitude_choices=[2, 3, 4])
        bal_mirai -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        mirai_txns.append({
            "txnId": f"TXN_MIRAI_{cur_date.strftime('%Y%m%d')}_{len(mirai_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_mirai, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": f"NEFT/{desc.upper().replace(' ', '_')}/{vendor.split()[0].upper()}",
            "reference": f"REF_MIRAI_DEB_{random.randint(100000, 999999)}",
            "counterparty": vendor,
            "counterpartyGstin": gstin,
            "accountHead": acc_head,
            "whatHappened": f"Advanced robotics component disbursement of ₹{amt:,.2f} paid to {vendor} for {desc}.",
            "whyReason": f"Verified precision technology expenditure: First two digits conform to Benford logarithmic distribution, authentic customs/GST documentation ({gstin}), arms-length commercial supplier.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1) & Customs Tariff Act"
        })

mirai_payload = build_rebit_payload(
    cin="U29100TN2023PTC456789",
    company_name="Mirai Mobility Robotics Private Limited",
    masked_acc="XXXXXX6789",
    fip_id="SBI-IN-FIP-005",
    opening_balance=38000000.0,
    transactions=mirai_txns
)
with open("data/mirai_rebit.json", "w", encoding="utf-8") as f:
    json.dump(mirai_payload, f, indent=2)

# -------------------------------------------------------------
# 7. Edutrek Learning: Byju's Archetype
# (Aggressive revenue recognition, uncollected student receivables, Rule 88C)
# -------------------------------------------------------------
edutrek_ca_books = {
    "company_cin": "U80903KA2021PTC156789",
    "accounting_software": "Zoho Books Enterprise v2026.2",
    "certified_by": "Batliboi & Associates CA (Resigned / Qualified)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 450000000.0,
        "trade_receivables_total": 315000000.0,
        "receivables_aging": {
            "under_30_days": 35000000.0,
            "31_to_90_days": 60000000.0,
            "over_180_days_doubtful": 220000000.0
        },
        "trade_payables": 125000000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 48000000.0,
            "tds_payable": 14500000.0,
            "pf_esi_payable": 6500000.0
        },
        "general_ledger_cash_balance": 15200000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "QUALIFIED_DISCLAIMER_OF_OPINION"
}
with open("data/edutrek_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(edutrek_ca_books, f, indent=2)

edutrek_partners = [
    ("EduSmart Distribution LLP", "29AAAFE1234D1Z5"),
    ("Vidya Bhavan Learning Networks", "07AAACV5678F1Z3"),
    ("NextGen Coaching Centres India", "33AABCN9012K1Z9"),
    ("Acme Student Tablet Distributors", "27AAACA3456L1Z1")
]
edutrek_gst_invoices = []
for i in range(24):
    inv_date = (start_date + timedelta(days=i*7)).strftime("%Y-%m-%d")
    p_name, p_gstin = edutrek_partners[i % len(edutrek_partners)]
    val = round(450000000.0 / 24, 2)
    taxable = round(val / 1.18, 2)
    gst_amt = round(val - taxable, 2)
    off_status = "UNOFF_SET_UNPAID" if i >= 8 else "OFFSET_PAID"
    edutrek_gst_invoices.append({
        "gstin_recipient": p_gstin,
        "receiver_name": p_name,
        "invoice_number": f"EDU-INV-2026-{i+1:04d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": gst_amt if p_gstin[:2] != "29" else 0.0,
        "cgst": round(gst_amt / 2, 2) if p_gstin[:2] == "29" else 0.0,
        "sgst": round(gst_amt / 2, 2) if p_gstin[:2] == "29" else 0.0,
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4060: Smart Learning Course Tablet Platform",
        "irn_hash": generate_sha256(f"NIC-IRN-EDU-{i+1:04d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": off_status,
        "type": "OUTWARD",
        "what_happened": f"EdTech course & tablet bundled sales invoice EDU-INV-2026-{i+1:04d} issued to {p_name} for ₹{val:,.2f}.",
        "why_reason": "Rule 88C unremitted tax deficit: Invoices uploaded to GSTR-1 to inflate top-line ARR, but marked UNOFF_SET_UNPAID on GSTR-3B." if off_status == "UNOFF_SET_UNPAID" else "Verified tax offset.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(edutrek_gst_invoices).to_csv("data/edutrek_gst.csv", index=False)

# Bank transactions for Edutrek (Only ₹13.4 Cr real collections vs ₹45 Cr booked!)
edutrek_txns = []
bal_edu = 45000000.0
total_edu_credit = 0.0
total_edu_target = 134000000.0

edu_collection_days = [start_date + timedelta(days=d) for d in range(184) if (start_date + timedelta(days=d)).weekday() in [0, 3]]
n_edu = len(edu_collection_days)
weights_edu = np.random.uniform(0.88, 1.12, size=n_edu)
weights_edu = weights_edu / weights_edu.sum()
amounts_edu = np.round(weights_edu * total_edu_target, 2)
amounts_edu[-1] = round(total_edu_target - amounts_edu[:-1].sum(), 2)
edu_day_map = {edu_collection_days[i].strftime("%Y-%m-%d"): amounts_edu[i] for i in range(n_edu)}

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows: capped at 134,000,000.0
    if date_str in edu_day_map:
        amt = edu_day_map[date_str]
        bal_edu += amt
        total_edu_credit += amt
        p_name, p_gstin = random.choice(edutrek_partners)
        t_stamp = make_timestamp(cur_date, min_hour=10, max_hour=14)

        edutrek_txns.append({
            "txnId": f"TXN_EDU_{cur_date.strftime('%Y%m%d')}_{len(edutrek_txns)+1:04d}",
            "type": "CREDIT",
            "mode": "RTGS",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_edu, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": f"RTGS/STUDENT_COURSE_FEES/{p_name.split()[0].upper()}",
            "reference": f"REF_EDU_{random.randint(100000000, 999999999)}",
            "counterparty": p_name,
            "counterpartyGstin": p_gstin,
            "accountHead": "Account 4060: Smart Learning Course Tablet Platform",
            "whatHappened": f"Student course fee batch collection of ₹{amt:,.2f} received from partner distributor {p_name}.",
            "whyReason": "Authentic partial student remittance; massive divergence from booked ARR of ₹45 Cr reveals ₹22 Cr in uncollected zombie debtors aged >180 days under ICAI SA 505.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 (External Confirmations)"
        })

    # 6 debits per day = 1,104 debits (Heavy burn for Meta/Google Ads and Hardware OEM)
    for _ in range(6):
        amt = round(random.uniform(150000, 450000), 2)
        bal_edu -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        edutrek_txns.append({
            "txnId": f"TXN_EDU_{cur_date.strftime('%Y%m%d')}_{len(edutrek_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_edu, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "NEFT/META_GOOGLE_CUSTOMER_ACQUISITION/CAMPAIGN_BURN",
            "reference": f"REF_EDU_BURN_{random.randint(100000000, 999999999)}",
            "counterparty": "Google India Pvt Ltd",
            "counterpartyGstin": "07AABCG5678K1Z3",
            "accountHead": "Account 5040: Digital Advertising & Customer Acquisition",
            "whatHappened": f"Customer acquisition ad spend of ₹{amt:,.2f} disbursed to Google India Pvt Ltd.",
            "whyReason": "High-velocity operational marketing burn severely compressing true cash runway under Ind AS 109.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1)"
        })

edutrek_payload = build_rebit_payload(
    cin="U80903KA2021PTC156789",
    company_name="Edutrek Learning Technologies Private Limited",
    masked_acc="XXXXXX1144",
    fip_id="KOTAK-IN-FIP-004",
    opening_balance=45000000.0,
    transactions=edutrek_txns
)
with open("data/edutrek_rebit.json", "w", encoding="utf-8") as f:
    json.dump(edutrek_payload, f, indent=2)

# -------------------------------------------------------------
# 8. KwikPay Digital: BharatPe Archetype
# (Promoter siphoning via director PAN, TDS smurfing, window dressing)
# -------------------------------------------------------------
kwikpay_ca_books = {
    "company_cin": "U72900DL2022PTC384512",
    "accounting_software": "Tally Prime Gold v4.2",
    "certified_by": "P. K. Bansal & Co. Chartered Accountants",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 360000000.0,
        "trade_receivables_total": 85000000.0,
        "receivables_aging": {
            "under_30_days": 45000000.0,
            "31_to_90_days": 22000000.0,
            "over_180_days_doubtful": 18000000.0
        },
        "trade_payables": 48000000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 18500000.0,
            "tds_payable": 4200000.0,
            "pf_esi_payable": 1800000.0
        },
        "general_ledger_cash_balance": 32000000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "QUALIFIED_ADVERSE_OPINION"
}
with open("data/kwikpay_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(kwikpay_ca_books, f, indent=2)

kwik_merchants = [
    ("Retail Merchant Network North", "07AAACR1111A1Z1"),
    ("NCR Food & Retail Chain LLP", "07AAACF2222B1Z3"),
    ("Bharat Merchant Settlement Hub", "07AAACB3333C1Z5")
]
kwikpay_gst_invoices = []
for i in range(18):
    inv_date = (start_date + timedelta(days=i*10)).strftime("%Y-%m-%d")
    m_name, m_gstin = kwik_merchants[i % len(kwik_merchants)]
    val = round(360000000.0 / 18, 2)
    taxable = round(val / 1.18, 2)
    gst_amt = round(val - taxable, 2)
    off_status = "UNOFF_SET_UNPAID" if i >= 6 else "OFFSET_PAID"
    kwikpay_gst_invoices.append({
        "gstin_recipient": m_gstin,
        "receiver_name": m_name,
        "invoice_number": f"KWIK-INV-2026-{i+1:04d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": 0.0,
        "cgst": round(gst_amt / 2, 2),
        "sgst": round(gst_amt / 2, 2),
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4050: Digital Merchant Settlement & QR Solutions",
        "irn_hash": generate_sha256(f"NIC-IRN-KWIK-{i+1:04d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": off_status,
        "type": "OUTWARD",
        "what_happened": f"Merchant MDR fee invoice KWIK-INV-2026-{i+1:04d} issued to {m_name} for ₹{val:,.2f}.",
        "why_reason": "Rule 88C tax default triggered due to ₹1.85 Cr unpaid GST liability on GSTR-3B." if off_status == "UNOFF_SET_UNPAID" else "Verified tax offset paid.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(kwikpay_gst_invoices).to_csv("data/kwikpay_gst.csv", index=False)

# KwikPay Bank transactions
kwikpay_txns = []
bal_kp = 35000000.0
total_kp_credit = 0.0

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Merchant inflows
    if cur_date.weekday() in [1, 4] and total_kp_credit < 210000000.0:
        amt = round(random.uniform(2500000, 4200000), 2)
        if total_kp_credit + amt > 210000000.0:
            amt = round(210000000.0 - total_kp_credit, 2)
        if amt > 0.01:
            bal_kp += amt
            total_kp_credit += amt
            m_name, m_gstin = random.choice(kwik_merchants)
            t_stamp = make_timestamp(cur_date, min_hour=11, max_hour=14)
            kwikpay_txns.append({
                "txnId": f"TXN_KWIK_{cur_date.strftime('%Y%m%d')}_{len(kwikpay_txns)+1:04d}",
                "type": "CREDIT",
                "mode": "NEFT",
                "amount": amt,
                "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
                "currentBalance": round(bal_kp, 2),
                "transactionTimestamp": t_stamp,
                "valueDate": date_str,
                "narration": f"NEFT/QR_MERCHANT_SETTLEMENT/{m_name.split()[0].upper()}",
                "reference": f"REF_KWIK_{random.randint(100000000, 999999999)}",
                "counterparty": m_name,
                "counterpartyGstin": m_gstin,

            "accountHead": "Account 4050: Digital Merchant Settlement & QR Solutions",
            "whatHappened": f"Merchant QR settlement remittance of ₹{amt:,.2f} received from {m_name}.",
            "whyReason": "Authentic merchant payment processing flow; divergence from claimed ARR reflects inflated merchant transaction volumes.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 - Partial Realization"
        })

    # 6 debits per day = 1,104 debits
    for _ in range(6):
        amt = round(random.uniform(80000, 250000), 2)
        bal_kp -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        kwikpay_txns.append({
            "txnId": f"TXN_KWIK_{cur_date.strftime('%Y%m%d')}_{len(kwikpay_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_kp, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "OPS/SERVER_INFRA_HOSTING/CLOUD_DEPLOY",
            "reference": f"REF_KWIK_DEB_{random.randint(100000000, 999999999)}",
            "counterparty": "National Cloud Networks LLP",
            "counterpartyGstin": "07AAACN5555M1Z2",
            "accountHead": "Account 5020: Cloud Server Infrastructure",
            "whatHappened": f"Server hosting infrastructure disbursement of ₹{amt:,.2f} paid to National Cloud Networks LLP.",
            "whyReason": "Verified technical server maintenance fee under Section 37(1).",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1)"
        })

# Siphoning trap: Outflow to Director Madhuri Mehra PAN (AMMPM3456F)
kwikpay_txns.append({
    "txnId": "TXN_20261115_SIPHON_KWIK",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 5850000.00,
    "amount_jpy": round(5850000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_kp - 5850000.0, 2),
    "transactionTimestamp": "2026-11-15T14:30:00+05:30",
    "valueDate": "2026-11-15",
    "narration": "RTGS/MEHRA_ADVISORY/HR_PROCUREMENT_FEE",
    "reference": "REF_SIPHON_KWIK_982",
    "counterparty": "Mehra Corporate Advisory & HR LLP",
    "counterpartyGstin": "07AMMPM3456F1Z8",  # Matches Director Madhuri Mehra PAN!
    "accountHead": "Account 5050: Recruitment, Payroll & HR Advisory",
    "whatHappened": "Direct RTGS debit of ₹58,50,000.00 (¥1,05,30,000) disbursed to Mehra Corporate Advisory & HR LLP for purported executive talent acquisition.",
    "whyReason": "Violates Companies Act 2013 Section 188 (Related Party Transactions) and Section 185 (Loans/Advances to Directors). Slicing characters 3-12 of counterparty GSTIN 07AMMPM3456F1Z8 embeds PAN AMMPM3456F belonging to Director Madhuri Mehra. Executed without shareholder approval or Form MGT-14 filing.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "Companies Act 2013 Section 188 & Section 185"
})

# TDS smurfing traps: Split payments at ₹49,500 to evade Sec 194C/J threshold
for s_idx in range(30):
    kwikpay_txns.append({
        "txnId": f"TXN_20261016_SMURF_{s_idx+1:02d}",
        "type": "DEBIT",
        "mode": "NEFT",
        "amount": 49500.00,
        "amount_jpy": round(49500.00 * FX_INR_TO_JPY, 2),
        "currentBalance": round(bal_kp - 49500.0 * (s_idx+1), 2),
        "transactionTimestamp": f"2026-10-16T10:{10+s_idx:02d}:00+05:30",
        "valueDate": "2026-10-16",
        "narration": f"NEFT/STARTECH_SPLIT_PAY/CONSULT_{s_idx+1}",
        "reference": f"SMURF_KWIK_{s_idx+1}",
        "counterparty": "StarTech Consultancy Services",
        "counterpartyGstin": "07AAACS1122D1Z9",
        "accountHead": "Account 5030: Technical Sub-contracting & Consulting",
        "whatHappened": f"Structured NEFT debit of exactly ₹49,500.00 (¥89,100) disbursed to StarTech Consultancy Services as part of 30 same-day split transactions totaling ₹14,85,000.00.",
        "whyReason": "Structured deliberately ₹500 below the statutory ₹50,000 threshold to evade mandatory 10% TDS withholding under Income Tax Act Section 194C/J. Attracts 100% penalty under Section 271C for willful tax deduction evasion.",
        "forensicStatus": "FLAGGED_ANOMALY",
        "statutoryCitation": "Income Tax Act 1961 Section 194C, Section 194J & Section 271C"
    })

# Window dressing contra
kwikpay_txns.append({
    "txnId": "TXN_20260929_WINDOW_IN",
    "type": "CREDIT",
    "mode": "NEFT",
    "amount": 3500000.00,
    "amount_jpy": round(3500000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_kp + 3500000.0, 2),
    "transactionTimestamp": "2026-09-29T16:20:00+05:30",
    "valueDate": "2026-09-29",
    "narration": "NEFT/PROMOTER_CONTRA_INFUSION/GROVER_HOLDINGS",
    "reference": "REF_CONTRA_KP_991",
    "counterparty": "Grover Capital & Holdings",
    "counterpartyGstin": "07AABPG9012L1Z3",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Temporary capital infusion of ₹35,00,000.00 (¥63,00,000) deposited on Day 29 of reporting month (2026-09-29) from promoter affiliate Grover Capital & Holdings.",
    "whyReason": "Violates ICAI SA 240 (Cutoff Manipulation) & Companies Act Section 129. Orchestrated solely to artificially dress up ending quarter cash balance on pitch deck balance sheet prior to immediate reversal.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})
kwikpay_txns.append({
    "txnId": "TXN_20261003_WINDOW_OUT",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 3480000.00,
    "amount_jpy": round(3480000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_kp + 20000.0, 2),
    "transactionTimestamp": "2026-10-03T10:10:00+05:30",
    "valueDate": "2026-10-03",
    "narration": "RTGS/CONTRA_REVERSAL/GROVER_HOLDINGS",
    "reference": "REF_CONTRA_KP_REV_992",
    "counterparty": "Grover Capital & Holdings",
    "counterpartyGstin": "07AABPG9012L1Z3",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Contra reversal of ₹34,80,000.00 (¥62,64,000) drained back to Grover Capital & Holdings 4 calendar days after month-end reporting cutoff.",
    "whyReason": "Completes circular window-dressing round-trip under ICAI SA 240. Masks true operational cash burn and creates fictitious temporary liquidity buffer.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})

kwikpay_payload = build_rebit_payload(
    cin="U72900DL2022PTC384512",
    company_name="KwikPay Digital Networks Private Limited",
    masked_acc="XXXXXX2290",
    fip_id="ICICI-IN-FIP-002",
    opening_balance=35000000.0,
    transactions=kwikpay_txns
)
with open("data/kwikpay_rebit.json", "w", encoding="utf-8") as f:
    json.dump(kwikpay_payload, f, indent=2)

# -------------------------------------------------------------
# 9. Zenith BioHealth: Realistic Series A MedTech
# (Clean governance, genuine hospital receivables with 76-day DSO lag)
# -------------------------------------------------------------
zenith_ca_books = {
    "company_cin": "U85110MH2023PTC398765",
    "accounting_software": "Zoho Books Enterprise v2026.1",
    "certified_by": "K. S. Aiyar & Co. Chartered Accountants (FRN 100186W)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 218000000.0,
        "trade_receivables_total": 32000000.0,
        "receivables_aging": {
            "under_30_days": 16000000.0,
            "31_to_90_days": 14500000.0,
            "over_180_days_doubtful": 1500000.0
        },
        "trade_payables": 14000000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 450000.0,
            "tds_payable": 280000.0,
            "pf_esi_payable": 120000.0
        },
        "general_ledger_cash_balance": 124500000.0
    },
    "related_party_disclosures_sec188": [],
    "audit_opinion": "UNQUALIFIED_WITH_EMPHASIS_OF_MATTER"
}
with open("data/zenith_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(zenith_ca_books, f, indent=2)

hospitals = [
    ("Apollo Hospitals Enterprise Ltd", "33AABCA0123A1Z5"),
    ("Fortis Healthcare Limited", "07AAACF4567B1Z2"),
    ("Max Healthcare Institute Ltd", "07AAACM8901C1Z8"),
    ("Manipal Health Enterprises Pvt Ltd", "29AAACM2345D1Z4")
]
zenith_gst_invoices = []
for i in range(20):
    inv_date = (start_date + timedelta(days=i*9)).strftime("%Y-%m-%d")
    h_name, h_gstin = hospitals[i % len(hospitals)]
    taxable = round(218000000.0 / 20, 2)
    gst_amt = round(taxable * 0.18, 2)
    val = round(taxable + gst_amt, 2)
    zenith_gst_invoices.append({
        "gstin_recipient": h_gstin,
        "receiver_name": h_name,
        "invoice_number": f"ZEN-INV-2026-{i+1:04d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": gst_amt if h_gstin[:2] != "27" else 0.0,
        "cgst": round(gst_amt / 2, 2) if h_gstin[:2] == "27" else 0.0,
        "sgst": round(gst_amt / 2, 2) if h_gstin[:2] == "27" else 0.0,
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4020: Hospital ICU Telehealth Diagnostics",
        "irn_hash": generate_sha256(f"NIC-IRN-ZEN-{i+1:04d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": "OFFSET_PAID",
        "type": "OUTWARD",
        "what_happened": f"Hospital ICU telehealth monitoring subscription invoice ZEN-INV-2026-{i+1:04d} issued to {h_name} for ₹{val:,.2f}.",
        "why_reason": "Verified healthcare enterprise invoice: 100% matched against NIC IRN hash, confirmed on GSTR-3B tax offset ledger, authentic 76-day hospital DSO settlement lag.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(zenith_gst_invoices).to_csv("data/zenith_gst.csv", index=False)

# Bank transactions for Zenith (Target credit: ₹168.0M to maintain Score 78 calibration)
zenith_txns = []
bal_zen = 85000000.0
total_zen_credit = 0.0
target_zen_credit = 167000000.0

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows from hospital networks
    if cur_date.weekday() in [2, 4] and total_zen_credit < target_zen_credit:
        amt = round(random.uniform(2800000, 4800000), 2)
        if total_zen_credit + amt > target_zen_credit:
            amt = round(target_zen_credit - total_zen_credit, 2)
        if amt > 0.01:
            bal_zen += amt
            total_zen_credit += amt
            h_name, h_gstin = random.choice(hospitals)
            t_stamp = make_timestamp(cur_date, min_hour=11, max_hour=15)
            zenith_txns.append({
                "txnId": f"TXN_ZEN_{cur_date.strftime('%Y%m%d')}_{len(zenith_txns)+1:04d}",
                "type": "CREDIT",
                "mode": "RTGS",
                "amount": amt,
                "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
                "currentBalance": round(bal_zen, 2),
                "transactionTimestamp": t_stamp,
                "valueDate": date_str,
                "narration": f"RTGS/HOSPITAL_SUBSCRIPTION/{h_name.split()[0].upper()}",
                "reference": f"REF_ZEN_{random.randint(100000000, 999999999)}",
                "counterparty": h_name,
                "counterpartyGstin": h_gstin,

            "accountHead": "Account 4020: Hospital ICU Telehealth Diagnostics",
            "whatHappened": f"Hospital ICU telehealth subscription settlement of ₹{amt:,.2f} (¥{round(amt * FX_INR_TO_JPY):,}) received from {h_name}.",
            "whyReason": "Verified genuine hospital payment: 100% matched against NIC IRN hash, confirmed on GSTR-3B tax offset, reflects authentic institutional 76-day DSO procurement cycle.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 (External Confirmations) - Clean Healthcare Settlement"
        })

    # Benford conforming operational debits (6 per day = 1,104 debits)
    for _ in range(6):
        amt = sample_benford_amount(magnitude_choices=[2, 3, 4])
        bal_zen -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        zenith_txns.append({
            "txnId": f"TXN_ZEN_{cur_date.strftime('%Y%m%d')}_{len(zenith_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_zen, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "NEFT/SENSOR_HARDWARE_ICU_CLOUD/VENDOR_OPS",
            "reference": f"REF_ZEN_DEB_{random.randint(100000000, 999999999)}",
            "counterparty": "MedTech Hardware Solutions India",
            "counterpartyGstin": "27AAACM9900H1Z2",
            "accountHead": "Account 5070: Medical Sensor Hardware & Cloud Operations",
            "whatHappened": f"Medical sensor hardware & ICU telemetry compute expense of ₹{amt:,.2f} disbursed to MedTech Hardware Solutions India.",
            "whyReason": "Verified medical hardware expenditure: Strictly conforms to Benford's Law distribution curve, valid tax invoice, arms-length vendor without promoter conflict.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1) - Bona Fide Business Expenditure"
        })

zenith_payload = build_rebit_payload(
    cin="U85110MH2023PTC398765",
    company_name="Zenith BioHealth Solutions Private Limited",
    masked_acc="XXXXXX5529",
    fip_id="HDFC-IN-FIP-001",
    opening_balance=85000000.0,
    transactions=zenith_txns
)
with open("data/zenith_rebit.json", "w", encoding="utf-8") as f:
    json.dump(zenith_payload, f, indent=2)

# -------------------------------------------------------------
# 10. AutoCare Network: GoMechanic Archetype
# (Fictitious garage network, circular spare parts billing,
# Section 269ST cash receipts >= ₹2L, Sec 40A(3) disallowed cash,
# Sec 188 promoter parts siphoning, Adverse Disclaimer)
# -------------------------------------------------------------
autocare_ca_books = {
    "company_cin": "U50400DL2021PTC378901",
    "accounting_software": "Tally Prime Gold v4.2",
    "certified_by": "R. Sharma & Associates Chartered Accountants (FRN 014528N)",
    "financial_period": "FY 2026-27 (Q2-Q3)",
    "trial_balance_inr": {
        "booked_sales_revenue": 1800000000.0,
        "trade_receivables_total": 950000000.0,
        "receivables_aging": {
            "under_30_days": 150000000.0,
            "31_to_90_days": 250000000.0,
            "over_180_days_doubtful": 550000000.0
        },
        "trade_payables": 380000000.0,
        "statutory_dues_payable": {
            "gst_output_liability": 185000000.0,
            "tds_payable": 24000000.0,
            "pf_esi_payable": 8500000.0
        },
        "general_ledger_cash_balance": 14500000.0
    },
    "related_party_disclosures_sec188": [
        {
            "party_name": "Oberoi Spares & Auto Components LLP",
            "nature_of_relationship": "Entity influenced by Director Rishabh Oberoi",
            "pan": "AROPO8901L",
            "amount_inr": 48000000.0,
            "board_approval_status": "NO_BOARD_RESOLUTION_MGT14"
        }
    ],
    "cash_transactions_sec269st": {
        "cash_receipts_exceeding_2_lakhs_inr": 18500000.0,
        "violation_count": 5,
        "statutory_penalty_under_sec271da_inr": 18500000.0
    },
    "audit_opinion": "ADVERSE_DISCLAIMER_OPINION"
}
with open("data/autocare_ca_books.json", "w", encoding="utf-8") as f:
    json.dump(autocare_ca_books, f, indent=2)

garage_partners = [
    ("Star AutoCare Hub Delhi", "07AAACS1234D1Z2"),
    ("Metro Garage Network NCR", "07AAACM5678E1Z4"),
    ("Apex Car Care Services", "07AAACA9012F1Z6"),
    ("GT Road Auto Works LLP", "06AAACG3456H1Z8"),
    ("Speedway Motors Gurgaon", "06AAACS7890J1Z1")
]
autocare_gst_invoices = []
for i in range(20):
    inv_date = (start_date + timedelta(days=i*9)).strftime("%Y-%m-%d")
    g_name, g_gstin = garage_partners[i % len(garage_partners)]
    val = round(1800000000.0 / 20, 2)
    taxable = round(val / 1.18, 2)
    gst_amt = round(val - taxable, 2)
    off_status = "UNOFF_SET_UNPAID" if i >= 5 else "OFFSET_PAID"
    autocare_gst_invoices.append({
        "gstin_recipient": g_gstin,
        "receiver_name": g_name,
        "invoice_number": f"AUTO-INV-2026-{i+1:04d}",
        "invoice_date": inv_date,
        "invoice_value": val,
        "taxable_value": taxable,
        "igst": gst_amt if g_gstin[:2] != "07" else 0.0,
        "cgst": round(gst_amt / 2, 2) if g_gstin[:2] == "07" else 0.0,
        "sgst": round(gst_amt / 2, 2) if g_gstin[:2] == "07" else 0.0,
        "gst_amount": gst_amt,
        "amount_jpy": round(val * FX_INR_TO_JPY, 2),
        "account_head": "Account 4070: Garage Service & Maintenance Network",
        "irn_hash": generate_sha256(f"NIC-IRN-AUTO-{i+1:04d}-{val}"),
        "irn_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED",
        "gstr3b_offset_status": off_status,
        "type": "OUTWARD",
        "what_happened": f"Automotive garage service network invoice AUTO-INV-2026-{i+1:04d} issued to {g_name} for ₹{val:,.2f}.",
        "why_reason": "Rule 88C unremitted tax deficit: Invoices uploaded to GSTR-1 to simulate national scale, but marked UNOFF_SET_UNPAID on GSTR-3B." if off_status == "UNOFF_SET_UNPAID" else "Verified tax offset paid.",
        "verification_status": "NIC_CRYPTOGRAPHICALLY_VERIFIED"
    })
pd.DataFrame(autocare_gst_invoices).to_csv("data/autocare_gst.csv", index=False)

# AutoCare bank transactions
autocare_txns = []
bal_auto = 42000000.0
total_auto_credit = 0.0
target_auto_credit = 380000000.0

for day_idx in range(184):
    cur_date = start_date + timedelta(days=day_idx)
    date_str = cur_date.strftime("%Y-%m-%d")

    # Inflows from garage partners
    if cur_date.weekday() in [1, 3] and total_auto_credit < target_auto_credit:
        amt = round(random.uniform(4000000, 8000000), 2)
        if total_auto_credit + amt > target_auto_credit:
            amt = round(target_auto_credit - total_auto_credit, 2)
        if amt > 0.01:
            bal_auto += amt
            total_auto_credit += amt
            g_name, g_gstin = random.choice(garage_partners)
            t_stamp = make_timestamp(cur_date, min_hour=11, max_hour=14)
            autocare_txns.append({
                "txnId": f"TXN_AUTO_{cur_date.strftime('%Y%m%d')}_{len(autocare_txns)+1:04d}",
                "type": "CREDIT",
                "mode": "NEFT",
                "amount": amt,
                "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
                "currentBalance": round(bal_auto, 2),
                "transactionTimestamp": t_stamp,
                "valueDate": date_str,
                "narration": f"NEFT/GARAGE_SETTLEMENT/{g_name.split()[0].upper()}",
                "reference": f"REF_AUTO_{random.randint(100000000, 999999999)}",
                "counterparty": g_name,
                "counterpartyGstin": g_gstin,

            "accountHead": "Account 4070: Garage Service & Maintenance Network",
            "whatHappened": f"Garage partner settlement remittance of ₹{amt:,.2f} received from {g_name}.",
            "whyReason": "Authentic partial garage service collection; divergence from ₹180 Cr claimed ARR reveals massive fictitious garage network billing.",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "ICAI SA 505 - Partial Realization"
        })

    # Operational debits (5 per day = 920 debits)
    for _ in range(5):
        amt = round(random.uniform(150000, 450000), 2)
        bal_auto -= amt
        t_stamp = make_timestamp(cur_date, min_hour=9, max_hour=18)
        autocare_txns.append({
            "txnId": f"TXN_AUTO_{cur_date.strftime('%Y%m%d')}_{len(autocare_txns)+1:05d}",
            "type": "DEBIT",
            "mode": "NEFT",
            "amount": amt,
            "amount_jpy": round(amt * FX_INR_TO_JPY, 2),
            "currentBalance": round(bal_auto, 2),
            "transactionTimestamp": t_stamp,
            "valueDate": date_str,
            "narration": "NEFT/PARTS_INVENTORY_PROCUREMENT/DELHI_HUB",
            "reference": f"REF_AUTO_DEB_{random.randint(100000000, 999999999)}",
            "counterparty": "National Spare Parts Aggregators LLP",
            "counterpartyGstin": "07AAACN8877K1Z4",
            "accountHead": "Account 5070: Spare Parts & Hardware Components Inventory",
            "whatHappened": f"Automotive parts inventory procurement expense of ₹{amt:,.2f} disbursed to National Spare Parts Aggregators LLP.",
            "whyReason": "Routine garage spare parts purchase under Section 37(1).",
            "forensicStatus": "VERIFIED_CLEAN",
            "statutoryCitation": "Income Tax Act 1961 Section 37(1)"
        })

# Section 269ST Cash Violations: Prohibited cash receipts >= ₹2,00,000 in a day
sec269st_cash_days = [
    ("2026-08-14", 250000.0),
    ("2026-09-10", 380000.0),
    ("2026-10-05", 420000.0),
    ("2026-11-12", 500000.0),
    ("2026-12-08", 300000.0)
]
for c_date, c_amt in sec269st_cash_days:
    bal_auto += c_amt
    autocare_txns.append({
        "txnId": f"TXN_CASH_269ST_{c_date.replace('-', '')}",
        "type": "CREDIT",
        "mode": "CASH",
        "amount": c_amt,
        "amount_jpy": round(c_amt * FX_INR_TO_JPY, 2),
        "currentBalance": round(bal_auto, 2),
        "transactionTimestamp": f"{c_date}T16:45:00+05:30",
        "valueDate": c_date,
        "narration": "CASH DEPOSIT/GARAGE_COLLECTION/NCR_HUB",
        "reference": f"REF_CASH_269ST_{random.randint(10000, 99999)}",
        "counterparty": "Partner Garage Cash Network",
        "counterpartyGstin": "",
        "accountHead": "Account 1020: Physical Cash In Hand / Garage Collections",
        "whatHappened": f"Single-day physical cash deposit of ₹{c_amt:,.2f} (¥{round(c_amt * FX_INR_TO_JPY):,}) deposited into current account from garage network partner.",
        "whyReason": f"Violates Income Tax Act 1961 Section 269ST, which strictly prohibits receiving cash of ₹2,00,000 or more from a person in a day or in respect of a single transaction. Attracts 100% statutory penalty of ₹{c_amt:,.2f} under Section 271DA and signals unaccounted black money channel.",
        "forensicStatus": "FLAGGED_ANOMALY",
        "statutoryCitation": "Income Tax Act 1961 Section 269ST & Section 271DA"
    })

# Section 40A(3) Disallowed Cash Debits (> ₹10,000 cash payment)
sec40a3_days = [
    ("2026-08-20", 25000.0),
    ("2026-09-18", 35000.0),
    ("2026-10-22", 40000.0)
]
for d_date, d_amt in sec40a3_days:
    bal_auto -= d_amt
    autocare_txns.append({
        "txnId": f"TXN_CASH_40A3_{d_date.replace('-', '')}",
        "type": "DEBIT",
        "mode": "CASH",
        "amount": d_amt,
        "amount_jpy": round(d_amt * FX_INR_TO_JPY, 2),
        "currentBalance": round(bal_auto, 2),
        "transactionTimestamp": f"{d_date}T17:15:00+05:30",
        "valueDate": d_date,
        "narration": "CASH WDL/LOCAL_MECHANIC_PETTY_PAY",
        "reference": f"REF_CASH_40A3_{random.randint(10000, 99999)}",
        "counterparty": "Local Mechanic Cash Payee",
        "counterpartyGstin": "",
        "accountHead": "Account 5060: Garage Operations & Petty Mechanical Wages",
        "whatHappened": f"Cash withdrawal of ₹{d_amt:,.2f} disbursed for local mechanic petty expenses.",
        "whyReason": "Violates Income Tax Act 1961 Section 40A(3), which mandates 100% tax disallowance of any business expenditure exceeding ₹10,000 paid otherwise than by account payee cheque, bank draft, or electronic clearing system.",
        "forensicStatus": "FLAGGED_ANOMALY",
        "statutoryCitation": "Income Tax Act 1961 Section 40A(3)"
    })

# Siphoning trap: Outflow to Director Rishabh Oberoi PAN (AROPO8901L) via Oberoi Spares
bal_auto -= 4800000.0
autocare_txns.append({
    "txnId": "TXN_20261028_SIPHON_AUTO",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 4800000.00,
    "amount_jpy": round(4800000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_auto, 2),
    "transactionTimestamp": "2026-10-28T14:15:00+05:30",
    "valueDate": "2026-10-28",
    "narration": "RTGS/OBEROI_SPARES/BULK_COMPONENT_ADVANCE",
    "reference": "REF_SIPHON_AUTO_771",
    "counterparty": "Oberoi Spares & Auto Components LLP",
    "counterpartyGstin": "07AROPO8901L1Z9",
    "accountHead": "Account 5070: Bulk Spare Parts Component Advance",
    "whatHappened": "Direct RTGS disbursement of ₹48,00,000.00 (¥86,40,000) to Oberoi Spares & Auto Components LLP for alleged bulk inventory advance.",
    "whyReason": "Violates Companies Act 2013 Section 188 & Section 185. Vendor GSTIN embeds PAN AROPO8901L matching Director Rishabh Oberoi. Unapproved related party transfer without board resolution.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "Companies Act 2013 Section 188 & Section 185"
})

# TDS smurfing / threshold structuring traps: Split payments at ₹19,500 and ₹49,500
for s_idx in range(25):
    smurf_amt = 49500.00 if s_idx % 2 == 0 else 19500.00
    bal_auto -= smurf_amt
    autocare_txns.append({
        "txnId": f"TXN_20261108_AUTO_SMURF_{s_idx+1:02d}",
        "type": "DEBIT",
        "mode": "NEFT",
        "amount": smurf_amt,
        "amount_jpy": round(smurf_amt * FX_INR_TO_JPY, 2),
        "currentBalance": round(bal_auto, 2),
        "transactionTimestamp": f"2026-11-08T11:{10+s_idx:02d}:00+05:30",
        "valueDate": "2026-11-08",
        "narration": f"NEFT/GARAGE_COMMISSION/SPLIT_SLOT_{s_idx+1}",
        "reference": f"SMURF_AUTO_{s_idx+1}",
        "counterparty": "AutoQuick Diagnostic Systems",
        "counterpartyGstin": "07AAACA4455P1Z8",
        "accountHead": "Account 5030: Technical Sub-contracting & Consulting",
        "whatHappened": f"Structured NEFT disbursement of ₹{smurf_amt:,.2f} disbursed to AutoQuick Diagnostic Systems as part of 25 same-day split transactions.",
        "whyReason": "Structured deliberately below statutory threshold to evade mandatory withholding tax under Income Tax Act Section 194C/J. Attracts 100% penalty under Section 271C.",
        "forensicStatus": "FLAGGED_ANOMALY",
        "statutoryCitation": "Income Tax Act 1961 Section 194C, Section 194J & Section 271C"
    })

# Window dressing contra
bal_auto += 28000000.0
autocare_txns.append({
    "txnId": "TXN_20260928_WINDOW_IN_AUTO",
    "type": "CREDIT",
    "mode": "NEFT",
    "amount": 28000000.00,
    "amount_jpy": round(28000000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_auto, 2),
    "transactionTimestamp": "2026-09-28T17:00:00+05:30",
    "valueDate": "2026-09-28",
    "narration": "NEFT/PROMOTER_CONTRA_INFUSION/SINGHAL_HOLDINGS",
    "reference": "REF_CONTRA_AUTO_981",
    "counterparty": "Singhal Capital & Holdings",
    "counterpartyGstin": "07AABCA4567M1Z1",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Temporary capital infusion of ₹2,80,00,000.00 (¥5,04,00,000) deposited on Day 28 of reporting month (2026-09-28) from promoter affiliate Singhal Capital & Holdings.",
    "whyReason": "Violates ICAI SA 240 (Cutoff Manipulation) & Companies Act Section 129. Orchestrated solely to artificially dress up ending quarter cash balance on pitch deck balance sheet prior to immediate reversal.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})
bal_auto -= 27800000.0
autocare_txns.append({
    "txnId": "TXN_20261002_WINDOW_OUT_AUTO",
    "type": "DEBIT",
    "mode": "RTGS",
    "amount": 27800000.00,
    "amount_jpy": round(27800000.00 * FX_INR_TO_JPY, 2),
    "currentBalance": round(bal_auto, 2),
    "transactionTimestamp": "2026-10-02T10:30:00+05:30",
    "valueDate": "2026-10-02",
    "narration": "RTGS/CONTRA_REVERSAL/SINGHAL_HOLDINGS",
    "reference": "REF_CONTRA_AUTO_REV_982",
    "counterparty": "Singhal Capital & Holdings",
    "counterpartyGstin": "07AABCA4567M1Z1",
    "accountHead": "Account 3010: Promoter Contra Loan / Liquidity Infusion",
    "whatHappened": "Contra reversal of ₹2,78,00,000.00 (¥5,00,40,000) drained back to Singhal Capital & Holdings 4 calendar days after month-end reporting cutoff.",
    "whyReason": "Completes circular window-dressing round-trip under ICAI SA 240. Masks true operational cash burn and creates fictitious temporary liquidity buffer.",
    "forensicStatus": "FLAGGED_ANOMALY",
    "statutoryCitation": "ICAI SA 240 (Cutoff Manipulation) & Companies Act 2013 Section 129"
})

autocare_payload = build_rebit_payload(
    cin="U50400DL2021PTC378901",
    company_name="AutoCare Network India Private Limited",
    masked_acc="XXXXXX3789",
    fip_id="YESB-IN-FIP-003",
    opening_balance=42000000.0,
    transactions=autocare_txns
)
with open("data/autocare_rebit.json", "w", encoding="utf-8") as f:
    json.dump(autocare_payload, f, indent=2)

print("Master multi-source datasets successfully generated across CA Books, ReBIT, GSTN, and MCA layers!")
