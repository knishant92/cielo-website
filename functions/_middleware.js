// Cloudflare Pages middleware: writes one row per page request to Analytics Engine (binding LOGS, dataset cielo_access_log),
// the fields an nginx/Apache "combined" access log carries. scripts/access_log.py turns the rows back into a log file.
// /media/* is excluded in site/_routes.json (written by design/build_site.py), so images and video never pass through here.
// If the LOGS binding is missing (local dev, or not yet added in the Pages project settings) the request is served and nothing is logged.

export async function onRequest(context) {
  const { request, env, next } = context;
  const response = await next();
  try {
    if (env.LOGS) {
      const u = new URL(request.url);
      const h = request.headers;
      const len = response.headers.get("content-length");
      env.LOGS.writeDataPoint({
        indexes: [u.pathname.slice(0, 96)],
        blobs: [
          h.get("cf-connecting-ip") || "-",             // blob1 remote host
          request.method,                               // blob2
          u.pathname + u.search,                        // blob3 request target
          request.cf?.httpProtocol || "HTTP/1.1",       // blob4
          h.get("referer") || "-",                      // blob5
          h.get("user-agent") || "-",                   // blob6
          request.cf?.country || "-",                   // blob7 (extra: not in combined format)
          u.host,                                       // blob8
        ],
        doubles: [response.status, len === null ? -1 : Number(len)], // double1 status, double2 bytes (-1 = unknown)
      });
    }
  } catch (e) { console.error("access log write failed", String(e)); }
  return response;
}
