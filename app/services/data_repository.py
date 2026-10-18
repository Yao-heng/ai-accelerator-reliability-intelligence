import json
from pathlib import Path
from typing import Any


class DataRepository:
    """Loads local fictional sample data for the MVP API."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"

    def load_raw_logs(self) -> str:
        return (self.data_dir / "accelerator_logs.log").read_text(encoding="utf-8")

    def load_telemetry(self) -> list[dict[str, Any]]:
        return self._load_json_list("telemetry_samples.json")

    def load_gpu_telemetry_logs(self) -> str:
        return (self.data_dir / "gpu_telemetry_logs.jsonl").read_text(encoding="utf-8")

    def load_validation_matrix(self) -> list[dict[str, Any]]:
        return self._load_json_list("validation_matrix.json")

    def load_firmware_dependencies(self) -> dict[str, Any]:
        data = self._load_json("firmware_dependencies.json")
        if not isinstance(data, dict):
            raise ValueError("firmware_dependencies.json must contain a JSON object.")
        return data

    def _load_json_list(self, file_name: str) -> list[dict[str, Any]]:
        data = self._load_json(file_name)
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError(f"{file_name} must contain a JSON array of objects.")
        return data

    def _load_json(self, file_name: str) -> Any:
        return json.loads((self.data_dir / file_name).read_text(encoding="utf-8"))
