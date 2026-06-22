# SCOUT — the weekly opportunity scan

*This is the playbook for the scheduled Scout run. Give Claude this file (plus the
`_inland/` brain) as the instruction for a recurring task. The Scout's only job is to
keep `data/opportunities.json` populated with vetted, relevant opportunities — it does
not apply and does not produce edition assets.*

## Reading & writing the repo (important)

Always read and write the **live** `data/opportunities.json` on `main`, never the local
clone (which may be diverged). Use the helper, which goes through the GitHub API using the
token in the gitignored `.env`:

```bash
# read current live state
node scripts/inland-repo.mjs get data/opportunities.json > /tmp/opps.json
# commit a file back to the live repo
node scripts/inland-repo.mjs put data/opportunities.json /tmp/opps.json "scout: weekly scan"
node scripts/inland-repo.mjs put editions/<slug>/research-brief.md /tmp/brief.md "scout: brief for <slug>"
```

If `.env` (with `GITHUB_TOKEN`) is missing, stop and report — do not attempt `git push`.

## Steps

1. **Read context**: `_inland/about-inland.md`, `_inland/opportunity-criteria.md`,
   `_inland/sources.md`.
2. **Load current state**: read `data/opportunities.json`. Note every existing `id`,
   `title`, `funder`, and `link` so you can dedupe.
3. **Scan** the three channels in `sources.md` (public/EU culture funds, cultural
   institutes, partnerships/co-productions). Verify each candidate on its primary
   source — real, open deadline, INLAND-eligible.
4. **Filter & score** with the rubric in `opportunity-criteria.md`. Apply the hard
   filters; drop fails. Score fit 1–5 with a one-line rationale. Keep 3–5 (include 2s
   only if the week is thin; never 1s).
5. **Write** each new, non-duplicate opportunity as an object appended to
   `opportunities.json` → `opportunities[]`, using the schema below. Leave existing
   rows and any human edits (status, owner, notes) untouched.
6. **Commit & push** the updated `opportunities.json` to GitHub. The live dashboard
   reflects it immediately.
7. **Digest**: email/report a short summary — count of new finds, any URGENT
   (deadline ≤ 21 days), and the top 1–2 by fit.

## Object schema (one per opportunity)

```json
{
  "id": "kebab-stable-id",
  "title": "...",
  "funder": "...",
  "channel": "public-fund | cultural-institute | partnership",
  "link": "https://...",
  "deadline": "YYYY-MM-DD",
  "budget": "e.g. up to €25,000",
  "eligibility": "one line — why INLAND qualifies",
  "fit": 5,
  "fitRationale": "one line",
  "territory": "candidate territory / angle",
  "requiredDocs": ["Concept note", "Budget", "Timeline"],
  "researched": true,
  "flagged": false,
  "production": "none",
  "documents": [
    { "label": "Research brief", "url": "https://github.com/riccardol540-cloud/Inland-Opportunities/blob/main/editions/<slug>/research-brief.md" }
  ],
  "status": "new",
  "owner": "",
  "notes": "",
  "addedBy": "scout",
  "addedAt": "YYYY-MM-DD",
  "history": []
}
```

### Two kinds of write

- **Brand-new finds** the Scout discovers: add them fully researched —
  `researched: true` with fit, budget, docs filled in.
- **User suggestions** already in the board (`researched: false`, added via the
  dashboard): the Scout *enriches* them — fill fit/budget/territory/requiredDocs, write
  the research brief, attach it to `documents`, and flip `researched: true` so they
  unlock for Pursuing. Never touch their `status`, `owner`, `notes`, or `flagged`.

### The research brief

For each opportunity you research, write a short brief to
`editions/<slug>/research-brief.md` in the repo and add its GitHub URL to `documents`.
That's the document the card links to after research. Leave `flagged` to the humans and
`production` at `"none"` (the Producer owns that field).

## Rules

- **Never overwrite human edits.** Only add new opportunities and, if re-confirming an
  existing one, update factual fields (deadline, budget) — never `status`, `owner`, or
  `notes`, which belong to the collaborators.
- **Dedupe** on link + funder + title before adding.
- Default new rows to `status: "new"` so they land in the dashboard's Inbox.

## Cadence

Weekly is the default (e.g. Monday morning). Set this up as a scheduled task pointing
at this file.
