import { checkPassword, issueCookie, clearCookie, isAuthed, readBody } from "./_lib.js";

export default async function handler(req, res) {
  if (req.method === "GET") {
    return res.status(200).json({ authed: isAuthed(req) });
  }
  if (req.method === "DELETE") {
    res.setHeader("Set-Cookie", clearCookie());
    return res.status(200).json({ authed: false });
  }
  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST, DELETE");
    return res.status(405).json({ error: "Method not allowed" });
  }
  const body = await readBody(req);
  if (!checkPassword(body.password)) {
    return res.status(401).json({ error: "Incorrect password" });
  }
  res.setHeader("Set-Cookie", issueCookie());
  return res.status(200).json({ authed: true });
}
