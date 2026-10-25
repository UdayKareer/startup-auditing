import os
import sys
sys.path.insert(0, os.path.abspath("."))
import re
from frontend.i18n import TRANSLATIONS

def run():
    files = ['frontend/app.py', 'frontend/components.py', 'frontend/styles.py']
    content = ""
    for fpath in files:
        with open(fpath, encoding='utf-8') as f:
            content += f"\n# --- {fpath} ---\n" + f.read()

    # Find all t("...") or t('...') with word boundary before t
    t_matches = re.findall(r'(?<![a-zA-Z0-9_])t\(\s*["\']([a-zA-Z0-9_\-]+)["\']', content)
    unique_keys = sorted(list(set(t_matches)))
    print(f"Total unique t() keys referenced in UI code: {len(unique_keys)}")

    missing_in_dict = []
    missing_en = []
    missing_jp = []

    for k in unique_keys:
        if k not in TRANSLATIONS:
            missing_in_dict.append(k)
        else:
            if "en" not in TRANSLATIONS[k] or not TRANSLATIONS[k]["en"]:
                missing_en.append(k)
            if "jp" not in TRANSLATIONS[k] or not TRANSLATIONS[k]["jp"]:
                missing_jp.append(k)

    print(f"Keys completely missing from TRANSLATIONS: {missing_in_dict}")
    print(f"Keys missing 'en': {missing_en}")
    print(f"Keys missing 'jp': {missing_jp}")

if __name__ == '__main__':
    run()
