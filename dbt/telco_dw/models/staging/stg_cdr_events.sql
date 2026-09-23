with source_data as (
    select *
    from {{ source('raw', 'cdr_events') }}
),

deduplicated as (
    select
        event_id,
        '+90' || right(regexp_replace(msisdn, '\D', '', 'g'), 10) as msisdn,
        lower(trim(event_type)) as event_type,
        event_ts,
        duration_sec,
        bytes,
        cell_id,
        country_code,
        ingested_at,
        row_number() over (
            partition by event_id
            order by ingested_at
        ) as duplicate_rank
    from source_data
),

final as (
    select
        event_id,
        msisdn,
        event_type,
        event_ts,
        duration_sec,
        bytes,
        cell_id,
        country_code,
        ingested_at,
        event_type in ('voice', 'sms', 'data') as is_valid_event_type
    from deduplicated
    where duplicate_rank = 1
)

select *
from final

-- Dogrulama 1: dedup oncesi ve sonrasi satir sayisi
-- select 'before_dedup' as stage, count(*) as row_count
-- from raw.cdr_events
-- union all
-- select 'after_dedup' as stage, count(*) as row_count
-- from silver.stg_cdr_events;

-- Dogrulama 2: normalize edilmis msisdn distinct sayisi
-- select count(distinct msisdn) as distinct_msisdn_count
-- from silver.stg_cdr_events;