# Where people get stuck (and what to do)

Read the stage they're in when something goes wrong. Each item: what they see -> what to do. Button and
menu names are the ones in the Claude app, Era and GitHub (Oct 2026); if a screen looks different, ask
what they see (or a screenshot) before guessing.

## Claude app and plan
- **No "Code" tab, or Claude Code says it needs a paid plan** -> Claude Code needs **Pro ($20/mo) or
  higher**. They upgrade at claude.ai/settings (Billing), then reopen the app.
- **Can't find Routines** -> in the Code tab sidebar click **More** and add **Routines** to the sidebar.
- **Updates or the phone app can't reach this computer** -> Settings > Claude Code: turn on **Keep this
  computer awake for Remote Control**, **Let your phone and claude.ai start sessions here** and **Keep
  computer awake while Claude works**. (Only matters for running things from this computer; the cloud
  routine doesn't need it.)
- **Signed in to a different Claude account on the phone or claude.ai** -> everything (connectors,
  routines, the dashboard) lives in one Claude account. Sign in to the same one everywhere.

## Plugin install
- **Path**: Code tab > **Customize** > **Plugins** > white **+ Add** dropdown > **Add marketplace** >
  **Add from a repository** > paste `kjplayslife/kj-finance-dashboard-2` > **Sync** > **Add** on
  "KJ Finance Dashboard 2.0".
- **Typing "/kj" in a new chat shows nothing** -> check **+** > hover **Plugins**, or **Manage plugins** >
  **Yours**. Not there: add the marketplace again. There but off: turn it on. Then start a **new** Code
  session (skills load when a session starts).
- **An older KJ finance plugin is also on** -> turn it off (Customize > Plugins). Every 2.0 skill ends in
  "-v2" or is one of the setup skills (/era-setup, /github-setup).
- **No internet access to GitHub / Sync fails** -> **+ Add** > **Upload plugin** and drag in the plugin
  .zip from the course resources (it won't auto-update; re-add from the repository later).

## Era account
- **Sign-up**: https://era.app/#via=kj > **Get started for free** > **Continue free with Google** (or
  email). Do it in their own browser.
- **Already has an Era account under another email** -> use the account they'll keep; connectors and
  bank links belong to that one login.
- **Which plan** -> free covers **2 linked accounts** (each checking, savings and card counts). More
  than 2: the **Organize** plan, about **$9/month**, up to 15 accounts.
- **Upgrading** -> account bubble (top right) > **Upgrade** > uncheck **Show small biz** if it's checked >
  pick **Monthly** or **Quarterly** (top right) > **Start Organize for $1** (or the 10%-off-for-life
  option) > checkout through Stripe. They type their own card details; Claude never does.

## Linking banks and cards in Era
- **Path**: Era home > white **Connect** button > **Link with MX** > search the bank > sign in through
  the bank's window > a "connection successful" pop-up shows in the bottom right of the Era tab.
- **MX can't find the bank, the sign-in errors, or it never finishes** -> link that bank with
  **Stripe** instead. MX first because MX links refresh balances daily (Stripe links have kept old
  balances).
- **"Connection successful" but the account isn't in My Vault** -> **normal: it can take 15 minutes to
  1 hour** for a bank to sync through MX. Keep linking the others; check **My Vault** later. Don't
  link it again.
- **Linked the same bank twice** (e.g. MX and Stripe) -> every transaction will show twice. Remove the
  extra one in Era (My Vault), or tell the finance setup to exclude it.
- **Can't link a third account** -> that's the free limit; upgrade (Era account, above).
- **Bank asks to approve on their phone** -> expected; approve in the bank's app and go back.
- **The bank window closes, is blank, or says it worked and shows nothing** -> try again in a fresh
  browser window (pop-up blockers off for era.app).
- **Venmo / some small institutions aren't listed** -> skip them; money sent there from a linked
  checking account still shows up.
- **Where to see what's linked** -> **My Vault** (Bank connections); **Transactions** there shows
  purchases once the sync is done.

## Era connector in Claude
- **Path**: Era home > **Connect an AI agent** > **Claude** > opens claude.ai/directory/era-context >
  **Sign in to add** (the same Claude account as the desktop app) > Era's "Authorize application" page >
  **Allow access**.
- **Check**: Customize > **Connectors** > search "Era" -> **✓ Connected**. Not connected: click it and
  connect again.
- **Fallback** -> claude.ai/settings/connectors > add **Era Context**; if it isn't listed, **Add custom
  connector** with `https://context.era.app`.
- **Connected, but Claude Code can't find the Era tools** -> connectors show up in **new** sessions.
  Start a new Code session (same folder) and run the skill again.
- **Era tools show "Needs Approval"** -> fine; that's the normal setting and Claude will ask before
  each Era call in a chat.
- **Claude sees fewer accounts than My Vault** -> still syncing (wait), or over the free limit (accounts
  past the limit come back as `tier_excluded`; upgrade).

## Homebrew, Git and GitHub CLI (Mac; Windows uses winget)
- **The Homebrew install asks for "Password:" and nothing shows while typing** -> normal; type the Mac
  login password and press Return. It must be an admin account on this Mac.
- **"Press RETURN/ENTER to continue"** -> press Return. It may also install Apple's Command Line Tools,
  which can take several minutes.
- **"Warning: /opt/homebrew/bin is not in your PATH" / "Next steps"** -> the two or three lines it
  prints under "Next steps" must be run (Claude can add them to ~/.zprofile). Then open a new terminal.
- **"command not found: brew" or "gh"** -> the Next steps lines weren't run, or the terminal is old:
  open a new terminal (or run `eval "$(/opt/homebrew/bin/brew shellenv)"`).
- **"xcrun: error: invalid active developer path"** -> `xcode-select --install`, accept, wait, retry.
- **gh auth login: the browser page says "Signed in as" someone else** -> click **Use a different
  account**, sign in to the GitHub account they'll use, then **Continue**.
- **Where's the code?** -> the one-time code is in the **terminal** (copy it from there), not the browser.
- **Code expired / closed the page** -> run `gh auth login` again.
- **`gh auth status` shows two accounts** -> the *active* one must be the account they'll connect to
  Claude: `gh auth switch --user <name>`.
- **Git says "Please tell me who you are"** -> set `git config --global user.name` / `user.email`.
- **Windows** -> `winget install --id Git.Git -e` and `winget install --id GitHub.cli -e`, then a new
  terminal; the rest is the same.

## GitHub connector on Claude
- **Path**: Customize > **Connectors** > **Discover** > search "GitHub" > **Connect** > in the browser
  **Authorize**. Then Customize > Connectors > **Yours** > **GitHub Integration** > **Fix** > **Install
  GitHub App** > on GitHub pick **All repositories** > **Approve, Install, & Authorize**.
- **Done when** -> GitHub Integration shows two green checks: **GitHub account connected** and **Claude
  GitHub App** with their account "installed".
- **The account under "Claude GitHub App" isn't the one `gh` is signed in as** -> routines later fail
  with **"repository could not be found"**. **Disconnect** on GitHub Integration, sign the browser in to
  the right GitHub account (github.com), and connect again.
- **"Fix" still shows** -> the Claude GitHub App isn't installed yet; click **Fix** > **Install GitHub App**.
- **Chose "Only select repositories"** -> new repos (like the finance one) won't be visible. Change it at
  github.com/settings/installations > Claude > **Configure** > All repositories (or add the repo).
- **Check one repo** -> GitHub Integration > **Check repository status** > pick owner/repo.

## Cloud routine
- **"repository could not be found"** -> GitHub connector is a different account (above).
- **Run shows no Era tools** -> the routine needs the **Era Context** connector attached; or reconnect Era
  on claude.ai.
- **Artifact publish refused** -> the routine must read the artifact before publishing (ROUTINE.md does).
- **No phone notification** -> Claude phone app installed, signed in to the same account, notifications
  allowed for Claude in the phone's settings.

## Setup checklist
- Customize > Plugins > **Yours** > **KJ Finance Dashboard 2.0** is there and on.
- Customize > Connectors > **Yours** > **Era Context** is there; its tools show **Needs Approval**.
- Same page: **GitHub Integration**, first two boxes green.
- https://era.app/en-US/app > **My Vault**: every account shows up (allow up to an hour after linking).
