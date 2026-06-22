# SCOUT — the weekly opportunity scan

*This is the playbook for the scheduled Scout run. Give Claude this file (plus the
`_inland/` brain) as the instruction for a recurring task. The Scout's only job is to
keep `data/opportunities.json` populated with vetted, relevant opportunities — it does
not apply and does not produce edition assets.*

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
  "status": "new",
  "owner": "",
  "notes": "",
  "addedBy": "scout",
  "addedAt": "YYYY-MM-DD",
  "history": []
}
```

## Rules

- **Never overwrite human edits.** Only add new opportunities and, if re-confirming an
  existing one, update factual fields (deadline, budget) — never `status`, `owner`, or
  `notes`, which belong to the collaborators.
- **Dedupe** on link + funder + title before adding.
- Default new rows to `status: "new"` so they land in the dashboard's Inbox.

## Cadence

Weekly is the default (e.g. Monday morning). Set this up as a scheduled task pointing
at this file.
