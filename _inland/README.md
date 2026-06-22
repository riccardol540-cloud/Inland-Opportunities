# _inland — the INLAND shared brain

This folder is the single source of truth that every automated routine and working
session reads before it does anything. A scheduled task, a fresh Claude session, or a
collaborator can understand what INLAND is, what a good opportunity looks like, where to
look, and exactly which deliverables to produce — without re-deriving it each time.

## The pipeline this supports

The opportunity-to-edition workflow is **sliced into three layers** with different
cadences, costs, and levels of human judgment. It is not one routine.

```
  LAYER 1 — SCOUT            LAYER 2 — REVIEW GATE        LAYER 3 — PRODUCER
  (scheduled, weekly)        (collaborators, in the       (on-demand session/skill)
                              dashboard)
  ───────────────────        ────────────────────         ──────────────────────────
  Scans funders, calls,      People open the dashboard,   Reads data/opportunities.json,
  partnerships against       enter the password, and      picks up everything marked
  opportunity-criteria.md    move opportunities to        "pursuing", runs deep research
  + sources.md. Appends      Pursuing / add notes /       and produces the full edition
  new rows to                assign owners. Saved back    asset set (see deliverables.md),
  data/opportunities.json    to GitHub.                   mirroring Rwanda/Kashmir.
  and pushes. Cheap.         The human decision.          Expensive, deliberate.
```

The **shared source of truth** is `../data/opportunities.json`: the Scout writes it,
collaborators edit it through the dashboard, and the Producer reads it. Everything is in
the GitHub repo, so Claude sees user edits natively.

## Files

- `about-inland.md` — what INLAND is. Identity, voice, method, issues, funding model.
- `opportunity-criteria.md` — the Scout's scoring rubric and fit logic.
- `sources.md` — where the Scout looks.
- `deliverables.md` — the exact asset set the Producer builds, with house style.

## Related (repo root)

- `../SCOUT.md` — the weekly scan playbook.
- `../PRODUCER.md` — the on-demand production playbook.
- `../data/opportunities.json` — the pipeline source of truth.
- `../README.md` / `../DEPLOY.md` — the dashboard app and how to deploy it.
