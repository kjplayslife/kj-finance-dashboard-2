#!/usr/bin/env python3
"""Set up (or refresh) a finance folder from the plugin's engine.

Run from the plugin, pointing at the user's folder:
  python3 "$E/scripts/setup_folder.py" --dest . --name "Sam" --option local \
      --tax 0 --tithe 10 --savings 10 [--no-verses]

First run: copies the scripts, the dashboard template and the starting category rules, and writes
data/config.json from the answers. Later runs (--refresh): only replace scripts/ and
dashboard/template.html with the plugin's newer copies; the person's config, rules, overrides and
data are never touched. Prints what it did.
"""
import argparse
import json
import os
import shutil
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(os.path.dirname(ENGINE), ".claude-plugin", "plugin.json")) as _f:
    VERSION = json.load(_f)["version"]  # one version number, kept in plugin.json

CATEGORIES = ["Income", "Groceries", "Dining Out", "Shopping", "Subscriptions", "Rent and Utilities", "Gas & Auto",
              "Tithe", "Fees", "Other", "Card Payments", "Transfers", "Reimbursed", "Gift"]
NEED_DEFAULTS = {"Rent and Utilities": 3, "Groceries": 3, "Gas & Auto": 3, "Tithe": 3,
                 "Subscriptions": 2, "Fees": 2, "Dining Out": 1, "Shopping": 1}
GITIGNORE = """.DS_Store
__pycache__/
*.pyc
csv/
"""


def config_for(a):
    cats = [c for c in CATEGORIES if c != "Tithe" or a.tithe > 0 or a.tithe_category]
    title = a.title or ("%s's Finances" % a.name if a.name else "Personal Finances")
    return {
        "_how": "Settings for scripts/sync.py and the dashboard. Claude edits this for you; re-run sync after changes.",
        "plugin_version": VERSION,
        "owner_name": a.name,
        "dashboard_title": title,
        "backup_file": "%s Finance Dashboard.html" % a.name if a.name else "Finance Dashboard.html",
        "setup_option": a.option,
        "artifact_url": "",
        "verses": not a.no_verses,
        "_goals": "Percent of each month's real income to set aside. 0 = off. Tax comes off the top, giving after tax, savings after both.",
        "goals": {"taxPct": a.tax, "tithePct": a.tithe, "savingsPct": a.savings},
        "era": {"account_labels": {}, "exclude_accounts": {}},
        "_manual_balances": "Balances for accounts that come from CSV files: {label: {balance, asOf}}. Card balance = amount owed.",
        "manual_balances": {},
        "sign_in": {},
        "budgets": {},
        "categories": cats,
        "_need_defaults": "Starting Need rating by category (1 = want, 2 = could skip, 3 = need). Shown lighter until confirmed.",
        "need_defaults": {k: v for k, v in NEED_DEFAULTS.items() if k in cats},
        "non_spend": ["Income", "Card Payments", "Transfers", "Reimbursed", "Gift"],
        "hidden": ["Reimbursed"],
    }


def copy_engine(dest, rules_too):
    os.makedirs(os.path.join(dest, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(dest, "dashboard"), exist_ok=True)
    done = []
    for name in sorted(os.listdir(os.path.join(ENGINE, "scripts"))):
        if name.endswith(".py") and name != "setup_folder.py":
            shutil.copy2(os.path.join(ENGINE, "scripts", name), os.path.join(dest, "scripts", name))
            done.append("scripts/" + name)
    shutil.copy2(os.path.join(ENGINE, "dashboard", "template.html"), os.path.join(dest, "dashboard", "template.html"))
    done.append("dashboard/template.html")
    if rules_too:
        shutil.copy2(os.path.join(ENGINE, "data", "category-rules.json"), os.path.join(dest, "data", "category-rules.json"))
        done.append("data/category-rules.json")
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True)
    ap.add_argument("--refresh", action="store_true", help="only update scripts and the template")
    ap.add_argument("--name", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--option", choices=["cloud", "local", "csv"])
    ap.add_argument("--tax", type=float, default=0)
    ap.add_argument("--tithe", type=float, default=0)
    ap.add_argument("--savings", type=float, default=0)
    ap.add_argument("--tithe-category", action="store_true", help="keep a Tithe category even with no tithe goal")
    ap.add_argument("--no-verses", action="store_true")
    a = ap.parse_args()
    dest = os.path.abspath(a.dest)
    cfg_path = os.path.join(dest, "data", "config.json")

    if a.refresh:
        if not os.path.exists(cfg_path):
            sys.exit("No data/config.json in %s; this isn't a finance folder yet." % dest)
        done = copy_engine(dest, rules_too=False)
        with open(cfg_path) as f:
            cfg = json.load(f)
        cfg["plugin_version"] = VERSION
        with open(cfg_path, "w") as f:
            json.dump(cfg, f, indent=1)
        print("Refreshed to plugin %s:\n  %s" % (VERSION, "\n  ".join(done)))
        return

    if not a.option:
        sys.exit("--option is required (cloud, local or csv)")
    if os.path.exists(cfg_path):
        sys.exit("%s already has data/config.json. Use --refresh to update the scripts, or edit the config." % dest)
    for sub in ("data/raw", "csv"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    done = copy_engine(dest, rules_too=True)
    with open(cfg_path, "w") as f:
        json.dump(config_for(a), f, indent=1)
    done.append("data/config.json")
    with open(os.path.join(dest, "data", "overrides.json"), "w") as f:
        json.dump({"_how": "Fixes Claude makes for single transactions: {byId: {id: {category, display, date, need}}}", "byId": {}}, f, indent=1)
    done.append("data/overrides.json")
    gi = os.path.join(dest, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w") as f:
            f.write(GITIGNORE)
        done.append(".gitignore")
    print("Finance folder ready in %s (plugin %s):\n  %s" % (dest, VERSION, "\n  ".join(done)))


if __name__ == "__main__":
    main()
