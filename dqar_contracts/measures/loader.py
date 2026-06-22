from __future__ import annotations
from pathlib import Path
from importlib import resources
import json

from dqar_contracts.shared.measure import MeasureSpec


class MeasureNotFoundError(KeyError):
    """Raised when a requested measure_id has no packaged SQL artifact."""


class MeasureSQLLoader:
    """
    Loads measure SQL from contracts-packaged artifacts.

    Consumers (sql-on-fhir-libraries) call:
        loader = MeasureSQLLoader()
        spec = loader.load("CIS-E", measurement_period="MY2026")
        # use spec.sql, spec.view_definitions — never hardcode SQL

    Artifacts are packaged under dqar_contracts/measures/sql/<MP>/<measure_id>.json
    Each artifact is a serialized MeasureSpec.
    """

    def __init__(self, artifact_root: Path | None = None):
        # Default: package-internal resources. Override for tests.
        self._artifact_root = artifact_root

    def _resolve_path(self, measure_id: str, measurement_period: str) -> Path:
        if self._artifact_root is not None:
            return self._artifact_root / measurement_period / f"{measure_id}.json"
        base = resources.files("dqar_contracts.measures") / "sql" / measurement_period
        return Path(str(base / f"{measure_id}.json"))

    def load(self, measure_id: str, measurement_period: str) -> MeasureSpec:
        path = self._resolve_path(measure_id, measurement_period)
        if not path.exists():
            raise MeasureNotFoundError(
                f"No SQL artifact for {measure_id} in {measurement_period} at {path}"
            )
        data = json.loads(path.read_text())
        return MeasureSpec(**data)

    def list_available(self, measurement_period: str) -> list[str]:
        """Return measure_ids with packaged SQL for the given measurement period."""
        if self._artifact_root is not None:
            mp_dir = self._artifact_root / measurement_period
        else:
            mp_dir = Path(str(
                resources.files("dqar_contracts.measures") / "sql" / measurement_period
            ))
        if not mp_dir.exists():
            return []
        return sorted(p.stem for p in mp_dir.glob("*.json"))
