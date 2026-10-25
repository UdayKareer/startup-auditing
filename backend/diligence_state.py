"""
VeriLedger / Kizuna-Vault (Track OPEN-PS-01)
Cross-Dashboard Diligence Synchronization & Demo Reset Engine.
Persists shared consent requests, sovereign data rail linkage, and demo resets
so that actions in Investor Portal instantly reflect in Founder Dashboard & Dossier,
and vice-versa across multiple browser tabs/sessions.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from backend.registry_lookup import lookup_mca_entity, KNOWN_REGISTRY

STATE_FILE = os.path.join("data", "diligence_state.json")


def _get_default_state(preset_key: str = "clean_startup", mode: str = "connected") -> Dict[str, Any]:
    entity = lookup_mca_entity(preset_key)
    cin = entity.get("cin", "U72900KA2023PTC178921")
    handle = f"REQ-KIZUNA-2026-{preset_key[:4].upper()}-0914"

    is_preapproved = (mode in ["pre_approved", "connected"])
    now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    presets = {}
    for p_k in KNOWN_REGISTRY.keys():
        if mode == "pristine":
            is_p_appr = False
        else:
            is_p_appr = (p_k == preset_key)
        presets[p_k] = {
            "status": "APPROVED" if is_p_appr else "DISPATCHED",
            "dispatched_at": now_ts,
            "approved_at": now_ts if is_p_appr else None,
            "signatory": "Rajesh Sharma (DIN: 08921045)" if is_p_appr else None,
            "linked_rails": {
                "bank": True if is_p_appr else False,
                "gst": True if is_p_appr else False,
                "mca": True if is_p_appr else False,
            },
            "data_room_sealed": True if is_p_appr else False,
        }

    return {
        "active_preset": preset_key,
        "active_cin": cin,
        "entity_data": entity,
        "presets": presets,
        "request": {
            "handle": handle,
            "status": "APPROVED" if is_preapproved else "DISPATCHED",
            "dispatched_at": now_ts,
            "approved_at": now_ts if is_preapproved else None,
            "signatory": "Rajesh Sharma (DIN: 08921045)" if is_preapproved else None,
            "purpose": "Track OPEN-PS-01 Bilateral Series A Diligence Mandate",
            "requesting_entity": "Value Create Inc. (Tokyo) & JETRO India Startup Desk",
            "lead_officer": "Demo Persona — Tanaka Hiroshi (demo@kizuna-vault.example.com)",
            "scopes": [
                "RBI AA Bank Ledger (ReBIT DEPOSIT v2.0)",
                "GSTN Invoices & Returns (GSTR-1, GSTR-3B)",
                "MCA-21 Director DINs",
                "CA Books & Form PAS-3"
            ],
            "validity": "14 Days Time-Bound Grant (DPDP Act 2023 §6)"
        },
        "linked_rails": {
            "bank": True if is_preapproved else False,
            "gst": True if is_preapproved else False,
            "mca": True if is_preapproved else False
        },
        "data_room_sealed": True if is_preapproved else False,
        "passcode": entity.get("passcode", "TRUSTVAULT-VC901-TJH"),
        "merkle_root": entity.get("merkle_root", "0x8f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a"),
        "last_updated": now_ts,
        "system_status": "ONLINE"
    }


def load_diligence_state() -> Dict[str, Any]:
    """Loads current shared diligence state from disk, initializing if absent."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state and isinstance(state, dict) and "request" in state and "presets" in state:
                    return state
        except Exception:
            pass

    default_state = _get_default_state()
    save_diligence_state(default_state)
    return default_state


def save_diligence_state(state: Dict[str, Any]) -> None:
    """Safely saves shared diligence state to disk."""
    state["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    temp_file = STATE_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    for attempt in range(5):
        try:
            os.replace(temp_file, STATE_FILE)
            return
        except OSError:
            if attempt == 4:
                with open(STATE_FILE, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
                return
            time.sleep(0.05)


def dispatch_diligence_request(preset_key: Optional[str] = None) -> Dict[str, Any]:
    """Investor dispatches DPDP Act 2023 §6 diligence consent mandate."""
    state = load_diligence_state()
    p_key = preset_key or state.get("active_preset", "clean_startup")
    if preset_key and preset_key != state.get("active_preset"):
        entity = lookup_mca_entity(preset_key)
        state["active_preset"] = preset_key
        state["active_cin"] = entity.get("cin")
        state["entity_data"] = entity
        state["passcode"] = entity.get("passcode", "TRUSTVAULT-VC901-TJH")
        state["merkle_root"] = entity.get("merkle_root", "0x8f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a")

    now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    state["request"]["handle"] = f"REQ-KIZUNA-2026-{p_key[:4].upper()}-0914"
    state["request"]["status"] = "DISPATCHED"
    state["request"]["dispatched_at"] = now_ts
    state["request"]["approved_at"] = None
    state["request"]["signatory"] = None
    state["data_room_sealed"] = False

    if "presets" not in state:
        state["presets"] = {}
    if p_key not in state["presets"]:
        state["presets"][p_key] = {}
    state["presets"][p_key]["status"] = "DISPATCHED"
    state["presets"][p_key]["dispatched_at"] = now_ts
    state["presets"][p_key]["approved_at"] = None
    state["presets"][p_key]["signatory"] = None
    state["presets"][p_key]["data_room_sealed"] = False

    save_diligence_state(state)
    return state


def approve_diligence_request(signatory: Optional[str] = None) -> Dict[str, Any]:
    """Startup founder approves incoming diligence request via digital authorization."""
    state = load_diligence_state()
    p_key = state.get("active_preset", "clean_startup")
    now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    sig = signatory or "Rajesh Sharma (DIN: 08921045)"

    state["request"]["status"] = "APPROVED"
    state["request"]["approved_at"] = now_ts
    state["request"]["signatory"] = sig

    rails = state.get("linked_rails", {"bank": False, "gst": False, "mca": False})
    is_sealed = all(rails.values())
    state["data_room_sealed"] = is_sealed

    if "presets" not in state:
        state["presets"] = {}
    if p_key not in state["presets"]:
        state["presets"][p_key] = {}
    state["presets"][p_key]["status"] = "APPROVED"
    state["presets"][p_key]["approved_at"] = now_ts
    state["presets"][p_key]["signatory"] = sig
    state["presets"][p_key]["data_room_sealed"] = is_sealed

    save_diligence_state(state)
    return state


def link_data_rail(rail_name: str, linked: bool = True) -> Dict[str, Any]:
    """Links or unlinks an individual sovereign DPI data rail (bank, gst, mca, or all)."""
    state = load_diligence_state()
    p_key = state.get("active_preset", "clean_startup")
    rails = state.get("linked_rails", {"bank": False, "gst": False, "mca": False})

    if rail_name == "all":
        rails["bank"] = linked
        rails["gst"] = linked
        rails["mca"] = linked
    elif rail_name in rails:
        rails[rail_name] = linked

    state["linked_rails"] = rails
    is_all_linked = all(rails.values()) and state["request"].get("status") == "APPROVED"
    state["data_room_sealed"] = is_all_linked

    if "presets" not in state:
        state["presets"] = {}
    if p_key not in state["presets"]:
        state["presets"][p_key] = {}
    state["presets"][p_key]["linked_rails"] = dict(rails)
    state["presets"][p_key]["data_room_sealed"] = is_all_linked

    save_diligence_state(state)
    return state


def switch_active_preset(preset_key: str) -> Dict[str, Any]:
    """Switches the active test company preset across all portals."""
    entity = lookup_mca_entity(preset_key)
    state = load_diligence_state()
    cur_p = state.get("active_preset", "clean_startup")
    now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if "presets" not in state:
        state["presets"] = {}

    # Save current active preset's state
    state["presets"][cur_p] = {
        "status": state.get("request", {}).get("status", "DISPATCHED"),
        "dispatched_at": state.get("request", {}).get("dispatched_at", now_ts),
        "approved_at": state.get("request", {}).get("approved_at"),
        "signatory": state.get("request", {}).get("signatory"),
        "linked_rails": dict(state.get("linked_rails", {"bank": False, "gst": False, "mca": False})),
        "data_room_sealed": state.get("data_room_sealed", False),
    }

    # Retrieve target preset's state
    target_rec = state["presets"].get(preset_key)
    if not target_rec:
        target_rec = {
            "status": "DISPATCHED",
            "dispatched_at": now_ts,
            "approved_at": None,
            "signatory": None,
            "linked_rails": {"bank": False, "gst": False, "mca": False},
            "data_room_sealed": False,
        }
        state["presets"][preset_key] = target_rec

    state["active_preset"] = preset_key
    state["active_cin"] = entity.get("cin")
    state["entity_data"] = entity
    state["request"]["handle"] = f"REQ-KIZUNA-2026-{preset_key[:4].upper()}-0914"
    state["request"]["status"] = target_rec.get("status", "DISPATCHED")
    state["request"]["dispatched_at"] = target_rec.get("dispatched_at", now_ts)
    state["request"]["approved_at"] = target_rec.get("approved_at")
    state["request"]["signatory"] = target_rec.get("signatory")
    state["linked_rails"] = dict(target_rec.get("linked_rails", {"bank": False, "gst": False, "mca": False}))
    state["data_room_sealed"] = target_rec.get("data_room_sealed", False)
    state["passcode"] = entity.get("passcode", "TRUSTVAULT-VC901-TJH")
    state["merkle_root"] = entity.get("merkle_root", "0x8f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a")
    save_diligence_state(state)
    return state


def reset_all_demo_state(preset_key: str = "clean_startup", mode: str = "connected") -> Dict[str, Any]:
    """
    Clears all dashboards back to pristine demo reset mode or quick pre-approved demo mode.
    Ensures judges and evaluators see a 100% clean, predictable state during presentations.
    """
    fresh_state = _get_default_state(preset_key=preset_key, mode=mode)
    save_diligence_state(fresh_state)
    return fresh_state
