// Cloudflare Pages Function: POST /api/subscribe
// Newsletter sign-up from the band above the footer. Reuses LEAD_WEBHOOK (the same Apps Script + Sheet as the pilot form):
// the row lands with pilot = "Newsletter" and only the email filled, so the team can filter it in the Sheet.
// Without LEAD_WEBHOOK the sign-up is logged and a success is still returned.

export async function onRequestPost({ request, env }) {
  const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });
  let data;
  try { data = await request.json(); } catch { return json({ ok: false, error: "bad json" }, 400); }
  if (data.website) return json({ ok: true, spam: true }); // honeypot
  const clean = (v, n = 300) => (typeof v === "string" ? v.trim().slice(0, n) : "");
  const email = clean(data.email, 200);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json({ ok: false, error: "bad email" }, 422);
  const lead = {
    ts: new Date().toISOString(), pilot: "Newsletter", name: "", brand: "", email, phone: "", channels: "", skus: "", category: "",
    notes: "Newsletter sign-up", page: clean(data.page, 300), ip: request.headers.get("cf-connecting-ip") || "", country: request.cf?.country || "",
    type: "Subscriber",
  };
  if (env.LEAD_WEBHOOK) {
    try {
      const r = await fetch(env.LEAD_WEBHOOK, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(lead), redirect: "follow" });
      if (!r.ok) { console.error("subscribe webhook failed", r.status, JSON.stringify(lead)); return json({ ok: true, stored: false }); }
    } catch (e) { console.error("subscribe webhook error", String(e), JSON.stringify(lead)); return json({ ok: true, stored: false }); }
    return json({ ok: true, stored: true });
  }
  console.log("SUBSCRIBE (no webhook configured)", JSON.stringify(lead));
  return json({ ok: true, stored: false });
}

export function onRequestGet() { return new Response("POST only", { status: 405 }); }
