{{ config(
    materialized='table',         -- Materialize as a persistent table in Snowflake
    alias="employees",            -- Table name in Snowflake
    database="employee_db",       -- Target database in Snowflake
    schema="employee",            -- Target schema in Snowflake
    tags=["transformed_data"],    -- Tags for categorization and tracking
    cluster_by=["load_time"]      -- Optimize queries by clustering on load_time
) }}

SELECT
    CAST(NULL AS STRING) AS first,       -- Placeholder for employee first name
    CAST(NULL AS STRING) AS last,        -- Placeholder for employee last name
    CAST(NULL AS INT) AS age,            -- Placeholder for employee age
    CAST(NULL AS STRING) AS sex,         -- Placeholder for employee sex (M/F/Unknown)
    CAST(NULL AS STRING) AS age_group,   -- Placeholder for age categorization (Under 25, 25-35, etc.)
    CAST(NULL AS TIMESTAMP) AS load_time -- Placeholder for data load timestamp
WHERE FALSE;                             -- Ensures an empty table initially