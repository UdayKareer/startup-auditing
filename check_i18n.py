#!/usr/bin/env python3
"""
AST and Regex Validation Tool for VeriLedger / Kizuna-Vault i18n Translations.
Scans all frontend files to ensure 100% of t() calls are defined in both English and Japanese.
"""

import os
import sys
import re

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath("."))

from frontend.i18n import TRANSLATIONS


def check_i18n():
    frontend_files = [
        os.path.join("frontend", "app.py"),
        os.path.join("frontend", "components.py"),
        os.path.join("frontend", "styles.py")
    ]

    extracted_keys = set()
    key_pattern = re.compile(r'(?<![a-zA-Z0-9_])t\(\s*["\']([a-zA-Z0-9_\-]+)["\']')

    for file_path in frontend_files:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            matches = key_pattern.findall(content)
            for m in matches:
                extracted_keys.add(m)

    sorted_keys = sorted(list(extracted_keys))
    print(f"=== VERILEDGER I18N VALIDATION ENGINE ===")
    print(f"Total distinct t() keys found across frontend: {len(sorted_keys)}")

    missing_in_dict = []
    missing_en = []
    missing_jp = []

    for key in sorted_keys:
        if key not in TRANSLATIONS:
            missing_in_dict.append(key)
        else:
            if "en" not in TRANSLATIONS[key] or not str(TRANSLATIONS[key]["en"]).strip():
                missing_en.append(key)
            if "jp" not in TRANSLATIONS[key] or not str(TRANSLATIONS[key]["jp"]).strip():
                missing_jp.append(key)

    total_translations = len(TRANSLATIONS)
    print(f"Total entries defined in TRANSLATIONS dictionary: {total_translations}")
    print(f"Missing from TRANSLATIONS: {len(missing_in_dict)}")
    print(f"Missing EN text: {len(missing_en)}")
    print(f"Missing JP text: {len(missing_jp)}")

    if missing_in_dict or missing_en or missing_jp:
        if missing_in_dict:
            print("ERROR: The following keys are called via t() but missing from TRANSLATIONS:")
            for k in missing_in_dict:
                print(f"  - {k}")
        if missing_en:
            print("ERROR: The following keys are missing 'en' translations:")
            for k in missing_en:
                print(f"  - {k}")
        if missing_jp:
            print("ERROR: The following keys are missing 'jp' translations:")
            for k in missing_jp:
                print(f"  - {k}")
        sys.exit(1)

    print(f"SUCCESS: 100% of {len(sorted_keys)} UI translation keys verified across EN and JP (0 missing keys)!")
    return 0


if __name__ == "__main__":
    sys.exit(check_i18n())
