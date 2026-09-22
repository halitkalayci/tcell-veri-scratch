---
description: "mart modelini incremental'a çevir (watermark + lookback + backfill + idempotent)"
---
`${input:model:model adı (örn. fct_daily_usage)}` modelini incremental yap. dbt.instructions.md'deki incremental kuralları ZORUNLUDUR.

- `materialized='incremental'`, `incremental_strategy='delete+insert'`, `unique_key` = grain kolonları.
- Watermark: `max(max_ingested_at)` üzerinden, `var('lookback_days', 3)` gün geriye.
- Backfill: `var('start_date')` ve `var('end_date')` verilmişse `is_incremental()` filtresi yerine bu aralık kullanılır.
- Modele `max_ingested_at` kolonu ekle.
- Model başında yorum bloğu: neden ingested_at (event_ts değil), neden lookback, backfill nasıl çağrılır.
- Ardından test et: modeli iki kez çalıştır, satır sayısı değişmemeli (idempotency). Sonucu raporla.