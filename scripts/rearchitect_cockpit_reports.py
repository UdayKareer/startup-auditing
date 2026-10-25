"""Rewrite the cockpit tabs in frontend/app.py into 7 structured accountant-grade reports."""
import re

with open("frontend/app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Locate cockpit tabs start
tab_def_old = """    # Master Diligence Cockpit Tabs
    tab_analytics, tab_reconcile, tab_simulator, tab_redflags, tab_rbac, tab_clarify, tab_ringisho, tab_source = st.tabs([
        t("tab_visual_analytics", lang),
        t("tab_reconciliation", lang),
        t("tab_simulator", lang),
        t("tab_redflags", lang),
        t("tab_rbac", lang),
        t("tab_clarification", lang),
        t("tab_hanko", lang),
        t("tab_ledger_inspector", lang)
    ])"""

# Find where tab_source ends (end of the cockpit state)
# Find the start of tab_source
pos_tab_def = text.find("    # Master Diligence Cockpit Tabs")
if pos_tab_def == -1:
    print("Could not find pos_tab_def")
    exit(1)

# Check text from pos_tab_def to end of file
cockpit_prefix = text[:pos_tab_def]

# New structured cockpit body
new_cockpit_body = """    # Load raw sovereign datasets for accountant inspection
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

    # Master Diligence Cockpit Tabs - 7 Structured Accountant Reports
    report_labels = [
        "1. 投資審査要約 & 稟議書" if is_jp else "1. Executive Summary & Ringi-sho",
        "2. 公的確定預金元帳 (RBI AA)" if is_jp else "2. Audited Bank Statement (ReBIT AA)",
        "3. 政府電子インボイス (GSTN)" if is_jp else "3. Sovereign E-Invoices (GSTR-1/3B)",
        "4. CA公認会計士試算表" if is_jp else "4. CA Trial Balance & AR Aging",
        "5. 法定遵守違反 & 不正指摘" if is_jp else "5. Statutory Violations & Red Flags",
        "6. 4層突合 & 分析チャート" if is_jp else "6. Reconciliation & Analytics",
        "7. 開示権限 & シミュレーション" if is_jp else "7. Privacy & Ledger Sandbox"
    ]

    tab_ringisho, tab_bank, tab_gst, tab_ca, tab_redflags, tab_analytics, tab_rbac = st.tabs(report_labels)

    # ---------------------------------------------------------
    # REPORT 1: TOKYO BOARDROOM RINGI-SHO & PDF EXPORT
    # ---------------------------------------------------------
    with tab_ringisho:
        st.markdown(
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RINGI-SHO MEMO] {t('ringisho_title', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 12px;">
                {t('ringisho_desc', lang)}
            </div>
            \"\"\",
            unsafe_allow_html=True
        )

        st.markdown(
            f\"\"\"
            <div style="background-color: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 18px 22px; margin-bottom: 14px;">
                <div style="text-align: center; border-bottom: 1px solid {card_border}; padding-bottom: 10px; margin-bottom: 12px;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.05em;">
                        【投資審査稟議書】  案件番号: TJH-2026-VC01
                    </div>
                    <div style="font-size: 0.72rem; color: #64748B;">
                        作成日: 2026年10月24日 | 審査機関: 株式会社バリュークリエイト (Value Create Inc. Tokyo)
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.75rem; color: {txt_sec}; margin-bottom: 12px;">
                    <div>
                        <b>1. 対象企業名:</b> {audit_data['company_name']}<br/>
                        <b>2. 企業識別番号 (CIN):</b> <code>{audit_data['cin']}</code><br/>
                        <b>3. 総合判定:</b> <span class="{badge_style}"><b>{kanji_badge} ({verdict_text})</b></span>
                    </div>
                    <div>
                        <b>4. 信頼スコア:</b> <span style="font-size: 1rem; font-weight: 800; color: {score_clr}; font-family: monospace;">{score} / 100</span><br/>
                        <b>5. 実入金確認売上:</b> {format_currency(kpis['real_bank_credits_inr'], currency_mode=curr, lang_mode=lang)}<br/>
                        <b>6. 資金残存月数:</b> {kpis['true_runway_months']} ヶ月 (公的債務控除後)
                    </div>
                </div>
                <div style="font-size: 0.72rem; color: {txt_sec}; background: {'#F8FAFC' if theme_mode == 'light' else '#0F172A'}; border: 1px solid {card_border}; border-radius: 4px; padding: 8px 12px; margin-bottom: 10px;">
                    <b>SHA-256 原簿アンカー:</b> <code>{kpis.get('merkle_root', '0x8f3a1b2c4d5e')}</code>
                </div>
            </div>
            \"\"\",
            unsafe_allow_html=True
        )

        st.markdown(
            f\"<div style='font-size: 0.78rem; font-weight: 700; color: {txt_sec}; margin-bottom: 6px;'>"
            f\"{'稟議書 決裁印鑑レール (5段階調印済み)' if is_jp else 'Tokyo Ringi-sho Approval Seal Rail (5-Stage Certified Sign-off)'}\"
            f\"</div>\",
            unsafe_allow_html=True
        )
        render_hanko_rail(audit_data['hanko_stages'], lang=lang, allow_actions=True, preset_key=preset_key)
        st.markdown(\"<div style='height: 10px;'></div>\", unsafe_allow_html=True)

        pdf_filename = f\"{preset_key}_ringi_sho_memo.pdf\"
        pdf_path = os.path.join(\"export\", pdf_filename)
        try:
            generate_ringi_sho_pdf(audit_data, pdf_path)
            with open(pdf_path, \"rb\") as f:
                pdf_bytes = f.read()
        except Exception as e:
            pdf_bytes = b\"\"
            st.error(f\"Error generating PDF dossier: {str(e)}\")

        d_col1, d_col2 = st.columns([2.5, 1.5])
        with d_col1:
            st.markdown(
                f\"<div style='font-size: 0.74rem; color: #64748B;'>"
                f\"{'公式PDFには、二国間通貨財務表、第188条違反指摘、5連朱肉印、および暗号マークル原簿アンカーが正式収録されています。' if is_jp else 'The generated institutional PDF includes dual-currency financials, statutory findings, 5 Hanko seals, and SHA-256 Merkle anchor.'}\"
                f\"</div>\",
                unsafe_allow_html=True
            )
        with d_col2:
            if pdf_bytes:
                st.download_button(
                    label=t(\"btn_download_pdf\", lang),
                    data=pdf_bytes,
                    file_name=f\"Tokyo_Ringi_Sho_{audit_data['cin']}.pdf\",
                    mime=\"application/pdf\",
                    use_container_width=True,
                    type=\"primary\"
                )

    # ---------------------------------------------------------
    # REPORT 2: AUDITED BANK STATEMENT & GENERAL LEDGER
    # ---------------------------------------------------------
    with tab_bank:
        st.markdown(
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [BANK STATEMENT] {'公的確定預金元帳 (RBI Account Aggregator 照合済)' if is_jp else 'Audited Bank Statement & Cash Inflows/Outflows'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'公的銀行API (ReBIT DEPOSIT v2.0) 経由で取得された全明細。入金 (Cash In) と 出金 (Cash Out) を明確に分離して表示:' if is_jp else 'Direct statutory banking feed via RBI Account Aggregator protocol (ReBIT DEPOSIT v2.0). Itemizes Cash In vs Cash Out with exact posting dates:'}
            </div>
            \"\"\",
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
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [GSTN INVOICE REGISTER] {'政府電子納税申告原本 (GSTR-1 & GSTR-3B 電子インボイス原本)' if is_jp else 'Sovereign Electronic Invoicing Register (GSTR-1 & GSTR-3B)'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'財政省 CBIC / NIC 電子インボイスポータルに登録された正規請求書原本およびGSTR-3B納税相殺状況:' if is_jp else 'Verified outward and inward electronic invoices registered on CBIC / NIC portal with GSTR-3B tax offset status:'}
            </div>
            \"\"\",
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
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [CA TRIAL BALANCE] {'公認会計士 (CA) 監査証明済 試算表 & 売掛金減損スケジュール' if is_jp else 'Chartered Accountant Certified Trial Balance & Ind AS 109 AR Aging'}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 10px;">
                {'インド公認会計士協会 (ICAI) SA 240 / SA 505 基準に基づく試算表およびInd AS 109 Expected Credit Loss減損引当スケジュール:' if is_jp else 'Audited general ledger trial balance and Ind AS 109 3-stage Expected Credit Loss (ECL) debtor aging schedule:'}
            </div>
            \"\"\",
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
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RED FLAGS] {t('tab_redflags', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 12px;">
                {'インド会社法第188条 (関連当事者取引)、所得税法第269ST条/第194C/J条、およびCGST規則に基づく詳細指摘事項:' if is_jp else 'Itemized discrepancy registry evaluated against Companies Act 2013, Income Tax Act 1961, CGST Rules 2017, and ICAI Standards on Auditing:'}
            </div>
            \"\"\",
            unsafe_allow_html=True
        )

        # CA Statutory Decision Console: 4 Critical Pillars
        liquidity_data = audit_data.get('liquidity_contingency') or {}
        bad_debt_data = audit_data.get('bad_debt_provisioning') or {}
        solvency_data = audit_data.get('solvency_covenants') or {}
        circular_data = audit_data.get('circular_debt') or {}

        if liquidity_data or bad_debt_data or solvency_data or circular_data:
            st.markdown(
                f\"<div style='font-size: 0.80rem; font-weight: 800; color: {txt_pri}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;'>"
                f\"{'公認会計士 (CA) 法定判断ツリー & 倒産リスク統制コンソール' if is_jp else 'Chartered Accountant (CA) Statutory Decision Trees & Insolvency Control Console'}\"
                f\"</div>\",
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
                    f\"\"\"
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
                    \"\"\",
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
                    f\"\"\"
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
                    \"\"\",
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
                    f\"\"\"
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
                    \"\"\",
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
                    f\"\"\"
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
                    \"\"\",
                    unsafe_allow_html=True
                )

        discrepancies = audit_data.get('discrepancies_detail') or audit_data.get('discrepancies', [])
        if not discrepancies:
            clean_hdr = "[適格性確認済 ガバナンス合致]" if is_jp else "[CLEAN GOVERNANCE CONCORDANCE]"
            clean_desc = '指摘事項ゼロ。全取引は独立第三者間取引であり、ベンフォード異常値や税務未納は検知されませんでした。' if is_jp else 'Zero statutory violations detected. All transactions reflect arms-length commercial operations, Benford Nigrini MAD is within acceptable bounds, and tax payments match outward billing.'
            st.markdown(
                f\"\"\"
                <div style="background-color: {'rgba(5, 150, 105, 0.12)' if theme_mode == 'dark' else '#ECFDF5'}; border: 1px solid #059669; border-radius: 6px; padding: 18px 20px; color: {'#10B981' if theme_mode == 'dark' else '#059669'};">
                    <b>{clean_hdr}</b> {clean_desc}
                </div>
                \"\"\",
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
                    f\"\"\"
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
                    \"\"\",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f\"<div style='font-size: 0.82rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;'>"
            f\"{'不正疑義取引 ドリルダウン明細表' if is_jp else 'High-Density Forensic Red-Flag Transaction Drilldown Table'}\"
            f\"</div>\",
            unsafe_allow_html=True
        )
        render_redline_table(discrepancies, currency_mode=curr, lang=lang, theme=theme_mode)

    # ---------------------------------------------------------
    # REPORT 6: RECONCILIATION, WATERFALL & ANALYTICS
    # ---------------------------------------------------------
    with tab_analytics:
        st.markdown(
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [RECONCILIATION & WATERFALL] {'ピッチ主張、公認会計士試算表、税務申告書 (GSTR-1)、および銀行確定着金の4層突合' if is_jp else 'Multi-Source Financial Reconciliation, Discrepancy Waterfall & Benford Curves'}
            </div>
            \"\"\",
            unsafe_allow_html=True
        )

        ch1, ch2 = st.columns(2)
        with ch1:
            monthly_records = audit_data.get('monthly_reconciliation', [])
            fig_recon = render_reconciliation_chart(monthly_records, currency_mode=curr, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_recon, use_container_width=True)
        with ch2:
            benford_data = audit_data.get('benford_curve', {})
            fig_benford = render_benford_chart(benford_data, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_benford, use_container_width=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_wf = render_discrepancy_waterfall(audit_data, currency_mode=curr, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_wf, use_container_width=True)
        with col_chart2:
            fig_sankey = render_diligence_sankey_flow(audit_data, currency_mode=curr, lang=lang, theme=theme_mode)
            st.plotly_chart(fig_sankey, use_container_width=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        claimed_arr = kpis['claimed_arr_inr']
        ca_rev = kpis.get('ca_booked_revenue_inr', claimed_arr)
        bank_cash = kpis['real_bank_credits_inr']
        gst_total = kpis.get('gst_invoiced_turnover_inr', ca_rev)

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
            f\"\"\"
            <div style="font-size: 0.85rem; font-weight: 800; color: {txt_pri}; margin-bottom: 4px;">
                [DATA ROOM & RBAC] {t('rbac_title', lang)}
            </div>
            <div style="font-size: 0.74rem; color: {txt_sec}; margin-bottom: 14px;">
                {t('rbac_desc', lang)}
            </div>
            \"\"\",
            unsafe_allow_html=True
        )

        r_c1, r_c2, r_c3 = st.columns(3)
        with r_c1:
            st.markdown(
                f\"\"\"
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'銀行APIプロトコル (RBI AA)' if is_jp else 'BANKING PROTOCOL (RBI AA)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">HDFC Bank Current A/c</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'同意有効期限: 2026-11-30' if is_jp else 'Consent Valid Till 2026-11-30'}</div>
                </div>
                \"\"\",
                unsafe_allow_html=True
            )
        with r_c2:
            st.markdown(
                f\"\"\"
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'税務ネットワーク (GSTN GSP)' if is_jp else 'TAX NETWORK (GSTN GSP)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">GSTR-1 / 3B Daily Sync</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'GSP Webhook 接続中' if is_jp else 'Live GSP Webhook Connected'}</div>
                </div>
                \"\"\",
                unsafe_allow_html=True
            )
        with r_c3:
            st.markdown(
                f\"\"\"
                <div class="card" style="padding: 12px 14px; background-color: {card_bg}; border: 1px solid {card_border};">
                    <div style="font-size: 0.70rem; color: #64748B; font-weight: 700;">{'企業登記レジストリ (MCA-21)' if is_jp else 'CORPORATE REGISTRY (MCA-21)'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">Director DIN & PAN Index</div>
                    <div style="font-size: 0.70rem; color: #059669; font-weight: 600; margin-top: 4px;">● {'MCA-21 API 照合済' if is_jp else 'Direct API Verified Active'}</div>
                </div>
                \"\"\",
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        st.markdown(
            f\"<div style='font-size: 0.78rem; font-weight: 700; color: {txt_sec}; margin-bottom: 8px;'>"
            f\"{t('authorized_vcs_title', lang)}\"
            f\"</div>\",
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
                if inv['status'] == "ACTIVE":
                    if st.button(t("btn_revoke", lang), key=f"btn_revoke_{idx}", use_container_width=True):
                        inv['status'] = "REVOKED"
                        st.toast(f"{inv['investor']} のアクセス権限を取り消しました。" if is_jp else f"Access revoked for {inv['investor']}")
                        st.rerun()
                else:
                    st.markdown("<span class='badge-danger'>[REVOKED]</span>", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Interactive Ledger Sandbox & Mutation
        st.markdown(
            f\"\"\"
            <div style="font-size: 0.80rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;">
                {'対話型元帳サンドボックス (Interactive Ledger Sandbox)' if is_jp else 'Interactive Ledger Sandbox & Scenario Testing'}
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; margin-bottom: 8px;">
                {'元帳の取引金額や相手先GSTINを編集してリアルタイムで突合検知を検証します。' if is_jp else 'Modify transactions below to test live anomaly detection, Benford re-calibration, and Shinrai trust score recalculation:'}
            </div>
            \"\"\",
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
"""

# Reassemble the file
final_text = cockpit_prefix + new_cockpit_body

with open("frontend/app.py", "w", encoding="utf-8") as f:
    f.write(final_text)

print("Cockpit successfully restructured into 7 structured accountant-grade reports.")
