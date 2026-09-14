#!/usr/bin/env python3
"""Export the site's access log from Cloudflare Analytics Engine as an nginx/Apache "combined" format file.

    CLOUDFLARE_API_TOKEN=... python3 scripts/access_log.py 2026-09-14 2026-10-14 > access.log

Dates are UTC, start inclusive, end exclusive. Rows come from the cielo_access_log dataset written by
functions/_middleware.js (page requests only; /media/* is not logged). The token needs Account · Account Analytics · Read.
Queried one day at a time; a day that hits the 10,000-row cap is reported on stderr so the gap is visible.
"""
import os, sys, json, datetime, urllib.request

ACCOUNT = "6e3c183d99afeaf8eaf6968f04ce8498"   # Marketing.team@cieloecommerce.com's Cloudflare account
DATASET = "cielo_access_log"
CAP = 10000

def query(sql, token):
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/analytics_engine/sql",
                                 data=sql.encode(), headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    token = os.environ.get("CLOUDFLARE_API_TOKEN") or sys.exit("set CLOUDFLARE_API_TOKEN")
    start, end = (datetime.date.fromisoformat(a) for a in sys.argv[1:3])
    total, day = 0, start
    while day < end:
        nxt = day + datetime.timedelta(days=1)
        sql = (f"SELECT timestamp, blob1, blob2, blob3, blob4, blob5, blob6, double1, double2, _sample_interval "
               f"FROM {DATASET} WHERE timestamp >= toDateTime('{day} 00:00:00') AND timestamp < toDateTime('{nxt} 00:00:00') "
               f"ORDER BY timestamp LIMIT {CAP}")
        rows = query(sql, token).get("data", [])
        if len(rows) >= CAP: print(f"warning: {day} hit the {CAP}-row cap, rows are missing for that day", file=sys.stderr)
        for r in rows:
            ts = datetime.datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S").strftime("%d/%b/%Y:%H:%M:%S +0000")
            b = int(r["double2"]); size = "-" if b < 0 else str(b)
            line = (f'{r["blob1"]} - - [{ts}] "{r["blob2"]} {r["blob3"]} {r["blob4"]}" {int(r["double1"])} {size} '
                    f'"{r["blob5"]}" "{r["blob6"]}"')
            print(line)  # _sample_interval is 1 at this traffic; if it ever exceeds 1, one line stands for that many hits
            total += 1
        print(f"{day}: {len(rows)} rows", file=sys.stderr)
        day = nxt
    print(f"total: {total} lines", file=sys.stderr)

if __name__ == "__main__": main()
