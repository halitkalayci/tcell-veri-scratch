# Telco DW — Copilot Instructions

<!-- ▼▼▼  ▼▼▼ -->


<!-- ▲▲▲ ▲▲▲ -->

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