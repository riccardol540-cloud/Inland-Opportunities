// Shared helpers for the INLAND Opportunities dashboard API.
// No external dependencies — uses Node's built-in crypto and global fetch.
import crypto from "node:crypto";

const COOKIE_NAME = "inland_auth";
const SESSION_HOURS = 12;

function secret() {
  // AUTH_SECRET signs the session cookie. Falls back to the password so the
  // app still works if only DASHBOARD_PASSWORD is set, but set AUTH_SECRET too.
  return process.env.AUTH_SECRET || process.env.DASHBOARD_PASSWORD || "inland-dev-secret";
}

function sign(value) {
  return crypto.createHmac("sha256", secret()).update(value).digest("base64url");
}

// ---- session cookie ----------------------------------------------------------
export function issueCookie() {
  const exp = Date.now() + SESSION_HOURS * 3600 * 1000;
  const payload = `v1.${exp}`;
  const token = `${payload}.${sign(payload)}`;
  const maxAge = SESSION_HOURS * 3600;
  return `${COOKIE_NAME}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}

export function clearCookie() {
  return `${COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

export function isAuthed(req) {
  const raw = req.headers.cookie || "";
  const match = raw.split(/;\s*/).find((c) => c.startsWith(`${COOKIE_NAME}=`));
  if (!match) return false;
  const token = match.slice(COOKIE_NAME.length + 1);
  const parts = token.split(".");
  if (parts.length !== 3) return false;
  const [v, exp, mac] = parts;
  const payload = `${v}.${exp}`;
  if (sign(payload) !== mac) return false;
  if (Number(exp) < Date.now()) return false;
  return true;
}

export function checkPassword(input) {
  const expected = process.env.DASHBOARD_PASSWORD || "";
  if (!expected || typeof input !== "string") return false;
  // constant-time compare
  const a = Buffer.from(input);
  const b = Buffer.from(expected);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

// ---- GitHub as database ------------------------------------------------------
function ghConfig() {
  const repo = process.env.GITHUB_REPO; // e.g. "riccardol540-cloud/Inland-Opportunities"
  const branch = process.env.GITHUB_BRANCH || "main";
  const token = process.env.GITHUB_TOKEN;
  const path = process.env.DATA_PATH || "data/opportunities.json";
  if (!repo || !token) throw new Error("Missing GITHUB_REPO or GITHUB_TOKEN env var");
  return { repo, branch, token, path };
}

function ghHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "inland-opportunities-dashboard",
  };
}

// Returns { data, sha } where data is the parsed JSON document.
export async function readData() {
  const { repo, branch, token, path } = ghConfig();
  const url = `https://api.github.com/repos/${repo}/contents/${encodeURIComponent(path)}?ref=${branch}`;
  const res = await fetch(url, { headers: ghHeaders(token), cache: "no-store" });
  if (res.status === 404) {
    return { data: { meta: { schemaVersion: 1, lastUpdated: null }, opportunities: [] }, sha: null };
  }
  if (!res.ok) throw new Error(`GitHub read failed: ${res.status} ${await res.text()}`);
  const json = await res.json();
  const content = Buffer.from(json.content, "base64").toString("utf8");
  return { data: JSON.parse(content), sha: json.sha };
}

// Commits the updated document back to the repo. Pass the sha from readData().
export async function writeData(data, sha, message) {
  const { repo, branch, token, path } = ghConfig();
  data.meta = data.meta || {};
  data.meta.lastUpdated = new Date().toISOString();
  const url = `https://api.github.com/repos/${repo}/contents/${encodeURIComponent(path)}`;
  const body = {
    message: message || "Update opportunities via dashboard",
    content: Buffer.from(JSON.stringify(data, null, 2) + "\n", "utf8").toString("base64"),
    branch,
  };
  if (sha) body.sha = sha;
  const res = await fetch(url, { method: "PUT", headers: ghHeaders(token), body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`GitHub write failed: ${res.status} ${await res.text()}`);
  return res.json();
}

export function readBody(req) {
  if (req.body && typeof req.body === "object") return Promise.resolve(req.body);
  return new Promise((resolve) => {
    let raw = "";
    req.on("data", (c) => (raw += c));
    req.on("end", () => {
      try { resolve(raw ? JSON.parse(raw) : {}); } catch { resolve({}); }
    });
  });
}
