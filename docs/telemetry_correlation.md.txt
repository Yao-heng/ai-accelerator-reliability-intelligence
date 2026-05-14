# Telemetry Correlation

## Purpose

Telemetry correlation is the process of connecting fragmented infrastructure signals across firmware, BMC, OS, accelerator, power, thermal, and validation layers.

In AI accelerator systems, a single failure may not be visible from one log source. The goal is to correlate multiple signals and identify meaningful reliability patterns.

## Input Sources

- BIOS logs
- BMC SEL logs
- Redfish telemetry
- IPMI sensor readings
- Accelerator health logs
- PCIe / CXL / NVLink events
- Thermal and power telemetry
- Validation reports
- Jira / issue history

## Example Correlation Scenario

```text
GPU/TPU thermal warning
        ↓
Power rail fluctuation
        ↓
PCIe retraining event
        ↓
BMC SEL event
        ↓
Application timeout


AI-Native Workflow

flowchart TD
A[Raw Telemetry Sources] --> B[Normalize Logs]
B --> C[Timestamp Alignment]
C --> D[Cross-Layer Correlation]
D --> E[Pattern Detection]
E --> F[Root Cause Candidates]
F --> G[Recommended Validation / Mitigation]



Expected Output
Correlated event timeline
Possible root cause candidates
Similar historical issues
Risk score
Suggested validation test
Recommended owner or subsystem