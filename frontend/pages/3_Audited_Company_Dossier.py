"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Audited Company Dossier.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.
"""

import streamlit as st

st.set_page_config(
    page_title="VeriLedger | Audited Company Dossier",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.dossier_view import render_dossier_cockpit

# Render dedicated, self-contained Audited Company Dossier
render_dossier_cockpit()
