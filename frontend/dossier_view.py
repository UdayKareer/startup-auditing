"""
VeriLedger / Kizuna-Vault (絆) — Dedicated Audited Company Dossier & Cockpit.
Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.

Strictly adhering to Non-AI-Slop & Institutional Standards:
- Zero emojis
- Monospace tabular numerals (JetBrains Mono)
- Pure White / Obsidian Dark themes
- 7 Structured Accountant Reports
"""

import os
import json
import time
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from backend.main import full_audit, load_startup_bundle
from backend.schemas import AuditRequest
from backend.registry_lookup import lookup_mca_entity, get_all_quick_fill_options, get_public_case_studies
from export.memo_generator import generate_ringi_sho_pdf
from export.certificate_generator import generate_section_65b_certificate_pdf
from export.pack_bundler import build_audit_pack_zip_bytes
from frontend.styles import apply_styles
from frontend.i18n import t, format_currency, format_dual_currency_pair, FX_INR_TO_JPY
from frontend.components import (
    render_header,
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
    render_audited_bank_ledger,
    render_audited_gst_register,
    render_audited_trial_balance,
    render_public_case_studies,
    render_data_room_sealed_card,
)
from frontend.diligence_client import (
    sync_session_from_backend,
    approve_backend_request,
    link_backend_rail,
    switch_backend_preset,
)


def render_dossier_cockpit():
    """Renders the dedicated 7-report Audited Company Dossier Cockpit."""
    # Synchronize latest shared state across all dashboards
    sync_session_from_backend()
    # Session state safeguards
    if 'theme_mode' not in st.session_state:
        st.session_state['theme_mode'] = "light"
    if 'currency_mode' not in st.session_state:
        st.session_state['currency_mode'] = "INR"
    if 'lang_mode' not in st.session_state:
        st.session_state['lang_mode'] = "EN"
    if 'active_preset' not in st.session_state:
        st.session_state['active_preset'] = "clean_startup"

    theme_mode = st.session_state['theme_mode']
    curr = st.session_state['currency_mode']
    lang = st.session_state['lang_mode']
    is_jp = lang.upper() in ["JP", "JA"]

    apply_styles(theme=theme_mode)

    txt_pri = "#F8FAFC" if theme_mode == "dark" else "#0F172A"
    txt_sec = "#94A3B8" if theme_mode == "dark" else "#475569"
    card_bg = "#111827" if theme_mode == "dark" else "#FFFFFF"
    card_border = "#1E293B" if theme_mode == "dark" else "#CBD5E1"

    # Top Brand Header
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

    # Hydrate interactive stamps for this preset
    hanko_stages = audit_data.get('hanko_stages', [])
    stamps_dict = st.session_state.get('hanko_stamps', {}).get(preset_key, {})
    for stage in hanko_stages:
        s_id = stage.get("stage_id")
        if s_id in stamps_dict:
            saved_status = stamps_dict[s_id]
            stage["status"] = saved_status
            if saved_status == "APPROVED":
                stage["status_jp"] = "承認済"
            elif saved_status == "FLAGGED":
                stage["status_jp"] = "否認/保留"
            elif saved_status == "HELD":
                stage["status_jp"] = "審査中"
            elif saved_status == "PENDING":
                stage["status_jp"] = "決裁待ち"
    audit_data['hanko_stages'] = hanko_stages

    kpis = audit_data['kpis']
    score = kpis['governance_trust_score']
    kanji_badge = kpis['kanji_badge']
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
        if st.button("← Gateway" if not is_jp else "← ポータル", key="btn_back_landing_dossier", type="secondary", use_container_width=True):
            st.session_state['page_state'] = 'gatekeeper'
            st.query_params["view"] = "gatekeeper"
            try:
                st.switch_page("pages/1_Investor_Portal.py")
            except Exception:
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
            if chosen:
                st.session_state['active_preset'] = chosen
                st.session_state['_last_qp_preset'] = chosen
                st.session_state['custom_audit_data'] = None
                st.session_state['demo_bypass_unlocked'] = False
                st.query_params["preset"] = chosen
                switch_backend_preset(chosen)

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
            if st.button("← 投資家ポータルへ戻る" if is_jp else "← Return to Gatekeeper", key="btn_sealed_to_gate", use_container_width=True):
                st.session_state['page_state'] = 'gatekeeper'
                st.query_params["view"] = "gatekeeper"
                try:
                    st.switch_page("pages/1_Investor_Portal.py")
                except Exception:
                    st.rerun()
        with c_gate2:
            if st.button("【デモ高速開錠】創業者承認 & 全公的レール即時連携" if is_jp else "[FAST-TRACK DEMO] Grant Founder Approval & Link Rails", key="btn_sealed_fast_track", type="primary", use_container_width=True):
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
            if st.button("創業者ダッシュボードへ →" if is_jp else "Switch to Founder Dashboard →", key="btn_sealed_to_founder", type="secondary", use_container_width=True):
                st.session_state['page_state'] = 'founder_dashboard'
                st.query_params["view"] = "founder_dashboard"
                try:
                    st.switch_page("pages/2_Founder_Dashboard.py")
                except Exception:
                    st.rerun()
        return

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
                    key="btn_dl_ringisho_pdf_dossier"
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
                    key="btn_dl_sec65b_pdf_dossier"
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
                    key="btn_dl_audit_pack_zip_dossier"
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

        c_flt1, c_flt2 = st.columns([2, 1.2])
        with c_flt1:
            bank_search = st.text_input("取引内容・相手先・取引IDを検索:" if is_jp else "Search narration, counterparty, or transaction ID:", key="bank_search_box")
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

        render_audited_bank_ledger(
            transactions=txns_list,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode,
            search_term=bank_search,
            type_filter=active_filter
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
        render_audited_gst_register(
            gst_df=gst_raw,
            currency_mode=curr,
            lang=lang,
            theme=theme_mode
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
        render_redline_table(discrepancies, currency_mode=curr, lang=lang, theme=theme_mode)

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
                <div class="card" style="padding: 14px 16px;">
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">{'機密開示権限 (RBAC)' if is_jp else 'TIER A: FULL DILIGENCE'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 4px;">Value Create Inc. (Tokyo)</div>
                    <div style="font-size: 0.72rem; color: #059669; font-weight: 700; margin-top: 4px;">● {'承認済 (全元帳開示)' if is_jp else 'AUTHORIZED (UNREDACTED)'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with r_c2:
            st.markdown(
                f"""
                <div class="card" style="padding: 14px 16px;">
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">{'政府機関開示権限' if is_jp else 'TIER A: BILATERAL DESK'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 4px;">JETRO India Startup Desk</div>
                    <div style="font-size: 0.72rem; color: #059669; font-weight: 700; margin-top: 4px;">● {'承認済 (全元帳開示)' if is_jp else 'AUTHORIZED (UNREDACTED)'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with r_c3:
            st.markdown(
                f"""
                <div class="card" style="padding: 14px 16px;">
                    <div style="font-size: 0.72rem; color: #64748B; font-weight: 700;">{'マスキング開示権限' if is_jp else 'TIER B: MASKED LEDGER'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 4px;">SoftBank Vision Fund</div>
                    <div style="font-size: 0.72rem; color: #D97706; font-weight: 700; margin-top: 4px;">○ {'残高マスキング' if is_jp else 'BALANCES MASKED'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
