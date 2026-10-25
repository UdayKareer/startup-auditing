import os
import sys
import pypdf
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from backend.main import AuditRequest, full_audit
from export.memo_generator import generate_ringi_sho_pdf
from frontend.i18n import format_currency, format_dual_currency_pair, t


def test_dual_currency_formatting():
    val = 4500000  # 45 Lakhs INR = 81.00 Lakhs JPY = 810 万円
    inr_fmt = format_currency(val, "INR", "EN")
    jpy_fmt = format_currency(val, "JPY", "EN")
    dual_fmt = format_dual_currency_pair(val, "EN")
    assert "45.00 Lakhs" in inr_fmt
    assert "810 万円" in jpy_fmt
    assert "810 万円" in dual_fmt

    val_large = 100000000  # 10 Cr INR = 18.00 Cr JPY = 1.80 億円
    jpy_large = format_currency(val_large, "JPY", "JP")
    assert "1.80 億円" in jpy_large


def test_one_page_pdf_generation_all_presets():
    presets = ["clean_startup", "fraud_startup", "logipulse_startup", "mirai_startup"]
    for p in presets:
        audit = full_audit(AuditRequest(preset_key=p))
        out_pdf = f"export/test_{p}.pdf"
        generate_ringi_sho_pdf(audit, out_pdf)
        reader = pypdf.PdfReader(out_pdf)
        pages = len(reader.pages)
        assert pages == 1, f"Expected 1 page for {p}, got {pages}"


def test_hanko_stamp_pdf_propagation():
    audit_fraud = full_audit(AuditRequest(preset_key="fraud_startup"))
    mutated = 0
    for st in audit_fraud['hanko_stages']:
        if st['stage_id'].lower() == 'stage_1':
            st['status'] = 'APPROVED'
            st['status_jp'] = '承認済'
            mutated += 1
        elif st['stage_id'].lower() == 'stage_3':
            st['status'] = 'FLAGGED'
            st['status_jp'] = '否認/保留'
            mutated += 1
    assert mutated == 2, "Expected 2 stages to be mutated"

    out_stamped = "export/test_fraud_stamped.pdf"
    generate_ringi_sho_pdf(audit_fraud, out_stamped)
    reader_stamped = pypdf.PdfReader(out_stamped)
    assert len(reader_stamped.pages) == 1
    text = reader_stamped.pages[0].extract_text()
    assert "■" not in text and "\u25a0" not in text


def test_no_black_square_glyph_corruption_across_presets():
    """Verify that ReportLab correctly renders Japanese Kanji and Rupee signs without black square (■) tofu glyphs."""
    presets = ["clean_startup", "fraud_startup", "logipulse_startup", "mirai_startup"]
    for p in presets:
        audit = full_audit(AuditRequest(preset_key=p))
        out_pdf = f"export/test_{p}.pdf"
        generate_ringi_sho_pdf(audit, out_pdf)
        reader = pypdf.PdfReader(out_pdf)
        text = reader.pages[0].extract_text()
        assert "■" not in text, f"Found black square glyph corruption in {p}"
        assert "\u25a0" not in text, f"Found unicode tofu square in {p}"
        assert "投資審査稟議書" in text
        assert "₹" in text
        assert "¥" in text
