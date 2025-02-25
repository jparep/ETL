{{ config(materialized='table') }}  -- Materialize as a persistent table for analytics

SELECT
    age_group,                    -- Age group categorization
    sex,                          -- Employee sex (M/F/Unknown)
    COUNT(*) AS employee_count,   -- Count of employees per group
    AVG(age) AS avg_age,          -- Average age per group
    MAX(load_time) AS last_updated -- Most recent load timestamp
FROM {{ ref('stg_employees') }}       -- Reference the staging view
GROUP BY age_group, sex;              -- Aggregate by age group and sex