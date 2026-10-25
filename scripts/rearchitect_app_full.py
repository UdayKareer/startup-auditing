"""Rearchitect frontend/app.py for clean dropdown UI and structured multi-report company view."""
import os

with open("frontend/app.py", "r", encoding="utf-8") as f:
    text = f.read()

# =========================================================
# Part 1: Replace gatekeeper portfolio clutter with dropdown
# =========================================================

# Locate the start of portfolio tabs in gatekeeper
start_marker = "    # Ingestion & Evaluation Portfolio Tabs\n    portfolio_tab0, portfolio_tab1, portfolio_tab2, portfolio_tab3 = st.tabs(["
end_marker = "\nelif st.session_state['page_state'] == 'founder_dashboard':"

pos_start = text.find(start_marker)
pos_end = text.find(end_marker)

if pos_start == -1 or pos_end == -1:
    print(f"Error locating gatekeeper markers: pos_start={pos_start}, pos_end={pos_end}")
    exit(1)

new_gatekeeper_body = """    # ---------------------------------------------------------
    # TARGET ENTERPRISE SELECTION & DILIGENCE CONSENT DISPATCH
    # ---------------------------------------------------------
    st.markdown(
        f\"\"\"
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="font-size: 0.95rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.02em;">
                {'【審査対象企業選定】デューデリジェンス対象スタートアップの選択' if is_jp else '[TARGET PORTFOLIO SELECTION] Select Enterprise for Due Diligence'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-top: 3px;">
                {'審査対象企業をドロップダウンから選択し、公的登記・確定元帳を即時照会します。' if is_jp else 'Select a target enterprise from the portfolio dropdown or enter an Indian Corporate Identification Number (CIN):'}
            </div>
        </div>
        \"\"\",
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
            resolved = lookup_mca_entity(preset_dict[selected_preset]['cin'])
            st.session_state['active_preset'] = selected_preset
            st.session_state['active_cin'] = resolved['cin']
            st.session_state['cin_entity_data'] = resolved
            st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{selected_preset[:4].upper()}-0914"
            st.rerun()

    if selected_preset != cur_p:
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
        f\"\"\"
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.82rem; font-weight: 800; color: {txt_pri};">
                    {'法定精査同意ステータス (DPDP Act 2023 §6 Mandate)' if is_jp else 'Statutory Diligence Consent Mandate (DPDP Act 2023 §6)'}
                </span>
                <span class="{'badge-clean' if is_approved_by_founder else 'badge-review'}">
                    {'[PASS: 創業者承認済]' if is_approved_by_founder else '[STATUS: 同意要請中 / PENDING]'}
                </span>
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; line-height: 1.5; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; padding: 10px 14px; border-radius: 4px; border: 1px solid {card_border}; margin-bottom: 12px;">
                <b>{'要請機関' if is_jp else 'Requesting Entity'}:</b> Value Create Inc. (Tokyo) & JETRO India Startup Desk<br/>
                <b>{'担当責任者' if is_jp else 'Lead Officer'}:</b> Sato Kenji (sato.kenji@value-create.com)<br/>
                <b>{'同意ハンドル' if is_jp else 'Consent Handle'}:</b> <code style="color: #0284C7;">{mandate_handle}</code> • <b>{'要求データ範囲' if is_jp else 'Requested Rails'}:</b> RBI AA Bank Ledger, GSTN Invoices, MCA-21 Books
            </div>
        </div>
        \"\"\",
        unsafe_allow_html=True
    )

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        dispatch_label = "開示同意要請を再送 (Re-Dispatch Request)" if is_approved_by_founder else t("btn_dispatch_consent", lang)
        if st.button(dispatch_label, key="btn_gate_dispatch", type="secondary" if is_approved_by_founder else "primary", use_container_width=True):
            st.session_state['consent_request']['status'] = "DISPATCHED"
            st.session_state['consent_request']['handle'] = mandate_handle
            st.toast("創業者ダッシュボードへDPDP法定同意リクエストを送信しました。" if is_jp else "Diligence consent request dispatched to Founder Dashboard under DPDP Act 2023!")
            st.rerun()

    with act_col2:
        btn_open_dossier_lbl = "【専用査定ページを開く】個別企業監査レポートへ" if is_jp else "[OPEN DEDICATED AUDIT DOSSIER] View Company Reports"
        if st.button(btn_open_dossier_lbl, key="btn_open_dedicated_dossier", type="primary", use_container_width=True):
            st.session_state['active_preset'] = selected_preset
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
"""

text = text[:pos_start] + new_gatekeeper_body + text[pos_end:]
print("Gatekeeper section replaced successfully.")

# =========================================================
# Part 2: In founder_dashboard, make btn_fnd_cockpit go to cockpit
# =========================================================
text = text.replace(
    "st.session_state['page_state'] = 'telemetry'\n            st.query_params[\"view\"] = \"telemetry\"",
    "st.session_state['page_state'] = 'cockpit'\n            st.query_params[\"view\"] = \"cockpit\""
)

# Also ensure passcode unlock goes directly to cockpit instead of developer telemetry
text = text.replace(
    "st.session_state['page_state'] = 'telemetry'\n                    st.query_params[\"view\"] = \"telemetry\"",
    "st.session_state['page_state'] = 'cockpit'\n                    st.query_params[\"view\"] = \"cockpit\""
)

with open("frontend/app.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved updated frontend/app.py successfully.")
