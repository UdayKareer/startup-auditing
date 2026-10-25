"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Startup Founder Diligence Workspace.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.

Strictly adhering to Non-AI-Slop & Institutional Standards:
- Zero emojis
- Monospace tabular numerals (JetBrains Mono)
- Pure White / Obsidian Dark themes
- DPDP Act 2023 §6 Compliant Consent Workflow
- Sovereign DPI Rails: RBI AA (ReBIT DEPOSIT v2.0), GSTN (GSTR-1/3B), MCA-21
"""

import os
import json
import streamlit as st
import pandas as pd

from backend.main import full_audit, load_startup_bundle
from backend.schemas import AuditRequest
from backend.registry_lookup import lookup_mca_entity, get_all_quick_fill_options
from export.memo_generator import generate_ringi_sho_pdf
from frontend.styles import apply_styles
from frontend.i18n import t, format_currency, format_dual_currency_pair
from frontend.components import render_workflow_stepper, render_mca_entity_card
from frontend.diligence_client import (
    fetch_backend_diligence_state,
    approve_backend_request,
    link_backend_rail,
    switch_backend_preset,
    sync_session_from_backend
)


def render_founder_workspace():
    """Renders the dedicated, structured Founder Diligence & Onboarding Dashboard."""
    # Synchronize latest shared state across all dashboards
    sync_session_from_backend()
    # Session state safeguards
    if 'theme_mode' not in st.session_state:
        st.session_state['theme_mode'] = "light"
    if 'currency_mode' not in st.session_state:
        st.session_state['currency_mode'] = "INR"
    if 'lang_mode' not in st.session_state:
        st.session_state['lang_mode'] = "EN"
    if 'active_cin' not in st.session_state:
        st.session_state['active_cin'] = "U72900KA2023PTC178921"
    if 'active_preset' not in st.session_state:
        st.session_state['active_preset'] = "clean_startup"
    if 'cin_entity_data' not in st.session_state:
        st.session_state['cin_entity_data'] = lookup_mca_entity(st.session_state['active_cin'])
    if 'consent_request' not in st.session_state:
        st.session_state['consent_request'] = {
            "status": "APPROVED",
            "handle": "REQ-KIZUNA-2026-APEX-0914",
            "signatory": "Rajesh Sharma (DIN: 08921045)",
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
    demo_connected = st.session_state.get('demo_connected_mode', False) or (st.query_params.get('demo_mode') == 'connected')
    if 'aa_bank_linked' not in st.session_state:
        st.session_state['aa_bank_linked'] = demo_connected
    if 'gstin_tax_linked' not in st.session_state:
        st.session_state['gstin_tax_linked'] = demo_connected
    if 'mca_books_linked' not in st.session_state:
        st.session_state['mca_books_linked'] = demo_connected

    theme_mode = st.session_state['theme_mode']
    curr = st.session_state['currency_mode']
    lang = st.session_state['lang_mode']
    is_jp = lang.upper() in ["JP", "JA"]

    apply_styles(theme=theme_mode)

    txt_pri = "#F8FAFC" if theme_mode == "dark" else "#0F172A"
    txt_sec = "#CBD5E1" if theme_mode == "dark" else "#334155"
    card_bg = "#111827" if theme_mode == "dark" else "#FFFFFF"
    card_border = "#1E293B" if theme_mode == "dark" else "#CBD5E1"
    sub_bg = "#090D16" if theme_mode == "dark" else "#F8FAFC"

    # ---------------------------------------------------------
    # 1. FOUNDER BRAND HEADER & INSTITUTIONAL CONTROLS
    # ---------------------------------------------------------
    hdr_sub = "Bilateral India-Japan Due Diligence Gateway | Digital Personal Data Protection (DPDP) Act 2023 §6 Compliant" if not is_jp else "日印二国間スタートアップ監査レール | 2023年デジタル個人データ保護法 (DPDP Act §6) 準拠"
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 22px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 0.70rem; font-weight: 800; color: #059669; letter-spacing: 0.08em; text-transform: uppercase;">
                    {'[創業者専用ポータル] 法定同意・公的データ連携ワークスペース' if is_jp else '[FOUNDER DILIGENCE ROOM] SOVEREIGN CONSENT & DATA ROOM GATEWAY'}
                </div>
                <div style="font-size: 1.30rem; font-weight: 800; color: {txt_pri}; letter-spacing: -0.02em; margin-top: 2px;">
                    VeriLedger (絆) | {'スタートアップ創業者ダッシュボード' if is_jp else 'Startup Founder Diligence Dashboard'}
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 2px;">
                    {hdr_sub}
                </div>
            </div>
            <div style="text-align: right;">
                <span class="badge-clean">{'[通信暗号化: 正常]' if is_jp else '[SECURE SOVEREIGN SESSION]'}</span>
                <div style="font-size: 0.68rem; color: #64748B; font-family: monospace; margin-top: 4px;">
                    Protocol: ECDH Curve25519 + AES-GCM-256
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top Control Bar (Theme, Currency, Language)
    c_space, c_theme, c_curr, c_lang = st.columns([4.2, 1.8, 2.0, 2.0])
    with c_theme:
        theme_lbl = t("theme_toggle_dark", lang) if theme_mode == "light" else t("theme_toggle_light", lang)
        if st.button(theme_lbl, key="founder_theme_toggle", use_container_width=True):
            st.session_state['theme_mode'] = "dark" if theme_mode == "light" else "light"
            st.rerun()
    with c_curr:
        curr_lbl = t("currency_toggle_jpy", lang) if curr == "INR" else t("currency_toggle_inr", lang)
        if st.button(curr_lbl, key="founder_curr_toggle", use_container_width=True):
            st.session_state['currency_mode'] = "JPY" if curr == "INR" else "INR"
            st.rerun()
    with c_lang:
        lang_lbl = t("lang_toggle_jp", lang) if lang == "EN" else t("lang_toggle_en", lang)
        if st.button(lang_lbl, key="founder_lang_toggle", use_container_width=True):
            st.session_state['lang_mode'] = "JP" if lang == "EN" else "EN"
            st.rerun()

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 2. WORKFLOW STEPPER PROGRESS
    # ---------------------------------------------------------
    is_approved = st.session_state['consent_request'].get("status") == "APPROVED"
    is_all_linked = (
        st.session_state.get('aa_bank_linked', False) and
        st.session_state.get('gstin_tax_linked', False) and
        st.session_state.get('mca_books_linked', False)
    )

    if is_all_linked and is_approved:
        step_now = 4
    elif is_approved:
        step_now = 3
    elif st.session_state['consent_request'].get("status") == "DISPATCHED":
        step_now = 2
    else:
        step_now = 1

    render_workflow_stepper(current_step=step_now, lang=lang, theme=theme_mode)

    entity_data = st.session_state.get('cin_entity_data')
    if not entity_data:
        entity_data = lookup_mca_entity(st.session_state.get('active_cin', 'U72900KA2023PTC178921'))
        st.session_state['cin_entity_data'] = entity_data

    # ---------------------------------------------------------
    # 3. STEP 1: CORPORATE ENTITY DISCOVERY (CIN IDENTIFIER)
    # ---------------------------------------------------------
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.03em;">
                {t('step1_header', lang)}
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 3px; margin-bottom: 10px;">
                {t('step1_sub', lang)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_cin_in, col_cin_btn = st.columns([3.5, 1.5])
    with col_cin_in:
        cin_input_val = st.text_input(
            label=t("cin_input_label", lang),
            value=st.session_state.get('active_cin', 'U72900KA2023PTC178921'),
            help=t("cin_input_help", lang),
            key="founder_cin_input"
        )
    with col_cin_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button(t("btn_discover_entity", lang), key="btn_do_lookup", type="primary", use_container_width=True):
            resolved = lookup_mca_entity(cin_input_val)
            st.session_state['active_cin'] = resolved['cin']
            st.session_state['cin_entity_data'] = resolved
            st.session_state['active_preset'] = resolved['preset_key']
            st.session_state['aa_bank_linked'] = False
            st.session_state['gstin_tax_linked'] = False
            st.session_state['mca_books_linked'] = False
            st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{resolved['preset_key'][:4].upper()}-0914"
            st.rerun()

    auth_cap = entity_data.get("authorized_capital_inr", 5000000.0)
    paid_cap = entity_data.get("paid_up_capital_inr", 4250000.0)
    cap_str = f"₹{auth_cap/1e5:.1f} Lakhs / ₹{paid_cap/1e5:.1f} Lakhs" if auth_cap < 1e7 else f"₹{auth_cap/1e7:.2f} Cr / ₹{paid_cap/1e7:.2f} Cr"
    directors_str = ", ".join([f"{d.get('name')} (DIN: {d.get('din')})" for d in entity_data.get('directors', [])])

    # Prominent Company Identity Card (Name, Established, GST Number, and Shareable CIN)
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1.5px solid #0284C7; border-radius: 8px; padding: 20px 24px; margin-top: 10px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; margin-bottom: 14px;">
                <div>
                    <div style="font-size: 0.70rem; font-weight: 800; color: #0284C7; letter-spacing: 0.08em; text-transform: uppercase;">
                        {'[自社登記情報] 投資家向け公式共有カード' if is_jp else '[REGISTERED ENTERPRISE PROFILE] YOUR COMPANY CREDENTIALS'}
                    </div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: {txt_pri}; letter-spacing: -0.01em; margin-top: 2px;">
                        {entity_data.get('company_name')}
                    </div>
                    <div style="font-size: 0.74rem; color: #64748B; margin-top: 3px;">
                        {entity_data.get('roc_office')} • {entity_data.get('registered_address')}
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="badge-clean">{'[MCA-21 登記確認済]' if is_jp else '[MCA-21 VERIFIED ACTIVE]'}</span>
                    <span class="badge-mono">{'業歴' if is_jp else 'VINTAGE'}: {entity_data.get('vintage_years', 3.5)} {'年' if is_jp else 'YRS'}</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1.2fr 1.8fr; gap: 14px; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
                <div>
                    <div style="font-size: 0.68rem; font-weight: 700; color: #059669; text-transform: uppercase;">
                        {'設立年月日 (ESTABLISHED)' if is_jp else 'ESTABLISHED / INCORPORATED'}
                    </div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: {txt_pri}; font-family: monospace; margin-top: 2px;">
                        {entity_data.get('incorporation_date')}
                    </div>
                    <div style="font-size: 0.68rem; color: #64748B;">
                        {'会社法に基づく正規設立' if is_jp else 'Companies Act 2013 Verified'}
                    </div>
                </div>
                <div>
                    <div style="font-size: 0.68rem; font-weight: 700; color: #059669; text-transform: uppercase;">
                        {'GST登録番号 (GST NUMBER)' if is_jp else 'GST NUMBER (GSTIN)'}
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; margin-top: 2px; flex-wrap: wrap;">
                        <span style="font-size: 1.05rem; font-weight: 800; color: #059669; font-family: monospace;">
                            {entity_data.get('gstin')}
                        </span>
                        <span class="badge-clean" style="font-size: 0.62rem; padding: 2px 6px;">[ACTIVE]</span>
                    </div>
                    <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">
                        {'法人PAN' if is_jp else 'Linked Corporate PAN'}: <code style="color: #38BDF8;">{entity_data.get('pan')}</code>
                    </div>
                </div>
                <div style="background: {'#FFFFFF' if theme_mode == 'light' else '#111827'}; border: 1.5px solid #0284C7; border-radius: 4px; padding: 8px 12px;">
                    <div style="font-size: 0.68rem; font-weight: 800; color: #0284C7; text-transform: uppercase; letter-spacing: 0.04em;">
                        {'投資家に提出する法人番号 (CIN TO GIVE TO INVESTOR)' if is_jp else 'CIN NUMBER TO GIVE TO INVESTOR'}
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #0284C7; font-family: monospace; letter-spacing: 0.04em; margin-top: 2px;">
                        {entity_data.get('cin')}
                    </div>
                    <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">
                        {'この21桁のCIN番号を東京の投資審査機関（Value Create Inc. / JETRO）に共有してください' if is_jp else 'Give this 21-digit CIN to Value Create Inc. / JETRO Tokyo to unlock your diligence dossier'}
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.73rem; color: {txt_sec};">
                <div>
                    <b>{'授権資本 / 払込資本' if is_jp else 'Authorized / Paid-up Capital'}:</b> {cap_str}<br/>
                    <b>{'主要取引銀行' if is_jp else 'Registered Bank A/c'}:</b> {entity_data.get('bank_fip_display')}
                </div>
                <div>
                    <b>{'役員・公式署名権者' if is_jp else 'Directors (DINs)'}:</b> {directors_str}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Clean Demo Profile Switcher tucked into an expander (not cluttering main dashboard)
    with st.expander("【開発・審査デモ用】登録済みスタートアップ企業切替 (8 Sample Presets)" if is_jp else "[DEMO TOOLS] Switch Registered Test Enterprise Profile (8 Sample Presets)", expanded=False):
        st.markdown(
            f"<div style='font-size: 0.70rem; font-weight: 700; color: #64748B; margin-bottom: 6px;'>"
            f"{t('quick_fill_header', lang)}"
            f"</div>",
            unsafe_allow_html=True
        )
        quick_options = get_all_quick_fill_options()
        for r_idx in range(0, len(quick_options), 4):
            row_opts = quick_options[r_idx:r_idx + 4]
            cols = st.columns(len(row_opts))
            for col_idx, opt in enumerate(row_opts):
                btn_idx = r_idx + col_idx
                with cols[col_idx]:
                    btn_text = opt["name_jp"] if is_jp else opt["name"]
                    if st.button(f"[FILL] {btn_text[:20]}", key=f"qf_btn_{btn_idx}", use_container_width=True):
                        switch_backend_preset(opt["preset_key"])
                        resolved = lookup_mca_entity(opt["cin"])
                        st.session_state['active_cin'] = resolved['cin']
                        st.session_state['cin_entity_data'] = resolved
                        st.session_state['active_preset'] = resolved['preset_key']
                        st.session_state['aa_bank_linked'] = False
                        st.session_state['gstin_tax_linked'] = False
                        st.session_state['mca_books_linked'] = False
                        st.session_state['linked_rails'] = {"bank": False, "gst": False, "mca": False}
                        st.session_state['consent_request']['status'] = "DISPATCHED"
                        st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{resolved['preset_key'][:4].upper()}-0914"
                        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 4. STEP 2: INCOMING INVESTOR DILIGENCE CONSENT MANDATES
    # ---------------------------------------------------------
    first_dir = entity_data.get('directors', [{}])[0].get('name', 'Corporate Signatory')
    first_dir_din = entity_data.get('directors', [{}])[0].get('din', '00000000')

    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri};">
                    {t('step2_header', lang)}
                </div>
                <div>
                    <span class="{'badge-clean' if is_approved else 'badge-review'}">
                        {t('status_approved_founder', lang) if is_approved else t('status_pending_founder', lang)}
                    </span>
                </div>
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.4; margin-bottom: 10px;">
                {t('step2_sub', lang)}
            </div>
            <div style="background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px; font-size: 0.73rem; line-height: 1.6;">
                <b>{t('lbl_requesting_entity', lang)}:</b> Value Create Inc. (Tokyo) & JETRO India Startup Desk<br/>
                <b>{t('lbl_lead_officer', lang)}:</b> Demo Persona — Tanaka Hiroshi (demo@kizuna-vault.example.com)<br/>
                <b>{t('lbl_purpose', lang)}:</b> Track OPEN-PS-01 Bilateral Series A Diligence Mandate<br/>
                <b>{t('lbl_requested_scopes', lang)}:</b> RBI AA Bank Ledger (ReBIT DEPOSIT v2.0), GSTN Invoices & Returns (GSTR-1, GSTR-3B), MCA-21 Director DINs, CA Books<br/>
                <b>{t('lbl_validity', lang)}:</b> 14 Days Time-Bound Grant (DPDP Act 2023 §6)<br/>
                <b>Consent Mandate Handle:</b> <code style="color: #38BDF8;">{st.session_state['consent_request']['handle']}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_appr1, col_appr2 = st.columns([3, 1])
    with col_appr1:
        if not is_approved:
            st.markdown(
                f"<div style='font-size: 0.75rem; color: #D97706; padding: 8px 0; font-weight: 600;'>"
                f"{'東京審査委員会からのデューデリジェンス同意リクエストが保留中です。承認して公的データ元帳へのアクセスを許可してください。' if is_jp else 'Diligence consent request from Tokyo evaluation committee is pending corporate authorization.'}"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='font-size: 0.75rem; color: #059669; padding: 8px 0; font-weight: 700;'>"
                f"[PASS: AUTHORIZED] {'代表取締役により公式承認されました' if is_jp else 'Diligence request approved by corporate signatory'}: {first_dir} (DIN: {first_dir_din})"
                f"</div>",
                unsafe_allow_html=True
            )
    with col_appr2:
        if not is_approved:
            if st.button(t("btn_approve_request", lang), key="btn_fnd_approve", type="primary", use_container_width=True):
                approve_backend_request(signatory=f"{first_dir} (DIN: {first_dir_din})")
                st.session_state['consent_request']['status'] = "APPROVED"
                st.toast("精査同意リクエストを承認しました。" if is_jp else "Diligence consent request approved!")
                st.rerun()
        else:
            st.button("[PASS: APPROVED]", key="btn_already_approved", disabled=True, use_container_width=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 5. STEP 3: LINK SOVEREIGN FINANCIAL RAILS (AA + GSTIN + MCA)
    # ---------------------------------------------------------
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri};">
                {t('step3_header', lang)}
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 3px;">
                {t('step3_sub', lang)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_rail1, col_rail2, col_rail3 = st.columns(3)

    # Rail 1: RBI AA Bank Account
    with col_rail1:
        is_bank_ok = st.session_state.get('aa_bank_linked', False)
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; background: {card_bg}; border: 1px solid {'#059669' if is_bank_ok else card_border}; margin-bottom: 8px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'銀行元帳API (RBI AA)' if is_jp else 'BANKING PROTOCOL (RBI AA)'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">{entity_data.get('bank_name')} Current A/c</div>
                <div style="font-size: 0.70rem; color: {'#059669' if is_bank_ok else '#D97706'}; font-weight: 700; margin-top: 4px;">
                    {'● 連携済 (ReBIT v2.0)' if is_bank_ok else '○ 未連携 (要認証)' if is_jp else ('● LINKED (ReBIT v2.0)' if is_bank_ok else '○ DISCONNECTED')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not is_bank_ok:
            if st.button(t("btn_link_bank_aa", lang), key="btn_connect_bank", use_container_width=True):
                link_backend_rail("bank", True)
                st.session_state['aa_bank_linked'] = True
                st.toast("RBIアカウントアグリゲーター経由で銀行口座を連携しました。" if is_jp else "Bank account linked via RBI Account Aggregator!")
                st.rerun()
        else:
            bank_badge = (
                f"[PASS: VERIFIED] {entity_data.get('bank_name')} Current A/c Linked via RBI AA"
                if not is_jp
                else f"[PASS: 検証済] {entity_data.get('bank_name')} 口座連携完了 (RBI AA / ReBIT v2.0)"
            )
            st.markdown(
                f"<div class='badge-clean' style='font-size: 0.68rem; margin-top: 4px; padding: 6px 8px;'>"
                f"{bank_badge}"
                f"</div>",
                unsafe_allow_html=True
            )

    # Rail 2: GSTN Sovereign Tax Network
    with col_rail2:
        is_gst_ok = st.session_state.get('gstin_tax_linked', False)
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; background: {card_bg}; border: 1px solid {'#059669' if is_gst_ok else card_border}; margin-bottom: 8px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'税務ネットワーク (GSTN GSP)' if is_jp else 'TAX NETWORK (GSTN GSP)'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">
                    GSTIN: {entity_data.get('gstin')}
                    <span class="badge-clean" style="font-size: 0.60rem; padding: 1px 5px; margin-left: 4px;">[VERIFIED]</span>
                </div>
                <div style="font-size: 0.70rem; color: {'#059669' if is_gst_ok else '#D97706'}; font-weight: 700; margin-top: 4px;">
                    {'● 連携済 (GSTR-1/3B)' if is_gst_ok else '○ 未連携 (要認証)' if is_jp else ('● LINKED (GSTR-1/3B)' if is_gst_ok else '○ DISCONNECTED')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not is_gst_ok:
            if st.button(t("btn_link_tax_gstin", lang), key="btn_connect_gst", use_container_width=True):
                link_backend_rail("gst", True)
                st.session_state['gstin_tax_linked'] = True
                st.toast("国家税務レール (GSTIN) を連携しました。" if is_jp else "GSTIN linked via sovereign tax rail!")
                st.rerun()
        else:
            gst_badge = (
                f"[PASS: VERIFIED] GSTIN ({entity_data.get('gstin')}) Linked via Sovereign Tax Rail"
                if not is_jp
                else f"[PASS: 検証済] GSTIN ({entity_data.get('gstin')}) 税務申告連携完了 (GSTR-1/3B同期)"
            )
            st.markdown(
                f"<div class='badge-clean' style='font-size: 0.68rem; margin-top: 4px; padding: 6px 8px;'>"
                f"{gst_badge}"
                f"</div>",
                unsafe_allow_html=True
            )

    # Rail 3: MCA-21 & CA Books
    with col_rail3:
        is_mca_ok = st.session_state.get('mca_books_linked', False)
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; background: {card_bg}; border: 1px solid {'#059669' if is_mca_ok else card_border}; margin-bottom: 8px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'商業登記 & 試算表 (MCA/CA)' if is_jp else 'REGISTRY & BOOKS (MCA/CA)'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">Trial Balance & Form PAS-3</div>
                <div style="font-size: 0.70rem; color: {'#059669' if is_mca_ok else '#D97706'}; font-weight: 700; margin-top: 4px;">
                    {'● 突合完了' if is_mca_ok else '○ 未突合' if is_jp else ('● LINKED (PAS-3)' if is_mca_ok else '○ DISCONNECTED')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if not is_mca_ok:
            if st.button(t("btn_link_mca_books", lang), key="btn_connect_mca", use_container_width=True):
                link_backend_rail("mca", True)
                st.session_state['mca_books_linked'] = True
                st.toast("商業登記と公認会計士元帳を突合ロックしました。" if is_jp else "MCA & CA statutory books cross-linked!")
                st.rerun()
        else:
            st.markdown(
                f"<div class='badge-clean' style='font-size: 0.68rem; margin-top: 4px; padding: 6px 8px;'>"
                f"{t('badge_mca_linked_full', lang)}"
                f"</div>",
                unsafe_allow_html=True
            )

    # Fast-Track Link All
    if not is_all_linked:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        fast_track_txt = "[FAST-TRACK] Link All Sovereign Rails Instantly (一括全公的データ連携)" if is_jp else "[FAST-TRACK] Link All Sovereign Rails Instantly"
        if st.button(fast_track_txt, key="btn_link_all_fast", type="secondary"):
            approve_backend_request(signatory=f"{first_dir} (DIN: {first_dir_din})")
            link_backend_rail("all", True)
            st.session_state['consent_request']['status'] = "APPROVED"
            st.session_state['aa_bank_linked'] = True
            st.session_state['gstin_tax_linked'] = True
            st.session_state['mca_books_linked'] = True
            st.toast("全系統の国家公的データレールが連携されました。" if is_jp else "All sovereign data rails actively linked and verified!")
            st.rerun()
    else:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid #059669; border-radius: 4px; padding: 10px 14px; margin-top: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.78rem; font-weight: 800; color: #10B981; letter-spacing: 0.03em;">
                    [PASS] {t('all_rails_linked_banner', lang)}
                </span>
                <span style="font-size: 0.70rem; color: #64748B; font-family: monospace;">
                    Protocol: ECDH Curve25519 + AES-GCM-256
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 6. STEP 4: SEALED DATA ROOM & INVESTOR ACCESS MINTING
    # ---------------------------------------------------------
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri};">
                        {t('step4_header', lang)}
                    </div>
                    <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 2px;">
                        {t('step4_sub', lang)}
                    </div>
                </div>
                <div>
                    <span class="{'badge-clean' if is_all_linked else 'badge-review'}">
                        {'[SEALED: READY]' if is_all_linked else '[WAITING LINKAGE]'}
                    </span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.74rem; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; padding: 12px 14px; border-radius: 4px; border: 1px solid {card_border}; margin-top: 8px; margin-bottom: 12px;">
                <div>
                    <span style="color: #64748B; font-weight: 600;">{t('handshake_passcode_label', lang)}:</span><br/>
                    <code style="font-size: 1.05rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.04em;">{entity_data.get('passcode', 'TRUSTVAULT-VC901-TJH')}</code><br/>
                    <span style="font-size: 0.68rem; color: #64748B;">{t('passcode_help', lang)}</span>
                </div>
                <div>
                    <span style="color: #64748B; font-weight: 600;">{t('merkle_anchor_label_short', lang)}:</span><br/>
                    <code style="font-size: 0.72rem; color: #10B981; font-family: monospace; word-break: break-all;">{entity_data.get('merkle_root')}</code><br/>
                    <span style="font-size: 0.68rem; color: #64748B;">Whitelist: @value-create.com, @jetro.go.jp (14 Days)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # 7. FOUNDER DEDICATED ACTION BAR (STEP 4 ACTION GATEWAY)
    # ---------------------------------------------------------
    c_act1, c_act2 = st.columns([2.5, 2.0])

    with c_act1:
        cockpit_btn_txt = "【投資家監査レポートを確認】個別企業調書プレビュー" if is_jp else "[OPEN AUDITED DOSSIER COCKPIT] View Live Governance Score & Reports"
        if st.button(cockpit_btn_txt, key="btn_fnd_cockpit", type="primary", use_container_width=True, disabled=not is_all_linked):
            st.session_state['active_preset'] = entity_data['preset_key']
            st.session_state['custom_audit_data'] = None
            st.session_state['is_authenticated'] = True
            st.session_state['page_state'] = 'cockpit'
            st.query_params["view"] = "cockpit"
            st.query_params["preset"] = entity_data['preset_key']
            try:
                st.switch_page("frontend/pages/3_Audited_Company_Dossier.py")
            except Exception:
                try:
                    st.switch_page("pages/3_Audited_Company_Dossier.py")
                except Exception:
                    st.rerun()

    with c_act2:
        req_audit = AuditRequest(preset_key=entity_data['preset_key'])
        audit_for_memo = full_audit(req_audit)
        pdf_fn = f"{entity_data['preset_key']}_ringi_sho_memo.pdf"
        pdf_out_path = os.path.join("export", pdf_fn)
        try:
            generate_ringi_sho_pdf(audit_for_memo, pdf_out_path)
            with open(pdf_out_path, "rb") as f:
                pdf_bin = f.read()
        except Exception:
            pdf_bin = b""

        if pdf_bin:
            st.download_button(
                label=t("btn_download_ringisho", lang),
                data=pdf_bin,
                file_name=pdf_fn,
                mime="application/pdf",
                key="btn_fnd_dl_memo",
                use_container_width=True
            )
        else:
            st.button(t("btn_download_ringisho", lang), key="btn_fnd_memo_dummy", disabled=True, use_container_width=True)
