"""
Bilingual Translation & Formatting Engine for VeriLedger / Kizuna-Vault (絆)
Supports English (EN) and Japanese (JP / 日本語 - Tokyo Boardroom Mode).
Standardized for Value Create Inc. (Tokyo), JETRO, and Japan-India Cross-Border Diligence.
Strictly adheres to Institutional Anti-AI-Slop standard: Zero emojis, pure slate typography.
"""

from typing import Dict, Any, Union

FX_INR_TO_JPY = 1.80

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Brand & Navigation
    "app_title": {
        "en": "VERILEDGER (絆) | KIZUNA-VAULT",
        "jp": "VERILEDGER (絆) | キズナ・ヴォールト"
    },
    "app_subtitle": {
        "en": "Sovereign India-Japan Cross-Border Startup Diligence Engine",
        "jp": "日印クロスボーダー・スタートアップ財務・ガバナンス即時精査エンジン"
    },
    "partner_tag": {
        "en": "OFFICIAL EVALUATION RAIL: VALUE CREATE INC. (TOKYO) × JETRO",
        "jp": "公式審査機関: 株式会社バリュークリエイト (東京) × JETRO"
    },
    "dpi_status_badge": {
        "en": "[DPI ACTIVE] 4 SOVEREIGN DPI RAILS VERIFIED",
        "jp": "[DPI稼働] 4系統のインド国家DPI公的データ連携中 (検証済)"
    },
    "currency_toggle_inr": {
        "en": "Currency: ₹ INR (Crores / Lakhs)",
        "jp": "表示通貨: ₹ インドルピー (クロール / ラク)"
    },
    "currency_toggle_jpy": {
        "en": "Currency: ¥ JPY (億円 / 万円 @ 1.80)",
        "jp": "表示通貨: ¥ 日本円 (億円 / 万円 @ 1.80)"
    },
    "theme_toggle_light": {
        "en": "Theme: Pure White (Carta/Stripe)",
        "jp": "表示テーマ: ピュアホワイト (Stripe/Carta基準)"
    },
    "theme_toggle_dark": {
        "en": "Theme: Obsidian Dark (Bloomberg)",
        "jp": "表示テーマ: 黒曜石ダーク (端末モード)"
    },
    "lang_toggle_en": {
        "en": "Language: English",
        "jp": "言語: English"
    },
    "lang_toggle_jp": {
        "en": "Language: 日本語 (Tokyo Mode)",
        "jp": "言語: 日本語 (東京審議モード)"
    },
    "back_to_landing": {
        "en": "← Back to Portal / Switch Target",
        "jp": "← ポータルに戻る / 対象企業切替"
    },
    "re_audit": {
        "en": "[AUDIT] Re-Run Forensic Audit",
        "jp": "[再監査] 精査エンジン再実行"
    },

    # State 0: Gatekeeper View
    "gatekeeper_title": {
        "en": "CRYPTOGRAPHIC INVESTOR GATEKEEPER & ACCESS HANDSHAKE",
        "jp": "暗号化投資家ゲートキーパー & アクセス認証ハンドシェイク"
    },
    "gatekeeper_subtitle": {
        "en": "Under DPDP Act 2023 & RBI Account Aggregator regulations, unredacted corporate financial ledgers require time-bound cryptographic authorization.",
        "jp": "2023年デジタル個人データ保護法 (DPDP法) およびRBIアカウント・アグリゲーター規則に基づき、未加工財務元帳の閲覧には時限暗号アクセス権限が必要です。"
    },
    "passcode_label": {
        "en": "Ephemeral Handshake Passcode",
        "jp": "時限ハンドシェイク・パスコード"
    },
    "passcode_help": {
        "en": "Enter authorized passcode (Default for Value Create & JETRO: TRUSTVAULT-VC901-TJH)",
        "jp": "承認済パスコードを入力 (バリュークリエイト/JETRO審査用: TRUSTVAULT-VC901-TJH)"
    },
    "investor_email_label": {
        "en": "Corporate Institutional Email",
        "jp": "審査機関コーポレートメール"
    },
    "investor_role_label": {
        "en": "Investment Committee Role",
        "jp": "投資委員会役職"
    },
    "btn_unlock_dossier": {
        "en": "[DECRYPT & UNLOCK] AUDIT DOSSIER (審議データ復号)",
        "jp": "[復号・開示] デューデリジェンス調書の閲覧開始"
    },
    "btn_quick_fill": {
        "en": "[QUICK-FILL] Tokyo Committee Credentials",
        "jp": "[自動入力] 東京投資委員会 認証情報"
    },
    "merkle_anchor_label": {
        "en": "Sovereign SHA-256 Merkle Root Proof",
        "jp": "国家DPI SHA-256 マークルツリー原簿アンカー"
    },
    "merkle_desc": {
        "en": "Anchors banking, tax, and corporate registry snapshots preventing retrospective ledger tampering or invoice fabrications.",
        "jp": "銀行取引、税務申告、商業登記のスナップショットを暗号固定し、遡及的な元帳改ざんや架空請求を数学的に防止します。"
    },

    # Anonymized Teaser
    "teaser_title": {
        "en": "ANONYMIZED DISCLOSURE TEASER (Pre-Access Inspection)",
        "jp": "匿名化事前開示ティーザー (アクセス承認前概要)"
    },
    "operating_vintage": {
        "en": "Operating Vintage",
        "jp": "創業期間"
    },
    "sector_classification": {
        "en": "Target Sector",
        "jp": "事業分野"
    },
    "revenue_bracket": {
        "en": "Annual Turnover Bracket",
        "jp": "年間売上規模"
    },
    "verified_accounts": {
        "en": "Verified DPI Accounts",
        "jp": "検証済公的口座"
    },
    "pii_masking_notice": {
        "en": "Vendor names, counterparty PANs, and itemized debit lines are blinded via SHA-256 salt until unlocked.",
        "jp": "取引先名称、相手方PAN、個票明細はアクセス解除までSHA-256ソルトにより完全匿名化されています。"
    },

    # Portfolio Presets
    "portfolio_tab_discovery": {
        "en": "Entity Discovery & Bilateral Handshake (MCA-21)",
        "jp": "法人登記照会 & 二国間同意ハンドシェイク (MCA-21)"
    },
    "portfolio_tab1": {
        "en": "Target Case Study Portfolio (Pre-Loaded DPI Concordance)",
        "jp": "審査対象スタートアップ・ポートフォリオ (公的データ連携済)"
    },
    "portfolio_tab2": {
        "en": "Sovereign Data Room Ingestion Hub & Custom Upload",
        "jp": "国家公的データルーム受入ハブ & 新規元帳アップロード"
    },
    "portfolio_tab3": {
        "en": "Interactive Diligence Simulator & Anomaly Sandbox",
        "jp": "インタラクティブ精査シミュレーター & 異常値サンドボックス"
    },

    # DPI Badges
    "dpi_rbi": {
        "en": "BANKING PROTOCOL (RBI AA)",
        "jp": "銀行送金プロトコル (RBI AA)"
    },
    "dpi_rbi_desc": {
        "en": "ReBIT DEPOSIT v2.0 • X.509 Signed • Curve25519",
        "jp": "ReBIT v2.0準拠 • X.509電子署名 • 暗号通信"
    },
    "dpi_gst": {
        "en": "TAX NETWORK (GSTN GSP)",
        "jp": "税務ネットワーク (GSTN GSP)"
    },
    "dpi_gst_desc": {
        "en": "CBIC Notif. 04/2023 • NIC E-Invoice QR Verified",
        "jp": "財政省通達04/2023準拠 • NIC電子インボイスQR照合"
    },
    "dpi_mca": {
        "en": "CORPORATE REGISTRY (MCA-21)",
        "jp": "商業登記ネットワーク (MCA-21)"
    },
    "dpi_mca_desc": {
        "en": "Direct DIN / Director PAN Cross-Match Active",
        "jp": "取締役DIN・PAN番号直接照合済"
    },
    "dpi_ca": {
        "en": "STATUTORY AUDIT LEDGER",
        "jp": "法定監査済み元帳 (CA)"
    },
    "dpi_ca_desc": {
        "en": "Certified Trial Balance & Aging Schedule",
        "jp": "公認会計士認証 合計残高試算表・売掛金年齢表"
    },

    # Telemetry View (State 1)
    "telemetry_title": {
        "en": "SUB-200ms PARALLEL FORENSIC ENGINE TELEMETRY TRACE",
        "jp": "200ミリ秒並列マイクロサービス実行テレメトリー"
    },
    "telemetry_subtitle": {
        "en": "Executing deterministic reconciliations across banking, taxation, corporate filings, and statistical anomaly detectors.",
        "jp": "銀行取引、税務申告、会社法登記、統計的外れ値検知エンジンをマイクロ秒単位で並列実行中。"
    },
    "btn_proceed_cockpit": {
        "en": "Enter Master Diligence Cockpit →",
        "jp": "マスター精査コックピットへ進む →"
    },

    # State 2: Cockpit KPIs
    "kpi_shinrai": {
        "en": "OVERALL TRUST SCORE (0-100)",
        "jp": "総合信頼度スコア (SHINRAI TRUST SCORE)"
    },
    "kpi_shinrai_desc": {
        "en": "Overall health score: checks if the company follows tax laws, deposits real cash in the bank, and has zero founder fraud.",
        "jp": "総合安全性スコア: 銀行への実入金、税務申告の整合性、創業者による資金私的流出ゼロを100点満点で総合判定。"
    },
    "kpi_realization": {
        "en": "REAL CASH IN BANK (vs PITCH DECK SALES)",
        "jp": "実際の売上入金率 (本当に現金が入ったか)"
    },
    "kpi_realization_desc": {
        "en": "Percentage of claimed sales that actually arrived in the bank as real cash. Catches fake, circular, or uncollected revenue.",
        "jp": "ピッチで主張した売上が実際に銀行口座に入金された割合。架空売上や未回収の粉飾請求書を即座に見抜きます。"
    },
    "kpi_runway": {
        "en": "REAL SURVIVAL RUNWAY (MONTHS LEFT)",
        "jp": "実質キャッシュ寿命 (会社が存続できる月数)"
    },
    "kpi_runway_desc": {
        "en": "How many months the company can actually survive after deducting all unpaid government tax bills and debts (not what the pitch claims).",
        "jp": "未払いの国税・源泉徴収税・負債を銀行残高から即時差し引いた、会社が真に事業を継続できる実質残存月数。"
    },
    "kpi_conflict": {
        "en": "FOUNDER MONEY SIPHONING & FRAUD CHECK",
        "jp": "創業者への資金抜き・私的流用チェック"
    },
    "kpi_conflict_desc": {
        "en": "Checks if founders are secretly transferring company money into personal accounts or family shell companies (Companies Act Sec 188).",
        "jp": "創業者や役員が会社のお金を自分の個人口座やダミー会社へこっそり送金（利益相反・資金抜き）していないかを検証。"
    },

    # Kanji Badges
    "badge_clean": {
        "en": "[適格] VERIFIED CLEAN",
        "jp": "[適格] 投資適格・コンプライアンス適合"
    },
    "badge_review": {
        "en": "[要確認] REQUIRES REVIEW",
        "jp": "[要確認] 精査中・追加資料提出要請"
    },
    "badge_danger": {
        "en": "[精査要] CRITICAL RED FLAG",
        "jp": "[精査要] 重大リスク・投資見送り推奨"
    },

    # Cockpit Tabs
    "tab_summary": {
        "en": "Executive Summary & Audit Trail",
        "jp": "経営総括 & 監査証跡"
    },
    "tab_visual_analytics": {
        "en": "Visual Analytics & Diligence Cascade",
        "jp": "財務視覚分析 & 乖離カスケード"
    },
    "tab_reconciliation": {
        "en": "4-Way Multi-Source Financial Convergence",
        "jp": "4元データ収束検証表 (売上突合)"
    },
    "tab_redflags": {
        "en": "Itemized Statutory Red Flags Feed",
        "jp": "法定違反項目一覧 (レッドフラグ)"
    },
    "tab_simulator": {
        "en": "What-If Stress Testing & Anomaly Sandbox",
        "jp": "仮定ストレステスト & 異常値サンドボックス"
    },
    "tab_hanko": {
        "en": "Tokyo Boardroom Ringi-sho (稟議書)",
        "jp": "東京投資委員会 稟議書 (決裁印レール)"
    },
    "tab_rbac": {
        "en": "Founder DPDP Data Room & Access Manager",
        "jp": "創業者DPDPデータルーム & 権限管理"
    },
    "tab_clarification": {
        "en": "Human-in-the-Loop Clarification Panel",
        "jp": "創業者弁明・取締役会決議書提出"
    },
    "tab_ledger_inspector": {
        "en": "Ground Truth Source Ledger Inspector",
        "jp": "原本データ・元帳インスペクター"
    },

    # Hanko Seals / Governance Sign-Off Chain
    "hanko_rail_title": {
        "en": "5-STAGE DILIGENCE APPROVAL CHAIN | VALUE CREATE INC. & JETRO",
        "jp": "5段階デューデリジェンス決裁承認チェーン (VALUE CREATE INC. & JETRO 東京稟議基準)"
    },
    "hanko_drafter": {
        "en": "1. Drafter (起案)",
        "jp": "1. 起案 (国際投資担当)"
    },
    "hanko_reviewer": {
        "en": "2. Reviewer (審査)",
        "jp": "2. 審査 (法務・コンプライアンス)"
    },
    "hanko_auditor": {
        "en": "3. Forensic Auditor (精査)",
        "jp": "3. 精査 (財務DD・フォレンジック)"
    },
    "hanko_committee": {
        "en": "4. Committee (合議)",
        "jp": "4. 合議 (投資戦略委員会)"
    },
    "hanko_final": {
        "en": "5. Final Approver (決裁)",
        "jp": "5. 決裁 (代表取締役 / 統轄パートナー)"
    },
    "stamp_action_approve": {
        "en": "Stamp [APPROVED]",
        "jp": "【承認】押印"
    },
    "stamp_action_reject": {
        "en": "Stamp [FLAGGED / HOLD]",
        "jp": "【保留/精査】押印"
    },

    # Statutory Discrepancies
    "when_label": {
        "en": "WHEN (Date / Time Window)",
        "jp": "発生日時・会計期"
    },
    "where_label": {
        "en": "WHERE (Counterparty & Account Head)",
        "jp": "発生場所 (取引先・勘定科目)"
    },
    "what_why_label": {
        "en": "WHAT & WHY (Forensic Mechanism)",
        "jp": "指摘内容・手口詳細"
    },
    "citation_label": {
        "en": "STATUTORY CITATION",
        "jp": "根拠法令・条項"
    },
    "remediation_label": {
        "en": "TOKYO BOARDROOM REMEDIATION ACTION",
        "jp": "東京投資委員会 推奨対応策"
    },
    "monetary_exposure": {
        "en": "Monetary Exposure",
        "jp": "財務影響額"
    },

    # RBAC & Privacy
    "rbac_title": {
        "en": "FOUNDER-GATED DATA ROOM MANAGER (DPDP ACT 2023 COMPLIANT)",
        "jp": "創業者主導データルーム管理 (インド2023年DPDP法準拠)"
    },
    "rbac_desc": {
        "en": "The startup founder controls read permissions. Revoke or grant access tokens dynamically without leaking PII.",
        "jp": "閲覧権限はスタートアップ創業者が完全管理します。個人情報や取引先機密を漏洩することなく、投資家ごとの権限付与・即時剥奪が可能です。"
    },
    "active_connections_title": {
        "en": "Active Sovereign Data Connections",
        "jp": "接続中 国家公的APIデータ連携"
    },
    "authorized_vcs_title": {
        "en": "Authorized Japanese Investors & Committee Members",
        "jp": "承認済 日本側投資家・審査機関一覧"
    },
    "public_badge_title": {
        "en": "Public Clean Governance Trust Badge (Zero-Knowledge Embed)",
        "jp": "ゼロ知識証明型 クリーンガバナンス公開バッジ"
    },
    "btn_revoke": {
        "en": "[REVOKE ACCESS]",
        "jp": "[権限失効]"
    },
    "btn_invite_vc": {
        "en": "+ Issue New Investor Access Token",
        "jp": "+ 新規投資家トークン発行"
    },

    # Clarification
    "clarification_title": {
        "en": "HUMAN-IN-THE-LOOP CLARIFICATION & BOARD RESOLUTION FILING",
        "jp": "創業者弁明・取締役会決議書 (Form MGT-14) 提出ポータル"
    },
    "clarification_desc": {
        "en": "Prevent legitimate fast-moving companies from being killed by false positives. Upload Audit Committee pre-approvals or vendor agreements directly into the Tokyo diligence memo.",
        "jp": "誤検知による優良企業の投資見送りを防ぐため、取締役会決議書や正当な業務委託契約書をアップロードし、東京投資委員会へ直接弁明できます。"
    },
    "btn_submit_clarification": {
        "en": "Submit to Tokyo Committee Review Queue",
        "jp": "東京投資委員会 審査キューへ提出"
    },

    # Ringi-sho Export
    "ringisho_title": {
        "en": "INVESTMENT DUE DILIGENCE RINGI-SHO (投資審査稟議書)",
        "jp": "投資審査稟議書 (Value Create Inc. / JETRO 提出用)"
    },
    "ringisho_desc": {
        "en": "Generates an institutional 1-page bilingual boardroom diligence circular with dual-currency financials, statutory citations, corporate governance sign-off matrix, and cryptographic Merkle proof.",
        "jp": "日印二国間通貨表記、法令根拠、ガバナンス決裁マトリクス、およびSHA-256マークルツリー原簿署名を網羅した公式1ページ投資稟議書PDFを出力します。"
    },
    "btn_download_pdf": {
        "en": "[EXPORT PDF] Tokyo Boardroom Ringi-sho Dossier",
        "jp": "[PDF出力] 東京投資委員会 提出用稟議書"
    },

    # Waterfall Diligence Cascade
    "waterfall_title": {
        "en": "DISCREPANCY DILIGENCE CASCADE (PITCH CLAIMS → SOVEREIGN CASH)",
        "jp": "乖離流動性カスケード (主張売上 → 国家公的預金残高)"
    },
    "waterfall_subtitle": {
        "en": "Visual audit trail illustrating how phantom claims are peeled back through GST invoices down to unencumbered cleared bank deposits.",
        "jp": "ピッチ資料の主張売上から、架空売上・税務申告・取締役流出・公的税額がどのように差し引かれ真の現預金に着地するかを示す監査証跡。"
    },
    "wf_pitch_claim": {
        "en": "1. Pitch Claimed ARR",
        "jp": "1. ピッチ主張ARR"
    },
    "wf_unbilled_gap": {
        "en": "Less: Unbilled / Phantom Pitch Gap",
        "jp": "控除: 未請求・架空売上ギャップ"
    },
    "wf_gst_declared": {
        "en": "2. Sovereign GSTN Turnover",
        "jp": "2. 税務当局申告売上 (GSTR-1)"
    },
    "wf_uncollected_gap": {
        "en": "Less: Uncollected Bank Gap",
        "jp": "控除: 未回収・未着金ギャップ"
    },
    "wf_cleared_cash": {
        "en": "3. Cleared Bank Deposits",
        "jp": "3. 確定銀行預金入金 (ReBIT AA)"
    },
    "wf_sec188_leak": {
        "en": "Less: Sec 188 Promoter Leak",
        "jp": "控除: 取締役利益相反流出"
    },
    "wf_tax_dues": {
        "en": "Less: Unremitted Tax Dues",
        "jp": "控除: 未納公的税務債務"
    },
    "wf_true_cash": {
        "en": "4. True Operational Net Cash",
        "jp": "4. 実質純運転資金"
    },

    # Diligence Simulator
    "simulator_title": {
        "en": "INTERACTIVE DILIGENCE SIMULATOR & WHAT-IF STRESS TESTING",
        "jp": "インタラクティブ精査シミュレーター & 仮定ストレステスト"
    },
    "simulator_subtitle": {
        "en": "Dynamically adjust founder pitch claims and toggle forensic anomaly injections to observe real-time recalculation of Shinrai Trust Score, governance sign-offs, and cash divergence.",
        "jp": "創業者ピッチ主張数値を動的調整し、各不正異常値注入を切り替えることで、信頼スコア・合議決裁・現預金乖離率の即時再計算を検証できます。"
    },
    "sim_claimed_arr": {
        "en": "Claimed ARR Target (INR)",
        "jp": "主張年間売上 ARR (INR)"
    },
    "sim_claimed_burn": {
        "en": "Monthly Burn Rate (INR)",
        "jp": "月間キャッシュバーン (INR)"
    },
    "sim_claimed_runway": {
        "en": "Claimed Runway (Months)",
        "jp": "主張資金残存期間 (月数)"
    },
    "sim_toggle_siphoning": {
        "en": "Section 188 Promoter Siphoning (₹41.3L to Director PAN)",
        "jp": "会社法188条 取締役利益相反送金 (一致PANへ₹41.3L)"
    },
    "sim_toggle_window": {
        "en": "Month-End Contra Window Dressing (₹25.0L temporary infusion)",
        "jp": "期末決算粉飾コントラ入金 (₹25.0Lの一時流動性水増し)"
    },
    "sim_toggle_tax": {
        "en": "GSTR-3B Tax Evasion / Unremitted Liability (₹18.4L)",
        "jp": "GST未納税金債務 (₹18.4Lの公的債務控除)"
    },
    "sim_toggle_benford": {
        "en": "Benford F2D Digit Structuring (25 debits @ ₹49,500 under TDS limit)",
        "jp": "ベンフォードF2D構造化送金 (源泉徴収回避 49,500ルピー×25件)"
    },
    "sim_toggle_debtors": {
        "en": "Stale Doubtful Receivables > 180 Days (₹1.2 Cr credit impairment)",
        "jp": "180日超 滞留不良売掛金 (₹1.2億の減損処理)"
    },
    "sim_btn_apply": {
        "en": "Run Live What-If Re-Audit",
        "jp": "リアルタイム仮定監査を実行"
    },
    "sim_btn_reset": {
        "en": "Reset to Baseline",
        "jp": "基準値にリセット"
    },

    # Ingestion Hub
    "dataroom_validator_title": {
        "en": "SOVEREIGN DATA ROOM INGESTION HUB & SCHEMA VALIDATOR",
        "jp": "国家公的データルーム受入ハブ & スキーマ検証"
    },
    "dataroom_validator_desc": {
        "en": "Drop raw sovereign ledgers for instant parsing, cryptographic hash verification, and row count indexing.",
        "jp": "公的元帳を投入し、スキーマ即時検証、暗号ハッシュ照合、および行数インデックスを実行します。"
    },

    # KPI Subtitle & Badge Translations
    "kpi_phantom_gap_label": {
        "en": "Uncollected / Fake Sales:",
        "jp": "未入金・架空売上乖離:"
    },
    "kpi_cash_matched_label": {
        "en": "100% Real Cash in Bank:",
        "jp": "100% 銀行着金確認:"
    },
    "kpi_months_label": {
        "en": "Months",
        "jp": "ヶ月"
    },
    "kpi_claimed_label": {
        "en": "Pitch Deck Claimed",
        "jp": "ピッチ記載主張"
    },
    "kpi_net_tax_dues_label": {
        "en": "Unpaid Tax Bills",
        "jp": "未払国税債務"
    },
    "kpi_conflict_alert_badge": {
        "en": "MONEY LEAK ALERT",
        "jp": "不正流出検知"
    },
    "kpi_conflict_clean_badge": {
        "en": "100% CLEAN",
        "jp": "流出ゼロ・正常"
    },
    "kpi_conflict_exposure_label": {
        "en": "Secret Siphoned Money:",
        "jp": "創業者への不正流出額:"
    },
    "kpi_conflict_clean_label": {
        "en": "Zero Money Siphoning (100% Legitimate Vendors)",
        "jp": "個人口座への不正送金ゼロ (正常な外部取引先)"
    },
    "kpi_verified_badge": {
        "en": "VERIFIED",
        "jp": "検証済"
    },
    "kpi_real_badge": {
        "en": "REAL",
        "jp": "実質"
    },

    # 4-Way Reconciliation Table
    "recon_col_layer": {
        "en": "Diligence Layer",
        "jp": "検証レイヤー"
    },
    "recon_col_source": {
        "en": "Source System",
        "jp": "情報源システム"
    },
    "recon_col_turnover": {
        "en": "Turnover",
        "jp": "売上規模"
    },
    "recon_col_variance": {
        "en": "Variance vs Ground Truth Bank Cash",
        "jp": "確定銀行着金との乖離率"
    },
    "recon_layer_pitch": {
        "en": "1. Pitch Deck Claimed ARR",
        "jp": "1. ピッチ資料 主張ARR"
    },
    "recon_source_pitch": {
        "en": "Founder Pitch Deck PDF Claims",
        "jp": "創業者自己申告ピッチ資料"
    },
    "recon_layer_ca": {
        "en": "2. Startup CA Books (General Ledger)",
        "jp": "2. スタートアップCA元帳 (合計残高試算表)"
    },
    "recon_source_ca": {
        "en": "Zoho/Tally Certified Trial Balance",
        "jp": "公認会計士認証 試算表売上台帳"
    },
    "recon_layer_gst": {
        "en": "3. Government GSTN (GSTR-1 Invoiced)",
        "jp": "3. 国家GSTN税務申告 (GSTR-1確定インボイス)"
    },
    "recon_source_gst": {
        "en": "CBIC Sovereign Tax Return (GSTR-1 / 3B)",
        "jp": "財政省CBIC公的納税申告書 (GSTR-1/3B)"
    },
    "recon_layer_bank": {
        "en": "4. Cleared Bank Cash (RBI Account Aggregator)",
        "jp": "4. 確定銀行預金着金 (中央銀行AA原本)"
    },
    "recon_source_bank": {
        "en": "HDFC / ICICI Sovereign Bank Ledger",
        "jp": "HDFC/ICICI 銀行公的電子的預金元帳"
    },
    "recon_baseline_note": {
        "en": "0.0% (Ground Truth Baseline)",
        "jp": "0.0% (確定基準現預金・真正ベースライン)"
    },

    # Working Capital & Solvency Cards
    "wc_ccc_title": {
        "en": "CASH CONVERSION CYCLE (CCC)",
        "jp": "資金回収サイクル (CCC)"
    },
    "wc_ccc_status": {
        "en": "Conforming with Industry Standard",
        "jp": "業界標準適合 (適正水準)"
    },
    "wc_dso_title": {
        "en": "DAYS SALES OUTSTANDING (DSO)",
        "jp": "売掛金回転日数 (DSO)"
    },
    "wc_dso_status": {
        "en": "Normalized Collection Cycle",
        "jp": "標準回収サイクル内"
    },
    "wc_dscr_title": {
        "en": "DEBT SERVICE COVERAGE (DSCR)",
        "jp": "元利金返済カバー倍率 (DSCR)"
    },
    "wc_dscr_status": {
        "en": "No Covenant Breach (>1.25x)",
        "jp": "コベナンツ遵守 (>1.25倍)"
    },
    "recon_layer_1_name": {
        "en": "1. Pitch Deck Claimed ARR",
        "jp": "1. ピッチ資料 主張ARR"
    },
    "recon_layer_1_src": {
        "en": "Founder Pitch Deck PDF Claims",
        "jp": "創業者自己申告ピッチ資料"
    },
    "recon_layer_2_name": {
        "en": "2. Startup CA Books (General Ledger)",
        "jp": "2. スタートアップCA元帳 (合計残高試算表)"
    },
    "recon_layer_2_src": {
        "en": "Zoho/Tally Certified Trial Balance",
        "jp": "公認会計士認証 試算表売上台帳"
    },
    "recon_layer_3_name": {
        "en": "3. Government GSTN (GSTR-1 Invoiced)",
        "jp": "3. 国家GSTN税務申告 (GSTR-1確定インボイス)"
    },
    "recon_layer_3_src": {
        "en": "CBIC Sovereign Tax Return (GSTR-1 / 3B)",
        "jp": "財政省CBIC公的納税申告書 (GSTR-1/3B)"
    },
    "recon_layer_4_name": {
        "en": "4. Cleared Bank Cash (RBI Account Aggregator)",
        "jp": "4. 確定銀行預金着金 (中央銀行AA原本)"
    },
    "recon_layer_4_src": {
        "en": "HDFC / ICICI Sovereign Bank Ledger",
        "jp": "HDFC/ICICI 銀行公的電子的預金元帳"
    },
    "wc_quick_title": {
        "en": "QUICK RATIO & SOLVENCY",
        "jp": "当座比率・支払能力 (SOLVENCY)"
    },
    "wc_quick_status": {
        "en": "Zero IBC Insolvency Risk",
        "jp": "倒産破産法 (IBC) リスク無"
    },
    "wc_quick_ratio_title": {
        "en": "QUICK RATIO & SOLVENCY",
        "jp": "当座比率・支払能力 (SOLVENCY)"
    },
    "wc_quick_ratio_status": {
        "en": "Zero IBC Insolvency Risk",
        "jp": "倒産破産法 (IBC) リスク無"
    },

    # RBAC Buttons
    "btn_manage_aa": {
        "en": "Manage AA Consent",
        "jp": "AA同意権限を管理"
    },
    "btn_resync_gst": {
        "en": "Force Re-Sync GSTN",
        "jp": "GSTN税務データ再同期"
    },
    "btn_verify_roc": {
        "en": "Verify ROC Filings",
        "jp": "MCA-21登記情報を再検証"
    },

    # Clarification
    "upload_board_doc": {
        "en": "Upload Supporting Board Document (PDF / Form MGT-14)",
        "jp": "取締役会決議書・証憑提出 (PDF / Form MGT-14)"
    },
    "founder_statement_label": {
        "en": "Founder Diligence Statement / Commercial Justification",
        "jp": "創業者弁明書・商取引正当性説明"
    },
    "clarification_placeholder": {
        "en": "Explain commercial substance, Audit Committee pre-approval date, or board resolution number...",
        "jp": "取引の商業的合理性、監査委員会事前承認日、または取締役会決議番号を記載してください..."
    },
    "clarification_audit_trail": {
        "en": "Clarification Audit Trail",
        "jp": "弁明・追加提出ステータス証跡"
    },
    "no_clarifications": {
        "en": "No pending clarifications filed yet.",
        "jp": "提出済みの弁明書はありません。"
    },

    # Common Cockpit Buttons
    "btn_reaudit_cockpit": {
        "en": "[AUDIT] Re-Audit",
        "jp": "[再監査] 再精査実行"
    },
    "btn_back_to_portal": {
        "en": "← Back to Portal / Switch Target",
        "jp": "← ポータルに戻る / 対象企業切替"
    },

    # Dual Persona Switcher & Handshake Navigation
    "role_investor": {
        "en": "[INVESTOR] Diligence Rail",
        "jp": "[投資家] 審査レール"
    },
    "role_founder": {
        "en": "[FOUNDER] Startup Dashboard",
        "jp": "[創業者] スタートアップダッシュボード"
    },
    "role_cockpit": {
        "en": "[COCKPIT] Master Diligence Cockpit",
        "jp": "[審査] マスター財務・ガバナンス審査コックピット"
    },
    "role_telemetry": {
        "en": "[TELEMETRY] Ingestion Telemetry Trace",
        "jp": "[テレメトリー] リアルタイム取込テレメトリー"
    },
    "pipeline_step1": {
        "en": "1. Entity Discovery (CIN)",
        "jp": "1. 法人照会 (CIN)"
    },
    "pipeline_step2": {
        "en": "2. Consent Request",
        "jp": "2. 同意要請"
    },
    "pipeline_step3": {
        "en": "3. Approval & Linkage",
        "jp": "3. 承認 & 口座連携"
    },
    "pipeline_step4": {
        "en": "4. Sealed Cockpit",
        "jp": "4. 暗号化開示"
    },

    # Founder Dashboard & Step 1
    "founder_dashboard_title": {
        "en": "STARTUP FOUNDER DASHBOARD & DPI CONSENT VAULT",
        "jp": "スタートアップ創業者ダッシュボード & 国家DPI同意管理ヴォールト"
    },
    "founder_dashboard_subtitle": {
        "en": "Auto-discover MCA-21 registry records, review bilateral investor diligence requests, and link Account Aggregator (AA) to GSTIN and corporate ledgers.",
        "jp": "法人番号 (CIN) を入力して商業登記情報を自動照会し、東京審査機関からの精査同意リクエストの承認および銀行AA元帳・GST税務申告の連携を実行します。"
    },
    "step1_header": {
        "en": "STEP 1: UNIQUE ENTITY IDENTIFIER ENTRY (MCA-21 DISCOVERY)",
        "jp": "ステップ1: 法人番号入力 & 商業登記・税務・銀行の自動照会"
    },
    "step1_sub": {
        "en": "Enter unique corporate CIN number to fetch legal name, directors, capital, and tax/banking identifiers.",
        "jp": "法人番号 (CIN) を入力して登記上の会社名、取締役、資本金、GSTINおよび銀行口座情報を一括照会します。"
    },
    "cin_input_label": {
        "en": "Corporate Identification Number (CIN)",
        "jp": "法人識別番号 (CIN)"
    },
    "cin_input_help": {
        "en": "21-character alphanumeric Indian corporate registration number.",
        "jp": "インド企業省 (MCA-21) 発行の21桁法人識別番号。"
    },
    "btn_discover_entity": {
        "en": "[DISCOVER] Auto-Discover Entity Details",
        "jp": "[自動照会] 法人登記・税務・銀行情報を自動照会"
    },
    "quick_fill_header": {
        "en": "1-Click Quick Fill Registered Presets:",
        "jp": "ワンクリック迅速照会プリセット:"
    },

    # Discovered Entity Details Card
    "discovered_card_title": {
        "en": "MCA-21 MASTER REGISTRY PROFILE (VERIFIED ACTIVE)",
        "jp": "MCA-21 商業登記マスター情報 (公的確認済・有効)"
    },
    "lbl_company_name": {
        "en": "Company Legal Name",
        "jp": "法人正式名称"
    },
    "lbl_cin": {
        "en": "CIN Number",
        "jp": "法人番号 (CIN)"
    },
    "lbl_incorp_date": {
        "en": "Incorporation Date",
        "jp": "設立年月日"
    },
    "lbl_roc_office": {
        "en": "ROC Registry Jurisdiction",
        "jp": "管轄登記所 (ROC)"
    },
    "lbl_reg_address": {
        "en": "Registered Office Address",
        "jp": "登記上本店所在地"
    },
    "lbl_auth_paid_capital": {
        "en": "Authorized / Paid-up Capital",
        "jp": "授権資本 / 払込資本"
    },
    "lbl_directors": {
        "en": "Directors & Authorized Signatories",
        "jp": "取締役・公式署名権者一覧"
    },
    "lbl_registered_gstin": {
        "en": "Registered GSTIN",
        "jp": "登録GSTIN番号"
    },
    "lbl_primary_bank_fip": {
        "en": "Primary Bank FIP (AA Rail)",
        "jp": "主要取引銀行 (FIP / AA元帳)"
    },
    "lbl_mca_status": {
        "en": "MCA-21 Statutory Status",
        "jp": "会社法コンプライアンス状態"
    },

    # Step 2: Consent Request Dispatch
    "step2_header": {
        "en": "STEP 2: SOVEREIGN DILIGENCE CONSENT REQUEST DISPATCH",
        "jp": "ステップ2: 国家DPI準拠 精査同意リクエスト送信"
    },
    "step2_sub": {
        "en": "Value Create Inc. (Tokyo) & JETRO dispatch a cryptographic time-bound consent mandate to the startup founder under DPDP Act 2023.",
        "jp": "株式会社バリュークリエイト(東京)およびJETROより、DPDP法に基づき創業者署名権者へ時限同意リクエストを発行します。"
    },
    "lbl_requesting_entity": {
        "en": "Requesting Institutional Entity",
        "jp": "審査要請機関"
    },
    "lbl_lead_officer": {
        "en": "Lead Diligence Officer",
        "jp": "担当審査責任者"
    },
    "lbl_requested_scopes": {
        "en": "Requested Sovereign Data Scopes",
        "jp": "要請精査データ範囲"
    },
    "lbl_purpose": {
        "en": "Diligence Purpose",
        "jp": "精査目的"
    },
    "lbl_validity": {
        "en": "Mandate Validity",
        "jp": "同意有効期間"
    },
    "btn_dispatch_consent": {
        "en": "[DISPATCH] Dispatch Diligence Consent Request",
        "jp": "[送信] 精査同意リクエストを創業者へ送信"
    },
    "consent_dispatched_msg": {
        "en": "Consent request dispatched to founder signatory.",
        "jp": "創業者署名権者へ同意リクエストを送信しました。"
    },
    "status_pending_founder": {
        "en": "PENDING FOUNDER APPROVAL",
        "jp": "創業者承認待ち"
    },
    "status_approved_founder": {
        "en": "APPROVED BY CORPORATE SIGNATORY",
        "jp": "創業者承認完了"
    },

    # Step 3: Founder Review, Approval & Linkage
    "step3_header": {
        "en": "STEP 3: STARTUP FOUNDER DASHBOARD (REVIEW, APPROVE & LINK)",
        "jp": "ステップ3: 創業者ダッシュボード (同意承認 & 口座・税務連携)"
    },
    "step3_sub": {
        "en": "Founder reviews incoming diligence request, approves access with 1 click, and links Account Aggregator bank accounts directly to GSTIN and MCA records.",
        "jp": "創業者が申請を1クリックで承認し、RBIアカウントアグリゲーター (銀行元帳) とGST税務申告・会社法登記を直接連携します。"
    },
    "incoming_req_card_title": {
        "en": "Incoming Diligence Request from Tokyo Committee",
        "jp": "東京審査委員会からの受信同意リクエスト"
    },
    "btn_approve_request": {
        "en": "[APPROVE] Authorize Diligence Request",
        "jp": "[承認] 精査同意リクエストを承認する"
    },
    "btn_reject_request": {
        "en": "[REJECT] Reject Request",
        "jp": "[却下] 却下する"
    },
    "rail_linkage_title": {
        "en": "Sovereign Data Rails Linkage & API Authentication",
        "jp": "国家公的データレール直接連携 & API認証"
    },
    "btn_link_bank_aa": {
        "en": "[LINK] Link Bank Account via RBI AA",
        "jp": "[連携] 銀行口座をRBIアカウントアグリゲーター経由で連携"
    },
    "btn_link_tax_gstin": {
        "en": "[LINK] Link GSTIN via Sovereign Tax Rail",
        "jp": "[連携] 登録GSTINを国家税務レール経由で連携"
    },
    "btn_link_mca_books": {
        "en": "[LOCK] Cross-Link MCA & CA Statutory Books",
        "jp": "[ロック] 商業登記・公認会計士元帳を突合ロック"
    },
    "badge_bank_linked": {
        "en": "[VERIFIED] HDFC Current A/c Linked via RBI AA (ReBIT DEPOSIT Schema / X.509 Signed)",
        "jp": "[検証済] HDFC当座預金 口座連携完了 (ReBIT DEPOSIT v2.0 / X.509電子署名)"
    },
    "badge_gstin_linked_full": {
        "en": "[VERIFIED] GSTIN Linked via Sovereign Tax Rail (GSTR-1 & GSTR-3B Synced / NIC IRN QR Verified)",
        "jp": "[検証済] GSTIN 税務申告連携完了 (GSTR-1/3B同期 / NIC電子インボイスQR照合)"
    },
    "badge_mca_linked_full": {
        "en": "[VERIFIED] MCA-21 & CA Books Cross-Linked (Trial Balance & Equity PAS-3 Verified)",
        "jp": "[検証済] 商業登記・試算表突合完了 (試算表・PAS-3出資割当照合済)"
    },
    "all_rails_linked_banner": {
        "en": "ALL SOVEREIGN DATA RAILS ACTIVELY LINKED & VERIFIED",
        "jp": "全系統の国家公的データレールが正常に連携・検証されました"
    },

    # Step 4: Cryptographic Sealing & Cockpit Access
    "step4_header": {
        "en": "STEP 4: SEALED DATA ROOM & INVESTOR ACCESS MINTING",
        "jp": "ステップ4: 暗号マークルツリー固定 & 投資家パスコード発行"
    },
    "step4_sub": {
        "en": "Immutable SHA-256 Merkle root anchored across sovereign data snapshots. Investor handshake passcode minted for unlocked cockpit access.",
        "jp": "銀行・税務・登記の全公的スナップショットをSHA-256マークル根に暗号固定し、投資家向け時限パスコードを発行しました。"
    },
    "sealed_room_title": {
        "en": "Cryptographically Sealed Diligence Vault Ready",
        "jp": "暗号固定済 デューデリジェンス・データルーム準備完了"
    },
    "handshake_passcode_label": {
        "en": "Investor Handshake Passcode",
        "jp": "投資家ハンドシェイク・パスコード"
    },
    "merkle_anchor_label_short": {
        "en": "SHA-256 Merkle Root Anchor",
        "jp": "SHA-256 マークルツリー原簿固定値"
    },
    "btn_open_cockpit": {
        "en": "[EXECUTE] Launch Investor Diligence Cockpit",
        "jp": "[実行] 投資家審査コックピットを開く"
    },
    "btn_download_ringisho": {
        "en": "[EXPORT] Download Tokyo Ringi-sho PDF",
        "jp": "[出力] 東京投資審査稟議書 (PDF) をダウンロード"
    },
    "switch_view_to_investor": {
        "en": "Switch to Investor Gatekeeper View ->",
        "jp": "投資家ゲートキーパー画面へ切り替え ->"
    },
    "switch_view_to_founder": {
        "en": "Switch to Startup Founder Dashboard ->",
        "jp": "スタートアップ創業者ダッシュボードへ切り替え ->"
    }
}


def t(key: str, lang: str = "en") -> str:
    """Retrieve translated string with graceful fallback."""
    lang_key = "jp" if lang.lower() in ["jp", "ja", "japanese"] else "en"
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang_key, TRANSLATIONS[key].get("en", key))
    return key


def format_currency(val_inr: Union[int, float], currency_mode: str = "INR", lang_mode: str = "EN") -> str:
    """
    Format monetary amounts in dual currency:
    INR: ₹ X.XX Cr or ₹ X.X Lakhs
    JPY: ¥ X.XX 億円 or ¥ X,XXX 万円 (at 1.80 rate)
    """
    if val_inr is None:
        return "₹0"
    
    val_inr = float(val_inr)
    is_jp = lang_mode.upper() in ["JP", "JA"]
    sign = "-" if val_inr < 0 else ""
    abs_inr = abs(val_inr)

    if currency_mode.upper() == "JPY":
        abs_jpy = abs_inr * FX_INR_TO_JPY
        if abs_jpy >= 1e8:
            oku = abs_jpy / 1e8
            return f"{sign}¥{oku:.2f} 億円"
        elif abs_jpy >= 1e4:
            man = abs_jpy / 1e4
            return f"{sign}¥{man:,.0f} 万円"
        else:
            return f"{sign}¥{abs_jpy:,.0f}"
    else:
        if abs_inr >= 1e7:
            cr = abs_inr / 1e7
            return f"{sign}₹{cr:.2f} Cr"
        elif abs_inr >= 1e5:
            lakh = abs_inr / 1e5
            return f"{sign}₹{lakh:.2f} Lakhs"
        else:
            return f"{sign}₹{abs_inr:,.0f}"


def format_dual_currency_pair(val_inr: Union[int, float], lang_mode: str = "EN") -> str:
    """Returns primary INR alongside secondary JPY equivalent."""
    if val_inr is None:
        return "₹0 (¥0)"
    inr_str = format_currency(val_inr, currency_mode="INR", lang_mode=lang_mode)
    jpy_str = format_currency(val_inr, currency_mode="JPY", lang_mode=lang_mode)
    return f"{inr_str} ({jpy_str})"
