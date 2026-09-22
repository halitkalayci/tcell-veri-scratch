---
description: "raw tablo için dbt staging modeli + schema.yml testleri üret"
---
`${input:table:raw tablo adı (örn. cdr_events)}` için dbt staging modeli oluştur.

Adımlar:
1. `dbt/telco_dw/models/staging/sources.yml`'de kaynak yoksa ekle (`loaded_at_field: ingested_at` varsa freshness ile).
2. `models/staging/stg_${input:table}.sql` yaz: `{{ source('raw','${input:table}') }}` oku; copilot-instructions.md'deki şema gerçeklerini uygula (msisdn E.164, dedup ROW_NUMBER, status/event_type normalize, geçersizler için `is_valid_*` boolean kolonu — satır silme).
3. `models/staging/schema.yml`'e model açıklaması + kolon açıklamaları + unique/not_null/accepted_values testleri ekle.
4. Modelin sonuna yorum olarak 2 doğrulama sorgusu yaz (dedup öncesi/sonrası, distinct msisdn).
5. `dbt run --select stg_${input:table}` ve `dbt test --select stg_${input:table}` çalıştır; sonucu özetle.

Bitince: hangi varsayımları yaptığını ve instructions'a eklenmesi gereken yeni bir kural varsa öner.