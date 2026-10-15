# Validation Gap Analysis

## Purpose

Validation gap analysis identifies whether known production failure
patterns are covered by existing validation test cases.

In large-scale AI infrastructure, missing validation coverage can allow
small firmware or silicon issues to escape into production. This stage
answers one narrow question for each observed incident: does a
validation scenario cover this failure mode, on this firmware version,
in this workload phase?

## As implemented

Implementation: `ValidationGapAnalyzer` in
`app/services/validation_gap_analyzer.py`, exposed as
`GET /api/v1/validation/gaps`.

Inputs:

- Correlated events from `TelemetryCorrelator` (see
  `docs/telemetry_correlation.md`).
- Validation scenarios from `app/data/validation_matrix.json`, loaded
  into the `ValidationScenario` schema (`scenario_id`, `failure_mode`,
  `firmware_versions`, `workload_phases`, `environmental_conditions`,
  `coverage_level`, `last_run`).

Rules (`ValidationGapAnalyzer.analyze`):

1. Scenarios are matched to an event by exact `failure_mode`.
2. If no scenario has that failure mode, a gap is emitted with reason
   "No validation scenario covers this failure mode."
3. Otherwise a scenario covers the event only when **all** of these hold:
   the event's firmware version is in the scenario's
   `firmware_versions` (or `*` is present), the event's workload phase
   is in the scenario's `workload_phases` (or `*` is present), and the
   scenario's `coverage_level` is not `"none"`.
4. If matching scenarios exist but none covers the event, a gap is
   emitted with reason "Existing validation does not cover this firmware
   and workload condition."
5. Gap priority is `high` when the incident severity is `ERROR` or
   `CRITICAL`, otherwise `medium`.

With the bundled sample data this produces 4 gaps; see
`examples/sample_outputs/validation_gaps.json`. For example:

- `hbm_ecc_escalation` on firmware `7.4.2` during `kv-cache-spill`
  (the only HBM scenario, `VAL-HBM-001`, covers firmware `7.4.1` in
  `training-checkpoint` / `synthetic-memory-scrub` only)
- `fabric_crc_burst` on firmware `7.5.0-rc2` during
  `allreduce-gradient-sync` (no scenario covers this failure mode)
- `thermal_throttle_boundary` on firmware `7.4.2` during
  `sustained-inference` (the thermal scenario covers
  `synthetic-power-virus` only)

By contrast, the PCIe replay incident is covered: `VAL-PCIE-002` covers
`pcie_link_instability` on firmware `7.4.1`/`7.4.2` during
`host-dma-burst` with `coverage_level` `full`, so no gap is emitted.

## Output

Each gap is a `ValidationGap`:

- gap id and the incident id it came from
- failure mode and reason
- missing conditions (`firmware=…`, `workload_phase=…`,
  `failure_mode=…`)
- suggested validation (currently the same fixed text for every gap:
  "Add accelerated stress coverage that replays the observed telemetry
  envelope with firmware instrumentation enabled.")
- priority (`high` / `medium`)

## Not implemented

The following are design context, not shipped behavior:

- Extracting risks from silicon errata notes or free-text validation
  reports — there is no errata input; the comparison is
  structured-scenario vs. correlated-event only. The classic example
  from the original brief ("warm reset under high temperature" missing
  from a validation report) describes the intent, not an implemented
  text analysis.
- Checking environmental conditions (`environmental_conditions` are
  loaded but not compared) or specific test steps such as warm reset
  loops, cold boot, or S3/S4/S5 paths.
- Stale-test detection — scenario `last_run` dates are loaded but not
  used when deciding coverage.
- Per-gap tailored suggested test scenarios, a firmware workaround
  verification checklist, a validation readiness report, or a
  "production escape probability" — none of these are computed.
