from dqar_contracts.shared import Engagement, MeasurementPeriod, OrganizationRef


def test_engagement_roundtrip():
    e = Engagement(
        engagement_id="UC1-20251014-acme",
        organization=OrganizationRef(organization_id="acme", name="Acme Health"),
        measurement_period=MeasurementPeriod.MY2026,
    )
    assert e.measurement_period == MeasurementPeriod.MY2026
    assert Engagement(**e.model_dump()).engagement_id == "UC1-20251014-acme"


def test_organization_ref_optional_name():
    ref = OrganizationRef(organization_id="org-001")
    assert ref.name is None


def test_measurement_period_values():
    assert MeasurementPeriod.MY2025.value == "MY2025"
    assert MeasurementPeriod.MY2026.value == "MY2026"
