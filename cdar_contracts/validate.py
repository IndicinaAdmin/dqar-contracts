"""
cdar-contracts validate CLI.

Usage:
    python -m cdar_contracts.validate --schema egress_package --file ./path/to/manifest.json
    python -m cdar_contracts.validate --schema feed_manifest --file ./feed-manifest.json
    python -m cdar_contracts.validate --schema engagement --file ./config/engagements/client.json
    python -m cdar_contracts.validate --list-viewdefs   # check all ViewDefs have getResourceKey()

Called by CI in both dqar-client-kit and dqar-aidbox.
Exit code 0 = valid. Exit code 1 = invalid (details on stderr).
"""

import argparse
import importlib.resources as pkg
import json
import sys
from pathlib import Path

import jsonschema


SCHEMA_MAP = {
    "egress_package": "schemas/egress_package.json",
    "feed_manifest":  "schemas/feed_manifest.json",
    "engagement":     "schemas/engagement.json",
}


def _load_pkg_json(relative_path: str) -> dict:
    parts = relative_path.split("/")
    ref = pkg.files("cdar_contracts")
    for part in parts:
        ref = ref / part
    return json.loads(ref.read_text())


def validate_schema(schema_name: str, file_path: str) -> bool:
    if schema_name not in SCHEMA_MAP:
        print(f"Unknown schema '{schema_name}'. Available: {list(SCHEMA_MAP)}", file=sys.stderr)
        return False

    schema = _load_pkg_json(SCHEMA_MAP[schema_name])
    try:
        instance = json.loads(Path(file_path).read_text())
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {file_path}: {e}", file=sys.stderr)
        return False

    try:
        jsonschema.validate(instance, schema)
        print(f"✓ {file_path} is valid against {schema_name}")
        return True
    except jsonschema.ValidationError as e:
        print(f"✗ {file_path} failed {schema_name} validation:", file=sys.stderr)
        print(f"  {e.message}", file=sys.stderr)
        print(f"  Path: {' > '.join(str(p) for p in e.absolute_path)}", file=sys.stderr)
        return False


def check_viewdefs() -> bool:
    """Verify every ViewDefinition has getResourceKey() in its column projections."""
    vd_dir = pkg.files("cdar_contracts") / "viewdefinitions"
    all_ok = True
    for entry in vd_dir.iterdir():
        if not str(entry).endswith(".json"):
            continue
        vd = json.loads(entry.read_text())
        name = vd.get("name", str(entry))
        has_resource_key = False
        for select_clause in vd.get("select", []):
            for col in select_clause.get("column", []):
                if col.get("path") == "getResourceKey()":
                    has_resource_key = True
                    break
        if has_resource_key:
            print(f"✓ {name} has getResourceKey()")
        else:
            print(f"✗ {name} is MISSING getResourceKey() — lineage chain will break", file=sys.stderr)
            all_ok = False
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="CDAR contracts validator")
    parser.add_argument("--schema", help="Schema name to validate against")
    parser.add_argument("--file",   help="Path to the JSON file to validate")
    parser.add_argument("--list-viewdefs", action="store_true",
                        help="Check all ViewDefinitions for getResourceKey()")
    args = parser.parse_args()

    if args.list_viewdefs:
        ok = check_viewdefs()
        sys.exit(0 if ok else 1)

    if not args.schema or not args.file:
        parser.print_help()
        sys.exit(1)

    ok = validate_schema(args.schema, args.file)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
