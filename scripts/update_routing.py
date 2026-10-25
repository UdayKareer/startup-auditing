"""Update query param routing and render_role_switcher in frontend/app.py."""
import re

with open("frontend/app.py", "r", encoding="utf-8") as f:
    text = f.read()

# Update initial_sidebar_state
text = text.replace('initial_sidebar_state="collapsed"', 'initial_sidebar_state="expanded"')

# Update query param handling
old_qp = """# Sync query params if passed directly
if "view" in st.query_params and st.query_params["view"] in ["gatekeeper", "founder_dashboard", "telemetry", "cockpit"]:
    st.session_state['page_state'] = st.query_params["view"]
if "preset" in st.query_params:
    st.session_state['active_preset'] = st.query_params["preset"]"""

new_qp = """# Sync query params if passed directly
view_param = st.query_params.get("view", "").lower()
if view_param in ["investor", "gatekeeper"]:
    st.session_state['page_state'] = 'gatekeeper'
elif view_param in ["founder", "founder_dashboard"]:
    st.session_state['page_state'] = 'founder_dashboard'
elif view_param in ["cockpit", "dossier"]:
    st.session_state['page_state'] = 'cockpit'
elif view_param in ["telemetry"]:
    st.session_state['page_state'] = 'telemetry'

if "preset" in st.query_params:
    st.session_state['active_preset'] = st.query_params["preset"]"""

if old_qp in text:
    text = text.replace(old_qp, new_qp)
    print("Updated query param syncing.")
else:
    print("Could not match old_qp exactly, regex updating.")
    text = re.sub(
        r'# Sync query params if passed directly\s+if "view" in st\.query_params[^:]+:\s+st\.session_state\[\'page_state\'\] = st\.query_params\["view"\]\s+if "preset" in st\.query_params:\s+st\.session_state\[\'active_preset\'\] = st\.query_params\["preset"\]',
        new_qp,
        text
    )

# Update render_role_switcher
old_switcher = """def render_role_switcher(current_state: str, lang: str = "EN", lang_code: str = None):
    \"\"\"Renders high-density institutional persona switch bar without emojis.\"\"\"
    effective_lang = lang_code if lang_code is not None else lang
    c_r1, c_r2, c_r3 = st.columns([2.0, 2.0, 2.0])
    with c_r1:
        inv_active = current_state == "gatekeeper"
        inv_label = t("role_investor", effective_lang) + (" [ACTIVE]" if inv_active else "")
        if st.button(inv_label, key=f"nav_to_investor_{current_state}", type="primary" if inv_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'gatekeeper'
            st.query_params["view"] = "gatekeeper"
            st.rerun()
    with c_r2:
        fnd_active = current_state == "founder_dashboard"
        fnd_label = t("role_founder", effective_lang) + (" [ACTIVE]" if fnd_active else "")
        if st.button(fnd_label, key=f"nav_to_founder_{current_state}", type="primary" if fnd_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'founder_dashboard'
            st.query_params["view"] = "founder_dashboard"
            st.rerun()
    with c_r3:
        cockpit_active = current_state == "cockpit"
        cockpit_label = t("role_cockpit", effective_lang) + (" [ACTIVE]" if cockpit_active else "")
        if st.button(cockpit_label, key=f"nav_to_cockpit_{current_state}", type="primary" if cockpit_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'cockpit'
            st.query_params["view"] = "cockpit"
            st.rerun()"""

new_switcher = """def render_role_switcher(current_state: str, lang: str = "EN", lang_code: str = None):
    \"\"\"Renders high-density institutional persona switch bar with separate direct links.\"\"\"
    effective_lang = lang_code if lang_code is not None else lang
    is_jp = effective_lang.upper() in ["JP", "JA"]

    st.markdown(
        f\"\"\"
        <div style="background: {'#111827' if theme_mode == 'dark' else '#F8FAFC'}; border: 1px solid {'#1E293B' if theme_mode == 'dark' else '#CBD5E1'}; border-radius: 6px; padding: 8px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div style="font-size: 0.72rem; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.04em;">
                {'【独立ポータル切替】デモ用ダイレクトリンク (DEDICATED PORTAL ROUTING):' if is_jp else '[PORTAL ROUTING] SEPARATE DEDICATED DIRECT LINKS:'}
            </div>
            <div style="display: flex; gap: 14px; font-size: 0.70rem; font-family: monospace;">
                <span><b>1. Investor Portal:</b> <a href="/?view=investor" target="_self" style="color: #0284C7; font-weight: 700; text-decoration: underline;">/?view=investor</a></span>
                <span><b>2. Founder Room:</b> <a href="/?view=founder_dashboard" target="_self" style="color: #059669; font-weight: 700; text-decoration: underline;">/?view=founder</a></span>
                <span><b>3. Audited Dossier:</b> <a href="/?view=cockpit" target="_self" style="color: #B33927; font-weight: 700; text-decoration: underline;">/?view=cockpit</a></span>
            </div>
        </div>
        \"\"\",
        unsafe_allow_html=True
    )
    c_r1, c_r2, c_r3 = st.columns([2.0, 2.0, 2.0])
    with c_r1:
        inv_active = current_state in ["gatekeeper", "investor"]
        inv_label = t("role_investor", effective_lang) + (" [ACTIVE]" if inv_active else "")
        if st.button(inv_label, key=f"nav_to_investor_{current_state}", type="primary" if inv_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'gatekeeper'
            st.query_params["view"] = "investor"
            st.rerun()
    with c_r2:
        fnd_active = current_state in ["founder_dashboard", "founder"]
        fnd_label = t("role_founder", effective_lang) + (" [ACTIVE]" if fnd_active else "")
        if st.button(fnd_label, key=f"nav_to_founder_{current_state}", type="primary" if fnd_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'founder_dashboard'
            st.query_params["view"] = "founder_dashboard"
            st.rerun()
    with c_r3:
        cockpit_active = current_state in ["cockpit", "dossier"]
        cockpit_label = t("role_cockpit", effective_lang) + (" [ACTIVE]" if cockpit_active else "")
        if st.button(cockpit_label, key=f"nav_to_cockpit_{current_state}", type="primary" if cockpit_active else "secondary", use_container_width=True):
            st.session_state['page_state'] = 'cockpit'
            st.query_params["view"] = "cockpit"
            st.rerun()"""

if old_switcher in text:
    text = text.replace(old_switcher, new_switcher)
    print("Updated render_role_switcher.")
else:
    print("Warning: old_switcher not matched exactly.")

with open("frontend/app.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved frontend/app.py.")
