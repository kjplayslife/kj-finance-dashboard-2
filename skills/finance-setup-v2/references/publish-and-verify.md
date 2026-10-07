# Publish the dashboard and check it (every option)

sync.py builds two files every time:
- `<Name> Finance Dashboard.html` in the folder: the **local backup**. Opens in any browser, works
  offline; edits made in it stay in that browser only.
- `dashboard/artifact.html`: the same page for publishing as a private claude.ai **artifact**, which
  opens on their phone and desktop, and saves their ratings and category changes in its own database.

## First publish
1. If an `artifact-capabilities` skill is available, load it first (it covers the `db` capability).
2. Publish with the Artifact tool: `file_path` = the absolute path of `dashboard/artifact.html`,
   `icon` = "chart", and
   `capabilities` = `{"db": {"rules": [{"path": "", "read": "admin", "write": "admin"}]}}`
   (only the owner can read or write the saved edits).
3. Save the URL it returns as `artifact_url` in data/config.json, and in FINANCE.md.
4. It's private: only they can open it.
5. **Pin it and get it on their phone** (every setup, not just the automatic one):
   - Pin: on the artifact page in claude.ai (or the Artifacts list), choose **Pin** so it sits in their
     sidebar. If the Artifact tool's `pin` action is available, offer to pin it for them.
   - Phone: install the **Claude** app (App Store / Google Play), sign in with the same account, and
     allow notifications. The dashboard opens from the pinned list there, and the morning notification
     links to it.

## Every later publish
- If a cloud routine also publishes it (option 1), **read it first** (`action: "read"`, the `url`): a
  publish without a fresh read is refused when someone else published since.
- Publish `dashboard/artifact.html` with `url` = artifact_url. **Don't pass `capabilities`** (the stored
  `db` declaration carries forward; passing `{}` would wipe it), and no `icon`.
- Their edits live in the artifact's database and survive every republish. Never write to it.

## Check it (do this before calling setup done)
1. Open the local backup in the browser pane (`mcp__Claude_Browser__navigate` to the file:// path) and
   take a screenshot. Then check phone width (`resize_window` preset "mobile", screenshot, back to
   "desktop"). Look for: the header with their title and "Synced"/"Updated" time, numbers in the Overview
   cards, the month-over-month chart, the transfers tiles they chose (or none), bills if any, every tab
   rendering, and no console errors (`read_console_messages` with onlyErrors).
   - The pane shows local files as a `data:` page, so saving there is off; that's expected.
   - Charts animate; wait a second before screenshots.
2. Compare the Overview month totals with what sync.py printed.
3. Ask them to open the artifact link (on their phone too) and rate one transaction in the Daily Recap
   (tap 1, 2 or 3). If the `ArtifactData` tool is available, confirm it saved: `list` on collection
   `edits` for that artifact URL. If a red "Couldn't save your last change" note appears, republish
   once with the capabilities above.
4. Walk them through the tabs in two or three lines each, in plain words:
   - **Daily Recap**: what's new since they last pressed "Done for today"; rate each purchase 1 Want,
     2 Could skip, 3 Need, fix categories; bills due this week.
   - **Overview**: the month's income, spending, net, card debt, savings; tap a card to chart it; the
     set-asides to send from last month's income; bills coming up.
   - **Transactions**: every transaction, searchable; spending by month by category or by need.
   - **Budget**: budget vs actual; budgets can be edited there (saved per browser) or by asking Claude.
   - **Insights**: a month-by-month review with where to improve and a plan for next month.
   - **Accounts**: balances (each with the date the bank last updated it, orange if it's 3+ days old), what's owed, net worth over time; tap an account to open its sign-in page.
   - **Notes**: the pencil next to any transaction adds a note (who it was for, what it was, a
     reminder); notes show under the name, sync across devices, and the Transactions search finds them.
   - "+ New category" in any category menu: ask Claude to add one.
