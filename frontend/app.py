"""
VeriLedger / Kizuna-Vault (絆) — Cross-Border Startup Diligence Cockpit.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.

Strictly adheres to Institutional Anti-AI-Slop & Boardroom Standard:
- Pure White Institutional foundation (#FFFFFF) with crisp 1px slate boundaries (#E2E8F0, #CBD5E1)
- Alternative Obsidian Dark Terminal mode (#090D16, #111827)
- Monospace tabular numerals (JetBrains Mono)
- Authentic Japanese Cinnabar Vermilion (#B33927) Hanko seal rails
- Zero emojis, zero purple mesh gradients, zero unreadable glassmorphism

The 3-State Interactive Architecture:
- State 0: Pre-Access Gatekeeper & Portfolio Landing (Sovereign DPI badges, Merkle anchor, Passcode unlock, Data Room Hub, Simulator)
- State 1: Live Ingestion & Sub-200ms Telemetry Trace (Parallel microservice execution)
- State 2: Master Diligence Cockpit (Executive KPIs, 4-Way Reconciliation, Discrepancy Waterfall, Benford Curve, Hanko Rail, Red Flags, RBAC, Simulator, Source Inspector)
"""

import os
import json
import time
import hashlib
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from backend.main import full_audit, load_startup_bundle
from backend.schemas import AuditRequest
from backend.forensic_rules import ForensicAuditEngine, normalize_gst_dataframe, build_merkle_root
from export.memo_generator import generate_ringi_sho_pdf
from export.certificate_generator import generate_section_65b_certificate_pdf
from export.pack_bundler import build_audit_pack_zip_bytes
from frontend.styles import apply_styles
from frontend.i18n import t, format_currency, format_dual_currency_pair, FX_INR_TO_JPY
from frontend.components import (
    render_header,
    render_dpi_rail_badges,
    render_merkle_anchor,
    render_anonymized_teaser,
    render_telemetry_trace,
    render_kpi_card,
    render_trust_score_gauge,
    render_reconciliation_chart,
    render_benford_chart,
    render_discrepancy_waterfall,
    render_diligence_sankey_flow,
    render_hanko_rail,
    render_sovereign_triangulation_matrix,
    render_governance_signoff_matrix,
    render_redline_table,
    render_workflow_stepper,
    render_mca_entity_card,
    render_audited_bank_ledger,
    render_audited_gst_register,
    render_audited_trial_balance,
    render_public_case_studies,
    render_data_room_sealed_card,
)
from backend.registry_lookup import lookup_mca_entity, get_all_quick_fill_options, get_public_case_studies
from frontend.diligence_client import (
    fetch_backend_diligence_state,
    dispatch_backend_request,
    approve_backend_request,
    link_backend_rail,
    switch_backend_preset,
    reset_backend_demo,
    sync_session_from_backend
)

# -------------------------------------------------------------
# 1. Streamlit Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="VeriLedger (絆) | Diligence Engine",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. Session State Initialization
# -------------------------------------------------------------
if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = "light"

if 'page_state' not in st.session_state:
    init_view = str(st.query_params.get("view", "gatekeeper")).lower()
    st.session_state['page_state'] = init_view if init_view in ["gatekeeper", "investor", "founder", "founder_dashboard", "telemetry", "cockpit", "demo_admin", "demo_reset", "admin", "reset"] else "gatekeeper"

if 'active_cin' not in st.session_state:
    st.session_state['active_cin'] = "U72900KA2023PTC178921"

if 'cin_entity_data' not in st.session_state:
    st.session_state['cin_entity_data'] = lookup_mca_entity(st.session_state['active_cin'])

if 'consent_request' not in st.session_state:
    st.session_state['consent_request'] = {
        "status": "DISPATCHED",
        "handle": "REQ-KIZUNA-2026-APEX-0914",
        "requestor": "Value Create Inc. (Tokyo) & JETRO India Startup Desk",
        "officer": "Demo Persona — Tanaka Hiroshi (demo@kizuna-vault.example.com)",
        "purpose": "Track OPEN-PS-01 Bilateral Series A Diligence Mandate",
        "scopes": [
            "RBI Account Aggregator Banking Ledger (ReBIT DEPOSIT v2.0)",
            "GSTN Sovereign Invoicing & Tax Returns (GSTR-1 & GSTR-3B)",
            "MCA-21 Master Director & Charges Registry",
            "CA Certified Trial Balance & Vendor Debtor Aging"
        ],
        "validity": "14 Days (DPDP Act 2023 §6 Mandate)",
        "timestamp": "2026-10-24 14:30:00"
    }

if 'aa_bank_linked' not in st.session_state:
    st.session_state['aa_bank_linked'] = False

if 'gstin_tax_linked' not in st.session_state:
    st.session_state['gstin_tax_linked'] = False

if 'mca_books_linked' not in st.session_state:
    st.session_state['mca_books_linked'] = False

if 'active_preset' not in st.session_state:
    st.session_state['active_preset'] = st.query_params.get("preset", "clean_startup")

if 'currency_mode' not in st.session_state:
    st.session_state['currency_mode'] = "INR"

if 'lang_mode' not in st.session_state:
    st.session_state['lang_mode'] = "EN"

if 'is_authenticated' not in st.session_state:
    st.session_state['is_authenticated'] = False

if 'custom_audit_data' not in st.session_state:
    st.session_state['custom_audit_data'] = None

if 'custom_raw_bundle' not in st.session_state:
    st.session_state['custom_raw_bundle'] = None

if 'investor_tokens' not in st.session_state:
    st.session_state['investor_tokens'] = [
        {
            "investor": "Value Create Inc. (Tokyo)",
            "tier": "Tier A: Full Diligence & Unredacted Ledgers",
            "granted_on": "2026-10-20",
            "expires_on": "2026-11-03 (10 days)",
            "status": "ACTIVE",
            "token": "tok_vc901_tokyo"
        },
        {
            "investor": "JETRO India Startup Desk",
            "tier": "Tier A: Full Diligence & Unredacted Ledgers",
            "granted_on": "2026-10-22",
            "expires_on": "2026-11-05 (12 days)",
            "status": "ACTIVE",
            "token": "tok_jetro_delhi"
        },
        {
            "investor": "SoftBank Vision Fund (Tokyo Desk)",
            "tier": "Tier B: Redacted Diligence (Balances Masked)",
            "granted_on": "2026-10-24",
            "expires_on": "2026-11-07 (14 days)",
            "status": "ACTIVE",
            "token": "tok_softbank_asia"
        }
    ]

if 'aa_consent_active' not in st.session_state:
    st.session_state['aa_consent_active'] = True

if 'clarification_history' not in st.session_state:
    st.session_state['clarification_history'] = []

# Synchronize latest shared state across all dashboards
sync_session_from_backend()

# Sync query params if passed directly
view_param = st.query_params.get("view", "").lower()
if view_param in ["investor", "gatekeeper"]:
    st.session_state['page_state'] = 'gatekeeper'
elif view_param in ["founder", "founder_dashboard"]:
    st.session_state['page_state'] = 'founder_dashboard'
elif view_param in ["cockpit", "dossier"]:
    st.session_state['page_state'] = 'cockpit'
elif view_param in ["telemetry"]:
    st.session_state['page_state'] = 'telemetry'
elif view_param in ["demo", "demo_admin", "demo_reset", "admin", "reset"]:
    st.session_state['page_state'] = 'demo_admin'

if "preset" in st.query_params:
    qp_preset = st.query_params["preset"]
    if st.session_state.get('_last_qp_preset') != qp_preset:
        st.session_state['active_preset'] = qp_preset
        st.session_state['_last_qp_preset'] = qp_preset
        st.session_state['custom_audit_data'] = None

theme_mode = st.session_state['theme_mode']
curr = st.session_state['currency_mode']
lang = st.session_state['lang_mode']
is_jp = lang.upper() in ["JP", "JA"]

txt_pri = "#F8FAFC" if theme_mode == "dark" else "#0F172A"
txt_sec = "#CBD5E1" if theme_mode == "dark" else "#334155"
card_bg = "#111827" if theme_mode == "dark" else "#FFFFFF"
card_border = "#1E293B" if theme_mode == "dark" else "#CBD5E1"
sub_bg = "#090D16" if theme_mode == "dark" else "#F8FAFC"

# Apply institutional CSS (Obsidian / Pure White)
apply_styles(theme=theme_mode)


# =============================================================
# STATE 0: PRE-ACCESS GATEKEEPER & PORTFOLIO LANDING
# =============================================================
if st.session_state['page_state'] == 'gatekeeper':
    # Top Navigation & Brand Header
    render_header(currency=curr, lang=lang, theme_mode=theme_mode)

    # Header Control Bar for Theme, Currency & Language
    c_bar1, c_bar2, c_bar3, c_bar4 = st.columns([4, 2, 2, 2])
    with c_bar2:
        theme_lbl = t("theme_toggle_dark", lang) if theme_mode == "light" else t("theme_toggle_light", lang)
        if st.button(theme_lbl, key="landing_theme_toggle", use_container_width=True):
            st.session_state['theme_mode'] = "dark" if theme_mode == "light" else "light"
            st.rerun()
    with c_bar3:
        curr_lbl = t("currency_toggle_jpy", lang) if curr == "INR" else t("currency_toggle_inr", lang)
        if st.button(curr_lbl, key="landing_curr_toggle", use_container_width=True):
            st.session_state['currency_mode'] = "JPY" if curr == "INR" else "INR"
            st.rerun()
    with c_bar4:
        lang_lbl = t("lang_toggle_jp", lang) if lang == "EN" else t("lang_toggle_en", lang)
        if st.button(lang_lbl, key="landing_lang_toggle", use_container_width=True):
            st.session_state['lang_mode'] = "JP" if lang == "EN" else "EN"
            st.rerun()

    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Compute pipeline step
    is_appr = st.session_state['consent_request'].get("status") == "APPROVED"
    is_linked = (
        st.session_state.get('aa_bank_linked', False) and
        st.session_state.get('gstin_tax_linked', False) and
        st.session_state.get('mca_books_linked', False)
    )
    st_num = 4 if (is_appr and is_linked) else (3 if is_appr else 2)
    render_workflow_stepper(current_step=st_num, lang=lang, theme=theme_mode)

    # Sovereign Digital Public Infrastructure (DPI) Badges
    render_dpi_rail_badges(lang=lang, theme=theme_mode)

    # Cryptographic Merkle Root Anchor Banner
    render_merkle_anchor(
        merkle_root="0x8f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a",
        lang=lang,
        theme=theme_mode
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Pre-Access Split: Anonymized Teaser & Passcode Unlock Handshake
    col_teaser, col_handshake = st.columns([1.1, 0.9])

    with col_teaser:
        teaser_payload = {
            "operating_vintage_years": 3.5,
            "sector": "Enterprise Cloud Infrastructure & Logistics (B2B SaaS)",
            "revenue_tier": "₹10 Cr - ₹50 Cr ($1.2M - $6M ARR)",
            "verified_accounts": "1 Corporate Current Account, 2 GST Registrations"
        }
        render_anonymized_teaser(teaser_payload, lang=lang, theme=theme_mode)

    with col_handshake:
        st.markdown(
            f"""
            <div class="card" style="padding: 18px 20px; height: 100%;">
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px;">
                    [GATEKEEPER] {t('gatekeeper_title', lang)}
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; margin-bottom: 12px; line-height: 1.4;">
                    {t('gatekeeper_subtitle', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        passcode_input = st.text_input(
            label=t("passcode_label", lang),
            value="TRUSTVAULT-VC901-TJH",
            help=t("passcode_help", lang),
            key="input_passcode"
        )

        c_mail, c_role = st.columns(2)
        with c_mail:
            investor_email = st.text_input(
                label=t("investor_email_label", lang),
                value="tanaka.hiroshi@demo.example.com",
                key="input_investor_email"
            )
        with c_role:
            investor_role = st.text_input(
                label=t("investor_role_label", lang),
                value="Lead Diligence Director (Tokyo)",
                key="input_investor_role"
            )

        col_btn1, col_btn2 = st.columns([1.8, 1.2])
        with col_btn1:
            if st.button(t("btn_unlock_dossier", lang), key="btn_unlock", type="primary", use_container_width=True):
                valid_passcodes = ["TRUSTVAULT-VC901-TJH", "KIZUNA-TOKYO-VC901-TJH", "TOKYO-VC-901"]
                passcode_clean = passcode_input.strip().upper()
                allowed_domains = ["example.com", "demo.example.com", "kizuna-vault.example.com", "value-create.com", "jetro.go.jp", "softbank", "nomura"]
                is_whitelisted_email = any(d in investor_email.lower() for d in allowed_domains)
                if passcode_clean in valid_passcodes or is_whitelisted_email:
                    chosen_p = st.session_state.get('gatekeeper_enterprise_dropdown') or st.session_state.get('active_preset', 'clean_startup')
                    c_stat = st.session_state.get('consent_request', {}).get('status', 'DISPATCHED')
                    rails = st.session_state.get('linked_rails', {})
                    is_rails_ok = all(rails.values()) if rails else (st.session_state.get('aa_bank_linked', False) and st.session_state.get('gstin_tax_linked', False) and st.session_state.get('mca_books_linked', False))
                    if c_stat != "APPROVED" or not is_rails_ok:
                        st.warning("【開示制限】2023年DPDP法第6条に基づき、創業者による法定開示承認が完了するまでデータルームは施錠されています。創業者ダッシュボードから承認を実行するか、下記のデモ高速承認をご利用ください。" if is_jp else "[DPDP ACT 2023 §6 RESTRICTION] Diligence data room remains sealed until target enterprise founder authorizes the statutory mandate. Authorize via Founder Dashboard or use Fast-Track Demo Authorization below.")
                    else:
                        st.session_state['active_preset'] = chosen_p
                        st.session_state['cockpit_target_selector'] = chosen_p
                        st.session_state['_last_qp_preset'] = chosen_p
                        st.session_state['custom_audit_data'] = None
                        st.session_state['is_authenticated'] = True
                        st.session_state['page_state'] = 'cockpit'
                        st.query_params["view"] = "cockpit"
                        st.query_params["preset"] = chosen_p
                        st.rerun()
                else:
                    st.error("パスコードが無効であるか、未承認のドメインです。認証情報を確認してください。" if is_jp else "Invalid passcode or unauthorized institutional email. Please verify credentials.")

        with col_btn2:
            if st.button(t("btn_quick_fill", lang), key="btn_quickfill", use_container_width=True):
                st.session_state['input_passcode'] = "TRUSTVAULT-VC901-TJH"
                st.session_state['input_investor_email'] = "tanaka.hiroshi@demo.example.com"
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_jump1, col_jump2 = st.columns([3, 1.2])
    with col_jump1:
        st.markdown(
            f"<div style='font-size: 0.74rem; color: {txt_sec}; line-height: 1.5; padding: 4px 0;'>"
            f"<b>{'創業者オンボーディング & 口座連携:' if is_jp else 'Startup Founder Flow:'}</b> "
            f"{'法人番号(CIN)から商業登記を照会し、AA銀行口座・GSTIN連携を実行する場合は創業者ダッシュボードへお進みください。' if is_jp else 'To auto-discover MCA-21 registry, review consent mandates, and link RBI AA & GSTIN, access Founder Dashboard.'}"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_jump2:
        if st.button(t("switch_view_to_founder", lang), key="btn_gate_to_founder", type="secondary", use_container_width=True):
            st.session_state['page_state'] = 'founder_dashboard'
            st.query_params["view"] = "founder_dashboard"
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TARGET ENTERPRISE SELECTION & DILIGENCE CONSENT DISPATCH
    # ---------------------------------------------------------
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="font-size: 0.95rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.02em;">
                {'【審査対象企業選定】デューデリジェンス対象スタートアップの選択' if is_jp else '[TARGET PORTFOLIO SELECTION] Select Enterprise for Due Diligence'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-top: 3px;">
                {'審査対象企業をドロップダウンから選択し、公的登記・確定元帳を即時照会します。' if is_jp else 'Select a target enterprise from the portfolio dropdown or enter an Indian Corporate Identification Number (CIN):'}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    quick_options = get_all_quick_fill_options()
    preset_dict = {opt["preset_key"]: opt for opt in quick_options}

    cur_p = st.session_state.get('active_preset', 'clean_startup')
    if cur_p not in preset_dict:
        cur_p = 'clean_startup'
        st.session_state['active_preset'] = cur_p

    preset_keys = list(preset_dict.keys())
    curr_idx = preset_keys.index(cur_p) if cur_p in preset_keys else 0

    col_sel1, col_sel2 = st.columns([3.5, 1.5])
    with col_sel1:
        selected_preset = st.selectbox(
            label="審査対象スタートアップ (企業選択)" if is_jp else "Target Enterprise Portfolio Selection:",
            options=preset_keys,
            index=curr_idx,
            format_func=lambda k: f"{preset_dict[k]['name_jp'] if is_jp else preset_dict[k]['name']} — {preset_dict[k]['cin']} {preset_dict[k]['badge']}",
            key="gatekeeper_enterprise_dropdown"
        )
    with col_sel2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("対象企業の切替" if is_jp else "Switch Enterprise", key="btn_switch_target", use_container_width=True):
            switch_backend_preset(selected_preset)
            resolved = lookup_mca_entity(preset_dict[selected_preset]['cin'])
            st.session_state['active_preset'] = selected_preset
            st.session_state['active_cin'] = resolved['cin']
            st.session_state['cin_entity_data'] = resolved
            st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{selected_preset[:4].upper()}-0914"
            st.rerun()

    if selected_preset != cur_p:
        switch_backend_preset(selected_preset)
        st.session_state['active_preset'] = selected_preset
        resolved = lookup_mca_entity(preset_dict[selected_preset]['cin'])
        st.session_state['active_cin'] = resolved['cin']
        st.session_state['cin_entity_data'] = resolved
        st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{selected_preset[:4].upper()}-0914"
        st.rerun()

    entity_info = st.session_state.get('cin_entity_data') or lookup_mca_entity(preset_dict[selected_preset]['cin'])
    st.session_state['cin_entity_data'] = entity_info

    # Render Single Selected MCA-21 Corporate Card
    render_mca_entity_card(entity_info, lang=lang, theme=theme_mode)

    # Diligence Consent Mandate Status & Dual Action Buttons
    c_stat = st.session_state['consent_request'].get("status", "DISPATCHED")
    is_approved_by_founder = c_stat == "APPROVED"
    mandate_handle = st.session_state['consent_request'].get('handle', f"REQ-KIZUNA-2026-{selected_preset[:4].upper()}-0914")

    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.82rem; font-weight: 800; color: {txt_pri};">
                    {'法定精査同意ステータス (DPDP Act 2023 §6 Mandate)' if is_jp else 'Statutory Diligence Consent Mandate (DPDP Act 2023 §6)'}
                </span>
                <span class="{'badge-clean' if is_approved_by_founder else 'badge-review'}">
                    {('[PASS: 創業者承認済]' if is_approved_by_founder else '[STATUS: 同意要請中 / PENDING]') if is_jp else ('[PASS: FOUNDER CONSENT GRANTED]' if is_approved_by_founder else '[STATUS: CONSENT PENDING]')}
                </span>
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.5; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; padding: 10px 14px; border-radius: 4px; border: 1px solid {card_border}; margin-bottom: 12px;">
                <b>{'要請機関' if is_jp else 'Requesting Entity'}:</b> Value Create Inc. (Tokyo) & JETRO India Startup Desk<br/>
                <b>{'担当責任者' if is_jp else 'Lead Officer'}:</b> Demo Persona — Tanaka Hiroshi (demo@kizuna-vault.example.com)<br/>
                <b>{'同意ハンドル' if is_jp else 'Consent Handle'}:</b> <code style="color: #0284C7;">{mandate_handle}</code> • <b>{'要求データ範囲' if is_jp else 'Requested Rails'}:</b> RBI AA Bank Ledger, GSTN Invoices, MCA-21 Books
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        dispatch_label = "開示同意要請を再送 (Re-Dispatch Request)" if is_approved_by_founder else t("btn_dispatch_consent", lang)
        if st.button(dispatch_label, key="btn_gate_dispatch", type="secondary" if is_approved_by_founder else "primary", use_container_width=True):
            # Pure local state update — no backend dependency for demo reliability
            st.session_state['consent_request']['status'] = "DISPATCHED"
            st.session_state['consent_request']['handle'] = mandate_handle
            st.toast("創業者ダッシュボードへDPDP法定同意リクエストを送信しました。" if is_jp else "Diligence consent request dispatched to Founder Dashboard under DPDP Act 2023!")
            st.rerun()

    with act_col2:
        btn_open_dossier_lbl = "【専用査定ページを開く】個別企業監査レポートへ" if is_jp else "[OPEN DEDICATED AUDIT DOSSIER] View Company Reports"
        if is_approved_by_founder:
            if st.button(btn_open_dossier_lbl, key="btn_open_dedicated_dossier", type="primary", use_container_width=True):
                st.session_state['active_preset'] = selected_preset
                st.session_state['cockpit_target_selector'] = selected_preset
                st.session_state['_last_qp_preset'] = selected_preset
                st.session_state['custom_audit_data'] = None
                st.session_state['is_authenticated'] = True
                st.session_state['page_state'] = 'cockpit'
                st.query_params["view"] = "cockpit"
                st.query_params["preset"] = selected_preset
                st.rerun()
        else:
            disabled_lbl = "【データルーム施錠中】創業者承認待ち (DPDP Act §6)" if is_jp else "[CONSENT PENDING] Awaiting Founder Sign-off"
            st.button(disabled_lbl, key="btn_open_dossier_disabled", disabled=True, use_container_width=True)

    if not is_approved_by_founder:
        fast_track_col1, fast_track_col2 = st.columns([2.8, 2.2])
        with fast_track_col1:
            st.markdown(
                f"<div style='font-size: 0.74rem; color: #D97706; padding: 6px 0;'>"
                f"{'対象企業が未承認のためレポートは施錠されています。審査用デモ高速承認を行うか、創業者ポータルから承認してください。' if is_jp else 'Target enterprise consent is pending statutory sign-off. Use Fast-Track Demo Authorization or approve via Founder Dashboard.'}"
                f"</div>",
                unsafe_allow_html=True
            )
        with fast_track_col2:
            if st.button("【デモ高速承認】即時開錠してレポート閲覧" if is_jp else "[FAST-TRACK DEMO] Authorize & Unlock Dossier", key="btn_gate_fast_track_app", type="secondary", use_container_width=True):
                first_dir = entity_info.get('directors', [{}])[0].get('name', 'Corporate Signatory')
                first_din = entity_info.get('directors', [{}])[0].get('din', '00000000')
                approve_backend_request(signatory=f"{first_dir} (DIN: {first_din})")
                link_backend_rail("all", True)
                st.session_state['consent_request']['status'] = "APPROVED"
                st.session_state['aa_bank_linked'] = True
                st.session_state['gstin_tax_linked'] = True
                st.session_state['mca_books_linked'] = True
                st.session_state['demo_bypass_unlocked'] = True
                st.session_state['active_preset'] = selected_preset
                st.session_state['cockpit_target_selector'] = selected_preset
                st.session_state['_last_qp_preset'] = selected_preset
                st.session_state['custom_audit_data'] = None
                st.session_state['is_authenticated'] = True
                st.session_state['page_state'] = 'cockpit'
                st.query_params["view"] = "cockpit"
                st.query_params["preset"] = selected_preset
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    with st.expander("任意CIN法人番号の直接検索 または 独自データルームのアップロード" if is_jp else "Custom CIN Direct Registry Lookup or Private Data Room Upload", expanded=False):
        c_cin1, c_cin2 = st.columns([3, 1])
        with c_cin1:
            custom_cin_in = st.text_input(
                label="任意の21桁 CIN 法人番号:" if is_jp else "Enter any 21-digit Indian CIN Number:",
                value=st.session_state.get('active_cin', 'U72900KA2023PTC178921'),
                key="custom_cin_input_field"
            )
        with c_cin2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("登記照会実行" if is_jp else "Lookup CIN", key="btn_do_custom_cin", use_container_width=True):
                res_cin = lookup_mca_entity(custom_cin_in)
                st.session_state['active_cin'] = res_cin['cin']
                st.session_state['cin_entity_data'] = res_cin
                st.session_state['active_preset'] = res_cin['preset_key']
                st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    render_public_case_studies(lang=lang, theme=theme_mode, show_actions=True)

elif st.session_state['page_state'] == 'founder_dashboard':
    from frontend.founder_dashboard_view import render_founder_workspace
    render_founder_workspace()

elif st.session_state['page_state'] == 'demo_admin':
    from frontend.demo_admin_view import render_demo_admin_cockpit
    render_demo_admin_cockpit()

elif st.session_state['page_state'] == 'telemetry':
    render_header(currency=curr, lang=lang, theme_mode=theme_mode)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="font-size: 1.1rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
            [TELEMETRY] {t('telemetry_title', lang)}
        </div>
        <div style="font-size: 0.78rem; color: {txt_sec}; margin-bottom: 14px;">
            {t('telemetry_subtitle', lang)}
        </div>
        """,
        unsafe_allow_html=True
    )

    cur_p = st.session_state.get('active_preset', 'clean_startup')
    if cur_p == 'fraud_startup':
        target_name = "PhantomTech Solutions Private Limited (CIN: U74999DL2024PTC389102)"
        claims_detail = "ピッチ資料の主張数値を抽出 (主張ARR: ₹2.55 Cr | 月次燃焼額: ₹25L | 主張ランウェイ: 18ヶ月)" if is_jp else "Extracted Pitch Deck claims (Claimed ARR: ₹2.55 Cr | Burn: ₹25L/mo | Claimed Runway: 18 Mo)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 57.8%の架空売上乖離を検知" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 57.8% Phantom Revenue Gap detected"
        rp_detail = "取引先9社のPAN番号を照合; 取締役 Rajesh Sharma (PAN: ABCPS1234F) と一致! 会社法第188条 資金流出" if is_jp else "Sliced 9 Vendor PANs; Matched Director Rajesh Sharma (PAN: ABCPS1234F)! Section 188 Siphoning"
        benford_detail = "先頭2桁 (F2D) 出現頻度解析: ₹19.5Lおよび₹49.5Kに異常構造化を検知 (Nigrini MAD: 0.0051)" if is_jp else "First-Two-Digit distribution indicates structuring anomaly at ₹19.5L and ₹49.5K (Nigrini MAD: 0.0051)"
        bridge_detail = "重大指摘 Shinrai スコアカード生成 (18/100 【精査要】) および東京投資審査稟議書を作成" if is_jp else "Synthesized Critical Red-Flag Shinrai Scorecard (18/100 【精査要】) & Tokyo Ringi-sho Circular"
    elif cur_p == 'logipulse_startup':
        target_name = "LogiPulse Express Logistics Private Limited (CIN: U63090MH2022PTC345678)"
        claims_detail = "ピッチ資料の主張数値を抽出 (ARR: ₹3.10 Cr | 燃焼額: ₹28L/月 | 主張ランウェイ: 12ヶ月)" if is_jp else "Extracted Pitch Deck claims (ARR: ₹3.10 Cr | Burn: ₹28L/mo | Claimed Runway: 12 Mo)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 37.1%の売掛金回収遅延を検知" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 37.1% Debtors Collection Lag"
        rp_detail = "取引先14社のPAN番号を照合; MCA取締役インデックスとの直接利益相反ゼロ" if is_jp else "Sliced 14 Vendor PANs; 0 direct conflict matches with MCA Director index"
        benford_detail = "出金トランザクションの先頭2桁分布は許容範囲内 (Nigrini MAD: 0.0032)" if is_jp else "First-Two-Digit disbursements evaluate within acceptable limits (Nigrini MAD: 0.0032)"
        bridge_detail = "条件付審議 Shinrai スコアカード生成 (68/100 【要確認】) — 滞留不良売掛金を指摘" if is_jp else "Synthesized Conditional Review Scorecard (68/100 【要確認】) — Stale Doubtful Receivables flagged"
    elif cur_p == 'mirai_startup':
        target_name = "Mirai Mobility Robotics Private Limited (CIN: U29100TN2023PTC456789)"
        claims_detail = "ピッチ資料の主張数値を抽出 (ARR: ₹4.20 Cr | ハードウェアランウェイ: 18.5ヶ月 | 人員: 28名)" if is_jp else "Extracted Pitch Deck claims (ARR: ₹4.20 Cr | Hardware Runway: 18.5 Mo | Team: 28)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 99.5%の高い一致率を確認" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 99.5% Concordance Verified"
        rp_detail = "取引先18社のPAN番号を照合; 取締役利益相反ゼロ、適格日印ロボティクス合弁" if is_jp else "Sliced 18 Vendor PANs; 0 Promoter Conflicts; Compliant Indo-Japan Robotics JV"
        benford_detail = "出金分布は対数自然分布に完全適合 (Nigrini MAD: 0.0022)" if is_jp else "Conforming First-Two-Digit log10 distribution across disbursements (Nigrini MAD: 0.0022)"
        bridge_detail = "無修正適正 Shinrai スコアカード生成 (96/100 【適格】) および東京投資承認レール作成" if is_jp else "Synthesized Unqualified Clean Scorecard (96/100 【適格】) & Tokyo Boardroom Approval Rail"
    elif cur_p == 'edutrek_startup':
        target_name = "Edutrek Learning Technologies Private Limited (CIN: U80903KA2021PTC156789)"
        claims_detail = "ピッチ資料の主張数値を抽出 (主張ARR: ₹45.0 Cr | 月次燃焼額: ₹1.85 Cr | 主張ランウェイ: 24ヶ月)" if is_jp else "Extracted Pitch Deck claims (Claimed ARR: ₹45.0 Cr | Burn: ₹1.85 Cr/mo | Claimed Runway: 24 Mo)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 70.2%の未回収架空売上・Rule 88C DRC-01B乖離を検知" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 70.2% Uncollected Phantom Revenue & Rule 88C DRC-01B Gap"
        rp_detail = "取引先14社のPAN番号を照合; 架空回収未達・SA 505 外部残高不一致" if is_jp else "Sliced 14 Vendor PANs; Unconfirmed Phantom Debtors & ICAI SA 505 External Confirmation Failures"
        benford_detail = "先頭2桁 (F2D) 出現頻度解析: ₹18.0L〜₹24.0Lに不自然な売上請求スパイクを検知 (Nigrini MAD: 0.0039)" if is_jp else "First-Two-Digit distribution indicates revenue clustering at ₹18.0L-₹24.0L (Nigrini MAD: 0.0039)"
        bridge_detail = "重大指摘 Shinrai スコアカード生成 (22/100 【精査要】) — 架空売掛金・Rule 88C税務通知を警告" if is_jp else "Synthesized Critical Red-Flag Shinrai Scorecard (22/100 【精査要】) — Phantom Receivables & Rule 88C Tax Notice"
    elif cur_p == 'kwikpay_startup':
        target_name = "KwikPay Digital Networks Private Limited (CIN: U72900DL2022PTC384512)"
        claims_detail = "ピッチ資料の主張数値を抽出 (ARR: ₹36.0 Cr | 燃焼額: ₹48L/月 | 主張ランウェイ: 15ヶ月)" if is_jp else "Extracted Pitch Deck claims (ARR: ₹36.0 Cr | Burn: ₹48L/mo | Claimed Runway: 15 Mo)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 41.7%の月末コントラ相殺・売上膨張乖離を検知" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 41.7% Contra Round-Tripping & Gross Inflation Gap"
        rp_detail = "取引先PAN照合; 取締役配偶者 Madhuri Mehra (PAN: AMMPM3456F) へ ₹58.5L流出 (会社法第188条違反)" if is_jp else "Matched Director Relative Madhuri Mehra (PAN: AMMPM3456F); ₹58.5L Siphoning (Companies Act Sec 188 Violation)"
        benford_detail = "先頭2桁 (F2D) 出現頻度解析: Sec 194C/J TDS基準直下 (₹28.5K, ₹49.5K) にスマーフィング検知 (Nigrini MAD: 0.0062)" if is_jp else "First-Two-Digit analysis reveals TDS threshold smurfing below Sec 194C/J limits (Nigrini MAD: 0.0062)"
        bridge_detail = "重大指摘 Shinrai スコアカード生成 (15/100 【精査要】) — 創業者利益相反・不正TDS分割を告発" if is_jp else "Synthesized Critical Red-Flag Shinrai Scorecard (15/100 【精査要】) — Promoter Conflict & TDS Smurfing Indictment"
    elif cur_p == 'autocare_startup':
        target_name = "AutoCare Network India Private Limited (CIN: U50400DL2021PTC378901)"
        claims_detail = "ピッチ資料の主張数値を抽出 (主張ARR: ₹180.0 Cr | 月次燃焼額: ₹4.20 Cr | 主張ランウェイ: 14ヶ月)" if is_jp else "Extracted Pitch Deck claims (Claimed ARR: ₹180.0 Cr | Burn: ₹4.20 Cr/mo | Claimed Runway: 14 Mo)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 78.9%の架空ガレージ売上・第269ST条 現金受取乖離を検知" if is_jp else "Reconciled Cleared Cash vs GST Invoices — 78.9% Phantom Garage Billings & Section 269ST Cash Gaps"
        rp_detail = "取引先PAN照合; 取締役実質支配の Oberoi Spares (PAN: AAQPO9876C) へ ₹45.0L 不正部品仕入資金流出" if is_jp else "Matched Siphoned Entity Oberoi Spares (PAN: AAQPO9876C); ₹45.0L Siphoning (Companies Act Sec 188 Violation)"
        benford_detail = "先頭2桁 (F2D) 出現頻度解析: 第269ST条/40A(3)上限直下 (₹1.80L〜₹1.95L) に異常現金分割検知 (Nigrini MAD: 0.0075)" if is_jp else "First-Two-Digit analysis reveals cash limit evasion below Sec 269ST/40A(3) limits (Nigrini MAD: 0.0075)"
        bridge_detail = "重大指摘 Shinrai スコアカード生成 (10/100 【精査要】) — 架空ガレージ・第269ST条現金違反・監査意見不表明を警告" if is_jp else "Synthesized Critical Red-Flag Shinrai Scorecard (10/100 【精査要】) — Fictitious Garages & Sec 269ST Violations"
    elif cur_p == 'zenith_startup':
        target_name = "Zenith BioHealth Solutions Private Limited (CIN: U85110MH2023PTC398765)"
        claims_detail = "ピッチ資料の主張数値を抽出 (ARR: ₹12.5 Cr | 臨床バーン: ₹38L/月 | ランウェイ: 20ヶ月 | 人員: 36名)" if is_jp else "Extracted Pitch Deck claims (ARR: ₹12.5 Cr | Clinical Burn: ₹38L/mo | Runway: 20 Mo | Team: 36)"
        inflow_detail = "確定入金 vs GST申告売上の突合 — 76日DSO (国公立・私立病院の正常支払サイクル、未回収リスク軽微)" if is_jp else "Reconciled Cash vs GST Invoices — 76-Day Hospital DSO (Normal Institutional Cycle, Low Bad Debt Risk)"
        rp_detail = "取引先32社のPAN番号を照合; 医療機関・CRO正規契約、取締役利益相反ゼロ" if is_jp else "Sliced 32 Vendor PANs; Institutional Hospital/CRO Contracts, 0 Director Conflicts"
        benford_detail = "出金全件の先頭2桁対数分布を算出 (Nigrini MAD: 0.0029 - 適合)" if is_jp else "First-Two-Digit distribution conforms to Benford's Law (Nigrini MAD: 0.0029 - Conforming)"
        bridge_detail = "条件付適格 Shinrai スコアカード生成 (78/100 【要確認】) — 臨床拡大に向けた東京投資承認レール作成" if is_jp else "Synthesized Qualified Review Scorecard (78/100 【要確認】) — Tokyo Boardroom Clinical Approval Rail"
    elif cur_p == 'custom_upload' and st.session_state.get('custom_audit_data'):
        c_res = st.session_state['custom_audit_data']
        target_name = f"{c_res.get('company_name', 'Custom Enterprise')} (CIN: {c_res.get('cin', 'N/A')})"
        claims_detail = f"{'ピッチ主張売上を抽出' if is_jp else 'Extracted Pitch Deck claims'} (ARR: {format_currency(c_res['kpis'].get('claimed_arr_inr', 0), curr, lang)})"
        inflow_detail = f"{'確定入金 vs GST申告売上を突合' if is_jp else 'Reconciled Cash vs GST Invoices'} ({'乖離率' if is_jp else 'Divergence'}: {c_res['kpis'].get('cash_divergence_pct', 0)}%)"
        rp_detail = f"{'取引先PAN番号を照合; 流出指摘額' if is_jp else 'Sliced Vendor PANs; Siphoned exposure'}: {format_currency(c_res['kpis'].get('siphoned_funds_inr', 0), curr, lang)}"
        benford_detail = f"{'先頭2桁(F2D)分布を検証' if is_jp else 'Evaluated F2D distribution'} (Nigrini MAD: {c_res['kpis'].get('benford_nigrini_mad', 0.0028):.4f})"
        bridge_detail = f"{'Shinrai スコアカードを生成' if is_jp else 'Synthesized Shinrai Scorecard'} ({c_res['kpis'].get('governance_trust_score', 0)}/100 {c_res['kpis'].get('kanji_badge', '')})"
    else:
        target_name = "Apex AI Labs Private Limited (CIN: U72900KA2023PTC178921)"
        claims_detail = "ピッチ資料の主張数値を抽出 (ARR: ₹2.55 Cr | 燃焼額: ₹22L/月 | ランウェイ: 18ヶ月 | 人員: 32名)" if is_jp else "Extracted Pitch Deck claims (ARR: ₹2.55 Cr | Burn: ₹22L/mo | Runway: 18 Mo | Headcount: 32)"
        inflow_detail = "確定入金 vs GST申告課税売上高の突合 (100%完全一致を検証)" if is_jp else "Reconciled Cleared Cash vs GST Invoiced Turnover (100% concordance verified)"
        rp_detail = "GSTIN[2:12]から取引先48社のPANを抽出; MCA-21取締役DINインデックスと照合 (利益相反ゼロ)" if is_jp else "Sliced 48 Vendor PANs from GSTIN[2:12]; matched against MCA-21 Director DIN index (0 Conflicts)"
        benford_detail = "出金全件の先頭2桁対数分布を算出 (Nigrini MAD: 0.0028 - 適合)" if is_jp else "Calculated First-Two-Digit logarithmic distribution across disbursements (Nigrini MAD: 0.0028 - Conforming)"
        bridge_detail = "適格 Shinrai スコアカード生成 (94/100 【適格】) および東京投資審査稟議書を作成" if is_jp else "Synthesized Clean Shinrai Scorecard (94/100 【適格】) & Tokyo Ringi-sho Circular"

    if st.session_state.get('cin_entity_data'):
        c_ent = st.session_state['cin_entity_data']
        if c_ent.get('preset_key') == cur_p or c_ent.get('cin') == st.session_state.get('active_cin'):
            target_name = f"{c_ent.get('company_name')} (CIN: {c_ent.get('cin')})"

    st.markdown(
        f'<div style="font-size: 0.82rem; font-weight: 700; color: #38BDF8; font-family: monospace; margin-bottom: 8px;">'
        f"<b>{'精査対象パイプライン' if is_jp else 'TARGET AUDIT PIPELINE'}:</b> {target_name}"
        f'</div>',
        unsafe_allow_html=True
    )

    telemetry_steps = [
        {
            "service": "PyMuPDF + Gemini 2.5 Flash",
            "detail": claims_detail,
            "status": "PASS",
            "latency_ms": 18.4
        },
        {
            "service": "Pandas Sovereign Ingestor",
            "detail": "公的ReBIT銀行明細およびGSTインボイスを高速インメモリテンソルへ格納" if is_jp else "Ingested sovereign ReBIT Bank rows & GST Invoices into high-performance in-memory tensor",
            "status": "PASS",
            "latency_ms": 24.1
        },
        {
            "service": "/api/v1/forensic/inflow-match",
            "detail": inflow_detail,
            "status": "PASS" if "100%" in inflow_detail or "99.5%" in inflow_detail else "FLAG",
            "latency_ms": 28.6
        },
        {
            "service": "/api/v1/forensic/related-party",
            "detail": rp_detail,
            "status": "FLAG" if "Siphoning" in rp_detail or "Alert" in rp_detail or "資金流出" in rp_detail else "PASS",
            "latency_ms": 19.8
        },
        {
            "service": "/api/v1/forensic/benford-mad",
            "detail": benford_detail,
            "status": "FLAG" if "anomaly" in benford_detail or "異常" in benford_detail else "PASS",
            "latency_ms": 31.2
        },
        {
            "service": "Tokyo Bridge Diligence Engine",
            "detail": bridge_detail,
            "status": "PASS",
            "latency_ms": 22.5
        }
    ]

    total_latency = sum(s["latency_ms"] for s in telemetry_steps)
    render_telemetry_trace(telemetry_steps, total_latency, lang=lang)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c_tel1, c_tel2, c_tel3 = st.columns([2, 4, 2])
    with c_tel2:
        if st.button(t("btn_proceed_cockpit", lang), key="btn_go_cockpit", type="primary", use_container_width=True):
            st.session_state['page_state'] = 'cockpit'
            st.query_params["view"] = "cockpit"
            st.rerun()


# =============================================================
# STATE 2: MASTER FORENSIC DILIGENCE COCKPIT
# =============================================================
elif st.session_state['page_state'] == 'cockpit':
    # Top Navigation & Brand Header
    render_header(currency=curr, lang=lang, theme_mode=theme_mode)
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Execute Audit or Use Custom Data
    if 'cockpit_target_selector' in st.session_state and st.session_state['cockpit_target_selector']:
        preset_key = st.session_state['cockpit_target_selector']
        st.session_state['active_preset'] = preset_key
    else:
        preset_key = st.session_state.get('active_preset', 'clean_startup')

    if preset_key == 'custom_upload' and st.session_state.get('custom_audit_data') is not None:
        audit_data = st.session_state['custom_audit_data']
    else:
        st.session_state['custom_audit_data'] = None
        req = AuditRequest(preset_key=preset_key)
        audit_data = full_audit(req)

    # Ensure correct corporate entity details for the selected preset
    if preset_key != "custom_upload":
        p_ent = lookup_mca_entity(preset_key)
        if p_ent:
            audit_data['company_name'] = p_ent.get('company_name', audit_data.get('company_name'))
            audit_data['cin'] = p_ent.get('cin', audit_data.get('cin'))
            audit_data['entity_details'] = p_ent
    elif st.session_state.get('cin_entity_data'):
        c_ent = st.session_state['cin_entity_data']
        audit_data['company_name'] = c_ent.get('company_name', audit_data.get('company_name'))
        audit_data['cin'] = c_ent.get('cin', audit_data.get('cin'))

    kpis = audit_data['kpis']
    score = kpis['governance_trust_score']
    kanji_badge = kpis.get('kanji_badge', '【適格】')
    is_clean = score >= 80
    is_review = 60 <= score < 80
    is_danger = score < 60

    if is_clean:
        verdict_badge_text = "【適格】INVESTMENT GRADE" if not is_jp else "【投資適格】審査合格"
        verdict_pill_class = "badge-clean"
        score_status_msg = "Safe: High Governance, 100% Tax Compliant" if not is_jp else "安全: 高ガバナンス・法令遵守・投資適格"
        benchmark_badge = "TOP 10% (LOW RISK)" if not is_jp else "上位10% (優良)"
    elif is_review:
        verdict_badge_text = "【要精査】DILIGENCE REVIEW" if not is_jp else "【要精査】条件付審議"
        verdict_pill_class = "badge-review"
        score_status_msg = "Caution: Working Capital Drag / Slow Collections" if not is_jp else "注意: 売掛金滞留・要改善モニタリング"
        benchmark_badge = "MEDIAN 50% (CAUTION)" if not is_jp else "中位50% (注意)"
    else:
        verdict_badge_text = "【否認】CRITICAL RED FLAGS" if not is_jp else "【投資不可】重大不正検知"
        verdict_pill_class = "badge-danger"
        score_status_msg = "Severe Risk: Structural Phantom Revenue / Fund Leakage" if not is_jp else "危険警告: 架空売上・創業者不正流出を検知"
        benchmark_badge = "BOTTOM 5% (HIGH RISK)" if not is_jp else "下位5% (危険)"

    # Top Cockpit Toolbar
    nav1, nav2, nav3, nav4, nav5, nav6 = st.columns([1.5, 4.2, 1.5, 1.4, 1.5, 1.4])

    with nav1:
        if st.button("← Gateway" if not is_jp else "← ポータル", key="btn_back_landing", type="secondary", use_container_width=True):
            st.session_state['page_state'] = 'gatekeeper'
            st.query_params["view"] = "gatekeeper"
            st.rerun()

    with nav2:
        preset_options = {
            "clean_startup": "Apex AI Labs (適格SaaS / クリーン)" if is_jp else "Apex AI Labs (Clean SaaS)",
            "fraud_startup": "PhantomTech (不正レッドフラグ)" if is_jp else "PhantomTech (Forensic Red Flags)",
            "logipulse_startup": "LogiPulse (運転資本滞留 / 経営難)" if is_jp else "LogiPulse (Working Capital Drag)",
            "mirai_startup": "Mirai Mobility (日印共同事業 / 適格)" if is_jp else "Mirai Mobility (Clean Joint Venture)",
            "edutrek_startup": "Edutrek Learning (過大売上 / Rule 88C)" if is_jp else "Edutrek Learning (Aggressive Revenue / Rule 88C)",
            "kwikpay_startup": "KwikPay Digital (創業者流出 / TDS分割)" if is_jp else "KwikPay Digital (Sec 188 Siphoning / TDS Smurfing)",
            "autocare_startup": "AutoCare Network (架空ガレージ / 第269ST条)" if is_jp else "AutoCare Network (Fictitious Network / Sec 269ST)",
            "zenith_startup": "Zenith BioHealth (医療Tech / 審査合格)" if is_jp else "Zenith BioHealth (MedTech Series A / Qualified)"
        }
        if preset_key == "custom_upload":
            preset_options["custom_upload"] = f"{'カスタム:' if is_jp else 'Custom:'} {audit_data.get('company_name', 'Uploaded Data Room')[:20]}"

        current_idx = list(preset_options.keys()).index(preset_key) if preset_key in preset_options else 0

        def on_cockpit_target_change():
            chosen = st.session_state.get('cockpit_target_selector')
            # Only act when a real distinct preset is chosen; ignore lang-toggle reruns
            if chosen and chosen != st.session_state.get('_last_qp_preset'):
                st.session_state['active_preset'] = chosen
                st.session_state['_last_qp_preset'] = chosen
                st.session_state['custom_audit_data'] = None
                st.session_state['demo_bypass_unlocked'] = False
                st.query_params["preset"] = chosen
                try:
                    switch_backend_preset(chosen)
                except Exception:
                    pass  # Backend optional — demo runs fully offline

        st.selectbox(
            label="審査対象企業" if is_jp else "Target Enterprise",
            options=list(preset_options.keys()),
            format_func=lambda k: preset_options[k],
            index=current_idx,
            label_visibility="collapsed",
            key="cockpit_target_selector",
            on_change=on_cockpit_target_change
        )

    with nav3:
        theme_lbl = "Light Mode" if theme_mode == "dark" else "Dark Mode"
        if st.button(theme_lbl, key="cockpit_theme_toggle", use_container_width=True):
            st.session_state['theme_mode'] = "dark" if theme_mode == "light" else "light"
            st.rerun()

    with nav4:
        curr_lbl = "¥ JPY" if curr == "INR" else "₹ INR"
        if st.button(curr_lbl, key="cockpit_curr_toggle", use_container_width=True):
            st.session_state['currency_mode'] = "JPY" if curr == "INR" else "INR"
            st.rerun()

    with nav5:
        lang_lbl = "日本語" if lang == "EN" else "English"
        if st.button(lang_lbl, key="cockpit_lang_toggle", use_container_width=True):
            st.session_state['lang_mode'] = "JP" if lang == "EN" else "EN"
            st.rerun()

    with nav6:
        if st.button("↻ Re-Audit" if not is_jp else "↻ 再精査", key="btn_reaudit", type="primary", use_container_width=True):
            st.rerun()

    # DPDP Act 2023 §6 Statutory Gatekeeper Enforcement
    c_req = st.session_state.get('consent_request', {})
    c_stat = c_req.get("status", "DISPATCHED")
    rails = st.session_state.get('linked_rails', {})
    is_all_linked = all(rails.values()) if rails else (st.session_state.get('aa_bank_linked', False) and st.session_state.get('gstin_tax_linked', False) and st.session_state.get('mca_books_linked', False))
    is_sealed_ok = (c_stat == "APPROVED") and is_all_linked
    is_bypassed = st.session_state.get('demo_bypass_unlocked', False)

    if not is_sealed_ok and not is_bypassed:
        ent_info = audit_data.get('entity_details', {}) or lookup_mca_entity(preset_key)
        render_data_room_sealed_card(
            entity_data=ent_info,
            consent_request=c_req,
            linked_rails=rails,
            lang=lang,
            theme=theme_mode
        )
        c_gate1, c_gate2, c_gate3 = st.columns([1.5, 2.5, 1.5])
        with c_gate1:
            if st.button("← 投資家ポータルへ戻る" if is_jp else "← Return to Gatekeeper", key="btn_sealed_to_gate_app", use_container_width=True):
                st.session_state['page_state'] = 'gatekeeper'
                st.query_params["view"] = "gatekeeper"
                st.rerun()
        with c_gate2:
            if st.button("【デモ高速開錠】創業者承認 & 全公的レール即時連携" if is_jp else "[FAST-TRACK DEMO] Grant Founder Approval & Link Rails", key="btn_sealed_fast_track_app", type="primary", use_container_width=True):
                first_dir = ent_info.get('directors', [{}])[0].get('name', 'Corporate Signatory')
                first_din = ent_info.get('directors', [{}])[0].get('din', '00000000')
                approve_backend_request(signatory=f"{first_dir} (DIN: {first_din})")
                link_backend_rail("all", True)
                st.session_state['consent_request']['status'] = "APPROVED"
                st.session_state['aa_bank_linked'] = True
                st.session_state['gstin_tax_linked'] = True
                st.session_state['mca_books_linked'] = True
                st.session_state['demo_bypass_unlocked'] = True
                st.toast("創業者承認が完了し、全公的データレールが開錠されました。" if is_jp else "Founder consent authorized and sovereign DPI data rails unlocked!")
                st.rerun()
        with c_gate3:
            if st.button("創業者ダッシュボードへ →" if is_jp else "Switch to Founder Dashboard →", key="btn_sealed_to_founder_app", type="secondary", use_container_width=True):
                st.session_state['page_state'] = 'founder_dashboard'
                st.query_params["view"] = "founder_dashboard"
                st.rerun()
        st.stop()

    # Target Status & Cryptographic Anchor Ribbon Card
    badge_style = "badge-clean" if is_clean else ("badge-review" if is_review else "badge-danger")
    merkle_root_disp = kpis.get('merkle_root', '0x8f3a1b2c4d5e')
    if len(merkle_root_disp) > 28:
        merkle_root_disp = merkle_root_disp[:26] + "..."

    ent_info = audit_data.get('entity_details', {})
    roc_display = ent_info.get('roc_office', 'ROC Bangalore')
    vintage_display = f"{ent_info.get('vintage_years', '3.5')} Yrs"

    verdict_text = (
        "投資適格・コンプライアンス適合 (Clean Investable)"
        if is_clean and is_jp
        else ("精査要・重大リスク検知 (Critical Diligence Alert)" if is_danger and is_jp else kpis['verdict'])
    )

    st.markdown(
        f"""
        <div class="card" style="margin-top: 4px; margin-bottom: 12px; padding: 14px 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        <span style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.02em;">
                            {audit_data['company_name']}
                        </span>
                        <span class="{verdict_pill_class}" style="font-size: 0.76rem; padding: 3px 10px;">
                            {verdict_badge_text}
                        </span>
                    </div>
                    <div style="font-size: 0.72rem; color: {txt_sec}; font-family: 'JetBrains Mono', monospace; margin-top: 4px;">
                        CIN: <span style="color: #38BDF8; font-weight: 700;">{audit_data['cin']}</span> • {roc_display} • Vintage: {vintage_display} • Primary Rail: ReBIT DEPOSIT v2.0
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span class="badge-mono" title="Immutable SHA-256 Merkle root across all sovereign data snapshots">
                        MERKLE: <code>{merkle_root_disp}</code>
                    </span>
                    <span class="{badge_style}">
                        CA OPINION: [{audit_data.get('ca_audit_opinion', 'UNQUALIFIED')}]
                    </span>
                    <span class="badge-clean">
                        [4 SOVEREIGN RAILS SYNCED]
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4 Executive KPI Banners (Balanced 4 Columns)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        score_clr = "#059669" if is_clean else ("#D97706" if is_review else "#B33927")
        filled_blocks = min(10, max(0, int(round(score / 10.0))))
        empty_blocks = 10 - filled_blocks
        bar_html = f"<div style='display: flex; gap: 2px; margin-top: 6px; margin-bottom: 4px;'>" + \
                   "".join([f"<div style='height: 5px; flex: 1; background: {score_clr}; border-radius: 1px;'></div>" for _ in range(filled_blocks)]) + \
                   "".join([f"<div style='height: 5px; flex: 1; background: {'#E2E8F0' if theme_mode == 'light' else '#334155'}; border-radius: 1px;'></div>" for _ in range(empty_blocks)]) + \
                   f"</div>"

        render_kpi_card(
            title="GOVERNANCE TRUST SCORE" if not is_jp else "総合ガバナンス信頼スコア",
            value=f"<font color='{score_clr}'>{score}</font> <span style='font-size: 0.95rem; color: {txt_sec};'>/ 100</span>" + bar_html,
            subtitle=score_status_msg,
            badge_text=benchmark_badge,
            badge_type="clean" if is_clean else ("review" if is_review else "danger"),
            desc=t("kpi_shinrai_desc", lang)
        )

    with kpi_col2:
        div_pct = kpis['cash_divergence_pct']
        realization_pct = max(0.0, round(100.0 - div_pct, 1))
        cash_clr = "#059669" if div_pct < 10 else "#B33927"
        phantom_gap = kpis.get('phantom_revenue_inr', 0)
        gap_str = format_currency(phantom_gap, currency_mode=curr, lang_mode=lang)
        real_cash_str = format_currency(kpis['real_bank_credits_inr'], currency_mode=curr, lang_mode=lang)

        cash_sub = (
            f"Phantom Gap: -{gap_str} ({div_pct}% uncollected / fake sales)" if div_pct > 0
            else f"100% Cash Matched: {real_cash_str} verified via RBI AA"
        ) if not is_jp else (
            f"架空乖離額: -{gap_str} ({div_pct}% 未入金・架空懸念)" if div_pct > 0
            else f"100% 入金一致: {real_cash_str} (公的銀行着金済)"
        )

        render_kpi_card(
            title="CASH INFLOW REALIZATION" if not is_jp else "実入金売上回収率 (突合)",
            value=f"<font color='{cash_clr}'>{realization_pct}%</font>",
            subtitle=cash_sub,
            badge_text=f"{div_pct}% UNCOLLECTED" if div_pct > 0 else "100% VERIFIED",
            badge_type="danger" if div_pct > 0 else "clean",
            desc=t("kpi_realization_desc", lang)
        )

    with kpi_col3:
        true_rw = kpis['true_runway_months']
        claimed_rw = kpis['claimed_runway_months']
        rw_clr = "#059669" if true_rw >= 12 else ("#D97706" if true_rw >= 6 else "#B33927")
        tax_dues_str = format_currency(kpis.get('unremitted_tax_dues_inr', 0), currency_mode=curr, lang_mode=lang)

        rw_sub = (
            f"Claimed: {claimed_rw} Mo • Unremitted Tax Dues: {tax_dues_str}" if not is_jp
            else f"自称: {claimed_rw}ヶ月 • 滞納税金債務: {tax_dues_str}"
        )

        render_kpi_card(
            title="AUDITED SURVIVAL RUNWAY" if not is_jp else "実質資金残存月数 (公的控除後)",
            value=f"<font color='{rw_clr}'>{true_rw}</font> <span style='font-size: 0.95rem; color: {txt_sec};'>Months</span>" if not is_jp else f"<font color='{rw_clr}'>{true_rw}</font> <span style='font-size: 0.95rem; color: {txt_sec};'>ヶ月</span>",
            subtitle=rw_sub,
            badge_text=f"{true_rw} MO TRUE RUNWAY",
            badge_type="clean" if true_rw >= 12 else "danger",
            desc=t("kpi_runway_desc", lang)
        )

    with kpi_col4:
        siphoned = kpis.get('siphoned_funds_inr', 0)
        has_siphon = siphoned > 0
        siphon_str = format_currency(siphoned, currency_mode=curr, lang_mode=lang)

        if has_siphon:
            fraud_title = "PROMOTER FUND LEAKAGE" if not is_jp else "創業者・関連当事者 不正流出"
            fraud_val = f"<font color='#B33927'>[LEAK DETECTED]</font>" if not is_jp else f"<font color='#B33927'>[不正流出検知]</font>"
            fraud_sub = f"Sec 188 Promoter Loans: {siphon_str} diverted to personal accounts" if not is_jp else f"会社法第188条違反: 役員関係先へ {siphon_str} 迂回融資"
            fraud_badge = "CRITICAL VIOLATION"
            fraud_badge_type = "danger"
        elif kpis.get('phantom_revenue_inr', 0) > 0 and div_pct >= 20:
            fraud_title = "STATUTORY INVOICE INTEGRITY" if not is_jp else "法定売上・申告整合性"
            fraud_val = f"<font color='#B33927'>[RULE 88C NOTICE]</font>" if not is_jp else f"<font color='#B33927'>[Rule 88C 違反指摘]</font>"
            fraud_sub = f"GSTR-1 to GSTR-3B variance exceeds 20% statutory threshold" if not is_jp else f"GSTR-1と3Bの申告乖離が法定基準(20%)を超過"
            fraud_badge = "TAX AUDIT RISK"
            fraud_badge_type = "danger"
        elif score < 60:
            fraud_title = "FORENSIC INTEGRITY ALERTS" if not is_jp else "フォレンジック異常警告"
            fraud_val = f"<font color='#D97706'>[ANOMALY FLAGGED]</font>" if not is_jp else f"<font color='#D97706'>[異常値検知]</font>"
            fraud_sub = f"Benford Law F2D distribution & round-sum smurfing detected" if not is_jp else f"ベンフォード則第2桁歪みおよび端数分割送金を検知"
            fraud_badge = "DEEP AUDIT REQUIRED"
            fraud_badge_type = "review"
        else:
            fraud_title = "FORENSIC INTEGRITY AUDIT" if not is_jp else "フォレンジック健全性判定"
            fraud_val = f"<font color='#059669'>[0 LEAKS / CLEAN]</font>" if not is_jp else f"<font color='#059669'>[流出ゼロ / 適合]</font>"
            fraud_sub = f"Zero siphoning, 100% verified genuine commercial counterparties" if not is_jp else f"不正迂回流出ゼロ・全取引先の実在性を確認済"
            fraud_badge = "100% LEGITIMATE"
            fraud_badge_type = "clean"

        render_kpi_card(
            title=fraud_title,
            value=fraud_val,
            subtitle=fraud_sub,
            badge_text=fraud_badge,
            badge_type=fraud_badge_type,
            desc=t("kpi_conflict_desc", lang)
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Load raw sovereign datasets for accountant inspection
    target_key = preset_key
    if st.session_state.get('custom_raw_bundle') is not None and (target_key == "custom_upload" or "simulated" in target_key or target_key == "sandbox_mutated"):
        rebit_raw, gst_raw, dir_raw, claims_raw, ca_raw = st.session_state['custom_raw_bundle']
    else:
        load_key = "clean_startup" if target_key in ["custom_upload", "simulated_scenario", "sandbox_mutated"] else target_key
        rebit_raw, gst_raw, dir_raw, claims_raw, ca_raw = load_startup_bundle(load_key)

    # Robust transaction extraction
    acc_dict = rebit_raw.get('account') or rebit_raw.get('Account') or {}
    txns_dict = acc_dict.get('transactions') or acc_dict.get('Transactions') or {}
    txns_list = txns_dict.get('transaction') or txns_dict.get('Transaction') or []
    if isinstance(txns_list, dict):
        txns_list = [txns_list]

    # Master Diligence Cockpit Tabs - 7 Structured Accountant Reports (Concise labels to prevent overflow)
    report_labels = [
        "1. 投資審査要約" if is_jp else "1. Executive Memo",
        "2. 確定預金 (RBI AA)" if is_jp else "2. Bank Ledger (AA)",
        "3. 電子インボイス (GSTN)" if is_jp else "3. Tax Portal (GSTN)",
        "4. CA公認試算表" if is_jp else "4. CA Trial Balance",
        "5. 法定違反・不正指摘" if is_jp else "5. Statutory Red Flags",
        "6. 4層突合分析" if is_jp else "6. Reconciliation & Charts",
        "7. 開示権限・検証環境" if is_jp else "7. Governance Sandbox"
    ]

    tab_ringisho, tab_bank, tab_gst, tab_ca, tab_redflags, tab_analytics, tab_rbac = st.tabs(report_labels)

    # ---------------------------------------------------------
    # REPORT 1: TOKYO BOARDROOM RINGI-SHO & PDF EXPORT
    # ---------------------------------------------------------
    with tab_ringisho:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RINGI-SHO MEMO] {t('ringisho_title', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 12px;">
                {t('ringisho_desc', lang)}
            </div>
            """,
            unsafe_allow_html=True
        )

        ringi_card_title = "【投資審査稟議書】  案件番号: TJH-2026-VC01" if is_jp else "[INVESTMENT DILIGENCE RINGI-SHO]  File Ref: TJH-2026-VC01"
        ringi_meta = (
            "作成日: 2026年10月24日 | 審査機関: 株式会社バリュークリエイト (Value Create Inc. Tokyo)"
            if is_jp
            else "Generated: October 24, 2026 | Reviewing Body: Value Create Inc. (Tokyo) × JETRO Rail"
        )
        l_target = "1. 対象企業名:" if is_jp else "1. Target Enterprise:"
        l_cin = "2. 企業識別番号 (CIN):" if is_jp else "2. Corporate CIN:"
        l_verdict = "3. 総合判定:" if is_jp else "3. Overall Verdict:"
        l_score = "4. 信頼スコア:" if is_jp else "4. Trust Score:"
        l_cash = "5. 実入金確認売上:" if is_jp else "5. Verified Cleared Cash:"
        l_rw = "6. 資金残存月数:" if is_jp else "6. Survival Runway:"
        rw_suffix = f"{kpis['true_runway_months']} ヶ月 (公的債務控除後)" if is_jp else f"{kpis['true_runway_months']} Months (Post-Statutory Deductions)"
        l_merkle = "SHA-256 原簿アンカー:" if is_jp else "SHA-256 Merkle Anchor:"
        verdict_badge_text = kanji_badge if is_jp else ("[APPROVED]" if is_clean else ("[HIGH RISK]" if is_danger else "[REVIEW]"))

        st.markdown(
            f"""
            <div style="background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 18px 22px; margin-bottom: 14px;">
                <div style="text-align: center; border-bottom: 1px solid {card_border}; padding-bottom: 10px; margin-bottom: 12px;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.05em;">
                        {ringi_card_title}
                    </div>
                    <div style="font-size: 0.72rem; color: #64748B;">
                        {ringi_meta}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.75rem; color: {txt_sec}; margin-bottom: 12px;">
                    <div>
                        <b>{l_target}</b> {audit_data['company_name']}<br/>
                        <b>{l_cin}</b> <code>{audit_data['cin']}</code><br/>
                        <b>{l_verdict}</b> <span class="{badge_style}"><b>{verdict_badge_text} ({verdict_text})</b></span>
                    </div>
                    <div>
                        <b>{l_score}</b> <span style="font-size: 1rem; font-weight: 800; color: {score_clr}; font-family: monospace;">{score} / 100</span><br/>
                        <b>{l_cash}</b> {format_currency(kpis['real_bank_credits_inr'], currency_mode=curr, lang_mode=lang)}<br/>
                        <b>{l_rw}</b> {rw_suffix}
                    </div>
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; border: 1px solid {card_border}; border-radius: 4px; padding: 8px 12px; margin-bottom: 10px;">
                    <b>{l_merkle}</b> <code>{kpis.get('merkle_root', '0x8f3a1b2c4d5e')}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 4-Way Sovereign Triangulation Matrix
        render_sovereign_triangulation_matrix(
            audit_data=audit_data,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode
        )

        # Corporate Governance Diligence Sign-Off Matrix
        render_governance_signoff_matrix(
            stages=audit_data.get('hanko_stages', []),
            lang=lang,
            theme=theme_mode,
            allow_actions=True,
            preset_key=preset_key
        )

        pdf_filename = f"{preset_key}_ringi_sho_memo.pdf"
        pdf_path = os.path.join("export", pdf_filename)
        try:
            generate_ringi_sho_pdf(audit_data, pdf_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
        except Exception as e:
            pdf_bytes = b""
            st.error(f"Error generating PDF dossier: {str(e)}")

        cert_filename = f"{preset_key}_section_65b_certificate.pdf"
        cert_path = os.path.join("export", cert_filename)
        try:
            generate_section_65b_certificate_pdf(audit_data, cert_path)
            with open(cert_path, "rb") as f:
                cert_bytes = f.read()
        except Exception:
            cert_bytes = b""

        try:
            zip_bytes = build_audit_pack_zip_bytes(audit_data, preset_key)
        except Exception:
            zip_bytes = b""

        st.markdown(
            f"<div style='font-size: 0.74rem; color: #64748B; margin-bottom: 8px;'>"
            f"{'公式監査調書には、二国間通貨財務表、第188条違反指摘、機関投資家ガバナンス承認マトリクス、第65条B項電子証拠適格証明書、および暗号マークル原簿アンカーが正式収録されています。' if is_jp else 'The generated statutory audit pack includes dual-currency financials, statutory redlines, governance sign-off matrix, Section 65B Electronic Evidence certificate, and SHA-256 Merkle anchor.'}"
            f"</div>",
            unsafe_allow_html=True
        )

        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            if pdf_bytes:
                st.download_button(
                    label="[PDF] 東京投資委員会 稟議書" if is_jp else "[PDF] Tokyo Ringi-sho Dossier",
                    data=pdf_bytes,
                    file_name=f"Tokyo_Ringi_Sho_{audit_data['cin']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                    key="btn_dl_ringisho_pdf"
                )
        with col_dl2:
            if cert_bytes:
                st.download_button(
                    label="[PDF] 第65B条 電子証拠証明書" if is_jp else "[PDF] Section 65B Certificate",
                    data=cert_bytes,
                    file_name=f"Sec65B_Certificate_{audit_data['cin']}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="secondary",
                    key="btn_dl_sec65b_pdf"
                )
        with col_dl3:
            if zip_bytes:
                st.download_button(
                    label="[ZIP] 公的監査パック全一式" if is_jp else "[ZIP] Sovereign Audit Pack",
                    data=zip_bytes,
                    file_name=f"Sovereign_Audit_Pack_{audit_data['cin']}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="secondary",
                    key="btn_dl_audit_pack_zip"
                )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        with st.expander("実在公開企業・東京投資家ベンチマーク判例照合 (SoftBank Tokyo & Big-4 Audit Precedents)" if is_jp else "Real-World Corporate Precedents & SoftBank Tokyo Diligence Benchmarks", expanded=False):
            render_public_case_studies(lang=lang, theme=theme_mode, show_actions=True)

    # ---------------------------------------------------------
    # REPORT 2: AUDITED BANK STATEMENT & GENERAL LEDGER
    # ---------------------------------------------------------
    with tab_bank:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [BANK STATEMENT] {'公的確定預金元帳 (RBI Account Aggregator 照合済)' if is_jp else 'Audited Bank Statement & Cash Inflows/Outflows'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'公的銀行API (ReBIT DEPOSIT v2.0) 経由で取得された全明細。入金 (Cash In) と 出金 (Cash Out) を明確に分離して表示:' if is_jp else 'Direct statutory banking feed via RBI Account Aggregator protocol (ReBIT DEPOSIT v2.0). Itemizes Cash In vs Cash Out with exact posting dates:'}
            </div>
            """,
            unsafe_allow_html=True
        )

        c_flt1, c_flt2, c_flt3 = st.columns([2, 1.2, 1.0])
        with c_flt1:
            bank_search = st.text_input("取引内容・相手先・勘定科目・理由を検索:" if is_jp else "Search narration, counterparty, account head, or reason:", key="bank_search_box")
        with c_flt2:
            filter_opts = ["全取引 (ALL)", "確定入金のみ (CASH IN)", "確定出金のみ (CASH OUT)", "要精査・異常値のみ (FLAGGED)"] if is_jp else ["ALL", "CASH IN", "CASH OUT", "FLAGGED"]
            selected_filter_str = st.selectbox("取引抽出フィルター:" if is_jp else "Transaction Type Filter:", filter_opts, key="bank_filter_sel")
            if "CASH IN" in selected_filter_str or "入金" in selected_filter_str:
                active_filter = "CREDIT"
            elif "CASH OUT" in selected_filter_str or "出金" in selected_filter_str:
                active_filter = "DEBIT"
            elif "FLAGGED" in selected_filter_str or "要精査" in selected_filter_str:
                active_filter = "FLAGGED"
            else:
                active_filter = "ALL"
        with c_flt3:
            limit_opts = ["100件", "250件", "500件", "全件表示 (ALL)"] if is_jp else ["100 Rows", "250 Rows", "500 Rows", "ALL Rows"]
            selected_limit_str = st.selectbox("表示件数:" if is_jp else "Display Limit:", limit_opts, key="bank_limit_sel")
            if "250" in selected_limit_str:
                active_limit = 250
            elif "500" in selected_limit_str:
                active_limit = 500
            elif "ALL" in selected_limit_str or "全件" in selected_limit_str:
                active_limit = 0
            else:
                active_limit = 100

        render_audited_bank_ledger(
            transactions=txns_list,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode,
            search_term=bank_search,
            type_filter=active_filter,
            row_limit=active_limit
        )

    # ---------------------------------------------------------
    # REPORT 3: SOVEREIGN ELECTRONIC INVOICES (GSTN)
    # ---------------------------------------------------------
    with tab_gst:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [GSTN INVOICE REGISTER] {'政府電子納税申告原本 (GSTR-1 & GSTR-3B 電子インボイス原本)' if is_jp else 'Sovereign Electronic Invoicing Register (GSTR-1 & GSTR-3B)'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'財政省 CBIC / NIC 電子インボイスポータルに登録された正規請求書原本およびGSTR-3B納税相殺状況:' if is_jp else 'Verified outward and inward electronic invoices registered on CBIC / NIC portal with GSTR-3B tax offset status:'}
            </div>
            """,
            unsafe_allow_html=True
        )

        cg_flt1, cg_flt2 = st.columns([2, 1.0])
        with cg_flt1:
            gst_search = st.text_input("インボイス番号・相手先・GSTIN・勘定科目を検索:" if is_jp else "Search invoice number, client, GSTIN, or account head:", key="gst_search_box")
        with cg_flt2:
            gst_limit_opts = ["60件", "150件", "全件表示 (ALL)"] if is_jp else ["60 Invoices", "150 Invoices", "ALL Invoices"]
            sel_gst_limit = st.selectbox("インボイス表示件数:" if is_jp else "Invoice Limit:", gst_limit_opts, key="gst_limit_sel")
            active_gst_limit = 0 if ("ALL" in sel_gst_limit or "全件" in sel_gst_limit) else (150 if "150" in sel_gst_limit else 60)

        render_audited_gst_register(
            gst_df=gst_raw,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode,
            search_term=gst_search,
            row_limit=active_gst_limit
        )

    # ---------------------------------------------------------
    # REPORT 4: CHARTERED ACCOUNTANT TRIAL BALANCE & AR AGING
    # ---------------------------------------------------------
    with tab_ca:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [CA TRIAL BALANCE] {'公認会計士 (CA) 監査証明済 試算表 & 売掛金減損スケジュール' if is_jp else 'Chartered Accountant Certified Trial Balance & Ind AS 109 AR Aging'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'インド公認会計士協会 (ICAI) SA 240 / SA 505 基準に基づく試算表およびInd AS 109 Expected Credit Loss減損引当スケジュール:' if is_jp else 'Audited general ledger trial balance and Ind AS 109 3-stage Expected Credit Loss (ECL) debtor aging schedule:'}
            </div>
            """,
            unsafe_allow_html=True
        )
        render_audited_trial_balance(
            ca_books=ca_raw,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode
        )

    # ---------------------------------------------------------
    # REPORT 5: ITEMIZED STATUTORY RED FLAGS & VIOLATIONS
    # ---------------------------------------------------------
    with tab_redflags:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RED FLAGS] {t('tab_redflags', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 12px;">
                {'インド会社法第188条 (関連当事者取引)、所得税法第269ST条/第194C/J条、およびCGST規則に基づく詳細指摘事項:' if is_jp else 'Itemized discrepancy registry evaluated against Companies Act 2013, Income Tax Act 1961, CGST Rules 2017, and ICAI Standards on Auditing:'}
            </div>
            """,
            unsafe_allow_html=True
        )

        # CA Statutory Decision Console: 4 Critical Pillars
        liquidity_data = audit_data.get('liquidity_contingency') or {}
        bad_debt_data = audit_data.get('bad_debt_provisioning') or {}
        solvency_data = audit_data.get('solvency_covenants') or {}
        circular_data = audit_data.get('circular_debt') or {}

        if liquidity_data or bad_debt_data or solvency_data or circular_data:
            st.markdown(
                f"<div style='font-size: 0.80rem; font-weight: 800; color: {txt_pri}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>"
                f"{'公認会計士 (CA) 法定判断ツリー & 倒産リスク統制コンソール' if is_jp else 'Chartered Accountant (CA) Statutory Decision Trees & Insolvency Control Console'}"
                f"</div>",
                unsafe_allow_html=True
            )
            ca_col1, ca_col2 = st.columns(2)
            with ca_col1:
                # Dynamic Liquidity
                is_cash_distressed = liquidity_data.get('is_cash_distressed', False)
                l_badge = '<span class="badge-danger">[CRITICAL CASH DISTRESS]</span>' if is_cash_distressed else '<span class="badge-clean">[ADEQUATE CASH BUFFER]</span>'
                l_border = "#B33927" if is_cash_distressed else "#059669"
                l_bg = "rgba(179, 57, 39, 0.08)" if (is_cash_distressed and theme_mode == 'dark') else ("#FEF2F2" if is_cash_distressed else ("rgba(5, 150, 105, 0.08)" if theme_mode == 'dark' else "#ECFDF5"))
                l_dues_inr = liquidity_data.get('total_contingent_statutory_liability_inr', 0.0)
                l_dues_str = format_dual_currency_pair(l_dues_inr, lang_mode=lang)

                st.markdown(
                    f"""
                    <div style="background-color: {l_bg}; border: 1px solid {l_border}; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.78rem; font-weight: 800; color: {txt_pri};">
                                {'1. 動的流動性・法定不履行エスカレーション' if is_jp else '1. Dynamic Liquidity Default Escalation'}
                            </span>
                            {l_badge}
                        </div>
                        <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.45; margin-bottom: 6px;">
                            {'営業CF赤字またはランウェイ3ヶ月未満時に、所得税法第201条(1A)源泉利息、CGST第50条利息、EPFO損害金を自動加算:' if is_jp else 'Cash distress escalates unremitted dues into mandatory Sec 201(1A) 1.5%/mo TDS interest, CGST Sec 50 18% p.a. interest, and EPFO damages:'}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: {txt_pri}; font-family: monospace; background: {card_bg}; padding: 6px 10px; border-radius: 4px; border: 1px solid {card_border};">
                            <span>{'偶発的法定債務総額' if is_jp else 'Total Contingent Dues'}:</span>
                            <span style="font-weight: 800; color: {'#B33927' if is_cash_distressed else '#059669'};">{l_dues_str}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Solvency
                is_ibc_triggered = solvency_data.get('is_ibc_insolvency_triggered', False)
                s_badge = '<span class="badge-danger">[IBC SEC 7/9 CIRP HAZARD]</span>' if is_ibc_triggered else '<span class="badge-clean">[COVENANTS COMPLIANT]</span>'
                s_border = "#B33927" if is_ibc_triggered else "#059669"
                s_bg = "rgba(179, 57, 39, 0.08)" if (is_ibc_triggered and theme_mode == 'dark') else ("#FEF2F2" if is_ibc_triggered else ("rgba(5, 150, 105, 0.08)" if theme_mode == 'dark' else "#ECFDF5"))
                dscr_val = solvency_data.get('dscr', 0.0)
                quick_val = solvency_data.get('quick_ratio', 0.0)
                dscr_txt = "N/A (No Debt)" if dscr_val == 99.0 else f"{dscr_val:.2f}x"

                st.markdown(
                    f"""
                    <div style="background-color: {s_bg}; border: 1px solid {s_border}; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.78rem; font-weight: 800; color: {txt_pri};">
                                {'2. 債務規約 (DSCR) & 倒産リスク指標' if is_jp else '2. Debt Covenants (DSCR) & Solvency Triggers'}
                            </span>
                            {s_badge}
                        </div>
                        <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.45; margin-bottom: 6px;">
                            {'DSCR < 1.25x (債務不履行リスク) および 当座比率 < 0.8x (法定債務未払時の倒産法IBCトリガー):' if is_jp else 'DSCR < 1.25x flags covenant distress; Quick Ratio < 0.8x with pending statutory dues triggers Insolvency & Bankruptcy Code (IBC 2016):'}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: {txt_pri}; font-family: monospace; background: {card_bg}; padding: 6px 10px; border-radius: 4px; border: 1px solid {card_border};">
                            <span>DSCR: <b style="color: {'#B33927' if solvency_data.get('is_dscr_breached') else txt_pri};">{dscr_txt}</b> | {'当座比率' if is_jp else 'Quick Ratio'}: <b style="color: {'#B33927' if quick_val < 0.8 else txt_pri};">{quick_val:.2f}x</b></span>
                            <span style="font-weight: 800; color: {'#B33927' if is_ibc_triggered else '#059669'};">{'NCLT倒産リスク' if is_ibc_triggered else '健全' if is_jp else 'IBC CIRP Risk' if is_ibc_triggered else 'Solvent'}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with ca_col2:
                # Bad Debt Provisioning
                is_writeoff = bad_debt_data.get('is_write_off_triggered', False)
                b_badge = '<span class="badge-danger">[MANDATED ECL HAIRCUT]</span>' if is_writeoff else '<span class="badge-clean">[NORMAL WORKING CAPITAL]</span>'
                b_border = "#B33927" if is_writeoff else "#059669"
                b_bg = "rgba(179, 57, 39, 0.08)" if (is_writeoff and theme_mode == 'dark') else ("#FEF2F2" if is_writeoff else ("rgba(5, 150, 105, 0.08)" if theme_mode == 'dark' else "#ECFDF5"))
                haircut_pct = bad_debt_data.get('valuation_haircut_pct', 0.0)
                stg3_amt = bad_debt_data.get('stage3_credit_impaired_writeoff_inr', 0.0)
                stg3_str = format_dual_currency_pair(stg3_amt, lang_mode=lang)

                st.markdown(
                    f"""
                    <div style="background-color: {b_bg}; border: 1px solid {b_border}; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.78rem; font-weight: 800; color: {txt_pri};">
                                {'3. Ind AS 109 不良売掛金引当 & 評価減' if is_jp else '3. Ind AS 109 Bad Debt Provision & Valuation Haircut'}
                            </span>
                            {b_badge}
                        </div>
                        <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.45; margin-bottom: 6px;">
                            {'CCC > 60日 かつ DSO > 75日の回収不能時、90日超売掛金を100%損失処理し企業評価額を強制減額:' if is_jp else 'CCC > 60d and DSO > 75d indicate collection breakdown; mandates 100% Stage 3 write-off and valuation discount:'}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: {txt_pri}; font-family: monospace; background: {card_bg}; padding: 6px 10px; border-radius: 4px; border: 1px solid {card_border};">
                            <span>Stage 3: <b style="color: {'#B33927' if is_writeoff else txt_pri};">{stg3_str}</b></span>
                            <span style="font-weight: 800; color: {'#B33927' if is_writeoff else '#059669'};">{'評価減' if is_jp else 'Haircut'}: -{haircut_pct:.1f}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Circular Debt
                has_circular = circular_data.get('has_circular_debt', False)
                c_badge = '<span class="badge-danger">[CIRCULAR FINANCING LOOP]</span>' if has_circular else '<span class="badge-clean">[CLEAN EQUITY STRUCTURE]</span>'
                c_border = "#B33927" if has_circular else "#059669"
                c_bg = "rgba(179, 57, 39, 0.08)" if (has_circular and theme_mode == 'dark') else ("#FEF2F2" if has_circular else ("rgba(5, 150, 105, 0.08)" if theme_mode == 'dark' else "#ECFDF5"))
                circ_amt = circular_data.get('total_circular_amount_inr', 0.0)
                circ_str = format_dual_currency_pair(circ_amt, lang_mode=lang)

                st.markdown(
                    f"""
                    <div style="background-color: {c_bg}; border: 1px solid {c_border}; border-radius: 6px; padding: 12px 14px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-size: 0.78rem; font-weight: 800; color: {txt_pri};">
                                {'4. 循環融資 & 経営者借入ラウンドトリップ' if is_jp else '4. Circular Debt & Loan Round-Tripping'}
                            </span>
                            {c_badge}
                        </div>
                        <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.45; margin-bottom: 6px;">
                            {'プロモーター融資を会社口座に入金し架空売上を偽装後、ベンダー経費として還流させるループを検知 (会社法第185条):' if is_jp else 'Detects multi-hop loops: promoter loan credited -> routed to fake customer sales -> siphoned as vendor expense (Sec 185):'}
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: {txt_pri}; font-family: monospace; background: {card_bg}; padding: 6px 10px; border-radius: 4px; border: 1px solid {card_border};">
                            <span>{'循環金額' if is_jp else 'Round-Tripped Amt'}:</span>
                            <span style="font-weight: 800; color: {'#B33927' if has_circular else '#059669'};">{circ_str}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        discrepancies = audit_data.get('discrepancies_detail') or audit_data.get('discrepancies', [])
        if not discrepancies:
            clean_hdr = "[適格性確認済 ガバナンス合致]" if is_jp else "[CLEAN GOVERNANCE CONCORDANCE]"
            clean_desc = '指摘事項ゼロ。全取引は独立第三者間取引であり、ベンフォード異常値や税務未納は検知されませんでした。' if is_jp else 'Zero statutory violations detected. All transactions reflect arms-length commercial operations, Benford Nigrini MAD is within acceptable bounds, and tax payments match outward billing.'
            st.markdown(
                f"""
                <div style="background-color: {'rgba(5, 150, 105, 0.12)' if theme_mode == 'dark' else '#ECFDF5'}; border: 1px solid #059669; border-radius: 6px; padding: 18px 20px; color: {'#10B981' if theme_mode == 'dark' else '#059669'};">
                    <b>{clean_hdr}</b> {clean_desc}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for disc in discrepancies:
                is_crit = disc.get('severity') == 'CRITICAL'
                border_clr = "#B33927" if is_crit else "#D97706"
                bg_clr = "rgba(179, 57, 39, 0.15)" if (is_crit and theme_mode == 'dark') else ("#FEF2F2" if is_crit else ("rgba(217, 119, 6, 0.15)" if theme_mode == 'dark' else "#FFFBEB"))
                badge_style_d = "badge-danger" if is_crit else "badge-review"

                when_d = disc.get('when', {})
                where_d = disc.get('where', {})
                exp_amt = disc.get('amount_inr', 0)
                exp_str = format_dual_currency_pair(exp_amt, lang_mode=lang)

                st.markdown(
                    f"""
                    <div style="background-color: {bg_clr}; border: 1px solid {border_clr}; border-radius: 6px; padding: 16px 18px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                            <div>
                                <span class="{badge_style_d}">[{disc.get('severity')}] {disc.get('discrepancy_id')}</span>
                                <span style="font-size: 0.92rem; font-weight: 800; color: {txt_pri}; margin-left: 8px;">{disc.get('title')}</span>
                            </div>
                            <span style="font-size: 0.90rem; font-weight: 800; color: #B33927; font-family: monospace;">
                                {t('monetary_exposure', lang)}: {exp_str}
                            </span>
                        </div>
                        <div style="font-size: 0.76rem; color: {txt_pri}; line-height: 1.45; margin-bottom: 10px;">
                            <b>{t('what_why_label', lang)}:</b> {disc.get('what_and_why')}
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.72rem; background-color: {card_bg}; border: 1px solid {card_border}; color: {txt_pri}; border-radius: 4px; padding: 10px 14px; margin-bottom: 8px;">
                            <div>
                                <b>{t('when_label', lang)}:</b> {when_d.get('date')} ({when_d.get('time_window')})<br/>
                                <b>{'会計期間' if is_jp else 'FISCAL PERIOD'}:</b> {when_d.get('fiscal_period')}<br/>
                                <b>{'取引先企業' if is_jp else 'COUNTERPARTY'}:</b> {where_d.get('counterparty')}<br/>
                                <b>{'GSTIN / 抽出PAN' if is_jp else 'GSTIN / EXTRACTED PAN'}:</b> <code>{where_d.get('gstin', 'N/A')}</code> / <code style='color:#B33927;'>{where_d.get('extracted_pan', 'N/A')}</code>
                            </div>
                            <div>
                                <b>{'役員利益相反' if is_jp else 'DIRECTOR CONFLICT'}:</b> {where_d.get('matched_director', 'N/A')}<br/>
                                <b>{'勘定科目' if is_jp else 'ACCOUNT HEAD'}:</b> {where_d.get('account_head', 'N/A')}<br/>
                                <b>{'取引 / 請求番号' if is_jp else 'TXN / INVOICE ID'}:</b> <code>{where_d.get('transaction_id', 'N/A')}</code> / <code>{where_d.get('invoice_no', 'N/A')}</code><br/>
                                <b>{t('citation_label', lang)}:</b> {disc.get('statutory_citation')}
                            </div>
                        </div>
                        <div style="font-size: 0.72rem; color: {'#38BDF8' if theme_mode == 'dark' else '#0284C7'}; background-color: {'rgba(2, 132, 199, 0.12)' if theme_mode == 'dark' else '#EFF6FF'}; border: 1px solid {'#0284C7' if theme_mode == 'dark' else '#BFDBFE'}; border-radius: 4px; padding: 6px 12px;">
                            <b>{t('remediation_label', lang)}:</b> {disc.get('tokyo_remediation_action')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;'>"
            f"{'不正疑義取引 ドリルダウン明細表' if is_jp else 'High-Density Forensic Red-Flag Transaction Drilldown Table'}"
            f"</div>",
            unsafe_allow_html=True
        )

        rf_c1, rf_c2 = st.columns([2, 1.0])
        with rf_c1:
            rf_search = st.text_input("指摘事項・相手先・PAN・条文を検索:" if is_jp else "Search red flags, counterparty, PAN, or citation:", key="rf_search_box")
        with rf_c2:
            rf_opts = ["全指摘 (ALL)", "重大指摘のみ (CRITICAL)", "注意指摘のみ (WARNING)"] if is_jp else ["ALL", "CRITICAL", "WARNING"]
            sel_rf_str = st.selectbox("重要度フィルター:" if is_jp else "Severity Filter:", rf_opts, key="rf_sev_sel")
            rf_filter = "CRITICAL" if ("CRITICAL" in sel_rf_str or "重大" in sel_rf_str) else ("WARNING" if ("WARNING" in sel_rf_str or "注意" in sel_rf_str) else "ALL")

        render_redline_table(discrepancies, currency_mode=curr, lang=lang, theme=theme_mode, search_term=rf_search, severity_filter=rf_filter)


    # ---------------------------------------------------------
    # REPORT 6: RECONCILIATION, WATERFALL & ANALYTICS
    # ---------------------------------------------------------
    with tab_analytics:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RECONCILIATION & WATERFALL] {'ピッチ主張、公認会計士試算表、税務申告書 (GSTR-1)、および銀行確定着金の4層突合' if is_jp else 'Multi-Source Financial Reconciliation, Discrepancy Waterfall & Benford Curves'}
            </div>
            """,
            unsafe_allow_html=True
        )

        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            monthly_records = audit_data.get('monthly_reconciliation', [])
            fig_recon = render_reconciliation_chart(monthly_records, currency_mode=curr, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_recon, use_container_width=True)
        with ch2:
            benford_data = audit_data.get('benford_curve', {})
            fig_benford = render_benford_chart(benford_data, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_benford, use_container_width=True)
        with ch3:
            fig_sankey = render_diligence_sankey_flow(audit_data, currency_mode=curr, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_sankey, use_container_width=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        st.markdown(
            f"<div style='font-size:0.80rem; font-weight:800; color:{txt_pri}; margin: 12px 0 4px;'>"
            f"{'乖離流動性カスケード (最重要分析)' if is_jp else 'DISCREPANCY CASCADE — PRIMARY FORENSIC ANALYSIS'}"
            "</div>",
            unsafe_allow_html=True
        )
        fig_wf = render_discrepancy_waterfall(audit_data, currency_mode=curr, lang=lang, theme=theme_mode)
        st.plotly_chart(fig_wf, use_container_width=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        claimed_arr = kpis['claimed_arr_inr']
        ca_rev = kpis.get('ca_booked_revenue_inr', claimed_arr)
        bank_cash = kpis['real_bank_credits_inr']
        gst_total = kpis.get('gst_invoiced_turnover_inr') or audit_data.get('waterfall', {}).get('gst_declared_turnover_inr', ca_rev)

        comp_df = pd.DataFrame([
            {
                t("recon_col_layer", lang): t("recon_layer_1_name", lang),
                t("recon_col_source", lang): t("recon_layer_1_src", lang),
                f"{t('recon_col_turnover', lang)} ({curr})": format_currency(claimed_arr, currency_mode=curr, lang_mode=lang),
                t("recon_col_variance", lang): f"{round(((claimed_arr - bank_cash) / max(1.0, claimed_arr)) * 100, 1)}% {'乖離' if is_jp else 'Delta'}"
            },
            {
                t("recon_col_layer", lang): t("recon_layer_2_name", lang),
                t("recon_col_source", lang): t("recon_layer_2_src", lang),
                f"{t('recon_col_turnover', lang)} ({curr})": format_currency(ca_rev, currency_mode=curr, lang_mode=lang),
                t("recon_col_variance", lang): f"{round(((ca_rev - bank_cash) / max(1.0, ca_rev)) * 100, 1)}% {'帳簿・入金乖離' if is_jp else 'Book-to-Cash Gap'}"
            },
            {
                t("recon_col_layer", lang): t("recon_layer_3_name", lang),
                t("recon_col_source", lang): t("recon_layer_3_src", lang),
                f"{t('recon_col_turnover', lang)} ({curr})": format_currency(gst_total, currency_mode=curr, lang_mode=lang),
                t("recon_col_variance", lang): f"{kpis['cash_divergence_pct']}% {'架空売上乖離' if is_jp else 'Phantom Revenue Gap'}"
            },
            {
                t("recon_col_layer", lang): t("recon_layer_4_name", lang),
                t("recon_col_source", lang): t("recon_layer_4_src", lang),
                f"{t('recon_col_turnover', lang)} ({curr})": format_currency(bank_cash, currency_mode=curr, lang_mode=lang),
                t("recon_col_variance", lang): "0.0% (正真基準値)" if is_jp else "0.0% (Ground Truth Baseline)"
            }
        ])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # ---------------------------------------------------------
    # REPORT 7: PRIVACY, RBAC & INTERACTIVE SANDBOX
    # ---------------------------------------------------------
    with tab_rbac:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [DATA ROOM & RBAC] {t('rbac_title', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 14px;">
                {t('rbac_desc', lang)}
            </div>
            """,
            unsafe_allow_html=True
        )

        r_c1, r_c2, r_c3 = st.columns(3)
        with r_c1:
            st.markdown(
                f"""
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'銀行APIプロトコル (RBI AA)' if is_jp else 'BANKING PROTOCOL (RBI AA)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">HDFC Bank Current A/c</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'同意有効期限: 2026-11-30' if is_jp else 'Consent Valid Till 2026-11-30'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with r_c2:
            st.markdown(
                f"""
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'税務ネットワーク (GSTN GSP)' if is_jp else 'TAX NETWORK (GSTN GSP)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">GSTR-1 / 3B Daily Sync</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'GSP Webhook 接続中' if is_jp else 'Live GSP Webhook Connected'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with r_c3:
            st.markdown(
                f"""
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'企業登記レジストリ (MCA-21)' if is_jp else 'CORPORATE REGISTRY (MCA-21)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">Director DIN & PAN Index</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'MCA-21 API 照合済' if is_jp else 'Direct API Verified Active'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown(
            f"<div style='font-size: 0.78rem; font-weight: 700; color: {txt_sec}; margin-bottom: 8px;'>"
            f"{t('authorized_vcs_title', lang)}"
            f"</div>",
            unsafe_allow_html=True
        )

        for idx, inv in enumerate(st.session_state['investor_tokens']):
            inv_col1, inv_col2, inv_col3, inv_col4 = st.columns([3, 3, 2, 2])
            with inv_col1:
                st.markdown(f"**{inv['investor']}**")
            with inv_col2:
                st.markdown(f"<span class='badge-mono'>{inv['tier']}</span>", unsafe_allow_html=True)
            with inv_col3:
                st.markdown(f"<span style='font-size: 0.72rem; color: #64748B;'>{'有効期限:' if is_jp else 'Expires:'} {inv['expires_on']}</span>", unsafe_allow_html=True)
            with inv_col4:
                # Read-only status in investor view — only admin/founder can revoke
                if inv['status'] == "ACTIVE":
                    st.markdown("<span class='badge-clean'>[ACTIVE]</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='badge-danger'>[REVOKED]</span>", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Interactive Ledger Sandbox & Mutation
        st.markdown(
            f"""
            <div style="font-size: 0.80rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;">
                {'対話型元帳サンドボックス (Interactive Ledger Sandbox)' if is_jp else 'Interactive Ledger Sandbox & Scenario Testing'}
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; margin-bottom: 8px;">
                {'元帳の取引金額や相手先GSTINを編集してリアルタイムで突合検知を検証します。' if is_jp else 'Modify transactions below to test live anomaly detection, Benford re-calibration, and Shinrai trust score recalculation:'}
            </div>
            """,
            unsafe_allow_html=True
        )

        sample_slice = pd.DataFrame(txns_list[:15]) if txns_list else pd.DataFrame()
        if not sample_slice.empty:
            cols_to_edit = [c for c in ['txnId', 'valueDate', 'type', 'amount', 'counterparty', 'counterpartyGstin'] if c in sample_slice.columns]
            edited_df = st.data_editor(sample_slice[cols_to_edit], use_container_width=True, key="sandbox_editor_reports")

            sb_col1, sb_col2 = st.columns([2.2, 1.8])
            with sb_col1:
                btn_sb_recalc = "[サンドボックスから再計算]" if is_jp else "[RE-CALCULATE FORENSIC AUDIT FROM SANDBOX]"
                if st.button(btn_sb_recalc, key="btn_recalc_sandbox_reports", type="primary", use_container_width=True):
                    try:
                        import copy
                        updated_txns = copy.deepcopy(txns_list)
                        for row_idx, r_edited in edited_df.iterrows():
                            if row_idx < len(updated_txns):
                                for col in cols_to_edit:
                                    if col in r_edited:
                                        v_val = r_edited[col]
                                        if col == 'amount':
                                            try:
                                                v_val = float(v_val)
                                                updated_txns[row_idx]['amount_jpy'] = round(v_val * FX_INR_TO_JPY, 2)
                                            except:
                                                pass
                                        updated_txns[row_idx][col] = v_val


                        edited_rebit = copy.deepcopy(rebit_raw)
                        edited_rebit['account']['transactions']['transaction'] = updated_txns

                        engine = ForensicAuditEngine(fx_inr_to_jpy=FX_INR_TO_JPY)
                        mutated_res = engine.evaluate(
                            rebit_data=edited_rebit,
                            gst_df=gst_raw,
                            directors_df=dir_raw,
                            ca_books=ca_raw,
                            claimed_profile=claims_raw
                        )
                        mutated_res["preset_key"] = "sandbox_mutated"
                        st.session_state['custom_audit_data'] = mutated_res
                        st.session_state['custom_raw_bundle'] = (edited_rebit, gst_raw, dir_raw, claims_raw, ca_raw)
                        st.session_state['active_preset'] = "custom_upload"
                        st.toast("監査エンジン再計算完了: マークルツリールートと信頼スコアが更新されました。" if is_jp else "Forensic engine re-evaluated! Merkle tree root and Trust score updated.")
                        st.rerun()
                    except Exception as e_sb:
                        st.error(f"Sandbox re-evaluation error: {str(e_sb)}")

            with sb_col2:
                btn_sb_restore = "[元帳ベースラインに復元]" if is_jp else "[RESTORE ORIGINAL LEDGER BASELINE]"
                if st.button(btn_sb_restore, key="btn_restore_sandbox_reports", use_container_width=True):
                    st.session_state['custom_audit_data'] = None
                    st.session_state['custom_raw_bundle'] = None
                    st.toast("公的元帳のベースラインに復元しました。" if is_jp else "Restored to original sovereign ledger baseline.")
                    st.rerun()
