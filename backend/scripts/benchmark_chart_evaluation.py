"""
Baseline timing for SMART chart evaluation (fetch + parse + criteria evaluation).

Builds a synthetic chart, serves it through an in-process fake FHIR server
(paged at 100 results like Epic/Cerner), and times:
  - FHIR requests made (count, and pages followed)
  - parsing time inside FHIRClient.get_patient_data
  - SmartDiagnosticEngine.evaluate_encounter time

Network latency is NOT measured (no real EHR is contacted); pass
--latency-ms to add a fixed per-request delay and see its effect.

Usage:
    python backend/scripts/benchmark_chart_evaluation.py
    python backend/scripts/benchmark_chart_evaluation.py --profile heavy --latency-ms 150
"""

from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests  # noqa: E402

from backend.services import fhir_client as fhir  # noqa: E402
from backend.services.smart_diagnostic_engine import SmartDiagnosticEngine  # noqa: E402

PAGE = 100
PROFILES = {
    # labs over 2 years, vital-sign readings over 1 year
    "typical": {"lab_panels": 24, "vital_sets": 60},    # monthly labs, ~weekly vitals
    "heavy": {"lab_panels": 120, "vital_sets": 900},    # frequent labs, inpatient vitals q4-6h
}
LAB_CODES = [("2345-7", 110, "mg/dL"), ("2823-3", 4.4, "mmol/L"), ("2028-9", 24, "mmol/L"), ("6690-2", 7.5, "K/uL"),
             ("718-7", 13.5, "g/dL"), ("4548-4", 6.1, "%"), ("33914-3", 72, "mL/min/1.73m2"),
             ("13457-7", 130, "mg/dL"), ("3016-3", 2.1, "mIU/L"), ("1558-6", 104, "mg/dL")]


def _obs(code, value, unit, when, category):
    return {"resourceType": "Observation", "status": "final",
            "category": [{"coding": [{"code": category}]}],
            "code": {"coding": [{"system": "http://loinc.org", "code": code}]},
            "valueQuantity": {"value": value, "unit": unit},
            "effectiveDateTime": when.isoformat().replace("+00:00", "Z")}


def build_chart(profile: str, seed: int = 7):
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    cfg = PROFILES[profile]
    labs, vitals = [], []
    for i in range(cfg["lab_panels"]):
        when = now - timedelta(days=730 * i / cfg["lab_panels"])
        for code, base, unit in LAB_CODES:
            labs.append(_obs(code, round(base * rng.uniform(0.9, 1.1), 2), unit, when, "laboratory"))
    for i in range(cfg["vital_sets"]):
        when = now - timedelta(days=365 * i / cfg["vital_sets"])
        vitals.append({"resourceType": "Observation", "status": "final",
                       "category": [{"coding": [{"code": "vital-signs"}]}],
                       "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9"}]},
                       "effectiveDateTime": when.isoformat().replace("+00:00", "Z"),
                       "component": [
                           {"code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
                            "valueQuantity": {"value": rng.randint(110, 145), "unit": "mm[Hg]"}},
                           {"code": {"coding": [{"system": "http://loinc.org", "code": "8462-4"}]},
                            "valueQuantity": {"value": rng.randint(65, 92), "unit": "mm[Hg]"}}]})
        for code, base, unit in (("8867-4", 80, "/min"), ("9279-1", 16, "/min"), ("8310-5", 36.8, "Cel")):
            vitals.append(_obs(code, round(base * rng.uniform(0.9, 1.15), 1), unit, when, "vital-signs"))
    return labs, vitals


class FakeFHIR:
    """Answers FHIRClient's requests from an in-memory chart, paging at 100."""

    def __init__(self, labs, vitals, latency_ms=0):
        self.labs, self.vitals, self.latency = labs, vitals, latency_ms / 1000
        self.requests = 0

    def _filter(self, params):
        pool = self.labs + self.vitals
        if params.get("category"):
            wanted = params["category"]
            pool = [o for o in pool if o["category"][0]["coding"][0]["code"] == wanted]
        if params.get("code"):
            codes = {c.split("|")[-1] for c in params["code"].split(",")}
            pool = [o for o in pool if o["code"]["coding"][0]["code"] in codes
                    or any(c["code"]["coding"][0]["code"] in codes for c in o.get("component", []))]
        if params.get("date"):
            since = datetime.fromisoformat(params["date"][2:]).replace(tzinfo=timezone.utc)
            pool = [o for o in pool if datetime.fromisoformat(o["effectiveDateTime"].replace("Z", "+00:00")) >= since]
        return pool

    def bundle(self, params, offset=0):
        matches = self._filter(params)
        page = matches[offset:offset + PAGE]
        links = []
        if offset + PAGE < len(matches):
            query = "&".join(f"{k}={v}" for k, v in params.items() if k != "_offset")
            links.append({"relation": "next", "url": f"https://fake.fhir/Observation?{query}&_offset={offset + PAGE}"})
        return {"resourceType": "Bundle", "entry": [{"resource": o} for o in page], "link": links}

    def get(self, url, params=None, headers=None):
        self.requests += 1
        if self.latency:
            time.sleep(self.latency)
        parsed = urlparse(url)
        if "_offset" in url:
            q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            offset = int(q.pop("_offset"))
            body = self.bundle(q, offset)
        elif parsed.path.endswith("/Observation"):
            body = self.bundle({k: str(v) for k, v in (params or {}).items()})
        elif "/Patient/" in parsed.path:
            body = {"name": [{"family": "Bench"}], "birthDate": "1960-01-01", "gender": "female"}
        else:
            body = {"resourceType": "Bundle", "entry": []}
        return SimpleNamespace(ok=True, status_code=200, json=lambda b=body: b, raise_for_status=lambda: None,
                               text="")


def run(profile: str, runs: int, latency_ms: int):
    labs, vitals = build_chart(profile)
    engine = SmartDiagnosticEngine()
    needs = engine.observation_requirements()
    fetch_times, eval_times, request_counts = [], [], []
    real_get = requests.get
    try:
        for _ in range(runs):
            fake = FakeFHIR(labs, vitals, latency_ms)
            requests.get = fake.get
            client = fhir.FHIRClient("https://fake.fhir", "bench", access_token="t")
            t0 = time.perf_counter()
            data = client.get_patient_data("p", observation_requirements=needs)
            t1 = time.perf_counter()
            engine.evaluate_encounter(data)
            t2 = time.perf_counter()
            fetch_times.append(t1 - t0)
            eval_times.append(t2 - t1)
            request_counts.append(fake.requests)
    finally:
        requests.get = real_get

    def ms(xs):
        return f"median {statistics.median(xs) * 1000:.1f} ms (min {min(xs) * 1000:.1f}, max {max(xs) * 1000:.1f})"

    print(f"Profile '{profile}': {len(labs)} lab results over 2 years, {len(vitals)} vital-sign observations over 1 year")
    print(f"  Criteria lookback: labs {needs['labs']['lookback_days']} days ({len(needs['labs']['codes'])} codes), "
          f"vitals {needs['vitals']['lookback_days']} days ({len(needs['vitals']['codes'])} codes)")
    print(f"  Results loaded: {len(data.labs)} labs, {len(data.vitals)} vital readings")
    print(f"  FHIR requests per evaluation: {request_counts[0]}")
    label = "fetch + parse" + (f" (incl. {latency_ms} ms simulated latency/request)" if latency_ms else " (no network)")
    print(f"  {label}: {ms(fetch_times)}")
    print(f"  criteria evaluation ({len(engine.trees)} trees): {ms(eval_times)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=sorted(PROFILES), default=None)
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--latency-ms", type=int, default=0)
    args = ap.parse_args()
    t = time.perf_counter()
    SmartDiagnosticEngine()
    print(f"Engine start-up (load criteria from trees): {(time.perf_counter() - t) * 1000:.0f} ms")
    for profile in ([args.profile] if args.profile else sorted(PROFILES, reverse=True)):
        run(profile, args.runs, args.latency_ms)
