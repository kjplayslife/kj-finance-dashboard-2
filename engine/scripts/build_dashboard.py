#!/usr/bin/env python3
"""Put data/finance-data.json into dashboard/template.html.

Writes two files:
  <backup_file from config>   the stand-alone page, the local backup (opens in any browser)
  dashboard/artifact.html     the same page without <html>/<head>/<body>, for publishing as the
                              claude.ai artifact (the Artifact tool adds its own document skeleton)

sync.py runs this automatically; run it by hand only after editing the template or config.
"""
import html as htmlmod
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "dashboard", "template.html")
ARTIFACT = os.path.join(ROOT, "dashboard", "artifact.html")
MARK = "/*__FINANCE_DATA__*/null"
TITLE_MARK = "__DASHBOARD_TITLE__"


def config():
    path = os.path.join(ROOT, "data", "config.json")
    with open(path) as f:
        return json.load(f)


def backup_path():
    return os.path.join(ROOT, config().get("backup_file") or "Finance Dashboard.html")


def build(data_path=None, out=None, artifact=None):
    data_path = data_path or os.path.join(ROOT, "data", "finance-data.json")
    out, artifact = out or backup_path(), artifact or ARTIFACT
    with open(data_path) as f:
        data = json.load(f)
    with open(TEMPLATE) as f:
        page = f.read()
    if MARK not in page:
        raise SystemExit("Template is missing the %s placeholder" % MARK)
    # "</" inside a <script> must not close the tag early.
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = page.replace(MARK, payload).replace(TITLE_MARK, htmlmod.escape(data.get("title") or "Personal Finances"))
    with open(out, "w") as f:
        f.write(page)
    with open(artifact, "w") as f:
        f.write(artifact_body(page))
    return out


def artifact_body(page):
    """Keep <title>, scripts and styles from <head>, then the body content."""
    head = page.split("<head>", 1)[1].split("</head>", 1)[0]
    body = page.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    head = "\n".join(line for line in head.splitlines() if not line.startswith("<meta "))
    return head.strip() + "\n" + body.strip() + "\n"


if __name__ == "__main__":
    print("Wrote", os.path.relpath(build(), ROOT), "and", os.path.relpath(ARTIFACT, ROOT))
