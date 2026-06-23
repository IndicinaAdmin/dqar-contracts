import json
from pathlib import Path
import pytest
from cdar_contracts.measures import MeasureSQLLoader, MeasureNotFoundError
from cdar_contracts.shared.measure import MeasureSpec


def test_load_seed_artifact(tmp_path: Path):
    root = tmp_path / "sql"
    (root / "MY2026").mkdir(parents=True)
    (root / "MY2026" / "CIS-E.json").write_text(json.dumps({
        "id": {"measure_id": "CIS-E", "framework": "HEDIS", "measurement_period": "MY2026"},
        "sql": "SELECT 1;",
        "view_definitions": [{"name": "immunization_flat", "resource": "Immunization", "version": "1.0.0"}],
        "sql_version": "0.0.1-seed",
    }))
    loader = MeasureSQLLoader(artifact_root=root)
    spec = loader.load("CIS-E", "MY2026")
    assert isinstance(spec, MeasureSpec)
    assert spec.id.measure_id == "CIS-E"
    assert spec.view_definitions[0].resource == "Immunization"


def test_missing_measure_raises(tmp_path: Path):
    loader = MeasureSQLLoader(artifact_root=tmp_path / "sql")
    with pytest.raises(MeasureNotFoundError):
        loader.load("NOPE", "MY2026")


def test_list_available(tmp_path: Path):
    root = tmp_path / "sql"
    (root / "MY2026").mkdir(parents=True)
    (root / "MY2026" / "CIS-E.json").write_text("{}")
    loader = MeasureSQLLoader(artifact_root=root)
    assert "CIS-E" in loader.list_available("MY2026")


def test_list_available_empty_for_missing_period(tmp_path: Path):
    loader = MeasureSQLLoader(artifact_root=tmp_path / "sql")
    assert loader.list_available("MY2099") == []
