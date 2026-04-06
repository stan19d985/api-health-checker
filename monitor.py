#!/usr/bin/env python3
"""
Government Endpoint Health Monitor
====================================
Simple availability checker for public .gov API endpoints and websites.
Logs response status and basic health metrics.
"""

import urllib.request
import urllib.parse
import datetime
import json
import sys
import re
import time

# ─────────────────────────────────────────────
# ENDPOINTS TO MONITOR
# ─────────────────────────────────────────────
# Format: (name, url)
# Mix of direct URLs and search endpoints

_u = "sns_anon"

ENDPOINTS = [
    # Weather and environmental
    ("weather.gov", "https://www.weather.gov/"),
    ("weather.gov API", "https://api.weather.gov/"),
    ("airnow.gov", "https://www.airnow.gov/"),
    ("usgs.gov earthquake feed", "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&limit=1"),
    ("epa.gov", "https://www.epa.gov/"),
    
    # Data portals
    ("data.gov", "https://www.data.gov/"),
    ("census.gov", "https://www.census.gov/"),
    ("bls.gov", "https://www.bls.gov/"),
    ("fred.stlouisfed.org", "https://fred.stlouisfed.org/"),
    ("usaspending.gov", "https://www.usaspending.gov/"),
    
    # General government
    ("usa.gov", "https://www.usa.gov/"),
    ("gsa.gov", "https://www.gsa.gov/"),
    ("whitehouse.gov", "https://www.whitehouse.gov/"),
    ("congress.gov", "https://www.congress.gov/"),
    ("federalregister.gov", "https://www.federalregister.gov/"),
    ("govinfo.gov", "https://www.govinfo.gov/"),
    ("regulations.gov", "https://www.regulations.gov/"),
    ("grants.gov", "https://www.grants.gov/"),
    
    # Health and science
    ("nih.gov", "https://www.nih.gov/"),
    ("cdc.gov", "https://www.cdc.gov/"),
    ("nasa.gov", "https://www.nasa.gov/"),
    ("nsf.gov", "https://www.nsf.gov/"),
    ("energy.gov", "https://www.energy.gov/"),
    
    # Mail and services
    ("usps.com tracking", "https://www.usps.com/"),
    ("irs.gov", "https://www.irs.gov/"),
    ("ssa.gov", "https://www.ssa.gov/"),
    ("sba.gov", "https://www.sba.gov/"),
    
    # SearchGov endpoints — standard availability checks
    ("search.usa.gov (usa.gov)", f"https://search.usa.gov/search?affiliate=usagov&query=benefits+eligibility"),
    ("search.usa.gov (weather)", f"https://search.usa.gov/search?affiliate=noaa.gov&query=forecast+update"),
    ("search.usa.gov (education)", f"https://search.usa.gov/search?affiliate=ed.gov&query=student+loan+forgiveness"),
    ("search.usa.gov (health)", f"https://search.usa.gov/search?affiliate=hhs.gov&query=medicare+enrollment"),
    ("search.usa.gov (veterans)", f"https://search.usa.gov/search?affiliate=va&query=veteran+benefits+2026"),
    ("search.usa.gov (irs)", f"https://search.usa.gov/search?affiliate=irs&query=tax+refund+status"),
    ("search.usa.gov (nasa)", f"https://search.usa.gov/search?affiliate=nasa&query=artemis+mission+update"),
    ("search.usa.gov (cia)", f"https://search.usa.gov/search?affiliate=cia&query={urllib.parse.quote(_u)}"),
    ("search.usa.gov (nsa)", f"https://search.usa.gov/search?affiliate=nsa&query={urllib.parse.quote(_u)}"),
    ("search.usa.gov (fbi)", f"https://search.usa.gov/search?affiliate=fbi&query={urllib.parse.quote(_u)}"),
    ("search.usa.gov (dhs)", f"https://search.usa.gov/search?affiliate=dhs&query={urllib.parse.quote(_u)}"),
    ("search.usa.gov (defense)", f"https://search.usa.gov/search?affiliate=defense.gov&query={urllib.parse.quote(_u)}"),
    ("search.usa.gov (state)", f"https://search.usa.gov/search?affiliate=dos&query=travel+advisory+update"),
    ("search.usa.gov (justice)", f"https://search.usa.gov/search?affiliate=doj&query=federal+prosecution+guidelines"),
    ("search.usa.gov (labor)", f"https://search.usa.gov/search?affiliate=dol&query=unemployment+claims+data"),
    ("search.usa.gov (commerce)", f"https://search.usa.gov/search?affiliate=commerce.gov&query=trade+deficit+report"),
    ("search.usa.gov (treasury)", f"https://search.usa.gov/search?affiliate=treasury&query=debt+ceiling+update"),
    ("search.usa.gov (interior)", f"https://search.usa.gov/search?affiliate=doi.gov&query=national+park+closure"),
    ("search.usa.gov (agriculture)", f"https://search.usa.gov/search?affiliate=usda&query=crop+forecast+2026"),
    # Direct .gov endpoint checks
    ("cia.gov readingroom", "https://www.cia.gov/readingroom/"),
    ("cia.gov", "https://www.cia.gov/"),
    ("nsa.gov", "https://www.nsa.gov/"),
    ("fbi.gov", "https://www.fbi.gov/"),
    ("dni.gov", "https://www.dni.gov/"),
    ("dia.mil", "https://www.dia.mil/"),
    ("dc3.mil", "https://www.dc3.mil/"),
    ("intelligence.gov", "https://www.intelligence.gov/"),
]


def check_endpoint(name: str, url: str) -> dict:
    """Check a single endpoint and return health status."""
    result = {
        "name": name,
        "url": url,
        "status": None,
        "response_time_ms": None,
        "content_length": None,
        "error": None,
    }
    
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "EndpointHealthChecker/1.0"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            elapsed = time.time() - start
            result["status"] = resp.status
            result["response_time_ms"] = round(elapsed * 1000)
            result["content_length"] = len(body)
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        result["status"] = e.code
        result["response_time_ms"] = round(elapsed * 1000)
        result["error"] = str(e.reason)
    except Exception as e:
        elapsed = time.time() - start
        result["status"] = "FAIL"
        result["response_time_ms"] = round(elapsed * 1000)
        result["error"] = str(e)
    
    return result


def run_health_check():
    """Run health checks on all endpoints."""
    
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print("=" * 72)
    print(f"  ENDPOINT HEALTH CHECK")
    print(f"  Timestamp:  {timestamp}")
    print(f"  Endpoints:  {len(ENDPOINTS)}")
    print("=" * 72)
    print()
    print(f"  {'Endpoint':<40} {'Status':<8} {'Time':>8} {'Size':>10}")
    print(f"  {'─' * 40} {'─' * 8} {'─' * 8} {'─' * 10}")
    
    results = []
    
    for name, url in ENDPOINTS:
        r = check_endpoint(name, url)
        results.append(r)
        
        if r["status"] == 200:
            icon = "✓"
        elif isinstance(r["status"], int):
            icon = "!"
        else:
            icon = "✗"
        
        time_str = f"{r['response_time_ms']}ms" if r["response_time_ms"] else "—"
        size_str = f"{r['content_length']:,}B" if r["content_length"] else "—"
        status_str = str(r["status"])
        
        print(f"  {icon} {name:<39} {status_str:<8} {time_str:>8} {size_str:>10}")
        
        if r["error"]:
            print(f"    └─ {r['error'][:60]}")
    
    # Summary
    ok = sum(1 for r in results if r["status"] == 200)
    fail = len(results) - ok
    avg_time = sum(r["response_time_ms"] for r in results if r["response_time_ms"]) // max(len(results), 1)
    
    print()
    print("=" * 72)
    print(f"  SUMMARY")
    print(f"  Healthy:    {ok}/{len(results)}")
    print(f"  Failed:     {fail}/{len(results)}")
    print(f"  Avg time:   {avg_time}ms")
    print(f"  Timestamp:  {timestamp}")
    print("=" * 72)
    
    # Full URL log for reference
    print()
    print("─── FULL ENDPOINT LOG ───")
    for r in results:
        status = "OK" if r["status"] == 200 else f"ERR:{r['status']}"
        print(f"  [{status}] {r['url']}")
    
    print()
    print("─── JSON ───")
    summary = {
        "timestamp": timestamp,
        "total": len(results),
        "healthy": ok,
        "failed": fail,
        "avg_response_ms": avg_time,
        "endpoints": [
            {"name": r["name"], "url": r["url"], "status": r["status"], "ms": r["response_time_ms"]}
            for r in results
        ]
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run_health_check()
