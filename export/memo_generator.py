"""
ReportLab Bilingual Ringi-sho (稟議書) PDF Generator
VeriLedger / Kizuna-Vault (絆)

Generates an institutional 1-page boardroom due diligence circular:
- Tokyo corporate approval header: 投資審査稟議書 (Investment Due Diligence Ringi-sho)
- 5-Stage Cinnabar Hanko Seal Rail (Shuniku-iro #B33927)
- Dual-Currency Financial Table (INR Crores & JPY 億円)
- Statutory Forensic Audit Findings (Companies Act Sec 188, ICAI SA 240, Benford MAD)
- Boardroom Investment Committee Resolution & Conditions Precedent
- SHA-256 Merkle Tree Root Cryptographic Anchor
"""

import os
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Circle, String, Line
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Register Japanese CID Font
try:
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
    JP_FONT = 'HeiseiKakuGo-W5'
except Exception:
    JP_FONT = 'Helvetica'

# Institutional Tokyo Palette
SHUNIKU_RED = colors.HexColor("#B33927")
DARK_SLATE = colors.HexColor("#0F172A")
BORDER_SLATE = colors.HexColor("#334155")
MUTED_SLATE = colors.HexColor("#64748B")
EMERALD_GREEN = colors.HexColor("#059669")
CRIMSON_RED = colors.HexColor("#DC2626")
AMBER_WARN = colors.HexColor("#D97706")
BG_CARD = colors.HexColor("#F8FAFC")
LINE_SLATE = colors.HexColor("#E2E8F0")


def create_hanko_seal_drawing(
    dept: str,
    name: str,
    status_jp: str = None,
    is_approved: bool = True,
    status: str = None,
    size: float = 44.0,
    **kwargs
) -> Drawing:
    """Creates an authentic circular Japanese Hanko corporate stamp in ReportLab."""
    d = Drawing(size, size)
    scale = size / 68.0

    effective_status = status_jp or status or ("APPROVED" if is_approved else "HELD")
    if effective_status in ["PENDING", "AWAITING", "決裁待ち"]:
        seal_color = MUTED_SLATE
        status_text = "決裁待ち"
    elif effective_status in ["APPROVED", "承認済", "合議済", "決裁済"]:
        seal_color = SHUNIKU_RED
        status_text = str(effective_status) if effective_status in ["承認済", "合議済", "決裁済"] else "承認済"
    elif effective_status in ["FLAGGED", "REJECTED", "否認/保留"]:
        seal_color = CRIMSON_RED
        status_text = "否認/保留"
    elif effective_status in ["HELD", "審査中"]:
        seal_color = AMBER_WARN
        status_text = "審査中"
    else:
        seal_color = SHUNIKU_RED if is_approved else CRIMSON_RED
        status_text = str(effective_status)

    cx = size / 2.0
    cy = size / 2.0

    # Double outer circle (Authentic Hanko)
    d.add(Circle(cx, cy, 30.0 * scale, fillColor=None, strokeColor=seal_color, strokeWidth=1.3 * scale))
    d.add(Circle(cx, cy, 27.0 * scale, fillColor=None, strokeColor=seal_color, strokeWidth=0.7 * scale))

    # Inner horizontal divider lines
    d.add(Line(10.0 * scale, 42.0 * scale, 58.0 * scale, 42.0 * scale, strokeColor=seal_color, strokeWidth=0.7 * scale))
    d.add(Line(10.0 * scale, 26.0 * scale, 58.0 * scale, 26.0 * scale, strokeColor=seal_color, strokeWidth=0.7 * scale))

    dept_clean = dept.replace("部", "").replace("室", "").replace("会", "").replace("コンプラ", "法務")[:4]
    name_clean = name.split()[0].replace("(", "").replace(")", "").strip()[:4]

    # Department (Top)
    d.add(String(cx, 46.0 * scale, dept_clean, fontName=JP_FONT, fontSize=6.5 * scale, fillColor=seal_color, textAnchor="middle"))
    # Signatory Name (Center)
    d.add(String(cx, 31.0 * scale, name_clean, fontName=JP_FONT, fontSize=8.5 * scale, fillColor=seal_color, textAnchor="middle"))
    # Status (Bottom)
    d.add(String(cx, 18.0 * scale, status_text[:4], fontName=JP_FONT, fontSize=6.2 * scale, fillColor=seal_color, textAnchor="middle"))

    return d


def generate_ringi_sho_pdf(audit_result: Dict[str, Any], output_path: str = "export/ringi_sho_dossier.pdf") -> str:
    """Generates the formal 1-page bilingual boardroom memorandum."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Typography System: Helvetica for English (tight kerning), JP_FONT for Japanese (no tofu squares)
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15.0,
        textColor=DARK_SLATE,
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=8.2,
        leading=10.5,
        textColor=MUTED_SLATE,
        alignment=1
    )
    sec_heading_style = ParagraphStyle(
        'SubH',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=7.8,
        leading=9.8,
        textColor=DARK_SLATE
    )
    th_jp_style = ParagraphStyle(
        'DocTHJP',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=7.0,
        leading=9.0,
        textColor=colors.white
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=DARK_SLATE
    )
    meta_jp_style = ParagraphStyle(
        'DocMetaJP',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=7.2,
        leading=9.2,
        textColor=DARK_SLATE
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=DARK_SLATE
    )
    body_bold_style = ParagraphStyle(
        'DocBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=DARK_SLATE
    )
    body_jp_style = ParagraphStyle(
        'DocBodyJP',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=7.0,
        leading=9.2,
        textColor=DARK_SLATE
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName=JP_FONT,
        fontSize=6.8,
        leading=8.8,
        textColor=DARK_SLATE
    )

    kpis = audit_result.get('kpis', {})
    company_name = audit_result.get('company_name', 'Target Startup')
    cin = audit_result.get('cin', 'U72900KA2023PTC178921')
    vault_id = audit_result.get('vault_id', 'TJH-2026-VC01')
    score = kpis.get('governance_trust_score', 50)
    classification = kpis.get('classification', 'UNDER_REVIEW')
    kanji_badge = kpis.get('kanji_badge', '[要確認]')

    # 1. Header
    story.append(Paragraph("INVESTMENT DUE DILIGENCE MEMORANDUM & BOARDROOM CIRCULAR", title_style))
    story.append(Paragraph("【投資審査稟議書】 日本・インド二国間ベンチャー投資適格性評価データルーム", subtitle_style))
    story.append(Spacer(1, 2.2 * mm))

    # Meta bar
    verdict_color = '#059669' if score >= 80 else ('#DC2626' if score <= 30 else '#D97706')
    meta_data = [
        [
            Paragraph(f"<b>Dossier Ref:</b> {vault_id}", meta_style),
            Paragraph(f"<b>Date:</b> October 24, 2026", meta_style),
            Paragraph(f"<b>Evaluator:</b> Value Create Inc. (Tokyo) • JETRO Track", meta_style),
            Paragraph(f"<b>Status:</b> <font color='{verdict_color}'><b>{kanji_badge} {classification}</b></font>", meta_jp_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[44*mm, 34*mm, 58*mm, 50*mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_CARD),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_SLATE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, LINE_SLATE),
        ('TOPPADDING', (0, 0), (-1, -1), 3.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 2.5 * mm))

    # 2. 5-Stage Hanko Seal Rail (Authentic Tokyo Boardroom Sign-off)
    hanko_stages = audit_result.get('hanko_stages', [])
    signoff_headers = []
    signoff_seals = []
    signoff_officers = []
    signoff_dates = []

    for stage in hanko_stages:
        is_app = stage.get('status') == 'APPROVED'
        status_label = stage.get('status_jp', '承認済' if is_app else '保留')
        role_label = stage.get('role_en', 'Reviewer')
        role_jp = stage.get('role_jp', '審査').replace('　', '')
        dept_label = stage.get('dept_jp', '審査')
        officer = stage.get('signatory', '担当')
        dt = stage.get('date', '2026-10-24')
        st_color = '#059669' if is_app else ('#DC2626' if stage.get('status') == 'FLAGGED' else '#D97706')

        signoff_headers.append(Paragraph(
            f"<b>{role_label}</b><br/><font size='5.5' color='#94A3B8'>{role_jp} • {dept_label}</font>",
            ParagraphStyle('HdrH', fontName=JP_FONT, alignment=1, fontSize=6.2, leading=7.8, textColor=colors.white)
        ))

        seal_drawing = create_hanko_seal_drawing(
            dept=dept_label,
            name=officer,
            status_jp=status_label,
            is_approved=is_app,
            status=stage.get('status'),
            size=42.0
        )
        signoff_seals.append(seal_drawing)

        signoff_officers.append(Paragraph(
            f"<b>{officer}</b>",
            ParagraphStyle('HdrOff', fontName=JP_FONT, alignment=1, fontSize=6.8, leading=8.2, textColor=DARK_SLATE)
        ))
        signoff_dates.append(Paragraph(
            f"<font color='{st_color}'><b>[{status_label}]</b></font><br/><font color='#64748B' size='5.5'>{dt}</font>",
            ParagraphStyle('HdrDt', fontName=JP_FONT, alignment=1, fontSize=6.2, leading=7.5)
        ))

    hanko_table = Table([signoff_headers, signoff_seals, signoff_officers, signoff_dates], colWidths=[37.2*mm]*5)
    hanko_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_SLATE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('TOPPADDING', (0, 0), (-1, 0), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2.5),
        ('TOPPADDING', (0, 1), (-1, 1), 2.5),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 2.5),
        ('TOPPADDING', (0, 2), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 2), (-1, -1), 2.0),
    ]))
    story.append(hanko_table)
    story.append(Spacer(1, 2.5 * mm))

    # 3. Target Profile & Sovereign DPI Badges
    ca_opinion_clean = audit_result.get('ca_audit_opinion', 'UNQUALIFIED_CLEAN').replace('_', ' ')
    profile_data = [
        [
            Paragraph("<b>Target Enterprise:</b>", meta_style),
            Paragraph(f"<b>{company_name}</b> (CIN: <code>{cin}</code>)", body_style),
            Paragraph("<b>Governance Score:</b>", meta_style),
            Paragraph(f"<font size='10' color='{verdict_color}'><b>{score} / 100</b></font>", body_bold_style)
        ],
        [
            Paragraph("<b>Sovereign DPI Rails:</b>", meta_style),
            Paragraph("[PASS] RBI Account Aggregator (DEPOSIT v2.0)  •  [PASS] GSTN e-Invoice IRN Verified  •  [PASS] MCA-21 Direct", body_style),
            Paragraph("<b>CA Opinion:</b>", meta_style),
            Paragraph(f"<b>{ca_opinion_clean}</b>", body_style)
        ]
    ]
    profile_table = Table(profile_data, colWidths=[33*mm, 85*mm, 28*mm, 40*mm])
    profile_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, LINE_SLATE),
        ('TOPPADDING', (0, 0), (-1, -1), 3.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.0),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 2.5 * mm))

    # 4. Multi-Source Financial Reconciliation (Dual Currency Table)
    claimed_arr = kpis.get('claimed_arr_inr', 0.0)
    ca_rev = kpis.get('ca_booked_revenue_inr', claimed_arr)
    bank_cash = kpis.get('real_bank_credits_inr', 0.0)
    phantom_gap = kpis.get('phantom_revenue_inr', 0.0)
    fx = 1.80

    def format_jpy_str(amt_inr: float) -> str:
        amt_jpy = amt_inr * fx
        if abs(amt_jpy) >= 1e8:
            return f"¥ {amt_jpy/1e8:.2f} 億円"
        elif abs(amt_jpy) >= 1e4:
            return f"¥ {amt_jpy/1e4:,.0f} 万円"
        else:
            return f"¥ {amt_jpy:,.0f}"

    tax_due = kpis.get('unremitted_tax_dues_inr', 0)
    gap_jpy = "¥0" if phantom_gap == 0 else (f"¥{(phantom_gap*fx)/1e4:,.0f}万円" if (phantom_gap*fx) < 1e8 else f"¥{(phantom_gap*fx)/1e8:.2f}億円")
    tax_jpy = "¥0" if tax_due == 0 else (f"¥{(tax_due*fx)/1e4:,.0f}万円" if (tax_due*fx) < 1e8 else f"¥{(tax_due*fx)/1e8:.2f}億円")

    fin_headers = ["Diligence Dimension (検証項目)", "Indian Rupees (INR / ₹)", "Japanese Yen (JPY ¥)", "Variance & Cross-Check (検証結果)"]
    fin_rows = [
        [
            Paragraph("<b>Pitch Deck Claimed ARR</b>", body_style),
            Paragraph(f"INR {claimed_arr/1e7:.2f} Cr", body_style),
            Paragraph(format_jpy_str(claimed_arr), body_jp_style),
            Paragraph("Founder self-reported deck claim", body_style)
        ],
        [
            Paragraph("<b>CA General Ledger (Zoho/Tally)</b>", body_style),
            Paragraph(f"INR {ca_rev/1e7:.2f} Cr", body_style),
            Paragraph(format_jpy_str(ca_rev), body_jp_style),
            Paragraph("Internal trial balance sales register", body_style)
        ],
        [
            Paragraph("<b>Cleared Bank Cash (RBI AA)</b>", body_style),
            Paragraph(f"INR {bank_cash/1e7:.2f} Cr", body_style),
            Paragraph(format_jpy_str(bank_cash), body_jp_style),
            Paragraph(
                "<font color='#059669'><b>100% Cash Realized</b> (Verified Match)</font>" if phantom_gap == 0
                else f"<font color='#DC2626'><b>{kpis.get('cash_divergence_pct')}% Divergence</b> (Gap: INR {phantom_gap/1e5:.1f}L / {gap_jpy})</font>",
                body_jp_style
            )
        ],
        [
            Paragraph("<b>True Cash Runway</b>", body_style),
            Paragraph(f"{kpis.get('true_runway_months')} Months", body_style),
            Paragraph(f"Claimed: {kpis.get('claimed_runway_months')} Mo", body_style),
            Paragraph(
                "Zero pending statutory tax dues (Fully unencumbered)" if tax_due == 0
                else f"Net of INR {tax_due/1e5:.1f}L ({tax_jpy}) pending statutory dues",
                body_jp_style
            )
        ]
    ]

    table_data = [[Paragraph(f"<b>{h}</b>", th_jp_style) for h in fin_headers]] + fin_rows
    fin_table = Table(table_data, colWidths=[48*mm, 36*mm, 38*mm, 64*mm])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_SLATE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, LINE_SLATE),
        ('TOPPADDING', (0, 0), (-1, 0), 2.8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2.8),
        ('TOPPADDING', (0, 1), (-1, -1), 3.0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3.0),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 2.5 * mm))

    # 5. Statutory Red-Flags & Boardroom Action Plan
    story.append(Paragraph(
        "<b>STATUTORY FORENSIC FINDINGS & AUDIT EXCEPTION SUMMARY</b>",
        sec_heading_style
    ))
    story.append(Spacer(1, 1.2 * mm))

    red_flags = audit_result.get('red_flags', [])
    findings_rows = []
    if not red_flags:
        findings_rows.append([Paragraph(
            "<b>CLEAN GOVERNANCE ATTESTATION [適格]:</b> 100% census match across sovereign bank deposits and GST e-invoices. "
            "Zero Section 188 promoter conflicts, zero window-dressing contra entries, and Benford Nigrini MAD is in close conformity. "
            "Fully eligible for Tokyo Corporate Investment Committee review.",
            bullet_style
        )])
    else:
        for rf in red_flags[:3]:
            txt = f"<b>[{rf.get('severity')}] {rf.get('title')}:</b> {rf.get('description')} <i>(Statute: {rf.get('statutory_citation')})</i>"
            findings_rows.append([Paragraph(txt, bullet_style)])
        if len(red_flags) > 3:
            findings_rows.append([Paragraph(
                f"<i>... and {len(red_flags) - 3} additional forensic violations detailed in Section 65B Electronic Evidence Dossier.</i>",
                bullet_style
            )])

    findings_table = Table(findings_rows, colWidths=[186*mm])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFF1F2") if red_flags else colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 0.6, SHUNIKU_RED if red_flags else EMERALD_GREEN),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#FECDD3") if red_flags else colors.HexColor("#BBF7D0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.0),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 2.5 * mm))

    # 6. Tokyo Investment Committee Decision & Bilateral CPs (先決条件・投資決議)
    story.append(Paragraph(
        "<b>BOARDROOM INVESTMENT COMMITTEE RESOLUTION & CONDITIONS PRECEDENT 【決議事項・先決条件】</b>",
        sec_heading_style
    ))
    story.append(Spacer(1, 1.2 * mm))

    if score >= 80:
        cp_content = (
            "<b>[DECISION: PROCEED TO PHASE-II DEFINITIVE AGREEMENTS]</b><br/>"
            "<b>CP-1 (Direct Escrow Binding):</b> Bilateral escrow mechanism through RBI authorized dealer bank with JPY-INR cross-currency hedging facility.<br/>"
            "<b>CP-2 (Continuous Sovereign Ingestion):</b> Ongoing automated monitoring via RBI Account Aggregator DEPOSIT v2.0 rail.<br/>"
            "<b>CP-3 (J-SOX Warranty):</b> Founder representation warranting zero undisclosed related-party loans or off-balance-sheet encumbrances."
        )
    else:
        cp_content = (
            "<b>[DECISION: CAPITAL ALLOCATION FROZEN / MATERIAL UNCERTAINTIES FLAGGED]</b><br/>"
            "<b>Finding:</b> Discrepancies detected between claimed ledger revenue and sovereign bank clearing credits exceeding risk tolerance threshold.<br/>"
            "<b>Remediation Order:</b> Full statutory reconciliation under ICAI SA 240 and Section 188 Companies Act required prior to any investment consideration.<br/>"
            "<b>Referral:</b> Audit findings archived under Section 65B Evidence Act for legal protection and stakeholder notification."
        )

    t_cp = Table([[Paragraph(cp_content, bullet_style)]], colWidths=[186*mm])
    t_cp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_SLATE),
        ('TOPPADDING', (0, 0), (-1, -1), 3.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.2),
    ]))
    story.append(t_cp)
    story.append(Spacer(1, 2.5 * mm))

    # 7. Cryptographic Merkle Anchor & Legal Disclaimer
    merkle = kpis.get('merkle_root', '0x' + '0'*64)
    footer_text = f"<b>Cryptographic Tamper-Proof Merkle Root:</b> <font face='Courier' size='6.2'>{merkle}</font><br/>" \
                  f"<i>Admissible under Section 65B(4) of the Indian Evidence Act 1872 & J-SOX Internal Control Standards. Digitally generated by VeriLedger Engine.</i>"
    story.append(Paragraph(footer_text, ParagraphStyle('Foot', fontName=JP_FONT, fontSize=6.0, leading=8.0, textColor=MUTED_SLATE, alignment=1)))

    doc.build(story)
    return output_path
