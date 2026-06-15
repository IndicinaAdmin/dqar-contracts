-- CDC HbA1c Numerator Reconstruction — parallel to CQL expression
-- Numerator: HbA1c result in measurement period for members with diabetes denominator.

SELECT
    o.patient_id,
    o.observation_id,
    o.loinc_code,
    o.value_quantity        AS hba1c_value,
    o.value_unit,
    o.effective_date,
    -- Level 4: clinical plausibility — flag physiologically implausible values
    CASE WHEN o.value_quantity < 4.0 OR o.value_quantity > 15.0
         THEN true ELSE false END      AS plausibility_flag,
    (
        SELECT ext_ol.value->>'valueString'
        FROM auditevent ae
        CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'extension') ext_ol
        CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'entity') ent
        WHERE ent.value->>'reference' = 'Observation/' || o.observation_id
          AND ext_ol.value->>'url' = 'http://indicina.com/fhir/ext/ol-run-id'
        LIMIT 1
    )                                  AS ol_run_id,
    (
        SELECT ext_feed.value->>'valueString'
        FROM auditevent ae
        CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'extension') ext_feed
        CROSS JOIN LATERAL jsonb_array_elements(ae.resource->'entity') ent
        WHERE ent.value->>'reference' = 'Observation/' || o.observation_id
          AND ext_feed.value->>'url' = 'http://indicina.com/fhir/ext/source-feed-id'
        LIMIT 1
    )                                  AS source_feed_id
FROM sof.observation_hba1c o
JOIN sof.denominator_cdc d ON d.patient_id = o.patient_id
WHERE o.effective_date BETWEEN d.measurement_period_start
                           AND d.measurement_period_end
  AND o.value_quantity IS NOT NULL;
