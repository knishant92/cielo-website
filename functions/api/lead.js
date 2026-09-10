// Cloudflare Pages Function: POST /api/lead
// Forwards the pilot form to LEAD_WEBHOOK (a Google Apps Script web app that writes a Sheet row and emails the team).
// If LEAD_WEBHOOK is not configured, the lead is logged to the Pages function log and a success is still returned,
// so the visitor never sees an error. Configure LEAD_WEBHOOK in the Pages project: Settings → Variables and Secrets.

export async function onRequestPost({ request, env }) {
  const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
  let data;
  try { data = await request.json(); } catch { return json({ ok: false, error: "bad json" }, 400); }
  if (data.website) return json({ ok: true, spam: true }); // honeypot filled by a bot: pretend success, drop it
  const clean = (v, n = 500) => (typeof v === "string" ? v.trim().slice(0, n) : "");
  const lead = {
    ts: new Date().toISOString(),
    pilot: clean(data.pilot, 60), name: clean(data.name, 120), brand: clean(data.brand, 120),
    email: clean(data.email, 200), phone: clean(data.phone, 40),
    channels: Array.isArray(data.channels) ? data.channels.map((c) => clean(c, 40)).join(", ") : clean(data.channels, 200),
    skus: clean(data.skus, 40), category: clean(data.category, 120), notes: clean(data.notes, 2000),
    page: clean(data.page, 300), ip: request.headers.get("cf-connecting-ip") || "", country: request.cf?.country || "",
  };
  if (!lead.name || !lead.brand || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(lead.email)) return json({ ok: false, error: "missing fields" }, 422);
  if (env.LEAD_WEBHOOK) {
    try {
      const r = await fetch(env.LEAD_WEBHOOK, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(lead), redirect: "follow" });
      if (!r.ok) { console.error("lead webhook failed", r.status, JSON.stringify(lead)); return json({ ok: true, stored: false }); }
    } catch (e) { console.error("lead webhook error", String(e), JSON.stringify(lead)); return json({ ok: true, stored: false }); }
    return json({ ok: true, stored: true });
  }
  console.log("LEAD (no webhook configured)", JSON.stringify(lead));
  return json({ ok: true, stored: false });
}

export function onRequestGet() { return new Response("POST only", { status: 405 }); }
