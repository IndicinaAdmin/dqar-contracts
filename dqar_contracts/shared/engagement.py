"""
Engagement config loader and auth adapter.

Supported server types:
  aidbox   — OAuth2 client_credentials (fetches Bearer token from /auth/token)
             FHIR base: {base_url}/fhir
  hapi     — HTTP Basic auth or no auth
             FHIR base: {base_url} (base_url IS the FHIR endpoint)
  medplum  — OAuth2 client_credentials (fetches Bearer token from /oauth2/token)
             FHIR base: {base_url}/fhir/R4
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests


_SUPPORTED_SERVER_TYPES = ("aidbox", "hapi", "medplum")


@dataclass
class EngagementConfig:
    name: str
    server_type: str          # "aidbox" | "hapi" | "medplum"
    base_url: str
    # Aidbox / Medplum OAuth2
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    # HAPI Basic (both optional — HAPI is often open)
    basic_user: Optional[str] = None
    basic_password: Optional[str] = None
    # Computed — do not pass in constructor
    fhir_base: str = field(init=False)

    def __post_init__(self):
        if self.server_type == "aidbox":
            self.fhir_base = f"{self.base_url}/fhir"
        elif self.server_type == "medplum":
            self.fhir_base = f"{self.base_url}/fhir/R4"
        else:
            # hapi — base_url IS the FHIR endpoint
            self.fhir_base = self.base_url


def load_engagement(config_path) -> EngagementConfig:
    with open(config_path) as f:
        data = json.load(f)

    server_type = data["server_type"]
    if server_type not in _SUPPORTED_SERVER_TYPES:
        raise ValueError(
            f"Unsupported server_type '{server_type}'. "
            f"Must be one of: {', '.join(_SUPPORTED_SERVER_TYPES)}."
        )

    return EngagementConfig(
        name=data["name"],
        server_type=server_type,
        base_url=data["base_url"].rstrip("/"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        basic_user=data.get("basic_user"),
        basic_password=data.get("basic_password"),
    )


def get_fhir_headers(engagement: EngagementConfig) -> dict:
    """Return HTTP headers for FHIR requests, including auth."""
    base = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
    }

    if engagement.server_type == "aidbox":
        token = _fetch_aidbox_token(engagement)
        base["Authorization"] = f"Bearer {token}"

    elif engagement.server_type == "medplum":
        token = _fetch_medplum_token(engagement)
        base["Authorization"] = f"Bearer {token}"

    elif engagement.server_type == "hapi":
        if engagement.basic_user and engagement.basic_password:
            import base64
            creds = base64.b64encode(
                f"{engagement.basic_user}:{engagement.basic_password}".encode()
            ).decode()
            base["Authorization"] = f"Basic {creds}"
        # else: no auth (public HAPI instance)

    return base


def _fetch_aidbox_token(engagement: EngagementConfig) -> str:
    if not engagement.client_id or not engagement.client_secret:
        raise ValueError(
            f"Engagement '{engagement.name}' has server_type 'aidbox' "
            "but is missing client_id or client_secret."
        )
    response = requests.post(
        f"{engagement.base_url}/auth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": engagement.client_id,
            "client_secret": engagement.client_secret,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _fetch_medplum_token(engagement: EngagementConfig) -> str:
    if not engagement.client_id or not engagement.client_secret:
        raise ValueError(
            f"Engagement '{engagement.name}' has server_type 'medplum' "
            "but is missing client_id or client_secret."
        )
    response = requests.post(
        f"{engagement.base_url}/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": engagement.client_id,
            "client_secret": engagement.client_secret,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def engagement_schema_path() -> str:
    """Return the absolute path to the engagement config JSON Schema file."""
    import importlib.resources as pkg
    ref = pkg.files("dqar_contracts") / "schemas" / "engagement.json"
    return str(ref)


# ---------------------------------------------------------------------------
# Pydantic engagement / identity types shared across all downstream repos
# ---------------------------------------------------------------------------

from pydantic import BaseModel, Field as PydanticField
from enum import Enum
from typing import Optional as Opt


class MeasurementPeriod(str, Enum):
    MY2025 = "MY2025"
    MY2026 = "MY2026"
    MY2027 = "MY2027"
    MY2028 = "MY2028"
    MY2029 = "MY2029"


class OrganizationRef(BaseModel):
    """Reference to a health plan / organization under assessment."""
    organization_id: str = PydanticField(..., description="Canonical organization identifier")
    name: Opt[str] = PydanticField(None, description="Display name")


class Engagement(BaseModel):
    """A single DQAR engagement context, shared across kits."""
    engagement_id: str = PydanticField(..., description="e.g. UC1-20251014-acme")
    organization: OrganizationRef
    measurement_period: MeasurementPeriod
    prepared_by: Opt[str] = None
    prepared_date: Opt[str] = PydanticField(None, description="ISO 8601 date")
