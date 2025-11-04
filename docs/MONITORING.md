# Monitoring with Prometheus & Grafana

This repository includes a minimal monitoring compose file to run Prometheus and
Grafana for local exploration. It scrapes the backend `/metrics` endpoint that
the API exposes.

How to run
----------

From the repository root:

```bash
cd monitoring
docker compose up -d
```

Prometheus UI: http://localhost:9090
Grafana UI: http://localhost:3001 (admin/admin)

Notes
-----
- The Prometheus config uses `host.docker.internal:8000` as the default target.
  This works on Docker Desktop. If you run Prometheus in the same compose network
  as the API, change the target to `realdiag-software-api:8000` or add extra
  scrape_configs.
- Grafana is mapped to port 3001 to avoid colliding with the frontend.

Security
--------
This monitoring setup is intended for development and quick demos. Do not expose
Grafana or Prometheus to the public Internet without proper authentication and
network controls.
