# Claude Code — deploy this project

You are running in Claude Code on Riccardo's Mac, inside the `Inland-Opportunities/`
folder. This is a static dashboard (`public/`) + serverless functions (`api/`) backed by
a GitHub repo as its database. Deploy it to GitHub + Vercel by following the steps below.
Run the commands; pause only at the two spots marked **ASK RICCARDO**.

Repo: `https://github.com/riccardol540-cloud/Inland-Opportunities.git`

---

## 0. Sanity check

```bash
pwd                       # should end in /Inland-Opportunities
git log --oneline -1      # an initial commit already exists
node --version            # need >= 18
```

If this folder is NOT already a git repo (no commit shown), run:
```bash
git init && git add -A && git commit -m "Initial commit"
```

## 1. Push to GitHub

```bash
git remote add origin https://github.com/riccardol540-cloud/Inland-Opportunities.git 2>/dev/null || true
git branch -M main
git push -u origin main
```

If the push fails on auth, run `gh auth login` (or configure a credential helper) and
retry. If the remote already has commits, do `git pull --rebase origin main` then push.

## 2. GitHub token for the dashboard's write-back

The dashboard saves edits by committing `data/opportunities.json` back to the repo, so it
needs a token with write access.

**ASK RICCARDO** to create one (you cannot make it for him):
- GitHub → Settings → Developer settings → Fine-grained tokens → Generate new token
- Repository access: Only select repositories → `Inland-Opportunities`
- Permissions → Repository → **Contents: Read and write**
- Copy the `github_pat_...` value.

Hold this for step 4.

## 3. Link the Vercel project

```bash
npm i -g vercel        # if needed
vercel login           # if not already logged in
vercel link            # create/link a project; accept defaults
```

## 4. Environment variables

Generate the cookie secret:
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Set all five for Production and Preview. Use the password `inland2026`, the generated
secret, and the token from step 2:

```bash
printf 'inland2026' | vercel env add DASHBOARD_PASSWORD production
printf 'inland2026' | vercel env add DASHBOARD_PASSWORD preview
# AUTH_SECRET — paste the random hex from above:
vercel env add AUTH_SECRET production
vercel env add AUTH_SECRET preview
# GITHUB_TOKEN — paste the github_pat_... from step 2:
vercel env add GITHUB_TOKEN production
vercel env add GITHUB_TOKEN preview
printf 'riccardol540-cloud/Inland-Opportunities' | vercel env add GITHUB_REPO production
printf 'riccardol540-cloud/Inland-Opportunities' | vercel env add GITHUB_REPO preview
printf 'main' | vercel env add GITHUB_BRANCH production
printf 'main' | vercel env add GITHUB_BRANCH preview
```

(If the `printf | vercel env add` piping misbehaves in this shell, just run
`vercel env add <NAME>` and paste each value when prompted.)

## 5. Deploy

```bash
vercel --prod
```

## 6. Verify

- Open the printed production URL.
- You should hit a password screen; enter `inland2026`.
- The board shows one sample opportunity in **Inbox**.
- Test an edit: drag the sample to **Pursuing** (the `→ pursuing` button) and confirm a
  new commit appears in the GitHub repo (`data/opportunities.json` updated). That proves
  the write-back token works.

If the board loads but edits fail with a 500, the `GITHUB_TOKEN` is missing/insufficient
— recheck step 2 and that the env var is set, then `vercel --prod` again.

## 7. Report back to Riccardo

Give him: the production URL, confirmation the password works, and confirmation that a
test edit committed to GitHub. Mention he can optionally connect the repo in the Vercel
dashboard so future `git push`es (including the Scout's) auto-deploy.

---

### Env var reference

| Variable | Value |
|---|---|
| `DASHBOARD_PASSWORD` | `inland2026` |
| `AUTH_SECRET` | random 32-byte hex (generated in step 4) |
| `GITHUB_TOKEN` | fine-grained PAT, Contents: read/write |
| `GITHUB_REPO` | `riccardol540-cloud/Inland-Opportunities` |
| `GITHUB_BRANCH` | `main` |
