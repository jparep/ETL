{% macro validate_etl_data(table_name) %}
    -- Macro to validate ETL data quality post-load in Snowflake
    {% set validation_sql %}
        SELECT
            COUNT(*) AS total_records,              -- Total records in the table
            COUNT(DISTINCT first) AS unique_first_names,  -- Unique first names
            AVG(age) AS avg_age,                   -- Average age of employees
            COUNT(CASE WHEN sex NOT IN ('M', 'F', 'Unknown') THEN 1 END) AS invalid_sex_count,  -- Count of invalid sex values
            MAX(load_time) AS last_load_time       -- Most recent load timestamp
        FROM {{ table_name }}
        WHERE age IS NOT NULL                      -- Filter out null ages
            AND first IS NOT NULL                  -- Filter out null first names
            AND last IS NOT NULL                   -- Filter out null last names
    {% endset %}

    {% if execute %}
        {% set results = run_query(validation_sql) %}
        {{ log("ETL Data Validation Results: " ~ results|tojson, info=True) }}
        {% if results.rows[0]['invalid_sex_count'] > 0 %}
            {{ exceptions.raise_compiler_error("Invalid sex values detected in " ~ table_name) }}
        {% endif %}
    {% else %}
        {{ log("Dry run: ETL validation skipped.", info=True) }}
    {% endif %}
{% endmacro %}