# INLAND · Opportunities

A password-gated, GitHub-backed dashboard for the INLAND opportunity pipeline, plus the
playbooks that let Claude run the **Scout** (find opportunities) and **Producer** (build
the application + edition assets).

## How it fits together

```
Scout (weekly, Claude)  →  data/opportunities.json  ←  Producer (on-demand, Claude)
                                   ↕
                          Dashboard (this app, on Vercel)
                          collaborators triage behind a password
```

`data/opportunities.json` is the single source of truth. The dashboard reads and writes
it directly in this GitHub repo via the GitHub API, so every edit is a commit and Claude
sees collaborators' decisions natively.

## Repo layout

- `public/` — the dashboard (static SPA: password gate + editable board).
- `api/` — serverless functions: `login.js` (password → signed cookie),
  `opportunities.js` (GET reads, PATCH/POST/DELETE commit to GitHub).
- `data/opportunities.json` — the pipeline source of truth.
- `_inland/` — the shared brain (what INLAND is, criteria, sources, deliverables).
- `SCOUT.md` / `PRODUCER.md` — the Claude playbooks.
- `DEPLOY.md` — how to put this online (GitHub + Vercel).

## Using the dashboard

Open the deployed URL, enter the password, and you'll see three columns — **Inbox**,
**Pursuing**, **Archived**. For each opportunity you can change status (the `→` buttons),
set an owner, and add notes. Everything saves back to GitHub. Move what's worth doing to
**Pursuing**; that's the signal the Producer acts on.

## Required environment variables (set in Vercel)

| Variable | Value |
|---|---|
| `DASHBOARD_PASSWORD` | `inland2026` |
| `AUTH_SECRET` | any long random string (signs the session cookie) |
| `GITHUB_TOKEN` | a GitHub token with write access to this repo |
| `GITHUB_REPO` | `riccardol540-cloud/Inland-Opportunities` |
| `GITHUB_BRANCH` | `main` |

See `DEPLOY.md` for the full steps.
