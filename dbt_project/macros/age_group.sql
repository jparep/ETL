{% macro age_group(age_column) %}
    -- Macro to categorize ages into groups for dbt validation or transformation
    CASE
        WHEN {{ age_column }} < 25 THEN 'Under 25'
        WHEN {{ age_column }} BETWEEN 25 AND 35 THEN '25-35'
        WHEN {{ age_column }} BETWEEN 36 AND 45 THEN '36-45'
        ELSE 'Over 45'
    END
{% endmacro %}