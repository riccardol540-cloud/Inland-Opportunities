#!/usr/bin/env node
// Tiny GitHub-API helper so routines (Scout/Producer) read & write the LIVE repo
// (origin/main) directly — never the local clone, which may be diverged.
//
// Usage:
//   node scripts/inland-repo.mjs get  <repoPath>                       # prints file -> stdout
//   node scripts/inland-repo.mjs put  <repoPath> <localFile> "<msg>"   # commits localFile -> repoPath
//
// Reads GITHUB_TOKEN, GITHUB_REPO, GITHUB_BRANCH from process.env or a gitignored
// .env file in the repo root.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function loadEnv() {
  const f = path.join(ROOT, ".env");
  if (fs.existsSync(f)) {
    for (const line of fs.readFileSync(f, "utf8").split("\n")) {
      const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*)\s*$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
}
loadEnv();

const REPO = process.env.GITHUB_REPO;
const BRANCH = process.env.GITHUB_BRANCH || "main";
const TOKEN = process.env.GITHUB_TOKEN;
if (!REPO || !TOKEN) {
  console.error("Missing GITHUB_REPO or GITHUB_TOKEN (set them in .env or the environment).");
  process.exit(2);
}

const headers = {
  Authorization: `Bearer ${TOKEN}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": "inland-scout",
};

async function getFile(repoPath) {
  const url = `https://api.github.com/repos/${REPO}/contents/${encodeURIComponent(repoPath)}?ref=${BRANCH}`;
  const r = await fetch(url, { headers, cache: "no-store" });
  if (r.status === 404) return { content: null, sha: null };
  if (!r.ok) throw new Error(`GET ${repoPath} failed: ${r.status} ${await r.text()}`);
  const j = await r.json();
  return { content: Buffer.from(j.content, "base64").toString("utf8"), sha: j.sha };
}

async function putFile(repoPath, localFile, message) {
  const body = fs.readFileSync(localFile);
  const { sha } = await getFile(repoPath);
  const url = `https://api.github.com/repos/${REPO}/contents/${encodeURIComponent(repoPath)}`;
  const payload = {
    message: message || `Update ${repoPath}`,
    content: Buffer.from(body).toString("base64"),
    branch: BRANCH,
  };
  if (sha) payload.sha = sha;
  const r = await fetch(url, { method: "PUT", headers, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error(`PUT ${repoPath} failed: ${r.status} ${await r.text()}`);
  const j = await r.json();
  return j.commit && j.commit.sha;
}

const [cmd, a, b, c] = process.argv.slice(2);
try {
  if (cmd === "get") {
    const { content } = await getFile(a);
    if (content === null) { console.error(`(not found: ${a})`); process.exit(1); }
    process.stdout.write(content);
  } else if (cmd === "put") {
    const sha = await putFile(a, b, c);
    console.error(`committed ${a} -> ${sha}`);
  } else {
    console.error("Usage: inland-repo.mjs get <path> | put <path> <localFile> \"<msg>\"");
    process.exit(2);
  }
} catch (e) {
  console.error(String(e.message || e));
  process.exit(1);
}
