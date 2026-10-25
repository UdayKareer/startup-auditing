"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Investor Due Diligence Portal.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.
"""

import streamlit as st

st.set_page_config(
    page_title="VeriLedger | Investor Diligence Portal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.investor_portal_view import render_investor_portal

# Render dedicated, self-contained Investor Portal
render_investor_portal()
