# INLAND Opportunities — project context for Claude Code

This repo is the INLAND opportunity pipeline: a password-gated dashboard (on Vercel)
backed by `data/opportunities.json` in this repo, plus two Claude routines —
the **Scout** (finds/researches calls) and the **Producer** (drafts the full
application + edition assets for pursued opportunities).

## Read these first
- `_inland/about-inland.md` — what INLAND is: identity, voice/tone, method, issues, funding model.
- `_inland/research-angle.md` — territory-agnostic blueprint of the editorial angle; how to find/frame INLAND stories in *any* country (Rwanda/Kashmir are angle blueprints, not subject templates).
- `_inland/deliverables.md` — the exact asset set and house style to produce.
- `_inland/opportunity-criteria.md`, `_inland/sources.md` — fit rubric and where to look.
- `SCOUT.md`, `PRODUCER.md` — the two playbooks.
- `HANDOFF.md` — overall setup state and how the pieces fit.

## Pipeline
Suggest → Research → Pursue → Produce → Archive. Stages live as fields on each
opportunity in `data/opportunities.json` (see HANDOFF.md §3 for the field contract).

## Where routines run
- **Scout**: a Cowork scheduled task (weekly). It commits to the LIVE repo via the
  GitHub API helper (`scripts/inland-repo.mjs`) because that environment is sandboxed.
- **Producer**: run here in Claude Code via the `/producer` command. Because Claude Code
  has your real git credentials and a synced clone, the Producer uses plain git
  (`pull` → work → `commit` → `push`) — no token/helper needed.

## Editions / produced files
Produced files are committed into `editions/<territory>/` so the dashboard can link them
(`documents` array on the opportunity). Keep INLAND house style from `deliverables.md`.

## Don't
- Don't overwrite human-owned fields (`status`, `owner`, `notes`, `flagged`).
- Don't commit secrets. `.env` (with `GITHUB_TOKEN`) is gitignored.
