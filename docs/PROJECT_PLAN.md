# Project Plan: AI Accelerator Reliability Intelligence Platform

> **Status note (2026-10-15):** This file began as the original planning
> brief for the prototype. It has been reconciled with the code that
> actually shipped, which is the FastAPI application under `app/`.
> Where the original brief and the implementation diverged, this document
> now follows the implementation. Directions that were considered in the
> original brief but **not** implemented are listed explicitly at the end.

## Goal

Build a lightweight prototype that demonstrates a cross-layer reliability
workflow for GPU/TPU-class systems: fuse platform logs and accelerator
telemetry into one timeline, detect anomalies deterministically, score
risk, expose validation coverage gaps and firmware blast radius, and emit
prioritized, evidence-backed recommendations.

This is not a production system. The goal is to demonstrate architecture
thinking and a working, tested prototype against bundled sample data.

## Tech Stack (as implemented)

- Python 3.11+ (CI runs Python 3.12)
- FastAPI + Uvicorn + Pydantic v2
- JSON / JSONL sample data under `app/data/`
- pytest + httpx (FastAPI `TestClient`) for tests
- GitHub Actions CI (`.github/workflows/ci.yml`)

No LangChain, vector store (Chroma / FAISS), or Streamlit UI is used.
Those were options in the original brief; none of them shipped — see
"Considered but not implemented" below.

## Folder Structure (as implemented)

```text
app/
  main.py                         # FastAPI application entrypoint
  api/routes.py                   # REST routes under /api/v1
  models/schemas.py               # Pydantic domain models
  services/                       # Analysis services (see below)
  data/                           # Bundled sample data
docs/                             # This plan and three design notes
examples/                         # Captured API responses and sample outputs
scripts/                          # Smoke test and example generator
src/intelligence_analyzer.py      # LEGACY / UNUSED early draft, kept for reference
tests/                            # test_api.py (8 tests), test_services.py (7 tests)
```

## Functional Requirements (as implemented)

1. **Log Parser** — `app/services/log_parser.py` (`LogParser`)
   Parses the structured lines of `app/data/accelerator_logs.log` and
   extracts timestamp, severity, accelerator, rack, firmware version,
   subsystem, event code, message, and trailing key-value metadata.
   Unstructured lines fall back to a `WARNING` /
   `UNSTRUCTURED_LOG_LINE` record. Returns `AcceleratorLogEntry` objects.

2. **Telemetry Correlator** — `app/services/telemetry_correlator.py`
   (`TelemetryCorrelator`)
   Correlates warning/error/critical log events with the nearest
   telemetry sample (from `app/data/telemetry_samples.json`) for the same
   accelerator and firmware version. See `docs/telemetry_correlation.md`.

3. **Validation Gap Analyzer** — `app/services/validation_gap_analyzer.py`
   (`ValidationGapAnalyzer`)
   Compares each correlated event's failure mode, firmware version, and
   workload phase against the scenarios in
   `app/data/validation_matrix.json` and flags uncovered combinations.
   See `docs/validation_gap_analysis.md`.

4. **Firmware Dependency Mapper** — `app/services/firmware_dependency_mapper.py`
   (`FirmwareDependencyMapper`)
   Builds dependency adjacency and blast-radius views from
   `app/data/firmware_dependencies.json`.
   See `docs/firmware_dependency_mapping.md`.

5. **Recommendation Engine** — `app/services/recommendation_engine.py`
   (`RecommendationEngine`), plus
   `app/services/infrastructure_advisor.py`
   (`InfrastructureReliabilityAdvisor`) for the `/analyze` pipeline.
   Generates prioritized recommendations from correlated events,
   validation gaps, dependency blast radius, anomalies, and risk scores.
   Recommendations use the `ReliabilityRecommendation` schema
   (`recommendation_id`, `priority`, `title`, `rationale`, `evidence`,
   `affected_components`, `expected_impact`, `next_steps`) — see the real
   captured examples under `examples/`.

6. **Telemetry analysis pipeline** — `app/services/analyzer.py`
   (`ReliabilityAnalyzer`), with `telemetry_ingestion.py`,
   `anomaly_detector.py`, and `risk_scoring.py`.
   Ingests a telemetry payload (or the bundled
   `app/data/gpu_telemetry_logs.jsonl` by default), detects
   threshold-based anomalies, scores risk 0–100 per accelerator/rack,
   and returns operations recommendations.

7. **FastAPI Backend** — `app/main.py`, routes in `app/api/routes.py`

   ```text
   GET  /health
   GET  /api/v1/logs/parsed
   GET  /api/v1/telemetry/correlated
   GET  /api/v1/validation/gaps
   GET  /api/v1/firmware/dependencies
   GET  /api/v1/recommendations
   POST /api/v1/analyze
   POST /analyze            (root alias of POST /api/v1/analyze)
   ```

   The original brief proposed `POST /analyze/logs`,
   `POST /analyze/telemetry`, `POST /analyze/validation-gap`,
   `POST /analyze/dependency-map`, and `POST /analyze/recommendation`.
   Those paths were never implemented; the endpoints above are the real
   API surface (verified against `app.routes`).

## Sample Data

All sample data is fictional and lives under `app/data/`:

- `accelerator_logs.log` — multi-layer firmware/OS log lines
- `telemetry_samples.json` — normalized telemetry samples
- `gpu_telemetry_logs.jsonl` — telemetry stream with vendor-style field
  aliases (`gpu_id`, `fw`, `temp_c`, …) that ingestion normalizes
- `validation_matrix.json` — release validation coverage scenarios
- `firmware_dependencies.json` — firmware integration manifest for the
  fictional "AIX-9000" platform

No proprietary company data is included.

## Success Criteria

The prototype is successful if a user can:

- Run the FastAPI service (`uvicorn app.main:app`).
- Query the bundled sample logs, telemetry, gaps, and dependencies.
- Submit telemetry to `POST /api/v1/analyze` (or use the bundled data
  with an empty body) and receive structured analysis: ingestion summary,
  anomalies, risk scores, and recommendations.
- Run `pytest` (15 tests) and `python scripts/run_analysis_smoke_test.py`
  successfully — both also run in CI.

## Considered but not implemented

These appeared in the original brief or are natural extensions; none of
them are in the code today, and the README lists them under Roadmap:

- LangChain / local retrieval over errata notes, Chroma / FAISS vector
  search (no RAG or LLM inference of any kind)
- Streamlit UI
- Live BMC / Redfish / IPMI / PLDM collectors
- Stale-test detection in the validation gap analyzer (scenario
  `last_run` dates are loaded but not used to flag gaps)
- Sample files named `sample_bios_log.txt`, `sample_bmc_sel.json`,
  `sample_telemetry.json`, `sample_errata.md`, or
  `sample_validation_report.md`, and a `tests/test_basic_workflow.py`
  file (the shipped equivalents are listed above)
