# AI Accelerator Reliability Intelligence (AI-RI)

A FastAPI-based Microservice Infrastructure for Cross-Layer Telemetry Log Fusion, Real-Time Root Cause Analysis (RCA), and Automated Triage inside Hyperscale AI Factories.

This project is intentionally architected as a production-ready reliability intelligence service rather than a generic chatbot demo. It acts as the critical software-hardware bridge that ingests distributed telemetry, correlates core platform signals, and leverages domain-specific AI logic to automate triage and secure 99.999% uptime for high-density compute clusters.

---

## 🌟 Strategic Focus: Transforming Volume into Intelligence

As hyperscale AI infrastructure continues scaling across distributed topologies, reliability challenges have transcended traditional diagnostic capabilities. A single hardware or fabric fault can induce cascading synchronization timeouts (such as distributed All-Reduce Timeouts), halting massive LLM training clusters and resulting in catastrophic financial and SLA leakage.

When a high-density node crashes, operations teams are traditionally faced with an isolated "chaos of logs":
* **Host BIOS:** Hexadecimal Machine Check Exceptions (MCE Status registers)
* **Server BMC:** Fragmented System Event Logs (IPMI SEL)
* **Accelerator Subsystems:** Satellite BMC (SBMC) errata and fabric symbol errors (PLDM/MCTP sideband telemetry)

**AI-RI** serves as the definitive architecture to fuse these heterogeneous, multi-layer signals into a synchronized microsecond timeline at the exact millisecond of failure. By binding **24 years of enterprise server heritage**—forged across million-shipment portfolios like the ProLiant MicroServer, ML150/310/350, DL120/320 series, and the ultra-dense HPE Moonshot 1500 system—this framework maps raw hardware symptoms to precise silicon errata root causes and delivers actionable operational solutions instantly.

### 🧠 Deep Diagnostic Logic: Beyond the Black Box

The core inference engine of **AI-RI** is not a generic "black box" chatbot. It follows a rigorous, three-layer hardware-software co-engineering logic:

1.  **Deterministic Signature Identification:** 
    Instead of guessing, the system first traps low-level hardware telemetry via **PLDM/MCTP**. It parses raw binary registers such as **BIOS MCE (Machine Check Exceptions)** and **PCIe AER (Advanced Error Reporting)** to extract deterministic "physics-level" failure signatures (e.g., Vdroop transients, PCIe link training timeouts).

2.  **Temporal & Fleet Correlation:** 
    Using a sliding-window temporal alignment algorithm, the system fuses asynchronous logs across the entire cluster. It performs **Fleet Baseline Peer Comparison** to differentiate between individual hardware degradation and cluster-wide regression (e.g., identifying firmware-induced power profile defects across a specific cohort of nodes).

3.  **Semantic Reasoning via Silicon Errata RAG:** 
    The engine utilizes **Retrieval-Augmented Generation (RAG)** to index thousands of pages from Intel/NVIDIA **Silicon Errata manuals** and 24 years of proprietary RCA wiki data. It maps current failure vectors against documented silicon errata to deliver sub-second, actionable triage solutions that prevent cascading "All-Reduce" timeouts in LLM training.
---

## 🏗 Core Concepts & Capabilities

* **Silicon Errata Intelligence:** Cross-referencing CPU/GPU stepping anomalies and active hardware workarounds.
* **Cross-Layer Log Fusion:** Binding asynchronous telemetry across BIOS, BMC, and accelerator sideband.
* **Deterministic Pattern Mapping:** Converting complex hardware failure modes into clean, identifiable signature vectors.
* **Validation Gap Analysis:** Correlating real-world field crashes back to automated release-test matrices to eliminate coverage misses.
* **Automated Mitigations:** Driving Infrastructure-as-Code (IaC) routines to enforce dynamic power capping, thermal adjustment, or graceful node evacuation prior to cluster-wide failure.

---

## 📂 Project Structure

```text
app/
  api/
    routes.py                     # Thin RESTful API routes handling Redfish and telemetry ingestion
  data/
    accelerator_logs.log          # Raw multi-layer firmware and OS log lines
    firmware_dependencies.json    # Manifest mapping subsystem blast radius and adjacency
    gpu_telemetry_logs.jsonl      # High-cadence GPU fleet telemetry stream samples
    telemetry_samples.json        # Normalized JSON target matrices
    validation_matrix.json        # Release validation test coverage matrix
  models/
    schemas.py                    # Strong Pydantic domain models for rigorous validation
  services/
    anomaly_detector.py           # Real-time monitoring for HBM ECC, PCIe replays, and fabric CRC
    analyzer.py                   # Local intelligence and pattern arbitration orchestration
    data_repository.py            # Extensible local data access adapters
    firmware_dependency_mapper.py # Blast-radius calculation across runtime and firmware layers
    infrastructure_advisor.py     # High-level operations advisor (Rollout freezes, quarantines)
    log_parser.py                 # Structural converter translating hardware lines to domain objects
    recommendation_engine.py      # Core engine outputting Root Cause and Actionable Solutions
    risk_scoring.py               # Aggregated 0-100 risk matrices for rack and node-level triage
    telemetry_correlator.py       # Microsecond-window time-series alignment handler
    telemetry_ingestion.py        # Normalizes broad field aliases into canonical schemas
    validation_gap_analyzer.py    # Tracks missing test cases for workload phases and platforms
  main.py                         # FastAPI Application entrypoint
docs/
  PROJECT_PLAN.md
  firmware_dependency_mapping.md
  telemetry_correlation.md
  validation_gap_analysis.md
examples/
  api_responses/
  sample_outputs/
scripts/
  generate_examples.py            # Utility script simulating real-world infrastructure failures
requirements.txt


