# Telemetry Correlation

## Purpose

Telemetry correlation is the process of connecting fragmented
infrastructure signals across firmware, BMC, OS, accelerator, power, and
thermal layers.

In AI accelerator systems, a single failure may not be visible from one
log source. The goal of this stage is to bind each significant log event
to the platform state observed around it, so an engineer gets one
incident record instead of scattered fragments.

## As implemented

Implementation: `LogParser` and `TelemetryCorrelator` in
`app/services/log_parser.py` and `app/services/telemetry_correlator.py`,
exposed as `GET /api/v1/telemetry/correlated`.

Inputs (both are bundled sample files, loaded by `DataRepository`):

- `app/data/accelerator_logs.log` — structured log lines with timestamp,
  severity, accelerator, rack, firmware version, subsystem, event code,
  and a quoted message, plus trailing key-value metadata.
- `app/data/telemetry_samples.json` — normalized telemetry samples
  (`TelemetrySample` in `app/models/schemas.py`).

Correlation rules (`TelemetryCorrelator.correlate`):

1. Only log events with severity `WARNING`, `ERROR`, or `CRITICAL` are
   correlated; `INFO` events are skipped.
2. For each event, candidate telemetry samples are those with the same
   `accelerator_id` and — when the log line carries one — the same
   `firmware_version`.
3. The chosen sample is the candidate nearest in time to the log event
   (absolute timestamp difference).
4. Metrics from that sample are flagged against fixed thresholds
   (`METRIC_THRESHOLDS` in `telemetry_correlator.py`): temperature
   ≥ 88 °C, uncorrected HBM ECC > 0, PCIe replays ≥ 1000,
   power ≥ 650 W, fabric CRC errors > 0, inference latency ≥ 45 ms.
   Only non-nominal metrics are attached to the incident.
5. The failure mode is classified deterministically from the event code
   and flagged metrics, in this priority order: HBM ECC escalation,
   PCIe link instability, thermal throttle boundary, fabric CRC burst,
   power transient overshoot, otherwise
   `unknown_platform_degradation`.
6. Confidence is `0.45` when no metric is anomalous, otherwise
   `min(0.95, 0.65 + 0.1 × number of anomalous metrics)`.

With the bundled sample data this produces 6 correlated events
(`INC-0001` … `INC-0006`); see
`examples/sample_outputs/correlated_telemetry_events.json`.

## Output

Each correlated event is a `CorrelatedEvent`:

- incident id, timestamp, accelerator / rack / firmware version
- event code, subsystem, severity
- workload id and phase (from the matched telemetry sample, if any)
- summary (`"<event_code>: <message>"`)
- correlated metrics (name, value, threshold, status)
- likely failure mode and confidence (0–1)

## Not implemented

The following are design context, not shipped behavior:

- Live collection from BIOS/BMC logs, Redfish, IPMI sensor readings, or
  PCIe / CXL / NVLink event streams — the only inputs are the two bundled
  sample files above.
- Correlation by subsystem relationship, repeated-pattern detection, or
  time windows — matching is same-accelerator/firmware plus nearest
  timestamp only.
- Validation reports or Jira / issue history as inputs, and "similar
  historical issues" in the output.
- Risk scoring at this stage — risk scores are produced by a separate
  service (`RiskScorer`) in the `POST /api/v1/analyze` pipeline, not by
  the correlator.
