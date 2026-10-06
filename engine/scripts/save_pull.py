#!/usr/bin/env python3
"""Copy Era Context responses out of the Claude Code session log into data/raw/.

Era's MCP responses only exist inside the chat. Claude Code writes every tool
result to a session log (~/.claude/projects/<project>/<session>.jsonl), so this
script reads that log, keeps the accounts + transactions responses, and saves
them as data/raw/era-<date>-<session>.json. Re-running in the same session
overwrites that file with everything pulled so far.

Which log: the most recently written session log that has Era transaction results, looking first in
this folder's log directory and then in every Claude Code project written in the last 6 hours (a
scheduled task or cloud run may log under a different folder name).

Usage:
  python3 scripts/save_pull.py               # the session that just pulled from Era
  python3 scripts/save_pull.py --session ID  # a specific session
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, "data", "raw")
WANTED = ("accounts__list_financial_accounts", "transactions__list_transactions")


def project_log_dir():
    slug = re.sub(r"[^A-Za-z0-9]", "-", ROOT)
    return os.path.join(os.path.expanduser("~/.claude/projects"), slug)


def result_text(block):
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def parse_result(text):
    try:
        return json.loads(text)
    except ValueError:
        pass
    # Very large results can be written to a side file; follow the path if so.
    m = re.search(r"(/[^\s\"']+tool-results/[^\s\"']+)", text)
    if m and os.path.exists(m.group(1)):
        try:
            with open(m.group(1)) as f:
                data = json.load(f)
            # MCP side files hold the content blocks ([{"type": "text", "text": "{...}"}]), not the JSON itself.
            if isinstance(data, list):
                data = json.loads("".join(b.get("text", "") for b in data if isinstance(b, dict)))
            return data
        except ValueError:
            return None
    return None


def read_log(path):
    calls, results = {}, []
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    tool = block.get("name", "").split("__", 2)[-1]
                    if tool in WANTED:
                        calls[block["id"]] = {"tool": tool, "args": block.get("input") or {}}
                elif block.get("type") == "tool_result" and block.get("tool_use_id") in calls:
                    data = parse_result(result_text(block))
                    if not isinstance(data, dict) or block.get("is_error"):
                        continue
                    call = dict(calls[block["tool_use_id"]])
                    call["called_at"] = entry.get("timestamp")
                    call["response"] = data
                    results.append(call)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", help="session id (default: newest log for this folder)")
    opts = ap.parse_args()

    def session_results(main_log):
        log_dir = os.path.dirname(main_log)
        session = os.path.splitext(os.path.basename(main_log))[0]
        # Subagents in the same session write their own logs.
        logs = [main_log] + sorted(glob.glob(os.path.join(log_dir, session, "subagents", "*.jsonl")))
        res = []
        for path in logs:
            res.extend(read_log(path))
        res.sort(key=lambda r: r.get("called_at") or "")
        return session, res

    if opts.session:
        hits = glob.glob(os.path.expanduser("~/.claude/projects/*/%s.jsonl" % opts.session))
        if not hits:
            sys.exit("No session log named %s.jsonl under ~/.claude/projects" % opts.session)
        session, results = session_results(hits[0])
    else:
        here = glob.glob(os.path.join(project_log_dir(), "*.jsonl"))
        recent = [p for p in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
                  if time.time() - os.path.getmtime(p) < 6 * 3600]
        candidates = sorted(set(here) | set(recent), key=os.path.getmtime, reverse=True)
        if not candidates:
            sys.exit("No Claude Code session logs found under ~/.claude/projects")
        session, results = None, []
        for path in candidates[:40]:
            s_id, res = session_results(path)
            if any(r["tool"] == "transactions__list_transactions" and r["response"].get("transactions") for r in res):
                session, results = s_id, res
                break
        if session is None:
            sys.exit("No Era transaction results in the recent session logs. Pull from Era in this "
                     "session first, or pass --session <id>.")

    accounts = [r for r in results if r["tool"] == "accounts__list_financial_accounts"]
    pages = [r for r in results if r["tool"] == "transactions__list_transactions"
             and r["response"].get("transactions")]
    if not pages:
        sys.exit("No Era transaction responses found in session " + session)

    first = (pages[0].get("called_at") or datetime.now(timezone.utc).isoformat())[:10]
    out = {
        "session": session,
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "accounts_responses": accounts,
        "transaction_pages": pages,
    }
    os.makedirs(RAW_DIR, exist_ok=True)
    out_path = os.path.join(RAW_DIR, "era-%s-%s.json" % (first, session[:8]))
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)

    ids = {t["transaction_id"] for p in pages for t in p["response"]["transactions"]}
    print("Session  %s" % session)
    print("Saved    %s" % os.path.relpath(out_path, ROOT))
    print("         %d accounts responses, %d transaction pages, %d unique transactions"
          % (len(accounts), len(pages), len(ids)))


if __name__ == "__main__":
    main()
