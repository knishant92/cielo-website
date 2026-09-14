// Cloudflare Pages middleware: writes one row per page request to Analytics Engine (binding LOGS, dataset cielo_access_log),
// the fields an nginx/Apache "combined" access log carries. scripts/access_log.py turns the rows back into a log file.
// /media/* is excluded in site/_routes.json (written by design/build_site.py), so images and video never pass through here.
// If the LOGS binding is missing (local dev, or not yet added in the Pages project settings) the request is served and nothing is logged.

export async function onRequest(context) {
  const { request, env, next } = context;
  const response = await next();
  if (!env.LOGS) return response;
  const u = new URL(request.url);
  const h = request.headers;
  const row = {
    ip: h.get("cf-connecting-ip") || "-", method: request.method, target: u.pathname + u.search,
    proto: request.cf?.httpProtocol || "HTTP/1.1", referer: h.get("referer") || "-", ua: h.get("user-agent") || "-",
    country: request.cf?.country || "-", host: u.host, status: response.status,
  };
  // Pages sends no content-length, so measure a clone of the body after the response has gone out (waitUntil keeps the worker alive).
  const copy = response.clone();
  context.waitUntil((async () => {
    let bytes = -1;
    try { bytes = (await copy.arrayBuffer()).byteLength; } catch (e) {}
    try {
      env.LOGS.writeDataPoint({
        indexes: [u.pathname.slice(0, 96)],
        blobs: [row.ip, row.method, row.target, row.proto, row.referer, row.ua, row.country, row.host], // blob1..blob8
        doubles: [row.status, bytes], // double1 status, double2 bytes (-1 = unknown)
      });
    } catch (e) { console.error("access log write failed", String(e)); }
  })());
  return response;
}
