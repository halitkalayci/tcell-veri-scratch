---
description: "dbt mart modeli için data contract YAML üret (ODCS-benzeri)"
---
`contracts/${input:model}.yaml` data contract dosyasını yaz. Kaynaklar: `models/marts/schema.yml`, model SQL'i, copilot-instructions.md'deki iş tanımları.

Bölümler:
- `info`: id, version 1.0.0, owner (data-platform-team), contact (Slack kanalı), status: active, changelog
- `schema`: her kolon için name, type, required, description (semantic tanım instructions'tan), `pii: true` işaretleri, primary key
- `quality`: schema.yml'deki testleri kurallara çevir
- `sla`: freshness (07:00 Europe/Istanbul), max latency, availability
- `terms`: retention, usage, breaking-change notice süresi (14 gün)
- `consumers`: en az 3 tüketici, her biri contact'lı

Bitince: bu sözleşmeyi `datacontract test` ile doğrulamak için gereken `servers` bloğunu ekle.