"""
VeriLedger / Kizuna-Vault (Track OPEN-PS-01)
Standalone Demo Control & Master System Reset Cockpit Page.
"""

import streamlit as st

st.set_page_config(
    page_title="VeriLedger | Demo Admin & System Reset",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

from frontend.demo_admin_view import render_demo_admin_cockpit

render_demo_admin_cockpit()
