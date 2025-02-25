-- Test to ensure no invalid sex values exist in the employees table
SELECT *
FROM {{ ref('stg_employees') }}
WHERE sex NOT IN ('M', 'F', 'Unknown');