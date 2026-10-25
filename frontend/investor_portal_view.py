"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Investor Due Diligence Portal.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.

Strictly adhering to Non-AI-Slop & Institutional Standards:
- Zero emojis
- Monospace tabular numerals (JetBrains Mono)
- Pure White / Obsidian Dark themes
- Sovereign DPI Rails: RBI AA (ReBIT DEPOSIT v2.0), GSTN (GSTR-1/3B), MCA-21
"""

import os
import streamlit as st
import pandas as pd

from backend.registry_lookup import lookup_mca_entity, get_all_quick_fill_options
from frontend.styles import apply_styles
from frontend.i18n import t, format_currency
from frontend.components import (
    render_header,
    render_dpi_rail_badges,
    render_merkle_anchor,
    render_anonymized_teaser,
    render_workflow_stepper,
    render_mca_entity_card,
    render_public_case_studies,
)
from frontend.diligence_client import (
    fetch_backend_diligence_state,
    dispatch_backend_request,
    switch_backend_preset,
    sync_session_from_backend
)


def render_investor_portal():
    """Renders the dedicated Investor Due Diligence & Portfolio Selection Portal."""
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
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False

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

    # Top Brand Header
    render_header(currency=curr, lang=lang, theme_mode=theme_mode)

    # Control Bar (Theme, Currency, Language)
    c_bar1, c_bar2, c_bar3, c_bar4 = st.columns([4, 2, 2, 2])
    with c_bar2:
        theme_lbl = t("theme_toggle_dark", lang) if theme_mode == "light" else t("theme_toggle_light", lang)
        if st.button(theme_lbl, key="inv_theme_toggle", use_container_width=True):
            st.session_state['theme_mode'] = "dark" if theme_mode == "light" else "light"
            st.rerun()
    with c_bar3:
        curr_lbl = t("currency_toggle_jpy", lang) if curr == "INR" else t("currency_toggle_inr", lang)
        if st.button(curr_lbl, key="inv_curr_toggle", use_container_width=True):
            st.session_state['currency_mode'] = "JPY" if curr == "INR" else "INR"
            st.rerun()
    with c_bar4:
        lang_lbl = t("lang_toggle_jp", lang) if lang == "EN" else t("lang_toggle_en", lang)
        if st.button(lang_lbl, key="inv_lang_toggle", use_container_width=True):
            st.session_state['lang_mode'] = "JP" if lang == "EN" else "EN"
            st.rerun()

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
    render_dpi_rail_badges(lang=lang)

    # Cryptographic Merkle Root Anchor Banner
    render_merkle_anchor(
        merkle_root="0x8f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a",
        lang=lang
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
        render_anonymized_teaser(teaser_payload, lang=lang)

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
                    c_stat = st.session_state.get('consent_request', {}).get('status', 'DISPATCHED')
                    rails = st.session_state.get('linked_rails', {})
                    is_rails_ok = all(rails.values()) if rails else (st.session_state.get('aa_bank_linked', False) and st.session_state.get('gstin_tax_linked', False) and st.session_state.get('mca_books_linked', False))
                    if c_stat != "APPROVED" or not is_rails_ok:
                        st.warning("【開示制限】2023年DPDP法第6条に基づき、創業者による法定開示承認が完了するまでデータルームは施錠されています。創業者ダッシュボードから承認を実行するか、下記のデモ高速承認をご利用ください。" if is_jp else "[DPDP ACT 2023 §6 RESTRICTION] Diligence data room remains sealed until target enterprise founder authorizes the statutory mandate. Authorize via Founder Dashboard or use Fast-Track Demo Authorization below.")
                    else:
                        st.session_state['is_authenticated'] = True
                        st.session_state['page_state'] = 'cockpit'
                        st.query_params["view"] = "cockpit"
                        try:
                            st.switch_page("pages/3_Audited_Company_Dossier.py")
                        except Exception:
                            st.rerun()
                else:
                    st.error("パスコードが無効であるか、未承認のドメインです。認証情報を確認してください。" if is_jp else "Invalid passcode or unauthorized institutional email. Please verify credentials.")

        with col_btn2:
            if st.button(t("btn_quick_fill", lang), key="btn_quickfill", use_container_width=True):
                st.session_state['input_passcode'] = "TRUSTVAULT-VC901-TJH"
                st.session_state['input_investor_email'] = "tanaka.hiroshi@demo.example.com"
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
            st.rerun()

    if selected_preset != cur_p:
        switch_backend_preset(selected_preset)
        st.session_state['active_preset'] = selected_preset
        resolved = lookup_mca_entity(preset_dict[selected_preset]['cin'])
        st.session_state['active_cin'] = resolved['cin']
        st.session_state['cin_entity_data'] = resolved
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
            dispatch_backend_request(preset_key=selected_preset)
            st.session_state['consent_request']['status'] = "DISPATCHED"
            st.session_state['consent_request']['handle'] = mandate_handle
            st.toast("創業者ダッシュボードへDPDP法定同意リクエストを送信しました。" if is_jp else "Diligence consent request dispatched to Founder Dashboard under DPDP Act 2023!")
            st.rerun()

    with act_col2:
        btn_open_dossier_lbl = "【専用査定ページを開く】個別企業監査レポートへ" if is_jp else "[OPEN DEDICATED AUDIT DOSSIER] View Company Reports"
        if is_approved_by_founder:
            if st.button(btn_open_dossier_lbl, key="btn_open_dedicated_dossier", type="primary", use_container_width=True):
                st.session_state['active_preset'] = selected_preset
                st.session_state['custom_audit_data'] = None
                st.session_state['is_authenticated'] = True
                st.session_state['page_state'] = 'cockpit'
                st.query_params["view"] = "cockpit"
                st.query_params["preset"] = selected_preset
                try:
                    st.switch_page("pages/3_Audited_Company_Dossier.py")
                except Exception:
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
            if st.button("【デモ高速承認】即時開錠してレポート閲覧" if is_jp else "[FAST-TRACK DEMO] Authorize & Unlock Dossier", key="btn_gate_fast_track", type="secondary", use_container_width=True):
                from frontend.diligence_client import approve_backend_request, link_backend_rail
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
                st.session_state['is_authenticated'] = True
                st.session_state['page_state'] = 'cockpit'
                st.query_params["view"] = "cockpit"
                st.query_params["preset"] = selected_preset
                try:
                    st.switch_page("pages/3_Audited_Company_Dossier.py")
                except Exception:
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

