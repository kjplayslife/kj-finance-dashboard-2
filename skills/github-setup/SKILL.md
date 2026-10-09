---
name: github-setup
description: Set up GitHub for KJ Finance Dashboard 2.0 so the daily cloud update can work - a free GitHub account, Homebrew, Git and the GitHub CLI (winget on Windows), gh signed in, the GitHub connector and Claude GitHub App on Claude with the same account, a check that it's all right, then KJ's setup checklist item by item. Triggers on "/github-setup", "set up GitHub", "install the GitHub CLI", "connect GitHub to Claude", "repository could not be found", "am I ready to set up my dashboard", "setup checklist".
---

# GitHub setup (and the setup checklist)

Take the person from no GitHub to GitHub ready for Claude's cloud routines: a GitHub account, Git and
the GitHub CLI (`gh`) on this computer and signed in, and the GitHub connector on Claude using the
**same** GitHub account. Then run KJ's setup checklist and tell them whether they're ready for
`/finance-setup-v2`. This is the "GitHub Setup" module and "Setup Checklist" of KJ's course.

If something goes wrong, read `${CLAUDE_PLUGIN_ROOT}/skills/finance-setup-v2/references/where-people-get-stuck.md`
("Homebrew, Git and GitHub CLI", "GitHub connector on Claude", "Setup checklist") and use the fix it gives.

## How to run this
- **One step at a time.** One or two questions at a time with AskUserQuestion (recommended option first,
  marked "(Recommended)"). A few short lines per message, then wait.
- **Do the technical work yourself** in the Code tab: check versions, install with brew/winget, write
  config. Only bring them in for what needs them: their **Mac password**, signing in and approving in the
  browser, and the claude.ai connector.
- **Interactive commands go in their terminal.** Commands that ask for a password or wait for Return
  (the Homebrew installer, `gh auth login`) can't run in your own shell. Give each one in its own
  ```bash block (the app adds a Run button that runs it in a terminal) or have them paste it into
  Terminal, and say what it will ask. Everything else you run yourself.
- **They type their own passwords and codes.** Never ask for them in chat. Sign-ins happen in their own
  browser (`open "<url>"` on a Mac, `cmd.exe /c start "" "<url>"` on Windows).
- **Mac first.** Windows notes are in parentheses: winget instead of Homebrew, PowerShell instead of
  Terminal.

## 0. What's already done (quietly)
Run: `uname -s`, `git --version`, `gh --version`, `gh auth status`, and on a Mac `brew --version`
(also try `/opt/homebrew/bin/brew --version` and `/usr/local/bin/brew --version`, in case brew is
installed but not on PATH).
- Skip every step that's already done. If `gh auth status` shows an account, ask once (AskUserQuestion)
  whether that's the GitHub account they want to use for the dashboard.
- Everything done already: go to step 4 (the connector), which can't be checked from here.
- Otherwise one line: what you're about to do (about 15 minutes, one step at a time), then step 1.

## 1. GitHub account
AskUserQuestion: **"Do you have a GitHub account?"** ("No, I need one (Recommended)" / "Yes").
No: open https://github.com/signup in their browser; they sign up (free plan), verify the email if it
asks, and leave the GitHub tab open. Wait for "done".

## 2. Homebrew, Git and GitHub CLI
**Mac:**
1. **Homebrew** (skip if brew exists). Tell them: it will ask for their **Mac password** (the one they
   log in with; nothing shows while typing, that's normal), then "Press RETURN/ENTER to continue", and it
   may download Apple's Command Line Tools, which takes a few minutes. Give them:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   When it finishes it prints **"Next steps"** with lines to run. You do that part: on Apple silicon
   (`/opt/homebrew/bin/brew` exists)
   ```bash
   grep -q 'brew shellenv' ~/.zprofile 2>/dev/null || { echo >> ~/.zprofile; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile; }
   ```
   (on Intel Macs brew is in `/usr/local/bin`, already on PATH). In your own commands prefix
   `eval "$(/opt/homebrew/bin/brew shellenv)";` until a new session. Check `brew --version`.
   If their account isn't an admin on the Mac, Homebrew can't install: they need an admin to do it, or
   use the installers at https://git-scm.com and https://cli.github.com instead.
2. **Git and GitHub CLI**: you run `brew install git gh` (no password needed). Check `git --version` and
   `gh --version`.

**(Windows:** Git is already there (Claude Code needs it). You run
`winget install --id GitHub.cli -e --accept-source-agreements --accept-package-agreements`; if
`git --version` fails, also `winget install --id Git.Git -e`. New tools appear in a **new** terminal or
Code session; use the full path `"C:\Program Files\GitHub CLI\gh.exe"` until then.)

## 3. Sign gh in to GitHub
Tell them what it will ask, then give them this to run in their terminal:
```bash
gh auth login --hostname github.com --git-protocol https --web
```
- "Authenticate Git with your GitHub credentials?" -> **Y** (Return).
- It shows a **one-time code** in the terminal: copy it, then press Return to open the browser.
- In the browser, the **Device Activation** page shows "Signed in as <account>". If that's not the
  account they want, **Use a different account** first. Then **Continue**, paste the code, and
  **Authorize**.
Then you run `gh auth setup-git` and `gh auth status`. It should show "Logged in to github.com account
<name>" as the **active** account. Two accounts listed: make the right one active with
`gh auth switch --user <name>`. Remember this account name: step 4 has to match it.

**Git's name and email** (you do this; skip any that `git config --global --get user.name` /
`user.email` already return): use their GitHub display name and GitHub's private no-reply email, so
their real email never lands in commits:
```bash
gh api user --jq '.name // .login'          # -> user.name
gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"'   # -> user.email
git config --global user.name "<name>"
git config --global user.email "<id+login@users.noreply.github.com>"
```

## 4. Connect GitHub to Claude (same account)
In the Claude app:
1. Customize > **Connectors** > **Discover** > search "GitHub" > **Connect**. Their browser opens:
   **Authorize** (check it's the same GitHub account as `gh`: the page names it).
2. Back in the app: Customize > Connectors > **Yours** > **GitHub Integration** > **Fix** > **Install
   GitHub App**. On GitHub choose **All repositories** (easiest; the finance repo doesn't exist yet) >
   **Approve, Install, & Authorize**.
3. GitHub Integration should now show two green checks: **GitHub account connected** and **Claude
   GitHub App**, with an account listed as "installed".
(Same thing in a browser: https://claude.ai/settings/connectors.)

## 5. Check it will work for cloud routines
`gh` can't see the Claude GitHub App, so check it with them:
1. AskUserQuestion: **"On the GitHub Integration page, which account is listed under Claude GitHub
   App as installed?"** Offer the `gh` account name as the first option ("<name> (same as gh)") and
   "A different name" / "Nothing is listed".
2. **Same name**: good. **Different name**: routines would fail later with "repository could not be
   found". Fix: **Disconnect** on GitHub Integration, sign the browser in to github.com as `<gh account>`,
   and redo step 4. (Or, if the other account is the one they want, sign gh in to it instead: step 3.)
   **Nothing listed / "Fix" still shows**: the Claude GitHub App isn't installed: step 4.2.
3. If they picked "Only select repositories": tell them new repos won't be visible to routines until
   added; easier to switch to All repositories at github.com/settings/installations > Claude > Configure.
4. Optional, if they have any repo on that account: GitHub Integration > **Check repository status** >
   pick one; it should say cloud sessions have access.

## 6. Setup checklist (check what you can yourself)
Go down the list; check each one, then show the result as a short list with ✅ / ❌.
1. **Claude Pro or higher**: ask (AskUserQuestion: Pro / Max / Team or Enterprise / "Free"). Free: they
   need to upgrade at claude.ai/settings; the cloud routine needs it.
2. **Desktop app, Code tab**: you're running in it (if this isn't the desktop app's Code tab, say they'll
   need it for setup).
3. **Plugin installed and on**: yes, since this skill is running. They can also see it in Customize >
   Plugins > **Yours** > **KJ Finance Dashboard 2.0** (enabled).
4. **Era connected**: ToolSearch for "list_financial_accounts"; if found, one read-only
   `accounts__list_financial_accounts` call and say how many accounts it sees. In Customize > Connectors
   > **Yours**, **Era Context** is there (its tools say **Needs Approval**; that's fine). Not found: run
   **/era-setup** (or, if they just connected it, a new Code session).
5. **All banks in Era**: ask them to open https://era.app/en-US/app > **My Vault** and confirm every
   account is there (up to an hour after linking is normal). Compare with the Era list from item 4.
6. **Git and GitHub CLI**: `git --version`, `gh auth status` (active account = the one from step 5).
7. **GitHub connector**: GitHub Integration shows the first two boxes green, same account (step 5).
8. **Claude phone app**: ask whether it's installed (iPhone or Android), signed in to the **same** Claude
   account, with notifications allowed for Claude in the phone's settings. That's where the morning
   update and the dashboard link show up.
9. Optional, mention in one line: Settings > Claude Code > the "keep awake" and "let your phone start
   sessions" switches (only matter for running things from this computer).
Then:
- **All ✅**: "You're ready. Type **/finance-setup-v2** to build your dashboard." (In this session or a
  new one in the folder they want for their finances; a new Code session if Era was just connected.)
- **Anything ❌**: list just what's left, each with the one thing to do (or the skill to run), and offer
  to help with the first one now.
