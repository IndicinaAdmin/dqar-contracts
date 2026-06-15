-- CBP Numerator Reconstruction — parallel to CQL expression
-- Projects observation_id for lineage chain to AuditEvent.
-- Must produce identical patient set as CQL numerator population.
-- Disagreement between CQL result and this query is a Tier 2 finding.

WITH cbp_qualifying_obs AS (
    SELECT
        o.observation_id,
        o.patient_id,
        o.encounter_id,
        o.systolic,
        o.diastolic,
        o.effective_date,
        -- ol-run-id from AuditEvent — which ingest run produced this resource
        (
            SELECT ext_ol.value->>'valueString'
            FROM auditevent ae
            CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'extension') ext_ol
            CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'entity') ent
            WHERE ent.value->>'reference' = 'Observation/' || o.observation_id
              AND ext_ol.value->>'url' = 'http://indicina.com/fhir/ext/ol-run-id'
            LIMIT 1
        )                           AS ol_run_id,
        (
            SELECT ext_feed.value->>'valueString'
            FROM auditevent ae
            CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'extension') ext_feed
            CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'entity') ent
            WHERE ent.value->>'reference' = 'Observation/' || o.observation_id
              AND ext_feed.value->>'url' = 'http://indicina.com/fhir/ext/source-feed-id'
            LIMIT 1
        )                           AS source_feed_id
    FROM sof.observation_bp o
    JOIN sof.encounter_summary e ON e.encounter_id = o.encounter_id
    JOIN sof.denominator_cbp d   ON d.patient_id   = o.patient_id
    WHERE o.effective_date BETWEEN d.measurement_period_start
                               AND d.measurement_period_end
      AND o.systolic  IS NOT NULL
      AND o.diastolic IS NOT NULL
      -- Level 3: encounter type constraint — AMB or VR only
      AND e.class_code IN ('AMB', 'VR')
)
SELECT
    patient_id,
    observation_id,
    systolic,
    diastolic,
    effective_date,
    ol_run_id,
    source_feed_id,
    CASE WHEN systolic < 140 AND diastolic < 90 THEN true
         ELSE false END                AS cbp_numerator
FROM cbp_qualifying_obs;
