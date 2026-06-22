from __future__ import annotations
from pydantic import BaseModel, Field


class MeasureId(BaseModel):
    """Stable identifier for a HEDIS (or other framework) measure."""
    measure_id: str = Field(..., description="e.g. CIS-E, BCS-E, SPD-E")
    framework: str = Field("HEDIS", description="HEDIS, ACC, ACS, CMS, custom")
    measurement_period: str = Field(..., description="e.g. MY2026")


class ViewDefinitionRef(BaseModel):
    """Reference to a SQL-on-FHIR ViewDefinition the measure depends on."""
    name: str = Field(..., description="ViewDefinition name")
    resource: str = Field(..., description="FHIR resource type, e.g. Observation")
    version: str = Field(..., description="ViewDefinition version")


class MeasureSpec(BaseModel):
    """
    A measure's executable spec as served by the measure-SQL loader.
    sql-on-fhir-libraries loads this from contracts — never hardcodes SQL.
    """
    id: MeasureId
    sql: str = Field(..., description="The measure SQL (SQL-on-FHIR / dialect as documented)")
    view_definitions: list[ViewDefinitionRef] = Field(
        default_factory=list,
        description="ViewDefinitions this measure reads from",
    )
    sql_version: str = Field(..., description="Version of the SQL artifact, for lineage")
