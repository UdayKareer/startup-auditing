"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Startup Founder Dashboard.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.
"""

import streamlit as st

st.set_page_config(
    page_title="VeriLedger | Founder Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.founder_dashboard_view import render_founder_workspace

# Render dedicated, self-contained Founder Dashboard
render_founder_workspace()
