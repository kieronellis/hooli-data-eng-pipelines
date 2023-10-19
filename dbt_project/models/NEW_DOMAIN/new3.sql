{{
  config(
    tags = 'bi',
    meta = {
      "dagster": {"group": "bi2"}
    },
  )
}}
select * from {{ ref('new2') }}