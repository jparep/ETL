-- Cleans and normalizes raw employee data for validation
{{ config(materialized='view') }}  -- Materialize as a view for non-persistent validation

SELECT
    first,                        -- Employee first name
    last,                         -- Employee last name
    age,                          -- Employee age
    sex,                          -- Employee sex (M/F/Unknown)
    age_group,                    -- Age group categorization
    load_time                     -- Timestamp of data load
FROM {{ source('employee', 'employees') }}  -- Reference the source table in Snowflake
WHERE age IS NOT NULL                     -- Filter out null ages
    AND first IS NOT NULL                 -- Filter out null first names
    AND last IS NOT NULL;                 -- Filter out null last names