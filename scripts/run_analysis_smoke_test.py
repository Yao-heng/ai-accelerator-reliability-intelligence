import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.analyzer import ReliabilityAnalyzer
from app.services.data_repository import DataRepository


def main() -> None:
    repository = DataRepository()
    analyzer = ReliabilityAnalyzer()

    payload = repository.load_telemetry()
    response = analyzer.analyze(payload)

    output_dir = PROJECT_ROOT / "scripts" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "analysis_response.json"

    output_file.write_text(json.dumps(response.model_dump(mode="json"), indent=2), encoding="utf-8")

    print("Smoke test completed successfully.")
    print(f"Samples: {response.ingestion.sample_count}")
    print(f"Accelerators: {response.ingestion.accelerator_count}")
    print(f"Anomalies: {len(response.anomalies)}")
    print(f"Risk scores: {len(response.risk_scores)}")
    print(f"Recommendations: {len(response.recommendations)}")
    print(f"Saved analysis response to: {output_file}")


if __name__ == "__main__":
    main()
