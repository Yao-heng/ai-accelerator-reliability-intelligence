
---

## PROJECT_PLAN.md 給 Codex 用

```markdown
# Project Plan: AI Accelerator Reliability Intelligence Platform

## Goal

Build a lightweight MVP that demonstrates an AI-native infrastructure reliability workflow for GPU/TPU-class systems.

The MVP should ingest sample firmware logs, telemetry data, errata notes, and validation reports, then generate:

- correlated event timeline
- possible root cause candidates
- validation gap suggestions
- firmware dependency mapping
- reliability recommendation

## MVP Scope

This is not a production system.  
The goal is to demonstrate architecture thinking and a working prototype.

## Tech Stack

- Python
- FastAPI
- Markdown documentation
- JSON sample data
- Optional: LangChain or simple local retrieval logic
- Optional: Chroma / FAISS for vector search
- Optional: Streamlit UI later

## Folder Structure

```text
ai-accelerator-reliability-intelligence/
│
├── README.md
├── PROJECT_PLAN.md
│
├── docs/
│   ├── telemetry_correlation.md
│   ├── validation_gap_analysis.md
│   └── firmware_dependency_mapping.md
│
├── data/
│   ├── sample_bios_log.txt
│   ├── sample_bmc_sel.json
│   ├── sample_telemetry.json
│   ├── sample_errata.md
│   └── sample_validation_report.md
│
├── src/
│   ├── main.py
│   ├── log_parser.py
│   ├── telemetry_correlator.py
│   ├── validation_gap_analyzer.py
│   ├── dependency_mapper.py
│   └── recommendation_engine.py
│
└── tests/
    └── test_basic_workflow.py



Functional Requirements
1. Log Parser

Create src/log_parser.py.

It should parse sample BIOS/BMC logs and extract:

timestamp
event type
severity
subsystem
message

Return structured JSON.

2. Telemetry Correlator

Create src/telemetry_correlator.py.

It should correlate events by:

timestamp proximity
subsystem relationship
severity
repeated patterns

Output a correlated event timeline.
3. Validation Gap Analyzer

Create src/validation_gap_analyzer.py.

It should compare errata notes against validation reports and identify missing test coverage.

Example:
If errata says “warm reset under high temperature,” but validation report lacks “warm reset” or “high temperature,” flag a gap.

4. Firmware Dependency Mapper

Create src/dependency_mapper.py.

It should build simple dependency mappings:
Errata → Firmware Workaround → Validation Test → Telemetry Rule
Represent output as JSON.

5. Recommendation Engine

Create src/recommendation_engine.py.

It should generate simple recommendations based on:

correlated telemetry
validation gaps
dependency risks

Example output:
{
  "risk_level": "High",
  "possible_root_cause": "Firmware workaround missing for accelerator warm reset condition",
  "recommended_validation": "Add warm reset loop test under high temperature with accelerator workload active",
  "recommended_owner": "Firmware / Validation"
}

6. FastAPI Backend

Create src/main.py.

Expose endpoints:

GET /health
POST /analyze/logs
POST /analyze/telemetry
POST /analyze/validation-gap
POST /analyze/dependency-map
POST /analyze/recommendation
Sample Data Requirements

Create realistic but fictional sample data.

Do not include proprietary company data.

Use fictional names such as:

Accelerator-X B1 stepping
warm reset failure
high temperature condition
PCIe retraining event
BMC thermal warning
firmware workaround FW-WA-1024
README Update

Add:

project overview
architecture diagram
how to run
example API call
sample output
Success Criteria

The MVP is successful if a user can:

Run the FastAPI service.
Submit sample logs / telemetry.
Receive structured analysis.
See validation gaps.
See dependency mapping.
Receive a reliability recommendation.

Tone

This project should look like a systems architecture prototype, not a toy chatbot.

Use professional naming and clear documentation.

