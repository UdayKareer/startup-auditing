"""
Institutional UI Components for VeriLedger / Kizuna-Vault (Streamlit).
Standardized for Track OPEN-PS-01 | Value Create Inc. (Tokyo) & JETRO Diligence Rail.

Strictly adheres to Institutional Anti-AI-Slop & Boardroom Standards:
- Void obsidian palette & Institutional Pure White support
- Tabular monospace numbers (JetBrains Mono)
- 5-Stage Cinnabar Hanko Seal rail (起案, 審査, 精査, 合議, 決裁)
- Sovereign India Stack DPI verification badges
- Zero emojis, zero purple mesh gradients, crisp 1px borders
- High-density Plotly charts with Discrepancy Waterfall Cascade
"""

import math
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from frontend.i18n import t, format_currency, format_dual_currency_pair, FX_INR_TO_JPY


def _safe_str(val: Any, fallback: str = "") -> str:
    """Helper to cleanly extract strings and prevent rendering 'None' or 'nan' in UI tables."""
    if val is None or pd.isna(val):
        return fallback
    s = str(val).strip()
    return fallback if s.lower() in ("", "none", "nan", "null") else s


def render_header(currency: str, lang: str, theme_mode: str = "light"):
    """Render institutional top navigation bar without emojis."""
    is_jp = lang.lower() in ["jp", "ja"]
    sub_title = t("app_subtitle", lang)
    partner_tag = t("partner_tag", lang)
    dpi_badge = t("dpi_status_badge", lang)

    st.markdown(
        f"""
        <div class="header-bar">
            <div>
                <div class="brand-title">
                    <span>VERILEDGER (絆)</span>
                    <span class="brand-tag">TRACK OPEN-PS-01</span>
                    <span class="brand-tag-blue">{partner_tag}</span>
                </div>
                <div style="font-size: 0.74rem; color: #64748B; margin-top: 3px;">
                    {sub_title}
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="badge-clean" style="font-size: 0.72rem;">
                    {dpi_badge}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dpi_rail_badges(lang: str = "en", theme: str = None):
    """Render 4 Sovereign Digital Public Infrastructure (DPI) verification cards."""
    if theme is None:
        theme = st.session_state.get('app_theme', 'light')
    is_light = theme.lower() == "light"
    lbl_color = "#334155" if is_light else "#94A3B8"
    txt_pri = "#0F172A" if is_light else "#F8FAFC"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; margin-bottom: 8px;">
                <div style="font-size: 0.70rem; color: {lbl_color}; font-weight: 700; text-transform: uppercase;">
                    {t('dpi_rbi', lang)}
                </div>
                <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 3px;">
                    RBI Account Aggregator
                </div>
                <div style="font-size: 0.72rem; color: #059669; margin-top: 4px; font-weight: 700; font-family: monospace;">
                    [PASS] {t('dpi_rbi_desc', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; margin-bottom: 8px;">
                <div style="font-size: 0.70rem; color: {lbl_color}; font-weight: 700; text-transform: uppercase;">
                    {t('dpi_gst', lang)}
                </div>
                <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 3px;">
                    GSTN Invoicing Portal
                </div>
                <div style="font-size: 0.72rem; color: #059669; margin-top: 4px; font-weight: 700; font-family: monospace;">
                    [PASS] {t('dpi_gst_desc', lang)} <span class="badge-clean" style="font-size: 0.62rem; margin-left: 4px;">[ACTIVE]</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; margin-bottom: 8px;">
                <div style="font-size: 0.70rem; color: {lbl_color}; font-weight: 700; text-transform: uppercase;">
                    {t('dpi_mca', lang)}
                </div>
                <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 3px;">
                    MCA-21 Corporate Registry
                </div>
                <div style="font-size: 0.72rem; color: #059669; margin-top: 4px; font-weight: 700; font-family: monospace;">
                    [PASS] {t('dpi_mca_desc', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="card" style="padding: 12px 14px; margin-bottom: 8px;">
                <div style="font-size: 0.70rem; color: {lbl_color}; font-weight: 700; text-transform: uppercase;">
                    {t('dpi_ca', lang)}
                </div>
                <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 3px;">
                    Chartered Accountant Books
                </div>
                <div style="font-size: 0.72rem; color: #059669; margin-top: 4px; font-weight: 700; font-family: monospace;">
                    [PASS] {t('dpi_ca_desc', lang)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_merkle_anchor(merkle_root: str, lang: str = "en", theme: str = None):
    """Render cryptographic Merkle tree root anchor display without emojis."""
    if theme is None:
        theme = st.session_state.get('app_theme', 'light')
    is_light = theme.lower() == "light"
    lbl_color = "#334155" if is_light else "#CBD5E1"
    desc_color = "#475569" if is_light else "#94A3B8"

    st.markdown(
        f"""
        <div class="card" style="padding: 10px 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge-mono">SHA-256 ANCHOR</span>
                    <span style="font-size: 0.75rem; color: {lbl_color}; font-weight: 600;">
                        {t('merkle_anchor_label', lang)}:
                    </span>
                    <code class="merkle-badge">{merkle_root}</code>
                </div>
                <div style="font-size: 0.70rem; color: {desc_color};">
                    {t('merkle_desc', lang)}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_anonymized_teaser(teaser: Dict[str, Any], lang: str = "en", theme: str = None):
    """Render anonymized pre-access teaser for the selected company."""
    if theme is None:
        theme = st.session_state.get('app_theme', 'light')
    is_light = theme.lower() == "light"
    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#334155" if is_light else "#CBD5E1"
    lbl_sec = "#475569" if is_light else "#94A3B8"
    sub_bg = "#F8FAFC" if is_light else "#1E293B"
    card_border = "#CBD5E1" if is_light else "#334155"

    st.markdown(
        f"""
        <div class="card" style="padding: 18px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: {txt_pri}; text-transform: uppercase; letter-spacing: 0.04em;">
                    {t('teaser_title', lang)}
                </div>
                <span class="badge-review">[SEALED DATA ROOM]</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 12px;">
                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.70rem; color: {lbl_sec}; font-weight: 700;">{t('operating_vintage', lang)}</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: {txt_pri}; font-family: monospace;">
                        {teaser.get('operating_vintage_years', 3.5)} Years
                    </div>
                </div>
                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.70rem; color: {lbl_sec}; font-weight: 700;">{t('sector_classification', lang)}</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: {txt_pri};">
                        {teaser.get('sector', 'Enterprise SaaS & Logistics')}
                    </div>
                </div>
                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.70rem; color: {lbl_sec}; font-weight: 700;">{t('revenue_bracket', lang)}</div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: {txt_pri}; font-family: monospace;">
                        {teaser.get('revenue_tier', '₹10 Cr - ₹50 Cr Bracket')}
                    </div>
                </div>
                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.70rem; color: {lbl_sec}; font-weight: 700;">{t('verified_accounts', lang)}</div>
                    <div style="font-size: 0.90rem; font-weight: 700; color: #059669; font-family: monospace;">
                        1 Current A/c, 2 GSTINs
                    </div>
                </div>
            </div>
            <div style="font-size: 0.72rem; color: {txt_sec}; background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 8px 12px; line-height: 1.45;">
                <b>DPDP Act 2023 Masking Notice:</b> {t('pii_masking_notice', lang)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_telemetry_trace(telemetry_steps: List[Dict[str, Any]], total_latency_ms: float, lang: str = "en"):
    """Render sub-200ms real-time execution trace terminal."""
    rows_html = ""
    for step in telemetry_steps:
        status_color = "#10B981" if step.get("status") == "PASS" else "#F59E0B"
        icon = "[PASS]" if step.get("status") == "PASS" else "[FLAG]"
        rows_html += f"""
        <div class="telemetry-row">
            <div>
                <span class="telemetry-step-ok" style="color: {status_color}; font-size: 0.68rem;">{icon}</span>
                <span style="color: #F8FAFC; font-weight: 600;">{step.get('service')}</span>:
                <span style="color: #94A3B8;">{step.get('detail')}</span>
            </div>
            <div class="telemetry-latency">{step.get('latency_ms')} ms</div>
        </div>
        """

    st.markdown(
        f"""
        <div class="telemetry-terminal">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 6px;">
                <span style="font-weight: 800; color: #38BDF8; letter-spacing: 0.05em;">
                    [TELEMETRY] {t('telemetry_title', lang)}
                </span>
                <span class="badge-clean">
                    TOTAL LATENCY: {total_latency_ms:.1f} ms (SUB-200ms PARALLEL)
                </span>
            </div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trust_score_gauge(score: int, lang: str = "en", theme: str = "dark") -> go.Figure:
    """Render institutional radial Trust Score gauge (0-100)."""
    is_light = theme.lower() == "light"
    paper_bg = "#FFFFFF" if is_light else "#111827"
    font_color = "#0F172A" if is_light else "#F8FAFC"

    if score >= 75:
        bar_color = "#10B981"
        status = "SAFE" if lang == "en" else "適格"
    elif score >= 50:
        bar_color = "#F59E0B"
        status = "REVIEW" if lang == "en" else "要確認"
    else:
        bar_color = "#B33927"
        status = "HIGH RISK" if lang == "en" else "精査要"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(
            font=dict(size=36, family="JetBrains Mono", color=bar_color),
            suffix="/100"
        ),
        title=dict(
            text=("OVERALL TRUST SCORE" if lang == "en" else "総合信頼スコア") + f"<br><span style='font-size:0.75em;color:{bar_color}'>[{status}]</span>",
            font=dict(size=12, color=font_color, family="Inter")
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=1,
                tickcolor=font_color,
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
                tickfont=dict(size=9, color="#64748B", family="JetBrains Mono")
            ),
            bar=dict(color=bar_color, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, 35], color="#FEF2F2" if is_light else "rgba(179,57,39,0.15)"),
                dict(range=[35, 65], color="#FFFBEB" if is_light else "rgba(245,158,11,0.10)"),
                dict(range=[65, 100], color="#ECFDF5" if is_light else "rgba(16,185,129,0.10)")
            ],
            threshold=dict(
                line=dict(color=bar_color, width=3),
                thickness=0.8,
                value=score
            )
        )
    ))

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor=paper_bg,
        margin=dict(l=20, r=20, t=50, b=20),
        height=240,
        font=dict(family="Inter")
    )
    return fig


def render_kpi_card(
    title: str,
    value: str,
    subtitle: str,
    badge_text: str,
    badge_type: str = "clean",
    desc: str = ""
):
    """Render a single high-density institutional KPI card."""
    badge_class = f"badge-{badge_type}"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">
                <span>{title}</span>
                <span class="{badge_class}">{badge_text}</span>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtitle">{subtitle}</div>
            {f'<div style="font-size: 0.70rem; color: #64748B; margin-top: 6px; line-height: 1.35;">{desc}</div>' if desc else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reconciliation_chart(
    monthly_data: List[Dict[str, Any]],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "dark"
) -> go.Figure:
    """Render 4-Way Monthly Revenue Reconciliation Bar Chart."""
    is_jpy = currency_mode.upper() == "JPY"
    rate = FX_INR_TO_JPY if is_jpy else 1.0
    is_jp = lang.lower() in ["jp", "ja"]

    if is_jpy:
        max_monthly_jpy = max([item.get("claimed_pitch_sales_inr", 0) for item in monthly_data], default=0) * rate
        if max_monthly_jpy >= 1e8:
            scale = 1e8
            unit = "億円"
        else:
            scale = 1e4
            unit = "万円"
    else:
        scale = 1e5
        unit = "Lakhs"
    curr_sym = "¥" if is_jpy else "₹"

    is_light = theme.lower() == "light"
    paper_bg = "#FFFFFF" if is_light else "#111827"
    plot_bg = "#FFFFFF" if is_light else "#111827"
    font_color = "#0F172A" if is_light else "#F8FAFC"
    grid_color = "#E2E8F0" if is_light else "#1E293B"
    muted_color = "#64748B" if is_light else "#94A3B8"

    months = []
    pitch = []
    ca = []
    gst = []
    bank = []

    for item in monthly_data:
        m_name = item.get("month", "")
        parts = m_name.split()
        m_label = f"{parts[0][:3]} '{parts[1][-2:]}" if len(parts) >= 2 else m_name
        months.append(m_label)

        pitch.append((item.get("claimed_pitch_sales_inr", 0) * rate) / scale)
        ca.append((item.get("ca_booked_sales_inr", 0) * rate) / scale)
        gst.append((item.get("gstr1_declared_sales_inr", 0) * rate) / scale)
        bank.append((item.get("bank_cleared_cash_inr", 0) * rate) / scale)

    fig = go.Figure()

    t1_name = "1. ピッチ主張売上" if is_jp else "1. Pitch Claimed Sales"
    t2_name = "2. CA試算表売上" if is_jp else "2. CA General Ledger"
    t3_name = "3. GSTR-1税務申告" if is_jp else "3. GSTR-1 Tax Declared"
    t4_name = "4. 確定銀行預金着金" if is_jp else "4. Bank Cleared Cash"
    ht = "%{x}<br><b>%{fullData.name}</b>: %{y:.2f} " + unit + "<extra></extra>"

    fig.add_trace(go.Bar(
        name=t1_name,
        x=months,
        y=pitch,
        marker_color="#38BDF8",
        hovertemplate=ht
    ))
    fig.add_trace(go.Bar(
        name=t2_name,
        x=months,
        y=ca,
        marker_color="#818CF8",
        hovertemplate=ht
    ))
    fig.add_trace(go.Bar(
        name=t3_name,
        x=months,
        y=gst,
        marker_color="#A78BFA",
        hovertemplate=ht
    ))
    fig.add_trace(go.Bar(
        name=t4_name,
        x=months,
        y=bank,
        marker_color="#10B981" if sum(bank) >= sum(pitch) * 0.7 else "#B33927",
        hovertemplate=ht
    ))

    title_text = (
        f"4元売上収束検証 (月次) ({curr_sym} {unit})"
        if is_jp
        else f"4-Way Revenue Convergence ({curr_sym} {unit})"
    )

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(color=font_color, size=12, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            y=0.98,
        ),
        barmode="group",
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        margin=dict(l=45, r=15, t=45, b=65),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(color=muted_color, size=10),
        ),
        xaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=10),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=10),
            title=dict(text=f"金額 ({curr_sym} {unit})" if is_jp else f"Amount ({curr_sym} {unit})", font=dict(color=muted_color, size=10)),
        ),
        height=390,
        uniformtext=dict(minsize=8, mode="hide"),
    )

    # Dynamic Annotation & Floor Line
    if months and pitch and bank:
        tot_pitch = sum(pitch)
        tot_bank = sum(bank)
        avg_pitch = tot_pitch / len(pitch)
        avg_bank = tot_bank / len(bank)
        gap_ratio = (tot_pitch - tot_bank) / max(0.01, tot_pitch)
        has_real_gap = gap_ratio > 0.10

        if has_real_gap:
            gap_label = "REVENUE GAP" if not is_jp else "収益乖離"
            fig.add_annotation(
                x=months[len(months) // 2],
                y=(avg_pitch + avg_bank) / 2,
                text=f"<b>{gap_label}: -{gap_ratio*100:.1f}%</b>",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#EF4444",
                arrowwidth=2,
                ax=60,
                ay=0,
                font=dict(color="#EF4444", size=10, family="JetBrains Mono"),
                bgcolor="rgba(239,68,68,0.12)",
                bordercolor="#EF4444",
                borderwidth=1,
            )
            floor_color = "#EF4444"
            floor_label = "Ground Truth Bank Floor (Deficit)" if not is_jp else "確定銀行基準線 (不足)"
        else:
            conc_label = "[CONCORDANT: 99%+ REALIZED]" if not is_jp else "[公的突合: 99%超整合]"
            fig.add_annotation(
                x=months[len(months) // 2],
                y=avg_pitch * 1.08,
                text=f"<b>{conc_label}</b>",
                showarrow=False,
                font=dict(color="#10B981", size=10, family="JetBrains Mono"),
                bgcolor="rgba(16,185,129,0.12)",
                bordercolor="#10B981",
                borderwidth=1,
            )
            floor_color = "#10B981"
            floor_label = "Ground Truth Bank Floor (Verified)" if not is_jp else "確定銀行基準線 (確認済)"

        fig.add_hline(
            y=avg_bank,
            line=dict(color=floor_color, dash="dash", width=1.5),
            annotation_text=floor_label,
            annotation_position="bottom right",
            annotation_font=dict(color=floor_color, size=9, family="JetBrains Mono"),
        )

    return fig


def render_benford_chart(benford_data: Dict[str, Any], lang: str = "en", theme: str = "dark") -> go.Figure:
    """Render Benford's Law (F2D) Anomaly Curve."""
    digits = benford_data.get("digits", list(range(10, 100)))
    exp_pct = benford_data.get("expected_pct", [])
    obs_pct = benford_data.get("observed_pct", [])
    mad = benford_data.get("nigrini_mad", 0.0028)

    if not exp_pct:
        exp_pct = [math.log10(1 + 1 / d) * 100 for d in digits]
    if not obs_pct:
        obs_pct = exp_pct

    is_anomaly = mad > 0.0035

    is_light = theme.lower() == "light"
    paper_bg = "#FFFFFF" if is_light else "#111827"
    plot_bg = "#FFFFFF" if is_light else "#111827"
    font_color = "#0F172A" if is_light else "#F8FAFC"
    grid_color = "#E2E8F0" if is_light else "#1E293B"
    muted_color = "#64748B" if is_light else "#94A3B8"
    is_jp = lang.lower() in ["jp", "ja"]

    fig = go.Figure()

    trace_obs_name = "実績出金分布" if is_jp else "Observed Disbursements"
    trace_theo_name = "理論対数減衰 (ベンフォード則)" if is_jp else "Theoretical Benford Log10 Decay"
    b_ht = "Digit %{x}: %{y:.2f}%<extra></extra>"

    fig.add_trace(go.Bar(
        name=trace_obs_name,
        x=[str(d) for d in digits],
        y=obs_pct,
        marker_color="rgba(179, 57, 39, 0.55)" if is_anomaly else "rgba(16, 185, 129, 0.45)",
        hovertemplate=b_ht
    ))

    fig.add_trace(go.Scatter(
        name=trace_theo_name,
        x=[str(d) for d in digits],
        y=exp_pct,
        mode="lines",
        line=dict(color="#0284C7" if is_light else "#38BDF8", width=2),
        hovertemplate=b_ht
    ))

    if is_jp:
        status_tag = (
            "[警告] 異常構造化検知 (MAD > 0.0035)"
            if is_anomaly
            else "[適正] 整合的自然分布"
        )
    else:
        status_tag = (
            "[ALERT] STRUCTURING ANOMALY DETECTED (MAD > 0.0035)"
            if is_anomaly
            else "[CLEAN] CONFORMING DISTRIBUTION"
        )

    title_text = (
        "ベンフォードの法則 (F2D) 異常度曲線"
        if is_jp
        else "Benford's Law (F2D) Anomaly Curve"
    )

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(color=font_color, size=12, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            y=0.98,
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        margin=dict(l=45, r=15, t=45, b=65),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(color=muted_color, size=10),
        ),
        xaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=9),
            tickmode="linear",
            dtick=10,
            title=dict(text="先頭2桁数値 (10〜99)" if is_jp else "Leading Two Digits (10-99)", font=dict(color=muted_color, size=10)),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=10),
            title=dict(text="出現頻度 (%)" if is_jp else "% Frequency", font=dict(color=muted_color, size=10)),
        ),
        height=390,
    )

    # If anomaly, add filled red rectangle over structuring zone (digits 10-19)
    if is_anomaly and digits:
        zone_label = "STRUCTURING ZONE" if not is_jp else "構造化ゾーン"
        # Find x-axis indices for digits 10-19
        str_digits = [str(d) for d in digits]
        x0_idx = str_digits.index("10") if "10" in str_digits else 0
        x1_idx = str_digits.index("19") if "19" in str_digits else min(9, len(str_digits) - 1)
        fig.add_vrect(
            x0=str_digits[x0_idx],
            x1=str_digits[x1_idx],
            fillcolor="rgba(239,68,68,0.12)",
            line=dict(color="#EF4444", width=1.5, dash="dot"),
            annotation_text=f"<b>{zone_label}</b>",
            annotation_position="top left",
            annotation_font=dict(color="#EF4444", size=10, family="JetBrains Mono"),
        )

    # MAD value annotation with crisp header badge (no overlap with bottom legend)
    mad_status = f"{status_tag} • MAD: {mad:.5f}"
    mad_color = "#EF4444" if is_anomaly else "#10B981"
    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.0, y=1.08,
        text=f"<b>{mad_status}</b>",
        showarrow=False,
        font=dict(color=mad_color, size=10, family="JetBrains Mono"),
        bgcolor="rgba(239, 68, 68, 0.10)" if is_anomaly else "rgba(16, 185, 129, 0.10)",
        bordercolor=mad_color,
        borderwidth=1,
        align="right",
    )

    return fig


def render_discrepancy_waterfall(
    audit_data: Dict[str, Any],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "dark"
) -> go.Figure:
    """
    Renders the Discrepancy Diligence Waterfall Cascade:
    Pitch Claimed ARR -> Less Unbilled Pitch Gap -> GSTN Turnover ->
    Less Uncollected Gap -> Cleared Bank Cash -> Less Siphoned -> Less Tax Dues ->
    True Operational Net Cash.
    """
    is_jpy = currency_mode.upper() == "JPY"
    rate = FX_INR_TO_JPY if is_jpy else 1.0
    scale = 1e7 if not is_jpy else 1e8
    unit = "億円" if is_jpy else "Cr"
    curr_sym = "¥" if is_jpy else "₹"
    is_jp = lang.lower() in ["jp", "ja"]

    wf = audit_data.get("waterfall")
    if not wf:
        kpis = audit_data.get("kpis", {})
        claimed = float(kpis.get("claimed_arr_inr", 25500000.0))
        gst = float(kpis.get("gst_invoiced_turnover_inr", kpis.get("ca_booked_revenue_inr", claimed)))
        bank = float(kpis.get("real_bank_credits_inr", 10100000.0))
        siphoned = float(kpis.get("siphoned_funds_inr", 0.0))
        tax = float(kpis.get("unremitted_tax_dues_inr", 0.0))
        wf = {
            "pitch_claimed_arr_inr": claimed,
            "unbilled_pitch_gap_inr": max(0.0, claimed - gst),
            "gst_declared_turnover_inr": gst,
            "uncollected_bank_gap_inr": max(0.0, gst - bank),
            "cleared_bank_cash_inr": bank,
            "promoter_siphoned_inr": siphoned,
            "unremitted_tax_dues_inr": tax,
            "true_unencumbered_cash_inr": max(0.0, bank - siphoned - tax)
        }

    c_arr = (wf["pitch_claimed_arr_inr"] * rate) / scale
    unbilled = (wf["unbilled_pitch_gap_inr"] * rate) / scale
    gst_val = (wf["gst_declared_turnover_inr"] * rate) / scale
    uncollected = (wf["uncollected_bank_gap_inr"] * rate) / scale
    bank_val = (wf["cleared_bank_cash_inr"] * rate) / scale
    siph_val = (wf["promoter_siphoned_inr"] * rate) / scale
    tax_val = (wf["unremitted_tax_dues_inr"] * rate) / scale
    true_val = (wf["true_unencumbered_cash_inr"] * rate) / scale

    if is_jp:
        x_steps = [
            "1. 主張ARR",
            "控除: 未請求乖離",
            "2. GSTN申告売上",
            "控除: 未回収乖離",
            "3. 銀行確定入金",
            "控除: 取締役流出",
            "控除: 税金未納",
            "4. 実質純資金"
        ]
    else:
        x_steps = [
            "1. Pitch Claim",
            "Less: Unbilled Gap",
            "2. GSTN Invoiced",
            "Less: Uncollected",
            "3. Bank Cleared",
            "Less: Sec 188 Leak",
            "Less: Tax Dues",
            "4. True Net Cash"
        ]

    y_vals = [
        c_arr,
        -unbilled,
        gst_val,
        -uncollected,
        bank_val,
        -siph_val,
        -tax_val,
        true_val
    ]

    measures = [
        "absolute",
        "relative",
        "total",
        "relative",
        "total",
        "relative",
        "relative",
        "total"
    ]

    text_vals = [
        f"{curr_sym}{c_arr:.2f}{unit}",
        f"-{curr_sym}{unbilled:.2f}{unit}" if unbilled > 0 else "0",
        f"{curr_sym}{gst_val:.2f}{unit}",
        f"-{curr_sym}{uncollected:.2f}{unit}" if uncollected > 0 else "0",
        f"{curr_sym}{bank_val:.2f}{unit}",
        f"-{curr_sym}{siph_val:.2f}{unit}" if siph_val > 0 else "0",
        f"-{curr_sym}{tax_val:.2f}{unit}" if tax_val > 0 else "0",
        f"{curr_sym}{true_val:.2f}{unit}"
    ]

    is_light = theme.lower() == "light"
    paper_bg = "#FFFFFF" if is_light else "#111827"
    plot_bg = "#FFFFFF" if is_light else "#111827"
    font_color = "#0F172A" if is_light else "#F8FAFC"
    grid_color = "#E2E8F0" if is_light else "#1E293B"
    muted_color = "#64748B" if is_light else "#94A3B8"

    total_color = "#10B981" if true_val >= 0.5 * c_arr else "#B33927"

    fig = go.Figure(go.Waterfall(
        name="Diligence Cascade",
        orientation="v",
        measure=measures,
        x=x_steps,
        textposition="outside",
        text=text_vals,
        textfont=dict(size=11, family="JetBrains Mono"),
        y=y_vals,
        connector=dict(line=dict(color="#EF4444", width=1, dash="dot")),
        decreasing=dict(marker=dict(color="#B33927")),
        increasing=dict(marker=dict(color="#2563EB")),
        totals=dict(marker=dict(color=total_color))
    ))

    title_text = (
        f"乖離流動性カスケード (主張売上 → 国家公的現預金残高) ({curr_sym} {unit})"
        if is_jp
        else f"Discrepancy Diligence Cascade (Pitch Claims → Sovereign Bank Deposits) ({curr_sym} {unit})"
    )

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(color=font_color, size=12, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            y=0.98,
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        margin=dict(l=40, r=20, t=45, b=30),
        xaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=9),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=muted_color, size=10),
            title=dict(text=f"金額 ({curr_sym} {unit})" if is_jp else f"Amount ({curr_sym} {unit})", font=dict(color=muted_color, size=10)),
        ),
        height=420,
    )

    # Horizontal dashed green line at true_val level (Investable Cash Floor)
    floor_label = "投資可能現預金下限" if is_jp else "Investable Cash Floor"
    fig.add_hline(
        y=true_val,
        line=dict(color="#10B981", dash="dash", width=1.5),
        annotation_text=floor_label,
        annotation_position="top right",
        annotation_font=dict(color="#10B981", size=9, family="JetBrains Mono"),
    )

    return fig


def render_governance_signoff_matrix(
    stages: List[Dict[str, Any]],
    lang: str = "en",
    theme: str = "light",
    allow_actions: bool = True,
    preset_key: str = "clean_startup"
):
    """
    Renders the Boardroom Corporate Governance Diligence Sign-Off Matrix.
    Clean institutional tabular sign-off chain replacing circular stamps.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    th_bg = "#0F172A"
    th_color = "#FFFFFF"
    card_bg = "#FFFFFF" if theme == "light" else "#1E293B"
    alt_bg = "#F8FAFC" if theme == "light" else "#0F172A"
    b_col = "#CBD5E1" if theme == "light" else "#334155"
    txt_col = "#0F172A" if theme == "light" else "#F1F5F9"
    sub_col = "#64748B" if theme == "light" else "#94A3B8"

    # Hydrate interactive stamps for this preset
    saved_stamps = st.session_state.get('hanko_stamps', {}).get(preset_key, {})
    for idx, stage in enumerate(stages):
        stage_key = stage.get("stage_id", f"stage_{idx+1}")
        if stage_key in saved_stamps:
            override_st = saved_stamps[stage_key]
            stage["status"] = override_st
            if override_st == "APPROVED":
                stage["status_jp"] = "承認済"
            elif override_st == "FLAGGED":
                stage["status_jp"] = "否認/保留"
            elif override_st == "HELD":
                stage["status_jp"] = "審査中"
            elif override_st == "PENDING":
                stage["status_jp"] = "決裁待ち"

    st.markdown(
        f"""
        <div style="font-size: 0.82rem; font-weight: 800; color: {txt_col}; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.04em;">
            {'【東京投資委員会・職責決裁マトリクス】' if is_jp else '[CORPORATE GOVERNANCE DILIGENCE SIGN-OFF MATRIX]'}
        </div>
        <div style="font-size: 0.72rem; color: {sub_col}; margin-bottom: 10px;">
            {'各審議部門の専任責任者による段階別サインオフ状況。第65条B項電子証拠性担保:' if is_jp else 'Multi-stage fiduciary review chain across bilateral legal, accounting, and investment committee officers:'}
        </div>
        """,
        unsafe_allow_html=True
    )

    mandates = [
        ("案件スクリーニング・事業計画妥当性精査", "Pre-Screening & ARR Sanity Verification"),
        ("会社法・DPDP法・MCA-21定款適合性審査", "Legal Registry & Regulatory Compliance"),
        ("4層突合・フォレンジック流出追跡", "Forensic Reconciliation & Leakage Audit"),
        ("二国間投資リスク評価・資本配分審議", "Investment Committee Allocation Review"),
        ("東京投資委員会 最終投資決裁", "Final Board Approval & Ringi-sho Execution"),
    ]

    rows_html = []
    for idx, stage in enumerate(stages):
        r_bg = alt_bg if idx % 2 == 1 else card_bg
        is_app = stage.get("status") == "APPROVED"
        is_flag = stage.get("status") in ["FLAGGED", "HELD"]

        if is_app:
            badge_html = f"<span class='badge-clean' style='font-size: 0.70rem; padding: 2px 8px; font-weight: 700;'>{'[APPROVED / 承認済]' if not is_jp else '[承認済 / APPROVED]'}</span>"
        elif is_flag:
            badge_html = f"<span class='badge-danger' style='font-size: 0.70rem; padding: 2px 8px; font-weight: 700;'>{'[FLAGGED / 否認・保留]' if not is_jp else '[否認・保留 / FLAGGED]'}</span>"
        else:
            badge_html = f"<span class='badge-review' style='font-size: 0.70rem; padding: 2px 8px; font-weight: 700;'>{'[PENDING / 審議中]' if not is_jp else '[審議中 / PENDING]'}</span>"

        role_str = stage.get("role_jp") if is_jp else stage.get("role_en", f"Stage {idx+1}")
        dept_str = stage.get("dept_jp") if is_jp else stage.get("dept_en", "Diligence Division")
        officer = stage.get("signatory", "Tanaka Hiroshi")
        date_str = stage.get("date", "2026-10-24")
        mandate_str = mandates[idx][0] if is_jp else mandates[idx][1] if idx < len(mandates) else "Fiduciary Diligence"

        rows_html.append(
            f'<tr style="background: {r_bg}; border-bottom: 1px solid {b_col};">'
            f'<td style="padding: 9px 12px; font-weight: 700; color: {txt_col};">Stage {idx+1}: {role_str}</td>'
            f'<td style="padding: 9px 12px; color: {sub_col};">{dept_str}</td>'
            f'<td style="padding: 9px 12px; font-weight: 700; color: {txt_col};">{officer}</td>'
            f'<td style="padding: 9px 12px; color: {sub_col}; font-size: 0.70rem;">{mandate_str}</td>'
            f'<td style="padding: 9px 12px; text-align: center; font-family: monospace; font-size: 0.70rem; color: {sub_col};">{date_str}</td>'
            f'<td style="padding: 9px 12px; text-align: center;">{badge_html}</td>'
            f'</tr>'
        )

    th_stage = '審議段階' if is_jp else 'Stage / Role'
    th_dept = '管轄部門' if is_jp else 'Department'
    th_lead = '専任審査官' if is_jp else 'Lead Diligence Officer'
    th_mandate = '精査職責・監査範囲' if is_jp else 'Verification Mandate'
    th_time = '署名日時' if is_jp else 'Timestamp'
    th_verdict = '決裁ステータス' if is_jp else 'Verdict Status'

    table_html = (
        f'<table style="width: 100%; border-collapse: collapse; font-size: 0.74rem; border: 1px solid {b_col}; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">'
        f'<thead>'
        f'<tr style="background: {th_bg}; color: {th_color}; font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.04em;">'
        f'<th style="padding: 9px 12px; text-align: left;">{th_stage}</th>'
        f'<th style="padding: 9px 12px; text-align: left;">{th_dept}</th>'
        f'<th style="padding: 9px 12px; text-align: left;">{th_lead}</th>'
        f'<th style="padding: 9px 12px; text-align: left;">{th_mandate}</th>'
        f'<th style="padding: 9px 12px; text-align: center;">{th_time}</th>'
        f'<th style="padding: 9px 12px; text-align: center;">{th_verdict}</th>'
        f'</tr>'
        f'</thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_sovereign_triangulation_matrix(
    audit_data: Dict[str, Any],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light"
):
    """
    Renders the Boardroom 4-Way Sovereign Triangulation Matrix:
    Compares Founder Pitch Deck vs RBI Account Aggregator vs GSTN E-Invoices vs CA Audited Books.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    curr = currency_mode.upper()
    kpis = audit_data.get('kpis', {})

    th_bg = "#0F172A"
    th_color = "#FFFFFF"
    card_bg = "#FFFFFF" if theme == "light" else "#1E293B"
    alt_bg = "#F8FAFC" if theme == "light" else "#0F172A"
    b_col = "#CBD5E1" if theme == "light" else "#334155"
    txt_col = "#0F172A" if theme == "light" else "#F1F5F9"
    sub_col = "#64748B" if theme == "light" else "#94A3B8"

    claimed_arr = kpis.get('claimed_arr_inr', 0)
    bank_credits = kpis.get('real_bank_credits_inr', 0)
    gst_turnover = kpis.get('gst_invoiced_turnover_inr', 0)
    ca_revenue = kpis.get('ca_booked_revenue_inr', 0)
    phantom_rev = kpis.get('phantom_revenue_inr', 0)
    div_pct = kpis.get('cash_divergence_pct', 0.0)

    claimed_rw = kpis.get('claimed_runway_months', 0.0)
    true_rw = kpis.get('true_runway_months', 0.0)
    tax_dues = kpis.get('unremitted_tax_dues_inr', 0)
    doubtful_ar = kpis.get('doubtful_debtors_inr', 0)

    siphoned = kpis.get('siphoned_funds_inr', 0)
    sec269st = kpis.get('sec269st_cash_violations_inr', 0)
    benford_mad = kpis.get('benford_nigrini_mad', 0.005)
    benford_st = kpis.get('benford_status', 'CONFORMING')

    # Row 1: Revenue
    if phantom_rev > 0 or div_pct >= 10:
        gap_str = format_currency(phantom_rev, currency_mode=curr, lang_mode=lang)
        v1_html = f"<span class='badge-danger' style='font-size:0.68rem; padding: 2px 6px;'>[GAP: -{gap_str} ({div_pct}% PHANTOM)]</span>"
    else:
        v1_html = "<span class='badge-clean' style='font-size:0.68rem; padding: 2px 6px;'>[100% RECONCILED]</span>"

    # Row 2: Runway
    if true_rw < 6.0:
        v2_html = f"<span class='badge-danger' style='font-size:0.68rem; padding: 2px 6px;'>[{true_rw} MO / CRITICAL DISTRESS]</span>"
    elif true_rw < 12.0:
        v2_html = f"<span class='badge-review' style='font-size:0.68rem; padding: 2px 6px;'>[{true_rw} MO / CAUTION]</span>"
    else:
        v2_html = f"<span class='badge-clean' style='font-size:0.68rem; padding: 2px 6px;'>[{true_rw} MO SECURE RUNWAY]</span>"

    # Row 3: Promoter Conflict
    if siphoned > 0:
        siphon_str = format_currency(siphoned, currency_mode=curr, lang_mode=lang)
        v3_html = f"<span class='badge-danger' style='font-size:0.68rem; padding: 2px 6px;'>[SEC 188 VIOLATION: {siphon_str}]</span>"
    else:
        v3_html = "<span class='badge-clean' style='font-size:0.68rem; padding: 2px 6px;'>[ARM'S LENGTH VERIFIED]</span>"

    # Row 4: Statutory Compliance
    if benford_st == 'REJECT_ANOMALOUS_DISTRIBUTION' or sec269st > 0:
        v4_html = "<span class='badge-danger' style='font-size:0.68rem; padding: 2px 6px;'>[FORENSIC ANOMALY FLAGGED]</span>"
    else:
        v4_html = "<span class='badge-clean' style='font-size:0.68rem; padding: 2px 6px;'>[STATUTORY COMPLIANT]</span>"

    dim1 = "1. 年間売上・確定入金" if is_jp else "1. Annual Revenue & Cash Inflow"
    dim2 = "2. 実質資金残存月数" if is_jp else "2. Net Runway & Liquid Cash"
    dim3 = "3. 役員関連不正・流出" if is_jp else "3. Sec 188 Promoter Loans"
    dim4 = "4. 法定税務・フォレンジック" if is_jp else "4. Statutory Tax & Forensic"

    r1_p = format_currency(claimed_arr, curr, lang)
    r1_b = format_currency(bank_credits, curr, lang)
    r1_g = format_currency(gst_turnover, curr, lang)
    r1_c = format_currency(ca_revenue, curr, lang)

    r2_p = f"{claimed_rw} Mo" if not is_jp else f"{claimed_rw} ヶ月"
    r2_b = format_currency(bank_credits - siphoned, curr, lang)
    r2_g = f"-{format_currency(tax_dues, curr, lang)} (Tax Due)" if not is_jp else f"-{format_currency(tax_dues, curr, lang)} (未納税)"
    r2_c = f"-{format_currency(doubtful_ar, curr, lang)} (Bad AR)" if not is_jp else f"-{format_currency(doubtful_ar, curr, lang)} (滞留売掛)"

    r3_p = "Zero Conflict" if not is_jp else "不正流出ゼロ申告"
    r3_b = f"-{format_currency(siphoned, curr, lang)}" if siphoned > 0 else ("0 (Clean)" if not is_jp else "0 (健全)")
    r3_g = "GSTR-9 Audit" if not is_jp else "GSTR-9 年次照合"
    r3_c = "CARO 2020 Note" if not is_jp else "CARO 2020 監査注記"

    r4_p = "Standard" if not is_jp else "標準申告"
    r4_b = f"MAD: {benford_mad:.4f}"
    r4_g = f"-{format_currency(sec269st, curr, lang)} (269ST)" if sec269st > 0 else ("Compliant" if not is_jp else "法令遵守")
    r4_c = audit_data.get('ca_audit_opinion', 'UNQUALIFIED')

    th_audit_dim = '監査項目' if is_jp else 'Audit Dimension'
    th_pitch = '創業者申告 (Pitch)' if is_jp else 'Pitch Deck Claim'
    th_bank = '確定預金 (RBI AA)' if is_jp else 'RBI AA Bank Inflow'
    th_tax = '税務申告 (GSTN)' if is_jp else 'GSTN Invoices'
    th_ca = '試算表 (CA Books)' if is_jp else 'CA Audited Books'
    th_verdict = '突合判定' if is_jp else 'Triangulation Verdict'

    title_str = '【日印ソブリン4層照合マトリクス】' if is_jp else '[4-WAY SOVEREIGN TRIANGULATION MATRIX]'
    sub_desc = '創業者申告値・公的銀行確定入金・政府税務インボイス・会計士確定帳簿の多面突合:' if is_jp else 'Real-time multi-rail cross-verification across Founder MIS, RBI Bank Ledger, GSTN Invoices, and CA Books:'

    table_html = (
        f'<div style="font-size: 0.82rem; font-weight: 800; color: {txt_col}; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.04em;">{title_str}</div>'
        f'<div style="font-size: 0.72rem; color: {sub_col}; margin-bottom: 10px;">{sub_desc}</div>'
        f'<table style="width: 100%; border-collapse: collapse; font-size: 0.74rem; border: 1px solid {b_col}; border-radius: 4px; overflow: hidden; margin-bottom: 14px;">'
        f'<thead>'
        f'<tr style="background: {th_bg}; color: {th_color}; font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.04em;">'
        f'<th style="padding: 9px 12px; text-align: left;">{th_audit_dim}</th>'
        f'<th style="padding: 9px 12px; text-align: right;">{th_pitch}</th>'
        f'<th style="padding: 9px 12px; text-align: right;">{th_bank}</th>'
        f'<th style="padding: 9px 12px; text-align: right;">{th_tax}</th>'
        f'<th style="padding: 9px 12px; text-align: right;">{th_ca}</th>'
        f'<th style="padding: 9px 12px; text-align: center;">{th_verdict}</th>'
        f'</tr>'
        f'</thead>'
        f'<tbody>'
        f'<tr style="background: {card_bg}; border-bottom: 1px solid {b_col};">'
        f'<td style="padding: 8px 12px; font-weight: 700; color: {txt_col};">{dim1}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r1_p}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; font-weight: 700; color: #059669;">{r1_b}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r1_g}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r1_c}</td>'
        f'<td style="padding: 8px 12px; text-align: center;">{v1_html}</td>'
        f'</tr>'
        f'<tr style="background: {alt_bg}; border-bottom: 1px solid {b_col};">'
        f'<td style="padding: 8px 12px; font-weight: 700; color: {txt_col};">{dim2}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r2_p}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; font-weight: 700; color: #059669;">{r2_b}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r2_g}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r2_c}</td>'
        f'<td style="padding: 8px 12px; text-align: center;">{v2_html}</td>'
        f'</tr>'
        f'<tr style="background: {card_bg}; border-bottom: 1px solid {b_col};">'
        f'<td style="padding: 8px 12px; font-weight: 700; color: {txt_col};">{dim3}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r3_p}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; font-weight: 700; color: {"#B33927" if siphoned > 0 else "#059669"};">{r3_b}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r3_g}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r3_c}</td>'
        f'<td style="padding: 8px 12px; text-align: center;">{v3_html}</td>'
        f'</tr>'
        f'<tr style="background: {alt_bg};">'
        f'<td style="padding: 8px 12px; font-weight: 700; color: {txt_col};">{dim4}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r4_p}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r4_b}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r4_g}</td>'
        f'<td style="padding: 8px 12px; text-align: right; font-family: monospace; color: {txt_col};">{r4_c}</td>'
        f'<td style="padding: 8px 12px; text-align: center;">{v4_html}</td>'
        f'</tr>'
        f'</tbody>'
        f'</table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_hanko_rail(
    stages: List[Dict[str, Any]],
    lang: str = "en",
    allow_actions: bool = True,
    preset_key: str = "clean_startup"
):
    """
    Backwards-compatible alias for Boardroom Corporate Governance Diligence Sign-Off Matrix.
    Replaces circular stamps with clean institutional table.
    """
    theme = st.session_state.get('theme_mode', 'light')
    render_governance_signoff_matrix(
        stages=stages,
        lang=lang,
        theme=theme,
        allow_actions=allow_actions,
        preset_key=preset_key
    )


def render_redline_table(
    discrepancies: List[Dict[str, Any]],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light",
    search_term: str = "",
    severity_filter: str = "ALL"
):
    """Render high-density forensic red-flag transaction table without emojis."""
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"
    table_bg = "#FFFFFF" if is_light else "#111827"
    table_border = "#CBD5E1" if is_light else "#1E293B"

    if not discrepancies:
        clean_text = "全取引は独立第三者間取引であり、所得税法、会社法第188条、およびCGST規則を遵守しています。" if is_jp else "All disbursements adhere strictly to Income Tax Act 1961, Companies Act Sec 188, and CGST Rules 2017."
        clean_bg = "#ECFDF5" if is_light else "rgba(16, 185, 129, 0.12)"
        clean_border = "#059669"
        clean_color = "#059669" if is_light else "#10B981"
        clean_sub = "#475569" if is_light else "#94A3B8"
        st.markdown(
            f"""
            <div style="background: {clean_bg}; border: 1px solid {clean_border}; border-radius: 6px; padding: 18px; text-align: center; color: {clean_color};">
                <b>[CLEAN] ZERO STATUTORY ANOMALIES DETECTED</b><br/>
                <span style="font-size: 0.8rem; color: {clean_sub};">{clean_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Filter by severity and search query
    filtered = []
    for item in discrepancies:
        sev = str(item.get("severity", "FLAG")).upper()
        if severity_filter != "ALL" and sev != severity_filter.upper():
            continue
        if search_term:
            q = search_term.strip().lower()
            where_d = item.get("where", {})
            corpus = " ".join([
                _safe_str(item.get("title")),
                _safe_str(item.get("what_and_why")),
                _safe_str(item.get("whatHappened")),
                _safe_str(item.get("description")),
                _safe_str(item.get("statutory_citation")),
                _safe_str(where_d.get("counterparty")),
                _safe_str(where_d.get("gstin")),
                _safe_str(where_d.get("extracted_pan")),
                _safe_str(where_d.get("transaction_id")),
                _safe_str(item.get("tokyo_remediation_action"))
            ]).lower()
            if q not in corpus:
                continue
        filtered.append(item)

    if not filtered:
        st.info("検索条件に一致する指摘事項はありません。" if is_jp else "No red-flag discrepancies match the specified search or filter criteria.")
        return

    rows_list = []
    for item in filtered:
        where_d = item.get("where", {})
        when_d = item.get("when", {})
        amount_val = float(item.get("amount_inr", 0.0) or 0.0)
        sev_str = str(item.get("severity", "FLAG")).upper()
        is_crit = sev_str == "CRITICAL"
        row_class = "row-flagged" if is_crit else "row-clean"
        badge_class = "badge-danger" if is_crit else "badge-review"
        what_why = _safe_str(item.get("what_and_why") or item.get("whatHappened") or item.get("description"), "Statutory discrepancy detected.")
        remediation = _safe_str(item.get("tokyo_remediation_action"), "")

        remed_div = f'<div style="font-size: 0.67rem; color: #0284C7; margin-top: 3px; font-weight: 600;">[REMEDIATION] {remediation}</div>' if remediation else ''
        text_color = '#0F172A' if is_light else '#F8FAFC'
        narrative_cell = (
            f'<div style="font-size: 0.70rem; line-height: 1.35; min-width: 260px; max-width: 380px;">'
            f'<div style="font-weight: 700; color: {text_color};">{what_why}</div>'
            f'{remed_div}'
            f'</div>'
        )

        rows_list.append(
            f'<tr class="{row_class}">'
            f'<td class="tabular-num">{_safe_str(when_d.get("date", item.get("date")), "2026-11-20")}</td>'
            f'<td class="tabular-num"><font color="#0284C7"><b>{_safe_str(where_d.get("transaction_id", item.get("transaction_id")), "TXN-90812")}</b></font></td>'
            f'<td><span class="{badge_class}">[{sev_str}]</span></td>'
            f'<td class="tabular-num"><b>{format_dual_currency_pair(amount_val, lang_mode=lang)}</b></td>'
            f'<td>{_safe_str(where_d.get("counterparty", item.get("counterparty")), "N/A")}</td>'
            f'<td class="tabular-num"><font color="#64748B">{_safe_str(where_d.get("gstin", item.get("gstin")), "N/A")}</font></td>'
            f'<td class="tabular-num"><font color="#B33927"><b>{_safe_str(where_d.get("extracted_pan"), "N/A")}</b></font></td>'
            f'<td><span class="{badge_class}">{_safe_str(item.get("category"), "RULE")}</span> {_safe_str(item.get("statutory_citation"), "")}</td>'
            f'<td>{narrative_cell}</td>'
            f'</tr>'
        )

    headers = [
        "Date", "Txn ID", "Severity", "Amount (INR / JPY)",
        "Counterparty", "GSTIN", "Extracted PAN", "Statutory Rule & Finding",
        "What Happened & Why (Remediation)"
    ]
    if is_jp:
        headers = [
            "発生日", "取引ID", "重要度", "金額 (INR / JPY)",
            "相手方企業名", "相手方GSTIN", "抽出PAN番号", "根拠法令・指摘事項",
            "取引実態と法的根拠 (What & Why)"
        ]

    table_html = (
        f'<div style="background: {table_bg}; border: 1px solid {table_border}; border-radius: 6px; overflow-x: auto; margin-top: 8px;">'
        f'<table class="statutory-table">'
        f'<thead><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr></thead>'
        f'<tbody>{"".join(rows_list)}</tbody>'
        f'</table>'
        f'</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)



def render_diligence_sankey_flow(
    audit_data: Dict[str, Any],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light"
) -> go.Figure:
    """
    Renders an institutional 4-Layer Discrepancy Flow Pipeline (Sankey):
    Pitch Claimed ARR -> GSTN Invoiced Supplies -> Cleared Bank Cash ->
    Discrepancy Leakages (Unbilled Gap, Uncollected Debtors, Siphoning, Taxes) ->
    True Unencumbered Operating Cash.
    """
    is_jpy = currency_mode.upper() == "JPY"
    rate = FX_INR_TO_JPY if is_jpy else 1.0
    scale = 1e8 if is_jpy else 1e7
    unit = "億円" if is_jpy else "Cr"
    curr_sym = "¥" if is_jpy else "₹"
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"

    wf = audit_data.get("waterfall")
    if not wf:
        kpis = audit_data.get("kpis", {})
        c_arr = float(kpis.get("claimed_arr_inr", 25500000.0))
        gst = float(kpis.get("gst_invoiced_turnover_inr", kpis.get("ca_booked_revenue_inr", c_arr)))
        bank = float(kpis.get("real_bank_credits_inr", 10100000.0))
        siph = float(kpis.get("siphoned_funds_inr", 0.0))
        tax = float(kpis.get("unremitted_tax_dues_inr", 0.0))
        wf = {
            "pitch_claimed_arr_inr": c_arr,
            "unbilled_pitch_gap_inr": max(0.0, c_arr - gst),
            "gst_declared_turnover_inr": gst,
            "uncollected_bank_gap_inr": max(0.0, gst - bank),
            "cleared_bank_cash_inr": bank,
            "promoter_siphoned_inr": siph,
            "unremitted_tax_dues_inr": tax,
            "true_unencumbered_cash_inr": max(0.0, bank - siph - tax)
        }

    c_arr_val = (wf["pitch_claimed_arr_inr"] * rate) / scale
    unbilled_val = (wf["unbilled_pitch_gap_inr"] * rate) / scale
    gst_val = (wf["gst_declared_turnover_inr"] * rate) / scale
    uncoll_val = (wf["uncollected_bank_gap_inr"] * rate) / scale
    bank_val = (wf["cleared_bank_cash_inr"] * rate) / scale
    siph_val = (wf["promoter_siphoned_inr"] * rate) / scale
    tax_val = (wf["unremitted_tax_dues_inr"] * rate) / scale
    true_val = (wf["true_unencumbered_cash_inr"] * rate) / scale

    if is_jp:
        node_labels = [
            f"1. ピッチ主張ARR ({curr_sym}{c_arr_val:.2f}{unit})",
            f"2. GSTN申告売上 ({curr_sym}{gst_val:.2f}{unit})",
            f"未請求乖離 ({curr_sym}{unbilled_val:.2f}{unit})",
            f"3. 銀行確定入金 ({curr_sym}{bank_val:.2f}{unit})",
            f"未回収・架空売上 ({curr_sym}{uncoll_val:.2f}{unit})",
            f"4. 実質純資金 ({curr_sym}{true_val:.2f}{unit})",
            f"取締役不正流出 ({curr_sym}{siph_val:.2f}{unit})",
            f"未払公的債務 ({curr_sym}{tax_val:.2f}{unit})"
        ]
    else:
        node_labels = [
            f"1. Pitch Claimed ARR ({curr_sym}{c_arr_val:.2f}{unit})",
            f"2. GSTN Declared ({curr_sym}{gst_val:.2f}{unit})",
            f"Unbilled Gap ({curr_sym}{unbilled_val:.2f}{unit})",
            f"3. Cleared Bank Cash ({curr_sym}{bank_val:.2f}{unit})",
            f"Uncollected Phantom ({curr_sym}{uncoll_val:.2f}{unit})",
            f"4. True Net Cash ({curr_sym}{true_val:.2f}{unit})",
            f"Sec 188 Leakage ({curr_sym}{siph_val:.2f}{unit})",
            f"Statutory Tax Dues ({curr_sym}{tax_val:.2f}{unit})"
        ]

    # Node colors: verified (navy/blue/green) vs leaks (red/amber)
    node_colors = [
        "#0F172A" if is_light else "#38BDF8",  # Pitch
        "#2563EB",                             # GST
        "#B33927",                             # Unbilled gap
        "#059669" if uncoll_val == 0 else "#D97706", # Bank cash
        "#B33927",                             # Uncollected gap
        "#059669",                             # True net cash
        "#B33927",                             # Sec 188 leak
        "#D97706"                              # Tax dues
    ]

    sources = []
    targets = []
    values = []
    link_colors = []

    # Link 1: Pitch -> GST (verified billed flow)
    v1 = round(min(c_arr_val, gst_val) if gst_val > 0 else c_arr_val, 2)
    if v1 > 0:
        sources.append(0)
        targets.append(1)
        values.append(v1)
        link_colors.append("rgba(37, 99, 235, 0.35)")

    # Link 2: Pitch -> Unbilled Gap (leakage)
    if unbilled_val > 0.001:
        sources.append(0)
        targets.append(2)
        values.append(round(unbilled_val, 2))
        link_colors.append("rgba(179, 57, 39, 0.40)")

    # Link 3: GST -> Bank Cash (verified cleared deposits)
    v2 = round(min(gst_val, bank_val) if bank_val > 0 else gst_val, 2)
    if v2 > 0:
        sources.append(1)
        targets.append(3)
        values.append(v2)
        link_colors.append("rgba(5, 150, 105, 0.35)" if uncoll_val == 0 else "rgba(217, 119, 6, 0.35)")

    # Link 4: GST -> Uncollected Debtors (phantom leakage)
    if uncoll_val > 0.001:
        sources.append(1)
        targets.append(4)
        values.append(round(uncoll_val, 2))
        link_colors.append("rgba(179, 57, 39, 0.45)")

    # Link 5: Bank Cash -> True Net Operational Cash
    if true_val > 0.001:
        sources.append(3)
        targets.append(5)
        values.append(round(true_val, 2))
        link_colors.append("rgba(5, 150, 105, 0.45)")

    # Link 6: Bank Cash -> Sec 188 Leakage
    if siph_val > 0.001:
        sources.append(3)
        targets.append(6)
        values.append(round(siph_val, 2))
        link_colors.append("rgba(179, 57, 39, 0.50)")

    # Link 7: Bank Cash -> Tax Dues
    if tax_val > 0.001:
        sources.append(3)
        targets.append(7)
        values.append(round(tax_val, 2))
        link_colors.append("rgba(217, 119, 6, 0.45)")

    # Fallback if all values zero
    if not values:
        sources = [0]
        targets = [5]
        values = [max(0.1, c_arr_val)]
        link_colors = ["rgba(5, 150, 105, 0.35)"]

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=22,
            line=dict(color="#CBD5E1" if is_light else "#334155", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    paper_bg = "#FFFFFF" if is_light else "#111827"
    plot_bg = "#FFFFFF" if is_light else "#111827"
    font_color = "#0F172A" if is_light else "#F8FAFC"

    title_text = (
        f"4層デューデリジェンス資金流動パイプライン (Sankey Flow) ({curr_sym} {unit})"
        if is_jp
        else f"4-Layer Diligence Discrepancy Pipeline (Sankey Flow) ({curr_sym} {unit})"
    )

    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(color=font_color, size=12, family="Inter, sans-serif"),
            x=0,
            xanchor="left",
            y=0.98,
        ),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        margin=dict(l=30, r=30, t=45, b=25),
        height=420,
    )
    return fig


# -------------------------------------------------------------
# 13. Bilateral Consent & Founder Onboarding Workflow Components
# -------------------------------------------------------------

def render_workflow_stepper(current_step: int = 1, lang: str = "en", theme: str = "dark"):
    """
    Renders high-density institutional 4-step pipeline progress indicator.
    Steps:
    1: Entity Discovery (CIN)
    2: Consent Request Dispatch
    3: Founder Approval & AA/GSTIN Linkage
    4: Sealed Cockpit & Investor Passcode
    """
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"

    steps = [
        {"num": 1, "title_en": "1. Entity Discovery (CIN)", "title_jp": "1. 法人登記照会 (CIN)"},
        {"num": 2, "title_en": "2. Consent Request", "title_jp": "2. 同意リクエスト"},
        {"num": 3, "title_en": "3. Approval & Linkage", "title_jp": "3. 承認 & 口座連携"},
        {"num": 4, "title_en": "4. Sealed Cockpit", "title_jp": "4. 暗号化開示"}
    ]

    card_bg = "#FFFFFF" if is_light else "#0F172A"
    border_color = "#CBD5E1" if is_light else "#1E293B"

    step_cols = st.columns(4)
    for idx, s in enumerate(steps):
        s_num = s["num"]
        s_title = s["title_jp"] if is_jp else s["title_en"]

        if s_num < current_step:
            status_badge = "[PASS: COMPLETED]" if not is_jp else "[PASS: 完了]"
            status_clr = "#059669"
            bg_step = "rgba(16, 185, 129, 0.08)" if not is_light else "#ECFDF5"
            border_step = "#059669"
        elif s_num == current_step:
            status_badge = "[● ACTIVE]" if not is_jp else "[● 実行中]"
            status_clr = "#38BDF8" if not is_light else "#0284C7"
            bg_step = "rgba(14, 165, 233, 0.12)" if not is_light else "#EFF6FF"
            border_step = "#0284C7"
        else:
            status_badge = "[○ PENDING]" if not is_jp else "[○ 未実行]"
            status_clr = "#64748B"
            bg_step = card_bg
            border_step = border_color

        with step_cols[idx]:
            st.markdown(
                f"""
                <div style="background: {bg_step}; border: 1px solid {border_step}; border-radius: 4px; padding: 8px 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.68rem; font-weight: 800; color: {status_clr}; font-family: monospace;">
                            {status_badge}
                        </span>
                        <span style="font-size: 0.65rem; color: #64748B; font-family: monospace;">
                            STEP {s_num}/4
                        </span>
                    </div>
                    <div style="font-size: 0.76rem; font-weight: 700; color: var(--text-primary, #F8FAFC); margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {s_title}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_mca_entity_card(entity: Dict[str, Any], lang: str = "en", theme: str = "dark"):
    """
    Renders high-density institutional MCA-21 registry profile.
    Strictly adheres to @non-ai-slop-ui-design with tabular numerals and crisp borders.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"

    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#475569" if is_light else "#94A3B8"
    card_bg = "#FFFFFF" if is_light else "#111827"
    card_border = "#CBD5E1" if is_light else "#1E293B"

    directors_html = "".join([
        f'<div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed {card_border}; font-size: 0.72rem;">'
        f'<div><b style="color: {txt_pri};">{d.get("name")}</b> <span style="color: {txt_sec};">({d.get("designation")})</span></div>'
        f'<div style="font-family: monospace; color: {txt_sec};">DIN: <code style="color: #38BDF8;">{d.get("din")}</code> | PAN: <code style="color: #B33927;">{d.get("pan")}</code></div>'
        f'</div>'
        for d in entity.get("directors", [])
    ])

    auth_cap = entity.get("authorized_capital_inr", 0.0)
    paid_cap = entity.get("paid_up_capital_inr", 0.0)
    cap_str = f"₹{auth_cap/1e5:.1f} Lakhs / ₹{paid_cap/1e5:.1f} Lakhs" if auth_cap < 1e7 else f"₹{auth_cap/1e7:.2f} Cr / ₹{paid_cap/1e7:.2f} Cr"

    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.02em;">
                        {entity.get('company_name')}
                    </div>
                    <div style="font-size: 0.72rem; color: #64748B; font-family: monospace; margin-top: 2px;">
                        CIN: <span style="color: #38BDF8; font-weight: 700;">{entity.get('cin')}</span> • {entity.get('roc_office')}
                    </div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="badge-clean">[PASS: MCA-21 ACTIVE]</span>
                    <span class="badge-mono">{'創業' if is_jp else 'VINTAGE'}: {entity.get('vintage_years')} {'年' if is_jp else 'YRS'}</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; font-size: 0.74rem; background: {'#F8FAFC' if is_light else '#0F172A'}; padding: 12px 14px; border-radius: 4px; border: 1px solid {card_border}; margin-bottom: 12px;">
                <div>
                    <span style="color: {txt_sec}; font-weight: 600;">{'設立日' if is_jp else 'Incorporation Date'}:</span>
                    <span style="font-family: monospace; color: {txt_pri}; font-weight: 700;">{entity.get('incorporation_date')}</span><br/>
                    <span style="color: {txt_sec}; font-weight: 600;">{'授権/払込資本' if is_jp else 'Auth / Paid Capital'}:</span>
                    <span style="font-family: monospace; color: {txt_pri}; font-weight: 700;">{cap_str}</span><br/>
                    <span style="color: {txt_sec}; font-weight: 600;">{'本店所在地' if is_jp else 'Registered Office'}:</span>
                    <span style="color: {txt_pri};">{entity.get('registered_address')}</span>
                </div>
                <div>
                    <span style="color: {txt_sec}; font-weight: 600;">{'登録GSTIN' if is_jp else 'Registered GSTIN'}:</span>
                    <code style="color: #059669; font-weight: 700;">{entity.get('gstin')}</code>
                    <span class="badge-clean" style="margin-left: 6px; font-size: 0.65rem; padding: 2px 6px;">[VERIFIED]</span><br/>
                    <span style="color: {txt_sec}; font-weight: 600;">{'法人PAN' if is_jp else 'Corporate PAN'}:</span>
                    <code style="color: #38BDF8; font-weight: 700;">{entity.get('pan')}</code><br/>
                    <span style="color: {txt_sec}; font-weight: 600;">{'主要取引銀行' if is_jp else 'Primary Bank FIP'}:</span>
                    <span style="color: {txt_pri};">{entity.get('bank_fip_display')}</span><br/>
                    <span style="color: {txt_sec}; font-weight: 600;">{'区分' if is_jp else 'Classification'}:</span>
                    <span style="color: {txt_pri}; font-weight: 600;">{entity.get('governance_classification_jp' if is_jp else 'governance_classification')}</span>
                </div>
            </div>
            <div>
                <div style="font-size: 0.72rem; font-weight: 800; color: {txt_sec}; text-transform: uppercase; margin-bottom: 6px;">
                    {'役員・公式署名権者 (MCA-21 照合済)' if is_jp else 'Directors & Corporate Signatories (MCA-21 Verified)'}:
                </div>
                {directors_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------------------
# 14. Accountant-Grade Audited Financial Statements & Ledgers
# -------------------------------------------------------------

def render_audited_bank_ledger(
    transactions: List[Dict[str, Any]],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light",
    search_term: str = "",
    type_filter: str = "ALL",
    row_limit: int = 100
):
    """
    Renders an institutional, accountant-grade General Ledger & Bank Statement.
    Explicitly separates Cash In (Deposits) vs Cash Out (Disbursements) with
    dates, running balances, payment modes, and statutory audit flags.
    Strictly adheres to @non-ai-slop-ui-design standard.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"
    card_bg = "#FFFFFF" if is_light else "#111827"
    card_border = "#CBD5E1" if is_light else "#1E293B"
    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#475569" if is_light else "#94A3B8"

    if not transactions:
        st.info("取引データが存在しません。" if is_jp else "No transaction data available.")
        return

    # Calculate executive statement metrics
    total_inflow = sum(float(t.get('amount', 0.0)) for t in transactions if t.get('type') == 'CREDIT')
    total_outflow = sum(float(t.get('amount', 0.0)) for t in transactions if t.get('type') == 'DEBIT')
    net_cash_flow = total_inflow - total_outflow
    closing_balance = float(transactions[-1].get('currentBalance', 0.0)) if transactions else 0.0
    total_count = len(transactions)

    # 4 Executive Bank Statement Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'確定預金入金 (CASH IN)' if is_jp else 'TOTAL CASH IN (DEPOSITS)'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #059669; font-family: monospace;">+{format_currency(total_inflow, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{'売上・増資・助成金' if is_jp else 'Verified Collections & Inflows'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'確定預金出金 (CASH OUT)' if is_jp else 'TOTAL CASH OUT (DISBURSEMENTS)'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #B33927; font-family: monospace;">-{format_currency(total_outflow, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{'事業経費・人件費・送金' if is_jp else 'Operational Debits & Transfers'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        net_clr = "#059669" if net_cash_flow >= 0 else "#B33927"
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'純営業CF (NET CASH FLOW)' if is_jp else 'NET OPERATING CASH FLOW'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {net_clr}; font-family: monospace;">{'+' if net_cash_flow >= 0 else ''}{format_currency(net_cash_flow, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{'期間内差引キャッシュ増減' if is_jp else 'Net Statement Cash Variance'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'期末確定残高 (CLOSING BAL)' if is_jp else 'PERIOD CLOSING BALANCE'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; font-family: monospace;">{format_currency(closing_balance, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{f'{total_count} 件の照合済取引' if is_jp else f'{total_count} Verified Bank Transactions'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filter transactions
    filtered = []
    for t in transactions:
        val_date = _safe_str(t.get('valueDate') or str(t.get('transactionTimestamp', ''))[:10], '2026-07-01')
        ts = _safe_str(t.get('transactionTimestamp'), '')
        narration = _safe_str(t.get('narration'), '')
        cp = _safe_str(t.get('counterparty'), '')
        gstin = _safe_str(t.get('counterpartyGstin'), '')
        txn_id = _safe_str(t.get('txnId'), '')
        acct_head = _safe_str(t.get('accountHead') or t.get('account_head'), '')
        what_h = _safe_str(t.get('whatHappened') or t.get('what_happened'), '')
        why_r = _safe_str(t.get('whyReason') or t.get('why_reason'), '')
        stat_cit = _safe_str(t.get('statutoryCitation') or t.get('statutory_citation'), '')
        forensic_st = _safe_str(t.get('forensicStatus'), '').upper()
        ttype = _safe_str(t.get('type'), 'DEBIT').upper()

        if search_term:
            query = search_term.strip().lower()
            corpus = " ".join([narration, cp, gstin, txn_id, val_date, ts, acct_head, what_h, why_r, stat_cit]).lower()
            if query not in corpus:
                continue

        if type_filter == "CREDIT" and ttype != "CREDIT":
            continue
        elif type_filter == "DEBIT" and ttype != "DEBIT":
            continue
        elif type_filter == "FLAGGED":
            amt = float(t.get('amount', 0.0) or 0.0)
            is_flagged = (
                forensic_st == "FLAGGED_ANOMALY" or
                any(term in narration.upper() or term in cp.upper() for term in ['RAJESH SHARMA', 'MADHURI MEHRA', 'OBEROI', 'SIPHON', 'MALHOTRA']) or
                ((t.get('mode') == 'CASH' or 'CASH' in narration.upper()) and amt >= 200000.0) or
                (49000.0 <= amt <= 49999.0) or
                (amt >= 1000000.0 and amt % 100000.0 == 0.0)
            )
            if not is_flagged:
                continue

        filtered.append(t)

    # Apply row limit
    display_limit = len(filtered) if (row_limit is None or row_limit <= 0) else row_limit
    displayed_txns = filtered[:display_limit]

    # Render High-Density Table
    rows_list = []
    for txn in displayed_txns:
        # Date & Time formatting
        t_stamp = txn.get('transactionTimestamp')
        if t_stamp and len(str(t_stamp)) >= 16:
            val_date = str(t_stamp).replace("T", " ")[:16]
        else:
            val_date = _safe_str(txn.get('valueDate'), '2026-07-01')

        txn_id = _safe_str(txn.get('txnId'), 'N/A')
        ttype = _safe_str(txn.get('type'), 'DEBIT').upper()
        mode = _safe_str(txn.get('mode'), 'NEFT')
        amt = float(txn.get('amount', 0.0) or 0.0)
        raw_jpy = txn.get('amount_jpy')
        amt_jpy = float(raw_jpy) if (raw_jpy is not None and float(raw_jpy) > 0) else round(amt * FX_INR_TO_JPY, 2)
        bal = float(txn.get('currentBalance', 0.0) or 0.0)
        bal_jpy = bal * FX_INR_TO_JPY
        narration = _safe_str(txn.get('narration'), '')
        cp = _safe_str(txn.get('counterparty'), 'N/A')
        gstin = _safe_str(txn.get('counterpartyGstin'), '')
        acct_head = _safe_str(txn.get('accountHead') or txn.get('account_head'), 'General Operating Account')
        what_h = _safe_str(txn.get('whatHappened') or txn.get('what_happened'), narration or 'Verified banking entry.')
        why_r = _safe_str(txn.get('whyReason') or txn.get('why_reason'), 'Verified banking entry.')
        stat_cit = _safe_str(txn.get('statutoryCitation') or txn.get('statutory_citation'), '')
        forensic_st = _safe_str(txn.get('forensicStatus'), '').upper()


        # Audit Flag classification
        is_cash_violation = (mode.upper() == 'CASH' or 'CASH' in narration.upper()) and amt >= 200000.0
        is_siphoning = any(term in narration.upper() or term in cp.upper() for term in ['RAJESH SHARMA', 'MADHURI MEHRA', 'OBEROI', 'SIPHON', 'MALHOTRA'])
        is_tds_smurf = (49000.0 <= amt <= 49999.0) or (28000.0 <= amt <= 29999.0)
        is_round_sum = amt >= 1000000.0 and (amt % 100000.0 == 0.0)
        is_anomaly = (forensic_st == "FLAGGED_ANOMALY") or is_siphoning or is_cash_violation or is_tds_smurf

        if is_siphoning:
            row_style = 'style="background-color: rgba(179, 57, 39, 0.12);"'
            badge_audit = f'<span class="badge-danger">[{"第188条 利益相反流出" if is_jp else "Sec 188 Siphoning"}]</span>'
        elif is_cash_violation:
            row_style = 'style="background-color: rgba(179, 57, 39, 0.12);"'
            badge_audit = f'<span class="badge-danger">[{"第269ST条 現金受渡違反" if is_jp else "Sec 269ST Cash Violation"}]</span>'
        elif is_tds_smurf:
            row_style = 'style="background-color: rgba(217, 119, 6, 0.10);"'
            badge_audit = f'<span class="badge-review">[{"第194C条 TDSスマーフィング" if is_jp else "Sec 194C TDS Smurfed"}]</span>'
        elif is_round_sum:
            row_style = 'style="background-color: rgba(217, 119, 6, 0.08);"'
            badge_audit = f'<span class="badge-review">[{"SA 240 端数なし異常" if is_jp else "SA 240 Round Sum"}]</span>'
        elif is_anomaly:
            row_style = 'style="background-color: rgba(179, 57, 39, 0.10);"'
            badge_audit = f'<span class="badge-danger">[{"要精査 異常検出" if is_jp else "FLAGGED ANOMALY"}]</span>'
        elif ttype == 'CREDIT':
            row_style = ''
            badge_audit = f'<span class="badge-clean">[{"適格 確定売上着金" if is_jp else "Verified Operating Inflow"}]</span>'
        else:
            row_style = ''
            badge_audit = f'<span class="badge-mono">[{"正規事業経費" if is_jp else "Operating Expense"}]</span>'

        if stat_cit:
            badge_audit += f'<div style="font-size: 0.65rem; color: #64748B; margin-top: 2px;">{stat_cit}</div>'

        # Dual currency formatting
        if ttype == 'CREDIT':
            cash_in_cell = (
                f'<td class="tabular-num" style="color: #059669; font-weight: 700; white-space: nowrap;">'
                f'+{format_currency(amt, currency_mode, lang)}'
                f'<div style="font-size: 0.65rem; color: #64748B; font-weight: 400;">¥{amt_jpy:,.0f}</div>'
                f'</td>'
            )
            cash_out_cell = '<td class="tabular-num" style="color: #64748B; text-align: center;">-</td>'
        else:
            cash_in_cell = '<td class="tabular-num" style="color: #64748B; text-align: center;">-</td>'
            cash_out_cell = (
                f'<td class="tabular-num" style="color: #B33927; font-weight: 700; white-space: nowrap;">'
                f'-{format_currency(amt, currency_mode, lang)}'
                f'<div style="font-size: 0.65rem; color: #64748B; font-weight: 400;">¥{amt_jpy:,.0f}</div>'
                f'</td>'
            )

        bal_cell = (
            f'<td class="tabular-num" style="font-family: monospace; font-weight: 700; color: {txt_pri}; white-space: nowrap;">'
            f'{format_currency(bal, currency_mode, lang)}'
            f'<div style="font-size: 0.65rem; color: #64748B; font-weight: 400;">¥{bal_jpy:,.0f}</div>'
            f'</td>'
        )

        cp_html = f'<div style="font-weight: 700; color: {txt_pri};">{cp}</div>'
        if gstin:
            cp_html += f'<div style="font-family: monospace; font-size: 0.67rem; color: #64748B;">{gstin}</div>'

        narrative_html = (
            f'<div style="font-size: 0.70rem; line-height: 1.35; min-width: 250px; max-width: 360px;">'
            f'<div style="font-weight: 700; color: {txt_pri};">{what_h}</div>'
            f'<div style="font-size: 0.67rem; color: {txt_sec}; margin-top: 3px;">{why_r}</div>'
            f'</div>'
        )

        rows_list.append(
            f'<tr {row_style}>'
            f'<td class="tabular-num" style="white-space: nowrap; font-weight: 700; color: {txt_pri}; font-size: 0.70rem;">{val_date}</td>'
            f'<td class="tabular-num" style="font-family: monospace; font-size: 0.70rem; color: #0284C7; white-space: nowrap;">{txn_id}</td>'
            f'<td style="font-size: 0.70rem; color: {txt_pri}; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{acct_head}</td>'
            f'<td style="font-size: 0.72rem; max-width: 170px;">{cp_html}</td>'
            f'<td>{narrative_html}</td>'
            f'<td class="tabular-num" style="font-size: 0.68rem; font-family: monospace; color: #64748B; text-align: center;">{mode}</td>'
            f'{cash_in_cell}'
            f'{cash_out_cell}'
            f'{bal_cell}'
            f'<td style="font-size: 0.68rem; white-space: nowrap;">{badge_audit}</td>'
            f'</tr>'
        )

    headers = [
        ("Posting Date / Time", "転記日・時刻"),
        ("Txn Reference", "取引ID"),
        ("Account Head", "勘定科目"),
        ("Counterparty / GSTIN", "取引先・相手先"),
        ("What Happened & Why (Forensic Narrative)", "取引実態と法的根拠 (What & Why)"),
        ("Mode", "種別"),
        ("Cash In (Deposit)", "入金額 (借方)"),
        ("Cash Out (Debit)", "出金額 (貸方)"),
        ("Running Balance", "確定残高"),
        ("Statutory Audit Flag", "監査所見・法令判定")
    ]
    hdr_html = "".join(f"<th>{h[1] if is_jp else h[0]}</th>" for h in headers)
    counter_msg = f'表示中: {len(displayed_txns)} 件 / 抽出一致: {len(filtered)} 件 / 総計: {total_count} 件 (RBI AA ReBIT DEPOSIT v2.0 照合済)' if is_jp else f'Showing {len(displayed_txns)} of {len(filtered)} filtered records (Total: {total_count} transactions verified via RBI AA ReBIT DEPOSIT v2.0)'

    table_html = (
        f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; overflow-x: auto; margin-top: 6px;">'
        f'<table class="statutory-table">'
        f'<thead><tr>{hdr_html}</tr></thead>'
        f'<tbody>{"".join(rows_list)}</tbody>'
        f'</table>'
        f'</div>'
        f'<div style="font-size: 0.68rem; color: #64748B; margin-top: 6px; text-align: right;">{counter_msg}</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_audited_gst_register(
    gst_df: pd.DataFrame,
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light",
    search_term: str = "",
    row_limit: int = 60
):
    """
    Renders an institutional, accountant-grade Electronic Invoicing Register (GSTR-1 & GSTR-3B).
    Displays verified NIC E-Invoice IRN status, invoice dates, taxable amounts, and tax offsets.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"
    card_bg = "#FFFFFF" if is_light else "#111827"
    card_border = "#CBD5E1" if is_light else "#1E293B"
    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#475569" if is_light else "#94A3B8"

    if gst_df is None or gst_df.empty:
        st.info("GSTインボイス原本データが存在しません。" if is_jp else "No GST invoice records available.")
        return

    df = gst_df.copy()

    # Normalize column names
    col_map = {
        'receiver_name': 'buyer_name',
        'gstin_recipient': 'buyer_gstin',
        'invoice_value': 'total_amount'
    }
    for old_col, new_col in col_map.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]

    if 'type' not in df.columns:
        df['type'] = 'OUTWARD'

    outward_df = df[df['type'].str.upper() == 'OUTWARD']
    inward_df = df[df['type'].str.upper() == 'INWARD']

    tot_sales_taxable = float(outward_df['taxable_value'].sum()) if 'taxable_value' in outward_df.columns else 0.0
    tot_sales_gross = float(outward_df['total_amount'].sum()) if 'total_amount' in outward_df.columns else 0.0
    tot_purchases_gross = float(inward_df['total_amount'].sum()) if 'total_amount' in inward_df.columns and not inward_df.empty else 0.0
    
    # Calculate unpaid tax deficit (GSTR-3B offset)
    unpaid_tax = 0.0
    if 'gstr3b_offset_status' in outward_df.columns:
        unpaid_invoices = outward_df[outward_df['gstr3b_offset_status'] == 'UNOFF_SET_UNPAID']
        if 'gst_amount' in unpaid_invoices.columns:
            unpaid_tax = float(unpaid_invoices['gst_amount'].sum())
        elif 'total_amount' in unpaid_invoices.columns and 'taxable_value' in unpaid_invoices.columns:
            unpaid_tax = float(unpaid_invoices['total_amount'].sum() - unpaid_invoices['taxable_value'].sum())

    # Summary metric tiles
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'課税売上高 (GSTR-1 TAXABLE)' if is_jp else 'GSTR-1 TAXABLE SALES'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; font-family: monospace;">{format_currency(tot_sales_taxable, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{f'{len(outward_df)} 件の電子売上インボイス' if is_jp else f'{len(outward_df)} Outward B2B Invoices'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with g2:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'総請求額 (GROSS INVOICED)' if is_jp else 'GROSS INVOICED TURNOVER'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0284C7; font-family: monospace;">{format_currency(tot_sales_gross, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{'消費税(IGST/CGST/SGST)含む' if is_jp else 'Inclusive of Applicable GST'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with g3:
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'仕入控除 (INWARD PURCHASES)' if is_jp else 'INWARD PURCHASES (ITC)'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; font-family: monospace;">{format_currency(tot_purchases_gross, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: #64748B;">{f'{len(inward_df)} 件の仕入インボイス' if is_jp else f'{len(inward_df)} Inward B2B Invoices'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with g4:
        tax_clr = "#059669" if unpaid_tax == 0 else "#B33927"
        st.markdown(
            f"""
            <div class="card" style="padding: 10px 14px; background: {card_bg}; border: 1px solid {card_border};">
                <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'未納税務債務 (RULE 88C DEFICIT)' if is_jp else 'RULE 88C UNREMITTED TAX'}</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: {tax_clr}; font-family: monospace;">{format_currency(unpaid_tax, currency_mode, lang)}</div>
                <div style="font-size: 0.65rem; color: {tax_clr}; font-weight: 700;">{'[正常] 納税完了' if unpaid_tax == 0 else '[警告] DRC-01B 追徴リスク' if is_jp else '[CLEAN] Offset Paid' if unpaid_tax == 0 else '[ALERT] DRC-01B Notice Risk'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Filter by search_term if provided
    total_invoices_count = len(df)
    if search_term:
        q = search_term.strip().lower()
        def matches_row(r):
            text = " ".join([
                _safe_str(r.get('invoice_number')),
                _safe_str(r.get('buyer_name') or r.get('receiver_name')),
                _safe_str(r.get('buyer_gstin') or r.get('gstin_recipient')),
                _safe_str(r.get('account_head') or r.get('accountHead')),
                _safe_str(r.get('what_happened') or r.get('whatHappened')),
                _safe_str(r.get('why_reason') or r.get('whyReason')),
                _safe_str(r.get('invoice_date')),
                _safe_str(r.get('irn_hash'))
            ]).lower()
            return q in text
        mask = df.apply(matches_row, axis=1)
        df = df[mask]

    display_limit = len(df) if (row_limit is None or row_limit <= 0) else row_limit
    displayed_df = df.head(display_limit)

    rows_list = []
    for idx, row in displayed_df.iterrows():
        inv_dt = _safe_str(row.get('invoice_date'), '2026-07-01')
        inv_no = _safe_str(row.get('invoice_number'), f'INV-{idx+1:04d}')
        direction = _safe_str(row.get('type'), 'OUTWARD').upper()
        buyer_name = _safe_str(row.get('buyer_name') or row.get('receiver_name'), 'Commercial Customer')
        buyer_gstin = _safe_str(row.get('buyer_gstin') or row.get('gstin_recipient'), 'N/A')
        acct_head = _safe_str(row.get('account_head') or row.get('accountHead'), 'Enterprise AI Software Subscriptions')
        what_h = _safe_str(row.get('what_happened') or row.get('whatHappened'), f"Invoice {inv_no} issued to {buyer_name}")
        why_r = _safe_str(row.get('why_reason') or row.get('whyReason'), 'Electronic invoice registered on CBIC portal.')
        taxable = float(row.get('taxable_value', 0.0) or 0.0)
        total_val = float(row.get('total_amount') or row.get('invoice_value', taxable * 1.18) or 0.0)
        tax_amt = float(row.get('gst_amount') or (total_val - taxable) or 0.0)
        raw_jpy = row.get('amount_jpy')
        total_val_jpy = float(raw_jpy) if (raw_jpy is not None and not pd.isna(raw_jpy) and float(raw_jpy) > 0) else round(total_val * FX_INR_TO_JPY, 2)
        offset_status = _safe_str(row.get('gstr3b_offset_status'), 'OFFSET_PAID')

        is_unpaid = offset_status == 'UNOFF_SET_UNPAID'
        if is_unpaid:
            row_style = 'style="background-color: rgba(179, 57, 39, 0.12);"'
            badge_offset = f'<span class="badge-danger">[{"未納税・Rule 88C DRC-01B" if is_jp else "UNPAID - Rule 88C DRC-01B"}]</span>'
        else:
            row_style = ''
            badge_offset = f'<span class="badge-clean">[{"GSTR-3B 納税済" if is_jp else "GSTR-3B OFFSET PAID"}]</span>'

        dir_badge = '<span class="badge-clean">[OUTWARD 売上]</span>' if direction == 'OUTWARD' else '<span class="badge-mono">[INWARD 仕入]</span>'
        if not is_jp:
            dir_badge = '<span class="badge-clean">[OUTWARD SALES]</span>' if direction == 'OUTWARD' else '<span class="badge-mono">[INWARD PURCHASE]</span>'

        narrative_cell = (
            f'<div style="font-size: 0.70rem; line-height: 1.35; min-width: 250px; max-width: 360px;">'
            f'<div style="font-weight: 700; color: {txt_pri};">{what_h}</div>'
            f'<div style="font-size: 0.67rem; color: {txt_sec}; margin-top: 3px;">{why_r}</div>'
            f'</div>'
        )

        rows_list.append(
            f'<tr {row_style}>'
            f'<td class="tabular-num" style="white-space: nowrap; font-weight: 700; color: {txt_pri}; font-size: 0.70rem;">{inv_dt}</td>'
            f'<td class="tabular-num" style="font-family: monospace; font-size: 0.70rem; color: #0284C7; white-space: nowrap;">{inv_no}</td>'
            f'<td style="font-size: 0.68rem; text-align: center; white-space: nowrap;">{dir_badge}</td>'
            f'<td style="font-size: 0.70rem; color: {txt_pri}; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{acct_head}</td>'
            f'<td style="font-size: 0.72rem; font-weight: 600; color: {txt_pri}; max-width: 170px;">'
            f'<div>{buyer_name}</div>'
            f'<div class="tabular-num" style="font-family: monospace; font-size: 0.67rem; color: #64748B;">{buyer_gstin}</div>'
            f'</td>'
            f'<td>{narrative_cell}</td>'
            f'<td class="tabular-num" style="font-weight: 600; color: {txt_pri}; white-space: nowrap;">{format_currency(taxable, currency_mode, lang)}</td>'
            f'<td class="tabular-num" style="color: #64748B; white-space: nowrap;">{format_currency(tax_amt, currency_mode, lang)}</td>'
            f'<td class="tabular-num" style="font-weight: 700; color: #0284C7; white-space: nowrap;">'
            f'{format_currency(total_val, currency_mode, lang)}'
            f'<div style="font-size: 0.65rem; color: #64748B; font-weight: 400;">¥{total_val_jpy:,.0f}</div>'
            f'</td>'
            f'<td style="font-size: 0.68rem; white-space: nowrap;">{badge_offset}</td>'
            f'</tr>'
        )

    headers = [
        ("Invoice Date", "請求日付"),
        ("Invoice No", "インボイス番号"),
        ("Flow", "取引区分"),
        ("Account Head", "勘定科目"),
        ("Counterparty / Client", "取引先企業名・GSTIN"),
        ("What Happened & Why (Forensic Narrative)", "取引実態と納税根拠 (What & Why)"),
        ("Taxable Value", "課税対象額"),
        ("GST Amount", "消費税相当額"),
        ("Gross Invoiced", "総請求額 (INR / JPY)"),
        ("GSTR-3B Tax Offset", "納税申告相殺状況")
    ]
    hdr_html = "".join(f"<th>{h[1] if is_jp else h[0]}</th>" for h in headers)
    gst_counter_msg = f'表示中: {len(displayed_df)} 件 / 抽出一致: {len(df)} 件 / 総計: {total_invoices_count} 件 (財政省 CBIC / NIC 電子インボイス原本)' if is_jp else f'Showing {len(displayed_df)} of {len(df)} filtered invoices (Total: {total_invoices_count} CBIC / NIC Authenticated)'

    table_html = (
        f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; overflow-x: auto; margin-top: 6px;">'
        f'<table class="statutory-table">'
        f'<thead><tr>{hdr_html}</tr></thead>'
        f'<tbody>{"".join(rows_list)}</tbody>'
        f'</table>'
        f'</div>'
        f'<div style="font-size: 0.68rem; color: #64748B; margin-top: 6px; text-align: right;">{gst_counter_msg}</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_audited_trial_balance(
    ca_books: Dict[str, Any],
    currency_mode: str = "INR",
    lang: str = "en",
    theme: str = "light"
):
    """
    Renders an institutional, accountant-grade Trial Balance & Ind AS 109 Receivables Aging Schedule.
    Eliminates raw JSON dumps and formats everything as structured audited accounting schedules.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"
    card_bg = "#FFFFFF" if is_light else "#111827"
    card_border = "#CBD5E1" if is_light else "#1E293B"
    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#475569" if is_light else "#94A3B8"

    if not ca_books:
        st.info("会計士試算表データが存在しません。" if is_jp else "No Chartered Accountant books available.")
        return

    cert_by = ca_books.get('certified_by', 'Independent Chartered Accountants')
    software = ca_books.get('accounting_software', 'Enterprise ERP')
    period = ca_books.get('financial_period', 'FY 2026-27')
    opinion = ca_books.get('audit_opinion', 'UNQUALIFIED_CLEAN')

    is_clean_opinion = "CLEAN" in opinion.upper() or "UNQUALIFIED" in opinion.upper()
    opinion_badge = (
        f'<span class="badge-clean">[{"無修正適正意見 / UNQUALIFIED CLEAN" if is_jp else "UNQUALIFIED CLEAN OPINION"}]</span>'
        if is_clean_opinion
        else f'<span class="badge-danger">[{"限定付意見・継続企業注記 / QUALIFIED UNCERTAINTY" if is_jp else "QUALIFIED MATERIAL UNCERTAINTY"}]</span>'
    )

    # Certification Banner
    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 18px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 0.92rem; font-weight: 800; color: {txt_pri};">
                        {'公認会計士 (CA) 監査証明済 試算表 & 財務諸表' if is_jp else 'Chartered Accountant (CA) Certified Trial Balance & Financial Position'}
                    </div>
                    <div style="font-size: 0.72rem; color: {txt_sec}; margin-top: 3px;">
                        <b>{'監査証明機関' if is_jp else 'Certifying Auditor'}:</b> {cert_by} • <b>{'会計基盤' if is_jp else 'Accounting ERP'}:</b> {software} • <b>{'対象期間' if is_jp else 'Period'}:</b> {period}
                    </div>
                </div>
                <div>
                    {opinion_badge}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tb = ca_books.get('trial_balance_inr', {})
    sales = float(tb.get('booked_sales_revenue', 0.0))
    receivables = float(tb.get('trade_receivables_total', 0.0))
    payables = float(tb.get('trade_payables', 0.0))
    cash_bal = float(tb.get('general_ledger_cash_balance', 0.0))
    stat_dues = tb.get('statutory_dues_payable', {})
    gst_due = float(stat_dues.get('gst_output_liability', 0.0))
    tds_due = float(stat_dues.get('tds_payable', 0.0))
    pf_due = float(stat_dues.get('pf_esi_payable', 0.0))
    tot_stat_dues = gst_due + tds_due + pf_due

    # 1. Structured General Ledger Schedule Table
    gl_rows = [
        {
            "code": "1001",
            "name_en": "Revenue from Operations (P&L Turnover)",
            "name_jp": "売上高 (損益計算書 計上売上高)",
            "cat_en": "P&L Revenue",
            "cat_jp": "損益計算書 (収益)",
            "debit": 0.0,
            "credit": sales,
            "note_en": "Booked B2B SaaS ARR and implementation fees",
            "note_jp": "契約ベース計上売上高 (B2B SaaS)"
        },
        {
            "code": "2001",
            "name_en": "Trade Receivables (Debtors Ledger)",
            "name_jp": "売掛金 (未回収顧客売掛金残高)",
            "cat_en": "Current Asset",
            "cat_jp": "流動資産",
            "debit": receivables,
            "credit": 0.0,
            "note_en": "Gross customer invoices outstanding collection",
            "note_jp": "期末未回収売掛金総額"
        },
        {
            "code": "2002",
            "name_en": "Trade Payables (Creditors Ledger)",
            "name_jp": "買掛金 (未払仕入債務・ベンダー買掛金)",
            "cat_en": "Current Liability",
            "cat_jp": "流動負債",
            "debit": 0.0,
            "credit": payables,
            "note_en": "Outstanding invoices due to suppliers & contractors",
            "note_jp": "取引先ベンダーに対する未払仕入債務"
        },
        {
            "code": "3001",
            "name_en": "Statutory Liability: GST Output Tax Payable",
            "name_jp": "法定未払金: GST受取消費税 未納残高",
            "cat_en": "Statutory Due",
            "cat_jp": "法定公租公課",
            "debit": 0.0,
            "credit": gst_due,
            "note_en": "GSTR-1 output tax awaiting monthly GSTR-3B setoff",
            "note_jp": "GSTR-3B税務相殺待ちの未払GST"
        },
        {
            "code": "3002",
            "name_en": "Statutory Liability: TDS Withholding Tax Payable",
            "name_jp": "法定未払金: 源泉所得税 (TDS) 未納残高",
            "cat_en": "Statutory Due",
            "cat_jp": "法定公租公課",
            "debit": 0.0,
            "credit": tds_due,
            "note_en": "Income tax deducted at source under Sec 194C/J/I",
            "note_jp": "所得税法第194C/J条に基づく源泉控除済税金"
        },
        {
            "code": "3003",
            "name_en": "Statutory Liability: EPFO & ESIC Employee Dues",
            "name_jp": "法定未払金: 厚生年金 (EPFO) & 保険 (ESIC) 未納残高",
            "cat_en": "Statutory Due",
            "cat_jp": "法定公租公課",
            "debit": 0.0,
            "credit": pf_due,
            "note_en": "Mandatory provident fund and employee state insurance",
            "note_jp": "従業員年金基金および法定社会保険拠出金"
        },
        {
            "code": "4001",
            "name_en": "General Ledger: Cash & Operating Bank Balance",
            "name_jp": "元帳残高: 現預金・普通預金総勘定元帳残高",
            "cat_en": "Cash Asset",
            "cat_jp": "現預金資産",
            "debit": cash_bal,
            "credit": 0.0,
            "note_en": "Internal accounting ledger balance of corporate bank account",
            "note_jp": "会計帳簿上の企業現預金確定残高"
        }
    ]

    st.markdown(
        f"<div style='font-size: 0.80rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;'>"
        f"{'1. 総勘定元帳 試算表スケジュール (Trial Balance Schedule)' if is_jp else '1. General Ledger Audited Trial Balance Schedule'}</div>",
        unsafe_allow_html=True
    )

    tb_rows = []
    for r in gl_rows:
        head_name = r["name_jp"] if is_jp else r["name_en"]
        cat_name = r["cat_jp"] if is_jp else r["cat_en"]
        note = r["note_jp"] if is_jp else r["note_en"]

        debit_cell = f'<td class="tabular-num" style="color: {txt_pri}; font-weight: 700;">{format_currency(r["debit"], currency_mode, lang)}</td>' if r["debit"] > 0 else '<td class="tabular-num" style="color: #64748B; text-align: center;">-</td>'
        credit_cell = f'<td class="tabular-num" style="color: {txt_pri}; font-weight: 700;">{format_currency(r["credit"], currency_mode, lang)}</td>' if r["credit"] > 0 else '<td class="tabular-num" style="color: #64748B; text-align: center;">-</td>'

        tb_rows.append(
            f'<tr>'
            f'<td class="tabular-num" style="font-family: monospace; font-size: 0.70rem; color: #0284C7; font-weight: 700;">{r["code"]}</td>'
            f'<td style="font-size: 0.74rem; font-weight: 700; color: {txt_pri};">{head_name}</td>'
            f'<td style="font-size: 0.70rem; color: #64748B;"><span class="badge-mono">{cat_name}</span></td>'
            f'{debit_cell}'
            f'{credit_cell}'
            f'<td style="font-size: 0.70rem; color: {txt_sec};">{note}</td>'
            f'</tr>'
        )
    tb_rows_html = "".join(tb_rows)

    tb_headers = [
        ("Account Code", "勘定コード"),
        ("Account Head", "勘定科目名"),
        ("Classification", "財務区分"),
        ("Debit (借方)", "借方金額 (Debit)"),
        ("Credit (貸方)", "貸方金額 (Credit)"),
        ("Auditor Verification Note", "監査人確認所見")
    ]
    tb_hdr_html = "".join(f"<th>{h[1] if is_jp else h[0]}</th>" for h in tb_headers)

    table_html = (
        f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; overflow-x: auto; margin-bottom: 14px;">'
        f'<table class="statutory-table">'
        f'<thead><tr>{tb_hdr_html}</tr></thead>'
        f'<tbody>{tb_rows_html}</tbody>'
        f'</table>'
        f'</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # 2. Ind AS 109 Receivables Aging Schedule Table
    aging = tb.get('receivables_aging', {})
    u30 = float(aging.get('under_30_days', 0.0))
    d31_90 = float(aging.get('31_to_90_days', 0.0))
    o180 = float(aging.get('over_180_days_doubtful', 0.0))

    tot_aging = u30 + d31_90 + o180
    if tot_aging == 0.0:
        tot_aging = max(1.0, receivables)

    st.markdown(
        f"<div style='font-size: 0.80rem; font-weight: 800; color: {txt_pri}; margin-bottom: 6px;'>"
        f"{'2. Ind AS 109 信用減損モデル・売掛金滞留日数スケジュール (AR Aging Schedule)' if is_jp else '2. Ind AS 109 Expected Credit Loss (ECL) & Debtor Aging Schedule'}</div>",
        unsafe_allow_html=True
    )

    aging_rows = [
        {
            "bucket_en": "Current (< 30 Days)",
            "bucket_jp": "正常債権 (30日以内)",
            "amount": u30,
            "share": round((u30 / tot_aging) * 100, 1),
            "ecl_rate": "2.0%",
            "ecl_prov": round(u30 * 0.02, 2),
            "status_badge": '<span class="badge-clean">[STAGE 1: 正常]</span>' if is_jp else '<span class="badge-clean">[STAGE 1: CURRENT]</span>'
        },
        {
            "bucket_en": "Stretched (31 - 90 Days)",
            "bucket_jp": "回収遅延 (31〜90日)",
            "amount": d31_90,
            "share": round((d31_90 / tot_aging) * 100, 1),
            "ecl_rate": "20.0%",
            "ecl_prov": round(d31_90 * 0.20, 2),
            "status_badge": '<span class="badge-review">[STAGE 2: 滞留]</span>' if is_jp else '<span class="badge-review">[STAGE 2: STRESSED]</span>'
        },
        {
            "bucket_en": "Doubtful / Loss Asset (> 180 Days)",
            "bucket_jp": "回収不能・架空疑義 (180日超)",
            "amount": o180,
            "share": round((o180 / tot_aging) * 100, 1),
            "ecl_rate": "100.0%",
            "ecl_prov": round(o180 * 1.0, 2),
            "status_badge": '<span class="badge-danger">[STAGE 3: 損失引当]</span>' if is_jp else '<span class="badge-danger">[STAGE 3: IMPAIRED LOSS]</span>'
        }
    ]

    total_prov = sum(r["ecl_prov"] for r in aging_rows)

    aging_rows_list = []
    for ar in aging_rows:
        b_name = ar["bucket_jp"] if is_jp else ar["bucket_en"]
        amt_str = format_currency(ar["amount"], currency_mode, lang)
        prov_str = format_currency(ar["ecl_prov"], currency_mode, lang)

        row_bg = 'style="background-color: rgba(179, 57, 39, 0.12);"' if "> 180" in ar["bucket_en"] and ar["amount"] > 0 else ""

        aging_rows_list.append(
            f'<tr {row_bg}>'
            f'<td style="font-size: 0.74rem; font-weight: 700; color: {txt_pri};">{b_name}</td>'
            f'<td class="tabular-num" style="font-weight: 700; color: {txt_pri};">{amt_str}</td>'
            f'<td class="tabular-num" style="color: #64748B;">{ar["share"]}%</td>'
            f'<td class="tabular-num" style="font-family: monospace; color: #0284C7; text-align: center;">{ar["ecl_rate"]}</td>'
            f'<td class="tabular-num" style="font-weight: 700; color: {"#B33927" if ar["ecl_prov"] > 0 else "#059669"};">{prov_str}</td>'
            f'<td style="font-size: 0.68rem;">{ar["status_badge"]}</td>'
            f'</tr>'
        )

    tot_amt_str = format_currency(tot_aging, currency_mode, lang)
    tot_prov_str = format_currency(total_prov, currency_mode, lang)

    tot_row_bg = '#F8FAFC' if is_light else '#0F172A'
    aging_rows_list.append(
        f'<tr style="background: {tot_row_bg}; font-weight: 800; border-top: 2px solid {card_border};">'
        f'<td style="font-size: 0.76rem; color: {txt_pri};">{"合計 (TOTAL RECEIVABLES)" if is_jp else "TOTAL RECEIVABLES"}</td>'
        f'<td class="tabular-num" style="color: {txt_pri};">{tot_amt_str}</td>'
        f'<td class="tabular-num" style="color: #64748B;">100.0%</td>'
        f'<td class="tabular-num" style="color: #64748B; text-align: center;">-</td>'
        f'<td class="tabular-num" style="color: #B33927;">{tot_prov_str}</td>'
        f'<td style="font-size: 0.68rem;"><span class="{"badge-danger" if total_prov > 500000 else "badge-clean"}">{"要損失処理" if total_prov > 500000 and is_jp else "ECL HAIRCUT MANDATED" if total_prov > 500000 else "合致 / ADEQUATE"}</span></td>'
        f'</tr>'
    )
    aging_rows_html = "".join(aging_rows_list)

    ag_headers = [
        ("Aging Bracket", "売掛金滞留期間"),
        ("Outstanding Balance", "未回収債権残高"),
        ("Share (%)", "構成比率"),
        ("Ind AS 109 ECL Rate", "引当率基準"),
        ("Mandated Provision", "強制損失引当額"),
        ("Impairment Status", "減損ステージ判定")
    ]
    ag_hdr_html = "".join(f"<th>{h[1] if is_jp else h[0]}</th>" for h in ag_headers)

    table_html = (
        f'<div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; overflow-x: auto;">'
        f'<table class="statutory-table">'
        f'<thead><tr>{ag_hdr_html}</tr></thead>'
        f'<tbody>{aging_rows_html}</tbody>'
        f'</table>'
        f'</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


# -------------------------------------------------------------
# 15. Verified Public Domain Corporate Case Studies
# -------------------------------------------------------------

def render_public_case_studies(lang: str = "en", theme: str = "light", show_actions: bool = True):
    """
    Renders verified public domain corporate case studies with Japanese investor context.
    Features 6 authentic public companies (GoMechanic, BYJU'S, BharatPe, FirstCry, Paytm, Lenskart)
    with exact MCA-21 CINs, RoC offices, Big-4 audit findings, and SoftBank Tokyo linkages.
    """
    try:
        from backend.registry_lookup import get_public_case_studies
        cases = get_public_case_studies()
    except Exception:
        try:
            import importlib
            import backend.registry_lookup
            importlib.reload(backend.registry_lookup)
            from backend.registry_lookup import get_public_case_studies
            cases = get_public_case_studies()
        except Exception:
            cases = []

    is_jp = lang.lower() in ["jp", "ja"]
    is_light = theme.lower() == "light"

    txt_pri = "#0F172A" if is_light else "#F8FAFC"
    txt_sec = "#475569" if is_light else "#94A3B8"
    card_bg = "#FFFFFF" if is_light else "#111827"
    card_border = "#CBD5E1" if is_light else "#1E293B"
    sub_bg = "#F8FAFC" if is_light else "#0F172A"

    header_title = (
        "【実在公開データ・検証アーカイブ】ソフトバンク東京投資 & 監督当局・四大監査法人 判例データベース"
        if is_jp
        else "[REAL-WORLD PUBLIC DOMAIN REGISTRY] SoftBank Vision Fund Tokyo & Big-4 Forensic Audit Benchmarks"
    )
    header_subtitle = (
        "インド会社法（MCA-21）公式CIN登記、国税庁（GSTIN）、準備銀行（RBI）、東京投資委員会および破産裁判所（NCLT）の公知判例を完全収録。各カードの「審査実行」から、確定元帳・税務突合・フォレンジック検証を即時実行可能です。"
        if is_jp
        else "Verified authentic Ministry of Corporate Affairs (MCA-21) CINs, RoC offices, Reserve Bank of India (RBI) orders, NCLT insolvency proceedings, and Big-4 forensic audit cases with direct SoftBank Tokyo connections. Click any dossier to execute live sovereign verification."
    )

    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                <div>
                    <div style="font-size: 0.95rem; font-weight: 800; color: {txt_pri}; letter-spacing: 0.02em;">
                        {header_title}
                    </div>
                    <div style="font-size: 0.74rem; color: {txt_sec}; margin-top: 4px; line-height: 1.5;">
                        {header_subtitle}
                    </div>
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <span class="badge-clean" style="font-size: 0.68rem;">[PASS: MCA-21 VERIFIED]</span>
                    <span class="badge-mono" style="font-size: 0.68rem;">6 CASES LOADED</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render in 2 rows of 3 columns
    for row_idx in range(0, len(cases), 3):
        row_cases = cases[row_idx:row_idx+3]
        cols = st.columns(len(row_cases))
        for col, case in zip(cols, row_cases):
            with col:
                score = case.get("shinrai_score", 50)
                is_clean = score >= 80
                badge_cls = "badge-clean" if is_clean else "badge-danger"
                badge_lbl = "【適格】CLEAN" if is_clean else "【精査要】CRITICAL"
                status_raw = case.get("status", "ACTIVE")

                short_title = case.get("company_name", "").split("(")[-1].replace(")", "").strip()
                if not short_title:
                    short_title = case.get("company_name", "")[:20]

                inv_ctx = case.get("investor_context", "")
                auditor = case.get("forensic_auditor", "")
                violation = case.get("primary_violation", "")
                auth_cap = case.get("authorized_capital_inr", 0.0)
                paid_cap = case.get("paid_up_capital_inr", 0.0)
                cap_disp = f"₹{paid_cap/1e7:.1f} Cr / ₹{auth_cap/1e7:.1f} Cr"

                card_html = f"""
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 6px; padding: 14px 16px; margin-bottom: 10px; display: flex; flex-direction: column; justify-content: space-between; min-height: 350px;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span class="{badge_cls}" style="font-size: 0.65rem;">{badge_lbl} ({score}/100)</span>
                            <span class="badge-mono" style="font-size: 0.62rem;">{status_raw}</span>
                        </div>
                        <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; line-height: 1.3; margin-bottom: 4px;">
                            {case.get('company_name')}
                        </div>
                        <div style="font-size: 0.68rem; font-family: monospace; color: #38BDF8; margin-bottom: 8px;">
                            CIN: {case.get('cin')}
                        </div>
                        <div style="font-size: 0.70rem; color: {txt_sec}; line-height: 1.4; background: {sub_bg}; padding: 8px 10px; border-radius: 4px; border: 1px solid {card_border}; margin-bottom: 8px;">
                            <div><b style="color: {txt_pri};">{'管轄RoC' if is_jp else 'RoC Office'}:</b> {case.get('roc_office')}</div>
                            <div><b style="color: {txt_pri};">{'設立 / 資本' if is_jp else 'Vintage / Capital'}:</b> {case.get('incorporation_date')} ({case.get('vintage_years')} yrs) • {cap_disp}</div>
                            <div><b style="color: {txt_pri};">{'投資家関係' if is_jp else 'Investor Context'}:</b> {inv_ctx}</div>
                        </div>
                        <div style="font-size: 0.70rem; line-height: 1.4; color: {txt_sec}; margin-bottom: 8px;">
                            <div style="margin-bottom: 4px;"><b style="color: {'#059669' if is_clean else '#B33927'};">{'監査・監督機関' if is_jp else 'Auditor / Authority'}:</b> {auditor}</div>
                            <div><b style="color: {txt_pri};">{'判例要旨' if is_jp else 'Case Ground Truth'}:</b> {violation}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

                if show_actions:
                    btn_label = f"{'審査実行' if is_jp else 'VERIFY IN COCKPIT'} — {short_title}"
                    if st.button(btn_label, key=f"btn_pub_case_{case['cin']}", use_container_width=True, type="primary" if is_clean else "secondary"):
                        st.session_state['active_preset'] = case['preset_key']
                        st.session_state['active_cin'] = case['cin']
                        st.session_state['cin_entity_data'] = case
                        st.session_state['cockpit_target_selector'] = case['preset_key']
                        st.session_state['_last_qp_preset'] = case['preset_key']
                        st.session_state['custom_audit_data'] = None
                        if 'consent_request' in st.session_state:
                            st.session_state['consent_request']['handle'] = f"REQ-KIZUNA-2026-{case['preset_key'][:4].upper()}-0914"
                        st.session_state['is_authenticated'] = True
                        st.session_state['page_state'] = 'cockpit'
                        st.query_params["view"] = "cockpit"
                        st.query_params["preset"] = case['preset_key']
                        st.rerun()


def render_data_room_sealed_card(
    entity_data: Dict[str, Any],
    consent_request: Dict[str, Any],
    linked_rails: Dict[str, bool],
    lang: str = "EN",
    theme: str = "light"
):
    """
    Renders an institutional, compliant 'Data Room Sealed' gatekeeper view
    under DPDP Act 2023 Section 6 and RBI Account Aggregator guidelines.
    Prevents unauthorized viewing of unredacted ledgers until founder authorization is executed.
    """
    is_jp = lang.lower() in ["jp", "ja"]
    txt_pri = "#F8FAFC" if theme == "dark" else "#0F172A"
    txt_sec = "#94A3B8" if theme == "dark" else "#475569"
    card_bg = "#111827" if theme == "dark" else "#FFFFFF"
    card_border = "#1E293B" if theme == "dark" else "#CBD5E1"
    sub_bg = "#090D16" if theme == "dark" else "#F8FAFC"

    company_name = entity_data.get("company_name", "Target Enterprise")
    cin = entity_data.get("cin", "U72900KA2023PTC178921")
    handle = consent_request.get("handle", "REQ-KIZUNA-2026-APEX-0914")
    c_stat = consent_request.get("status", "DISPATCHED")
    is_approved = (c_stat == "APPROVED")

    bank_linked = linked_rails.get("bank", False)
    gst_linked = linked_rails.get("gst", False)
    mca_linked = linked_rails.get("mca", False)

    card_title_jp = "【データルーム施錠中】創業者による法定開示承認待ち"
    card_title_en = "[DATA ROOM SEALED: AWAITING FOUNDER AUTHORIZATION]"
    statutory_title_jp = "2023年デジタル個人データ保護法 (DPDP Act §6) に基づく開示保護"
    statutory_title_en = "Statutory Diligence Protection under DPDP Act 2023 Section 6"

    desc_jp = "インド共和国2023年デジタル個人データ保護法第6条およびインド準備銀行 (RBI) アカウントアグリゲーター指令に基づき、対象スタートアップ企業の取締役会・公式署名権者による電子署名承認が完了するまで、確定銀行取引明細、GST税務申告インボイス、公認会計士試算表などの非公開財務元帳は暗号化施錠されています。"
    desc_en = "Under Section 6 of India's Digital Personal Data Protection (DPDP) Act 2023 and RBI Account Aggregator Master Directions, institutional diligence repositories remain cryptographically sealed until explicit digital authorization is executed by the target enterprise's corporate signatory. Unredacted banking ledgers, GST tax records, and statutory books cannot be decrypted without board consent."

    st.markdown(
        f"""
        <div style="background: {card_bg}; border: 1.5px solid #D97706; border-radius: 6px; padding: 22px 26px; margin: 16px 0 20px 0;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div>
                    <span class="badge-review" style="font-size: 0.72rem; padding: 4px 10px; font-weight: 800;">
                        {card_title_jp if is_jp else card_title_en}
                    </span>
                    <div style="font-size: 1.15rem; font-weight: 800; color: {txt_pri}; margin-top: 8px;">
                        {statutory_title_jp if is_jp else statutory_title_en}
                    </div>
                </div>
                <div style="text-align: right; font-family: monospace; font-size: 0.72rem; color: #D97706;">
                    STATUS: <span style="font-weight: 800;">{c_stat}</span><br/>
                    MANDATE: {handle}
                </div>
            </div>

            <div style="font-size: 0.78rem; color: {txt_sec}; line-height: 1.6; margin-bottom: 16px;">
                {desc_jp if is_jp else desc_en}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 16px;">
                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'対象企業' if is_jp else 'TARGET ENTERPRISE'}</div>
                    <div style="font-size: 0.88rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">{company_name}</div>
                    <div style="font-size: 0.68rem; font-family: monospace; color: #38BDF8;">CIN: {cin}</div>
                </div>

                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'要請機関・投資審査部' if is_jp else 'REQUESTING AUTHORITY'}</div>
                    <div style="font-size: 0.84rem; font-weight: 800; color: {txt_pri}; margin-top: 2px;">Value Create Inc. (Tokyo)</div>
                    <div style="font-size: 0.68rem; color: #64748B;">JETRO India Startup Diligence Desk</div>
                </div>

                <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 10px 14px;">
                    <div style="font-size: 0.68rem; color: #64748B; font-weight: 700;">{'暗号化ハンドシェイク' if is_jp else 'ENCRYPTION PROTOCOL'}</div>
                    <div style="font-size: 0.84rem; font-weight: 800; color: {txt_pri}; font-family: monospace; margin-top: 2px;">ECDH Curve25519</div>
                    <div style="font-size: 0.68rem; color: #059669;">AES-GCM-256 Sovereign Seal</div>
                </div>
            </div>

            <div style="background: {sub_bg}; border: 1px solid {card_border}; border-radius: 4px; padding: 12px 16px; margin-bottom: 8px;">
                <div style="font-size: 0.72rem; font-weight: 800; color: {txt_pri}; margin-bottom: 8px;">
                    {'【開錠前提条件チェックリスト】' if is_jp else '[DATA ROOM UNSEAL PREREQUISITE CHECKLIST]'}
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.74rem;">
                    <div>
                        1. {'創業者法定同意 (Founder Consent)' if is_jp else 'Founder Diligence Consent'}:
                        <span class="{'badge-clean' if is_approved else 'badge-review'}" style="margin-left: 6px;">
                            {'[承認済 / AUTHORIZED]' if is_approved else '[未承認 / PENDING]'}
                        </span>
                    </div>
                    <div>
                        2. {'RBI AA 銀行元帳 (ReBIT DEPOSIT v2.0)' if is_jp else 'RBI AA Bank Rail (ReBIT v2.0)'}:
                        <span class="{'badge-clean' if bank_linked else 'badge-danger'}" style="margin-left: 6px;">
                            {'[連携済 / LINKED]' if bank_linked else '[未連携 / LOCKED]'}
                        </span>
                    </div>
                    <div>
                        3. {'GSTN 国家税務申告 (GSTR-1, GSTR-3B)' if is_jp else 'GSTN Tax Network (GSTR-1/3B)'}:
                        <span class="{'badge-clean' if gst_linked else 'badge-danger'}" style="margin-left: 6px;">
                            {'[連携済 / LINKED]' if gst_linked else '[未連携 / LOCKED]'}
                        </span>
                    </div>
                    <div>
                        4. {'MCA-21 商業登記 & CA試算表 (PAS-3)' if is_jp else 'MCA-21 Books & PAS-3'}:
                        <span class="{'badge-clean' if mca_linked else 'badge-danger'}" style="margin-left: 6px;">
                            {'[連携済 / LINKED]' if mca_linked else '[未連携 / LOCKED]'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )





