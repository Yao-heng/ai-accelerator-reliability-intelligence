"""Unit tests for DataRepository JSON shape validation.

The repository loads bundled sample-data files; these tests pin the
contract that a malformed file (wrong top-level JSON shape) fails loudly
with ValueError instead of surfacing later as a confusing type error.
"""

import json
from pathlib import Path

import pytest

from app.services.data_repository import DataRepository


def write(tmp_path: Path, name: str, payload: object) -> DataRepository:
    (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return DataRepository(data_dir=tmp_path)


def test_load_telemetry_roundtrip(tmp_path: Path) -> None:
    repo = write(tmp_path, "telemetry_samples.json", [{"a": 1}, {"b": 2}])

    assert repo.load_telemetry() == [{"a": 1}, {"b": 2}]


def test_load_telemetry_rejects_non_array_payload(tmp_path: Path) -> None:
    repo = write(tmp_path, "telemetry_samples.json", {"not": "a list"})

    with pytest.raises(ValueError, match="array of objects"):
        repo.load_telemetry()


def test_load_telemetry_rejects_array_of_non_objects(tmp_path: Path) -> None:
    repo = write(tmp_path, "telemetry_samples.json", [1, 2, 3])

    with pytest.raises(ValueError, match="array of objects"):
        repo.load_telemetry()


def test_load_firmware_dependencies_rejects_non_object_payload(tmp_path: Path) -> None:
    repo = write(tmp_path, "firmware_dependencies.json", ["not", "an", "object"])

    with pytest.raises(ValueError, match="JSON object"):
        repo.load_firmware_dependencies()
