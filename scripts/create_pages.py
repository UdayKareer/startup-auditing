"""Create separate dedicated pages for Streamlit multi-page app."""
import os

pages_dir = os.path.join("frontend", "pages")
os.makedirs(pages_dir, exist_ok=True)

# 1. Investor Portal Page
page1_content = """# -*- coding: utf-8 -*-
\"\"\"Dedicated Investor Due Diligence & Portfolio Selection Portal.\"\"\"
import streamlit as st

st.session_state['page_state'] = 'gatekeeper'
st.query_params['view'] = 'investor'

# Execute main app controller with gatekeeper state
from frontend.app import *
"""

with open(os.path.join(pages_dir, "1_Investor_Portal.py"), "w", encoding="utf-8") as f:
    f.write(page1_content)

# 2. Founder Dashboard Page
page2_content = """# -*- coding: utf-8 -*-
\"\"\"Dedicated Startup Founder Consent & Sovereign Data Room Portal.\"\"\"
import streamlit as st

st.session_state['page_state'] = 'founder_dashboard'
st.query_params['view'] = 'founder_dashboard'

# Execute main app controller with founder_dashboard state
from frontend.app import *
"""

with open(os.path.join(pages_dir, "2_Founder_Dashboard.py"), "w", encoding="utf-8") as f:
    f.write(page2_content)

# 3. Audited Company Dossier Page
page3_content = """# -*- coding: utf-8 -*-
\"\"\"Dedicated Audited Company Dossier & Tokyo Boardroom Ringi-sho Cockpit.\"\"\"
import streamlit as st

st.session_state['page_state'] = 'cockpit'
st.query_params['view'] = 'cockpit'

# Execute main app controller with cockpit state
from frontend.app import *
"""

with open(os.path.join(pages_dir, "3_Audited_Company_Dossier.py"), "w", encoding="utf-8") as f:
    f.write(page3_content)

print("Created frontend/pages successfully.")
