{{
  config(
    tags = 'bi',
    meta = {
      "dagster": {"group": "bi2"}
    },
  )
}}
select * from {{ ref('company_stats') }}