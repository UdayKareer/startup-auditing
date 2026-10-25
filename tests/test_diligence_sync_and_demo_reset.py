"""
Test Suite for Cross-Dashboard Diligence Synchronization & Demo Reset Cockpit.
Track OPEN-PS-01 | VeriLedger / Kizuna-Vault (絆).
Validates:
1. Shared diligence state loading, dispatch, and approval.
2. Sovereign rail linkage (Bank, GST, MCA) and data room auto-sealing.
3. 1-Click demo reset in 'pristine' and 'pre_approved' modes.
4. Test company preset switching across dashboards.
5. Zero-emoji linting on all newly authored modules.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.diligence_state import (
    load_diligence_state,
    dispatch_diligence_request,
    approve_diligence_request,
    link_data_rail,
    switch_active_preset,
    reset_all_demo_state,
    STATE_FILE,
)

client = TestClient(app)


def test_diligence_state_endpoint_get():
    """Verifies GET /api/v1/diligence/state returns a well-formed sovereign state."""
    response = client.get("/api/v1/diligence/state")
    assert response.status_code == 200
    data = response.json()
    assert "active_preset" in data
    assert "request" in data
    assert "linked_rails" in data
    assert "handle" in data["request"]
    assert "status" in data["request"]


def test_diligence_request_dispatch_flow():
    """Verifies that an investor can dispatch a time-bound DPDP Act 2023 consent mandate."""
    response = client.post("/api/v1/diligence/request/dispatch", json={"preset_key": "clean_startup"})
    assert response.status_code == 200
    data = response.json()
    assert data["request"]["status"] == "DISPATCHED"
    assert data["request"]["dispatched_at"] is not None
    assert "REQ-KIZUNA-2026-CLEA-0914" in data["request"]["handle"]


def test_diligence_request_approval_flow():
    """Verifies that a founder can authorize an incoming diligence request."""
    signatory = "Rajesh Sharma (DIN: 08921045)"
    response = client.post("/api/v1/diligence/request/approve", json={"signatory": signatory})
    assert response.status_code == 200
    data = response.json()
    assert data["request"]["status"] == "APPROVED"
    assert data["request"]["approved_at"] is not None
    assert data["request"]["signatory"] == signatory


def test_sovereign_data_rail_linkage_flow():
    """Verifies individual and batch rail linkage (Bank, GST, MCA)."""
    # Link Bank only
    r_bank = client.post("/api/v1/diligence/rails/link", json={"rail": "bank", "linked": True})
    assert r_bank.status_code == 200
    assert r_bank.json()["linked_rails"]["bank"] is True

    # Link GST only
    r_gst = client.post("/api/v1/diligence/rails/link", json={"rail": "gst", "linked": True})
    assert r_gst.status_code == 200
    assert r_gst.json()["linked_rails"]["gst"] is True

    # Link MCA only
    r_mca = client.post("/api/v1/diligence/rails/link", json={"rail": "mca", "linked": True})
    assert r_mca.status_code == 200
    assert r_mca.json()["linked_rails"]["mca"] is True

    # Since all 3 are linked and request is approved, data room must be sealed!
    assert r_mca.json()["data_room_sealed"] is True


def test_one_click_demo_reset_pristine_mode():
    """Verifies that the demo reset endpoint resets all dashboards back to pristine unlinked mode."""
    response = client.post("/api/v1/diligence/reset", json={"preset_key": "clean_startup", "mode": "pristine"})
    assert response.status_code == 200
    data = response.json()
    assert data["request"]["status"] == "DISPATCHED"
    assert data["linked_rails"]["bank"] is False
    assert data["linked_rails"]["gst"] is False
    assert data["linked_rails"]["mca"] is False
    assert data["data_room_sealed"] is False


def test_one_click_demo_reset_pre_approved_mode():
    """Verifies that the 30-second rapid presentation mode pre-approves and links everything."""
    response = client.post("/api/v1/diligence/reset", json={"preset_key": "clean_startup", "mode": "pre_approved"})
    assert response.status_code == 200
    data = response.json()
    assert data["request"]["status"] == "APPROVED"
    assert data["linked_rails"]["bank"] is True
    assert data["linked_rails"]["gst"] is True
    assert data["linked_rails"]["mca"] is True
    assert data["data_room_sealed"] is True


def test_switch_active_preset():
    """Verifies switching the active company preset across connected dashboards."""
    response = client.post("/api/v1/diligence/switch-preset", json={"preset_key": "fraud_startup"})
    assert response.status_code == 200
    data = response.json()
    assert data["active_preset"] == "fraud_startup"
    assert "FRAU" in data["request"]["handle"]

    # Switch back to clean_startup
    client.post("/api/v1/diligence/switch-preset", json={"preset_key": "clean_startup"})


def test_demo_admin_views_can_be_imported():
    """Verifies that demo admin view and pages can be imported cleanly."""
    from frontend.demo_admin_view import render_demo_admin_cockpit
    from frontend.diligence_client import (
        fetch_backend_diligence_state,
        dispatch_backend_request,
        approve_backend_request,
        link_backend_rail,
        reset_backend_demo,
    )
    assert callable(render_demo_admin_cockpit)
    assert callable(fetch_backend_diligence_state)


def test_zero_emojis_in_new_modules():
    """Ensures strict adherence to @non-ai-slop-ui-design with zero emojis."""
    new_files = [
        os.path.join("backend", "diligence_state.py"),
        os.path.join("frontend", "diligence_client.py"),
        os.path.join("frontend", "demo_admin_view.py"),
        os.path.join("frontend", "pages", "4_Demo_Reset.py"),
    ]
    # Standard emoji unicode ranges
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport and Map
        (0x2600, 0x26FF),    # Misc symbols
        (0x2700, 0x27BF),    # Dingbats
        (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
    ]
    for filepath in new_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        for char in content:
            code = ord(char)
            for start, end in emoji_ranges:
                assert not (start <= code <= end), f"Disallowed emoji '{char}' (U+{code:04X}) detected in {filepath}"


def test_all_four_pages_apptest_execution():
    """Verify that all 4 standalone multi-page views execute cleanly via Streamlit AppTest."""
    from streamlit.testing.v1 import AppTest

    pages = [
        os.path.join("frontend", "pages", "1_Investor_Portal.py"),
        os.path.join("frontend", "pages", "2_Founder_Dashboard.py"),
        os.path.join("frontend", "pages", "3_Audited_Company_Dossier.py"),
        os.path.join("frontend", "pages", "4_Demo_Reset.py"),
    ]

    for rel_path in pages:
        abs_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", rel_path))
        at = AppTest.from_file(abs_p)
        at.run(timeout=10)
        assert not at.exception, f"AppTest execution error in {rel_path}: {at.exception}"


def test_demo_admin_cockpit_actions_apptest():
    """Verify that Demo Reset cockpit buttons trigger and run cleanly."""
    from streamlit.testing.v1 import AppTest

    abs_p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "pages", "4_Demo_Reset.py"))
    at = AppTest.from_file(abs_p)
    at.run(timeout=10)
    assert not at.exception

    # Locate reset and fast track buttons
    rst_btns = [b for b in at.button if b.key == "btn_do_master_reset"]
    assert len(rst_btns) == 1
    fast_btns = [b for b in at.button if b.key == "btn_do_fast_track"]
    assert len(fast_btns) == 1

