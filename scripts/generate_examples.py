import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.data_repository import DataRepository
from app.services.firmware_dependency_mapper import FirmwareDependencyMapper
from app.services.log_parser import LogParser
from app.services.recommendation_engine import RecommendationEngine
from app.services.telemetry_correlator import TelemetryCorrelator
from app.services.validation_gap_analyzer import ValidationGapAnalyzer


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def serialize_models(models: list) -> list[dict]:
    return [model.model_dump(mode="json") for model in models]


def main() -> None:
    repository = DataRepository()
    logs = LogParser().parse(repository.load_raw_logs())
    correlated = TelemetryCorrelator().correlate(logs, repository.load_telemetry())
    gaps = ValidationGapAnalyzer().analyze(correlated, repository.load_validation_matrix())
    dependencies = FirmwareDependencyMapper().map_dependencies(
        repository.load_firmware_dependencies()
    )
    recommendations = RecommendationEngine().recommend(correlated, gaps, dependencies)

    output_dir = PROJECT_ROOT / "examples" / "sample_outputs"
    write_json(output_dir / "parsed_logs.json", serialize_models(logs))
    write_json(output_dir / "correlated_telemetry_events.json", serialize_models(correlated))
    write_json(output_dir / "validation_gaps.json", serialize_models(gaps))
    write_json(output_dir / "firmware_dependency_map.json", dependencies.model_dump(mode="json"))
    write_json(output_dir / "reliability_recommendations.json", serialize_models(recommendations))

    api_dir = PROJECT_ROOT / "examples" / "api_responses"
    write_json(api_dir / "GET_api_v1_logs_parsed.json", serialize_models(logs))
    write_json(api_dir / "GET_api_v1_telemetry_correlated.json", serialize_models(correlated))
    write_json(api_dir / "GET_api_v1_validation_gaps.json", serialize_models(gaps))
    write_json(api_dir / "GET_api_v1_firmware_dependencies.json", dependencies.model_dump(mode="json"))
    write_json(api_dir / "GET_api_v1_recommendations.json", serialize_models(recommendations))


if __name__ == "__main__":
    main()
