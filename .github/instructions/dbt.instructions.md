---
applyTo: "sql/**/*.sql"
---
# Ham SQL kuralları (PostgreSQL 16)
- CTE zinciri kullan; iç içe subquery yazma. Her CTE'nin üstünde bir satır yorum: amacı.
- CTE isimleri katmanı anlatsın: `deduped`, `normalized`, `filtered`, `aggregated`, `current_subscribers`.
- Aggregate window'larda (sum/avg/count over) frame'i açıkça yaz (`ROWS BETWEEN ...`); default RANGE'e güvenme. Ranking fonksiyonlarında (row_number/rank/dense_rank) frame YAZMA — anlamsızdır.
- Deterministik sıralama: `ORDER BY`'a her zaman tekil bir iş anahtarı tie-breaker ekle (ör. `recharge_id`, `subscriber_id`). `ctid` kullanma — fiziksel adres, VACUUM sonrası değişir.
- Performans önerisi istenirse önce `EXPLAIN (ANALYZE, BUFFERS)` çıktısını iste; çıktısız index önerme.
- Sorgunun sonuna `-- DOĞRULAMA` başlığı altında en az 2 kontrol sorgusu ekle.