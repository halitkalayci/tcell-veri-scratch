# Telco DW — Copilot Instructions

## Proje

- Bu repo bir telekom veri platformudur: raw (bronze) → silver → gold; dbt ile transform, Airflow ile orkestrasyon, PostgreSQL 16.
- Tüm örnek veri sentetiktir. Gerçek müşteri verisi bu repoya ve prompt'lara ASLA girmez.

## Şema Gerçekleri (raw katmanı kirlidir, bu normaldir)

- `msisdn` raw'da karışık formattadır (+905..., 05..., 905..., 5...). Silver'dan itibaren E.164: `'+90' || right(regexp_replace(msisdn, '\D', '', 'g'), 10)`.
- `raw.cdr_events.event_id` tekil DEĞİLDİR; kaynak ~%2 duplicate gönderir. Silver'da dedup zorunlu: `ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY ingested_at)`, rn = 1.
- `status` varyantlıdır (ACTIVE / active / Aktif). Karşılaştırmadan önce: `upper(status) IN ('ACTIVE','AKTIF') → 'ACTIVE'`.
- `raw.subscribers`'ta aynı msisdn birden fazla satırda olabilir (eski + yeni kayıt). Güncel kayıt = en büyük `activation_date`; eşitlikte en büyük `subscriber_id`.
- `event_ts` olayın zamanı, `ingested_at` warehouse'a giriş zamanı; ikisi de UTC. Aralarında 0–72 saat fark olabilir (late-arriving data).
- `event_type` varyantlıdır; `lower()` ile normalize et. voice/sms/data dışındakiler geçersizdir → `is_valid_event_type = false`, satır SİLİNMEZ.


## İş Tanımları
- **Aktif abone**: İlgili ayda en az 1 geçerli CDR (voice/sms/data) üretmiş VE güncel kaydının statüsü ACTIVE olan abone.
- **Churn**: Son 60 günde hiç geçerli CDR üretmemiş VE güncel statüsü ACTIVE olmayan abone.
- **ARPU**: Aylık toplam yükleme (amount_try) / o ayın aktif abone sayısı.
- **Günlük kullanım grain'i**: `fct_daily_usage` tablosunda bir satır = bir msisdn × bir gün (UTC).

## Genel Kurallar
- Tarih filtreleri ASLA `BETWEEN` ile yazılmaz; `>= başlangıç AND < bitiş` kullanılır (timestamp sınır hatası).
- Bir fact'i bir dim'e join etmeden önce dim'in join anahtarında tekil olduğu garanti edilir (fan-out önlemi). `DISTINCT` tekilleştirme sayılmaz; `ROW_NUMBER` kullanılır.
- `LEFT JOIN`'den sonra sağ tablonun kolonu `WHERE`'de filtrelenmez (join INNER'a döner); filtre `ON`'a ya da `CASE`'e taşınır.
- `COUNT(*)` yerine `COUNT(DISTINCT ...)` gerekip gerekmediği her agregasyonda değerlendirilir ve yorum satırında gerekçelendirilir.
- Ortalamaların ortalaması alınmaz; ağırlıklı hesap yapılır.
- Her üretilen sorgu/modelin sonuna en az 2 doğrulama sorgusu eklenir: satır sayısı kontrolü, distinct anahtar kontrolü.
- Şifre, host, connection string koda gömülmez; environment variable, Airflow Connection veya dbt profile kullanılır.
- Kod yorumları ve model açıklamaları Türkçe; tanımlayıcı isimler (tablo, kolon, değişken) İngilizce snake_case.

## Katman-özel kurallar
`.github/instructions/` altındaki dosyalar ilgili yollarda otomatik uygulanır: `sql.instructions.md`, `dbt.instructions.md`, `airflow.instructions.md`.