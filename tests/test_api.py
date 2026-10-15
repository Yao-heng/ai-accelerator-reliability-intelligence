"""API integration tests for the AI Accelerator Reliability Intelligence service.

Run from the repository root:  pytest
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_get_parsed_logs() -> None:
    response = client.get("/api/v1/logs/parsed")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list) and logs
    assert "accelerator_id" in logs[0]


def test_get_correlated_telemetry() -> None:
    response = client.get("/api/v1/telemetry/correlated")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_validation_gaps() -> None:
    response = client.get("/api/v1/validation/gaps")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_firmware_dependencies() -> None:
    response = client.get("/api/v1/firmware/dependencies")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_get_recommendations() -> None:
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    recommendations = response.json()
    assert isinstance(recommendations, list) and recommendations


def test_analyze_with_bundled_data() -> None:
    response = client.post("/api/v1/analyze", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["ingestion"]["sample_count"] > 0
    assert body["risk_scores"]


def test_analyze_with_custom_telemetry() -> None:
    payload = {
        "telemetry": [
            {
                "timestamp": "2026-05-12T14:02:13Z",
                "accelerator_id": "GPU-TEST-01",
                "rack_id": "RACK-TEST",
                "firmware_version": "fw-1.0.0",
                "workload_id": "WL-TEST",
                "workload_phase": "training",
                "temperature_c": 95.0,
                "hbm_ecc_corrected": 0,
                "hbm_ecc_uncorrected": 3,
                "pcie_replay_count": 2000,
                "power_watts": 700.0,
                "fabric_crc_errors": 20,
                "inference_latency_ms": 80.0,
            }
        ]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    body = response.json()
    metrics = {anomaly["metric"] for anomaly in body["anomalies"]}
    assert "temperature_c" in metrics
    assert "hbm_ecc_uncorrected" in metrics
