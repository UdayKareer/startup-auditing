"""
VeriLedger / Kizuna-Vault (Track OPEN-PS-01)
Demo Control & Master System Reset Cockpit.
Provides 1-click reset for hackathon presenters and judges to clear all dashboards
back to pristine initial mode or instantly pre-approve data rails for live demos.
"""

import time
import urllib.request
import streamlit as st
from typing import Dict, Any

from frontend.styles import apply_styles
from backend.registry_lookup import get_all_quick_fill_options
from frontend.diligence_client import (
    fetch_backend_diligence_state,
    reset_backend_demo,
    approve_backend_request,
    link_backend_rail,
    switch_backend_preset,
    sync_session_from_backend
)


def render_demo_admin_cockpit():
    """Renders the master demo control and reset dashboard."""
    if 'theme_mode' not in st.session_state:
        st.session_state['theme_mode'] = "dark"
    if 'currency_mode' not in st.session_state:
        st.session_state['currency_mode'] = "INR"
    if 'lang_mode' not in st.session_state:
        st.session_state['lang_mode'] = "EN"

    theme_mode = st.session_state['theme_mode']
    lang = st.session_state['lang_mode']
    is_jp = lang.upper() in ["JP", "JA"]

    apply_styles(theme=theme_mode)

    # Sync latest shared state
    shared_state = fetch_backend_diligence_state()
    sync_session_from_backend(shared_state)

    txt_pri = "#F8FAFC" if theme_mode == "dark" else "#0F172A"
    txt_sec = "#94A3B8" if theme_mode == "dark" else "#64748B"
    card_bg = "#0F172A" if theme_mode == "dark" else "#FFFFFF"
    card_border = "#1E293B" if theme_mode == "dark" else "#E2E8F0"

    # Header Banner
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-left: 4px solid #B33927; border-radius: 6px; padding: 18px 24px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div style="font-size: 0.72rem; font-family: monospace; font-weight: 700; color: #B33927; letter-spacing: 0.08em; text-transform: uppercase;">
                        {'[プレゼンテーション管理] システム全体初期化 & 審査員デモ制御盤' if is_jp else '[PRESENTATION CONTROL] Master Demo Cockpit & State Reset Engine'}
                    </div>
                    <div style="font-size: 1.45rem; font-weight: 900; color: {txt_pri}; letter-spacing: -0.02em; margin-top: 2px;">
                        VeriLedger (絆) | Demo Admin & System Reset
                    </div>
                    <div style="font-size: 0.74rem; color: {txt_sec}; margin-top: 4px;">
                        {'審査デモ中の状態クリア、企業プロファイル瞬時切替、および各専用ポータルへの直接アクセス制御' if is_jp else 'Live presentation reset tool: clear all dashboard states back to pristine mode or simulate instant approval in 1-click.'}
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="badge-clean">[BACKEND: 8000 OPERATIONAL]</span>
                    <span class="badge-mono">[STREAMLIT: 8501 LIVE]</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top Control Bar (Theme & Language)
    top_c1, top_c2, top_c3 = st.columns([1, 1, 1])
    with top_c1:
        th_idx = 0 if theme_mode == "dark" else 1
        new_th = st.selectbox(
            "Visual Theme",
            options=["Obsidian Dark (Boardroom)", "Pure White (Institutional)"],
            index=th_idx,
            key="demo_admin_theme_sel",
            label_visibility="collapsed"
        )
        picked_th = "dark" if "Dark" in new_th else "light"
        if picked_th != theme_mode:
            st.session_state['theme_mode'] = picked_th
            st.rerun()

    with top_c2:
        cur_idx = 0 if st.session_state['currency_mode'] == "JPY" else 1
        new_cur = st.selectbox(
            "Currency",
            options=["¥ JPY (Tokyo Boardroom)", "₹ INR (Indian Ledger)"],
            index=cur_idx,
            key="demo_admin_cur_sel",
            label_visibility="collapsed"
        )
        picked_cur = "JPY" if "JPY" in new_cur else "INR"
        if picked_cur != st.session_state['currency_mode']:
            st.session_state['currency_mode'] = picked_cur
            st.rerun()

    with top_c3:
        lang_idx = 0 if is_jp else 1
        new_lang = st.selectbox(
            "Language",
            options=["日本語 (Tokyo Metro)", "English (Statutory Diligence)"],
            index=lang_idx,
            key="demo_admin_lang_sel",
            label_visibility="collapsed"
        )
        picked_lang = "JP" if "日本語" in new_lang else "EN"
        if (picked_lang == "JP") != is_jp:
            st.session_state['lang_mode'] = picked_lang
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 1: MASTER 1-CLICK RESET & FAST-FORWARD ACTIONS
    # -------------------------------------------------------------
    st.markdown(
        f"""
        <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em;">
            {'1. デモ状態のリセット & クイック進行制御' if is_jp else '1. One-Click Demo Reset & Fast-Track Controls'}
        </div>
        """,
        unsafe_allow_html=True
    )

    rst_col1, rst_col2 = st.columns(2)
    cur_p = shared_state.get("active_preset", "clean_startup")

    with rst_col1:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid #DC2626; border-radius: 6px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #EF4444;">
                    {'【初期状態へ完全リセット】' if is_jp else '[MASTER RESET] Restore to Pristine State'}
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 4px; line-height: 1.4;">
                    {'全ダッシュボードの同意状態、データ連携、一時キャッシュをクリアし、未承認・未連携の初期状態に戻します。' if is_jp else 'Resets diligence consent to DISPATCHED, disconnects all 3 data rails, and locks the sealed data room for a fresh pitch demo.'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("全ダッシュボード初期化 (Reset All Dashboards to Initial)", key="btn_do_master_reset", type="primary", use_container_width=True):
            reset_backend_demo(preset_key=cur_p, mode="pristine")
            st.toast("全ダッシュボードを初期デモ状態にリセットしました。" if is_jp else "[SUCCESS] All dashboards restored to pristine initial state!")
            st.rerun()

    with rst_col2:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid #059669; border-radius: 6px; padding: 14px 16px; margin-bottom: 10px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #10B981;">
                    {'【30秒ピッチ用: 全項目一括承認 & 封印】' if is_jp else '[FAST-TRACK] Instant Pre-Approve & Seal All Rails'}
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 4px; line-height: 1.4;">
                    {'法定同意を即時承認し、銀行・税務・登記簿の3公的レールを一括連携して、直ちに監査査定レポートを解禁します。' if is_jp else 'Instantly authorizes consent, connects all 3 sovereign rails, anchors Merkle root, and seals data room for rapid 30s presentations.'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("全項目一括承認・連携 (Fast-Track Approve & Link All)", key="btn_do_fast_track", type="secondary", use_container_width=True):
            reset_backend_demo(preset_key=cur_p, mode="pre_approved")
            st.toast("全データレールを一括承認・連携しました。" if is_jp else "[FAST-TRACK ACTIVE] All rails approved and data room sealed!")
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 2: LIVE SYNCHRONIZED STATE TELEMETRY
    # -------------------------------------------------------------
    st.markdown(
        f"""
        <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em;">
            {'2. リアルタイム共有ステータス監視 (Cross-Dashboard Live State)' if is_jp else '2. Live Synchronized Diligence State Telemetry'}
        </div>
        """,
        unsafe_allow_html=True
    )

    req = shared_state.get("request", {})
    rails = shared_state.get("linked_rails", {})
    is_appr = req.get("status") == "APPROVED"
    is_sealed = shared_state.get("data_room_sealed", False)

    tel1, tel2, tel3, tel4 = st.columns(4)
    with tel1:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 12px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'対象企業' if is_jp else 'ACTIVE PRESET'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">{cur_p}</div>
                <div style="font-size: 0.68rem; font-family: monospace; color: #38BDF8; margin-top: 2px;">{shared_state.get('active_cin', '')[:14]}...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tel2:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {'#059669' if is_appr else card_border}; border-radius: 4px; padding: 10px 12px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'法定同意' if is_jp else 'CONSENT STATUS'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {'#10B981' if is_appr else '#F59E0B'}; margin-top: 2px;">
                    {'[PASS: 承認済]' if is_appr else '[STATUS: DISPATCHED]'}
                </div>
                <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">{req.get('handle', '')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tel3:
        linked_count = sum(1 for v in rails.values() if v)
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {'#059669' if linked_count == 3 else card_border}; border-radius: 4px; padding: 10px 12px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'公的データレール' if is_jp else 'DATA RAILS'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {'#10B981' if linked_count == 3 else '#38BDF8'}; margin-top: 2px;">
                    {linked_count} / 3 {'系統連携完了' if is_jp else 'LINKED'}
                </div>
                <div style="font-size: 0.68rem; color: #64748B; margin-top: 2px;">Bank: {'OK' if rails.get('bank') else 'NO'} | GST: {'OK' if rails.get('gst') else 'NO'} | MCA: {'OK' if rails.get('mca') else 'NO'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with tel4:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {'#059669' if is_sealed else card_border}; border-radius: 4px; padding: 10px 12px;">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'データルーム' if is_jp else 'DATA ROOM'}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: {'#10B981' if is_sealed else '#94A3B8'}; margin-top: 2px;">
                    {'[SEALED: READY]' if is_sealed else '[WAITING LINKAGE]'}
                </div>
                <div style="font-size: 0.68rem; font-family: monospace; color: #38BDF8; margin-top: 2px;">Passcode: TRUSTVAULT...</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 3: SWITCH TEST COMPANY PRESET
    # -------------------------------------------------------------
    st.markdown(
        f"""
        <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em;">
            {'3. 審査デモ用 対象企業プロファイルの切替' if is_jp else '3. Switch Test Enterprise Profile Across Dashboards'}
        </div>
        """,
        unsafe_allow_html=True
    )

    preset_list = get_all_quick_fill_options()
    preset_dict = {p['preset_key']: p for p in preset_list}
    preset_keys = [p['preset_key'] for p in preset_list]
    cur_idx = preset_keys.index(cur_p) if cur_p in preset_keys else 0

    sel_col1, sel_col2 = st.columns([3, 1])
    with sel_col1:
        chosen_p = st.selectbox(
            "Select Test Scenario Enterprise",
            options=preset_keys,
            format_func=lambda k: f"{preset_dict[k]['name_jp' if is_jp else 'name']} — {preset_dict[k]['cin']}",
            index=cur_idx,
            key="demo_admin_preset_selector",
            label_visibility="collapsed"
        )
    with sel_col2:
        if st.button("全画面へ企業切替適用" if is_jp else "Apply Enterprise to All Dashboards", key="btn_apply_preset_all", use_container_width=True):
            switch_backend_preset(chosen_p)
            st.toast(f"対象企業を {preset_dict[chosen_p]['name']} に切り替えました。" if is_jp else f"Switched active enterprise to {preset_dict[chosen_p]['name']} across all portals!")
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECTION 4: DIRECT LAUNCHPAD TO INDEPENDENT DASHBOARDS
    # -------------------------------------------------------------
    st.markdown(
        f"""
        <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em;">
            {'4. 各独立ダッシュボードへの直接遷移リンク' if is_jp else '4. Direct Launchpad to Independent Dashboards'}
        </div>
        """,
        unsafe_allow_html=True
    )

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 16px; margin-bottom: 8px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri};">
                    {'[創業者ダッシュボード]' if is_jp else '[FOUNDER DASHBOARD]'}
                </div>
                <div style="font-size: 0.70rem; color: {txt_sec}; margin-top: 4px;">
                    {'CIN法人認証、同意承認、および国家データレールの接続' if is_jp else 'MCA-21 discovery, DPDP consent approval, and sovereign rail linkage.'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("開く: 創業者画面" if is_jp else "Open Founder Dashboard", key="demo_nav_founder", use_container_width=True):
            st.session_state['page_state'] = "founder_dashboard"
            st.query_params["view"] = "founder_dashboard"
            try:
                st.switch_page("pages/2_Founder_Dashboard.py")
            except Exception:
                st.rerun()

    with nav2:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 16px; margin-bottom: 8px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri};">
                    {'[投資家ポータル]' if is_jp else '[INVESTOR PORTAL]'}
                </div>
                <div style="font-size: 0.70rem; color: {txt_sec}; margin-top: 4px;">
                    {'Value Create / JETRO 精査要請の発行および企業登記カード' if is_jp else 'Tokyo investor discovery gate, consent dispatch, and unlock.'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("開く: 投資家ポータル" if is_jp else "Open Investor Portal", key="demo_nav_investor", use_container_width=True):
            st.session_state['page_state'] = "gatekeeper"
            st.query_params["view"] = "investor"
            try:
                st.switch_page("pages/1_Investor_Portal.py")
            except Exception:
                st.rerun()

    with nav3:
        st.markdown(
            f"""
            <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 16px; margin-bottom: 8px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri};">
                    {'[個別企業 査定レポート]' if is_jp else '[AUDITED COMPANY DOSSIER]'}
                </div>
                <div style="font-size: 0.70rem; color: {txt_sec}; margin-top: 4px;">
                    {'7項目マスター査定レポート (稟議書、銀行通帳、GST、違反検知)' if is_jp else 'Tokyo Ringi-sho, ReBIT bank ledger, GSTN cross-reconciliation.'}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("開く: 査定レポート" if is_jp else "Open Audited Dossier", key="demo_nav_dossier", use_container_width=True):
            st.session_state['page_state'] = "cockpit"
            st.query_params["view"] = "cockpit"
            try:
                st.switch_page("pages/3_Audited_Company_Dossier.py")
            except Exception:
                st.rerun()
