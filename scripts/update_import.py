"""Script to rearchitect frontend/app.py to be clean, dropdown-driven, and multi-report."""
import re

content = open("frontend/app.py", "r", encoding="utf-8").read()

# 1. Update imports from frontend.components
old_import = """from frontend.components import (
    render_header,
    render_dpi_rail_badges,
    render_merkle_anchor,
    render_anonymized_teaser,
    render_telemetry_trace,
    render_kpi_card,
    render_reconciliation_chart,
    render_benford_chart,
    render_discrepancy_waterfall,
    render_diligence_sankey_flow,
    render_hanko_rail,
    render_redline_table,
    render_workflow_stepper,
    render_mca_entity_card,
)"""

new_import = """from frontend.components import (
    render_header,
    render_dpi_rail_badges,
    render_merkle_anchor,
    render_anonymized_teaser,
    render_telemetry_trace,
    render_kpi_card,
    render_reconciliation_chart,
    render_benford_chart,
    render_discrepancy_waterfall,
    render_diligence_sankey_flow,
    render_hanko_rail,
    render_redline_table,
    render_workflow_stepper,
    render_mca_entity_card,
    render_audited_bank_ledger,
    render_audited_gst_register,
    render_audited_trial_balance,
)"""

if old_import in content:
    content = content.replace(old_import, new_import)
    print("Updated imports successfully.")
else:
    print("Warning: old_import pattern not found exactly, attempting normalized match.")
    content = re.sub(
        r'from frontend\.components import \([^)]+\)',
        new_import,
        content
    )

open("frontend/app.py", "w", encoding="utf-8").write(content)
print("Saved frontend/app.py.")
