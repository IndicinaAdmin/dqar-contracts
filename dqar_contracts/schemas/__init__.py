"""Path helpers for bundled JSON schemas."""

import importlib.resources as pkg


def _schema_path(filename: str) -> str:
    ref = pkg.files("dqar_contracts") / "schemas" / filename
    return str(ref)


def engagement_schema_path() -> str:
    return _schema_path("engagement.json")


def egress_package_schema_path() -> str:
    return _schema_path("egress_package.json")


def feed_manifest_schema_path() -> str:
    return _schema_path("feed_manifest.json")
