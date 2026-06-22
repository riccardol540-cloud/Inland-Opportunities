# INLAND Opportunities — setup state & routines to wire

Handoff note for picking this up in a fresh session. It summarises what's built, how it
fits together, and the routines that still need to be created and wired in.

---

## 1. What this system is

An opportunity pipeline for INLAND: find funding/residency/partnership calls, triage
them as a team, and have Claude produce the full application + edition assets for the
ones worth pursuing. It's deliberately **sliced into three layers** by cadence, cost,
and judgment:

```
LAYER 1 — SCOUT            LAYER 2 — REVIEW GATE        LAYER 3 — PRODUCER
(scheduled, weekly)        (people, in the dashboard)   (on-demand session/skill)
Finds + researches calls   Triage: flag, assign,        Drafts the full application
→ writes opportunities     move to Pursuing             + edition asset set
  .json, commits to repo                                → commits to editions/, links docs
```

Pipeline stages on the board: **Suggest → Research → Pursue → Produce → Archive.**

## 2. What's already built and live

- **Dashboard** (deployed on Vercel, password-gated `inland2026`): editable board with
  Inbox / Pursuing / Archived, fit scores, flag/priority star, document links,
  production badge, per-card staged save (owner/notes) with a header save-state
  indicator. Drag-and-drop + buttons.
- **GitHub-as-database**: `data/opportunities.json` is the single source of truth. The
  dashboard reads/writes it via the GitHub API (serverless functions in `api/`, token in
  Vercel env). Writes are field-level merges with sha-retry, so humans and agents can
  write to the same file safely.
- **The brain** (`_inland/`): `about-inland.md`, `opportunity-criteria.md`, `sources.md`,
  `deliverables.md` — the canonical context every routine must read first.
- **Playbooks** (`SCOUT.md`, `PRODUCER.md`): the step-by-step for each Claude routine.
- **`editions/`**: where produced files are committed (per Option A) so links work for
  everyone.

Repo: `https://github.com/riccardol540-cloud/Inland-Opportunities.git`

## 3. Data model (the contract between dashboard and routines)

Each opportunity in `data/opportunities.json`:

| field | who sets it | notes |
|---|---|---|
| `id`, `title`, `funder`, `channel`, `link` | Scout / suggester | identity |
| `deadline`, `budget`, `eligibility` | Scout | factual |
| `fit` (1–5), `fitRationale`, `territory`, `requiredDocs` | Scout | research output |
| `researched` (bool) | Scout | `false` until scanned; locks Pursuing |
| `status` (`new`/`pursuing`/`archived`) | people | column |
| `flagged` (bool) | people | priority; Producer does these first |
| `owner`, `notes` | people | staged save |
| `production` (`none`/`in_progress`/`drafted`) | Producer | drives the badge |
| `documents` [{label,url}] | Scout + Producer | GitHub URLs to created files |
| `history` [] | all | audit log |

**Do not rename these fields** without updating `api/opportunities.js` (EDITABLE list)
and the dashboard.

---

## 4. Routines — current state

### A. SCOUT — recurring research routine  ✅ LIVE (Cowork scheduled task)

- **Where it runs**: a **Cowork scheduled task**, id `inland-opportunity-scout`, cron
  `0 8 * * 1` (Mondays ~8am local). Manage it under Cowork → Scheduled.
- **What it does**: follows `SCOUT.md` — reads the brain, scans the three channels,
  scores fit, writes a research brief to `editions/<slug>/research-brief.md`,
  appends/enriches rows in `data/opportunities.json`, links the brief in `documents`,
  and reports a digest in the task result. Two jobs: discover new calls **and** enrich
  user-suggested cards (`researched: false`) so they unlock for Pursuing.
- **How it writes**: because Cowork is sandboxed (and the local clone can be diverged),
  it commits to the LIVE repo via the **GitHub API helper** `scripts/inland-repo.mjs`,
  which reads `GITHUB_TOKEN`/`GITHUB_REPO`/`GITHUB_BRANCH` from a gitignored **`.env`**
  in the repo root. Pull that file once with `vercel env pull .env --environment=production`.
  If `.env` is missing, the run stops and reports — it never `git push`es.
- **Proven**: a manual run on 2026-06-22 added two Goethe opportunities + briefs and they
  rendered on the dashboard.

### B. PRODUCER — on-demand production routine  ⚙️ command ready (Claude Code)

- **Where it runs**: **Claude Code** on your Mac, as the `/producer` slash command.
  ✅ Installed — the command lives at `.claude/commands/producer.md` (moved there from
  the old `claude-code/producer.md` staging location on 2026-06-22).
- **What it does**: follows `PRODUCER.md` — `git pull --rebase`, takes
  `status === "pursuing"` (flagged → deadline → fit, or a target passed as an argument),
  sets `production: "in_progress"`, runs deep research, produces the full asset set into
  `editions/<territory>/`, sets `production: "drafted"`, links every file in `documents`,
  then commits + pushes. Presents for review; never changes `status` (Archive is the
  team's call).
- **How it writes**: plain `git` — Claude Code has your real credentials and a synced
  clone, so **no token/.env needed** here (unlike the Scout).
- **Run it**: open Claude Code in the repo, then `/producer` (or `/producer <id>`). Needs
  the document skills (docx, xlsx, pptx, pdf) available.

### C. (Optional) DEADLINE WATCH — not built

- A small scheduled task that scans `pursuing` items and pings when a deadline is within
  N days. Cheap; nice-to-have later.

---

## 5. Open decisions / notes for the next session

- **One repo, two kinds of writer**: everything lives in this single repo. The dashboard
  (on Vercel) commits via the `GITHUB_TOKEN` in Vercel's env; the Scout/Producer run as
  Claude sessions on a **local clone of the same repo** and push with that environment's
  git login. There is no second repo and no separate token for the routines — running
  them in Claude Code on your Mac means they just use your existing git auth. The only
  thing to confirm is that wherever the routines run has push access to `main`.
- **Trigger model agreed**: Produce stays on-demand (flag + Pursuing column tell Claude
  what's queued); do not auto-fire deep research on every move to Pursuing.
- **Editions storage agreed**: Option A — produced files committed to `editions/` in the
  repo so dashboard links resolve for all collaborators.
- **Deploy/push**: changes committed in the workspace still need `git push` + Vercel
  redeploy from a machine with your credentials (see `CLAUDE_CODE_DEPLOY.md`).

## 6. Key files to read first in the new session

1. `_inland/about-inland.md` — what INLAND is.
2. `SCOUT.md` and `PRODUCER.md` — the routines to build.
3. `data/opportunities.json` — the data contract.
4. `README.md` / `DEPLOY.md` / `CLAUDE_CODE_DEPLOY.md` — app + deploy.
