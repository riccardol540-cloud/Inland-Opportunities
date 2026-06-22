# DEPLOY — putting the dashboard online

The app is built and committed. These steps push it to your GitHub repo and deploy it on
Vercel. Run them on your machine (your terminal, or ask Claude Code to run them) — they
need your GitHub and Vercel logins, which a sandbox can't access.

Repo: `https://github.com/riccardol540-cloud/Inland-Opportunities.git`

---

## 1. Create a GitHub token (for the dashboard's write-back)

The dashboard saves edits by committing `data/opportunities.json` back to the repo, so it
needs a token with write access.

1. GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token.
2. Repository access: **Only select repositories** → `Inland-Opportunities`.
3. Permissions → Repository permissions → **Contents: Read and write**.
4. Generate and copy the token (starts with `github_pat_...`). Keep it secret.

## 2. Push the code to GitHub

From inside the `Inland-Opportunities/` folder:

```bash
git remote add origin https://github.com/riccardol540-cloud/Inland-Opportunities.git
git branch -M main
git push -u origin main
```

(The folder is already a git repo with an initial commit. If `origin` already exists,
skip the first line.)

## 3. Deploy with the Vercel CLI

```bash
npm i -g vercel        # if not already installed
vercel login           # if not already logged in
vercel link            # link this folder to a new Vercel project (accept defaults)
```

## 4. Set the environment variables

Generate a random secret for the session cookie:

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Then add all five (paste the values when prompted; choose Production + Preview):

```bash
vercel env add DASHBOARD_PASSWORD     # inland2026
vercel env add AUTH_SECRET            # the random string from above
vercel env add GITHUB_TOKEN           # the github_pat_... from step 1
vercel env add GITHUB_REPO            # riccardol540-cloud/Inland-Opportunities
vercel env add GITHUB_BRANCH          # main
```

(You can also set these in the Vercel dashboard → Project → Settings → Environment
Variables — handy for pasting the token without it landing in shell history.)

## 5. Ship it

```bash
vercel --prod
```

Vercel prints the live URL. Open it, enter `inland2026`, and you'll see the board with
the one sample opportunity. Share the URL + password with collaborators.

---

## Notes

- **Auto-deploy**: once linked, you can also connect the GitHub repo in the Vercel
  dashboard so every `git push` (including the Scout's commits) redeploys automatically.
- **Security**: the password is checked server-side and the session is an HttpOnly,
  signed cookie — it can't be read or forged in the browser. The token lives only in
  Vercel's env, never in the client. Pages are marked `noindex`.
- **First real data**: delete the sample row from the dashboard (or let the first Scout
  run add real ones).
