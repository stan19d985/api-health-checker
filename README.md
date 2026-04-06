# Endpoint Health Monitor

Simple health checker for public government API endpoints and websites. Logs availability, response times, and status codes.

## What It Does

Pings 45+ public `.gov` endpoints and logs whether they're up, how fast they respond, and the response size. Useful for tracking government site availability over time.

## Monitored Categories

- Weather & environmental (weather.gov, airnow.gov, USGS)
- Data portals (data.gov, census.gov, BLS, FRED)
- Government services (usa.gov, IRS, USPS, SSA, SBA)
- Health & science (NIH, CDC, NASA, NSF)
- Legislative (congress.gov, Federal Register, regulations.gov)
- SearchGov endpoints (search.usa.gov across various agencies)

## Usage

```bash
python monitor.py
```

## Automated

Runs daily via GitHub Actions at 06:00 UTC. Logs committed to `logs/` directory.

## Output

```
  Endpoint                                 Status   Time        Size
  weather.gov                              200      342ms     48,291B
  data.gov                                 200      518ms     31,002B
  census.gov                               200      267ms     52,118B
  ...
```

## License

MIT
