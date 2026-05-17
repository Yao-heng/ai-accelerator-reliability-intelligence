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
        return self._load_json("telemetry_samples.json")

    def load_validation_matrix(self) -> list[dict[str, Any]]:
        return self._load_json("validation_matrix.json")

    def load_firmware_dependencies(self) -> dict[str, Any]:
        return self._load_json("firmware_dependencies.json")

    def _load_json(self, file_name: str) -> Any:
        return json.loads((self.data_dir / file_name).read_text(encoding="utf-8"))
