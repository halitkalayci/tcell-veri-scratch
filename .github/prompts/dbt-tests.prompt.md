---
description: "model için kapsamlı dbt test seti (generic + singular + tutarlılık)"
---
`${input:model}` için test seti yaz.

1. `schema.yml`: unique kombinasyon (dbt_utils), not_null, accepted_values / accepted_range (dbt_expectations), relationships (ilgili dim'e).
2. `tests/` altında singular testler:
   - **Tutarlılık**: mart'taki toplam metrik ile staging'deki toplam arasındaki fark %0.01'i geçmesin (fan-out kanıtı).
   - **Güncellik**: en büyük tarih bugünden en fazla 1 gün geride.
   - **Geçerlilik**: negatif / olanaksız değer yok (ör. voice_minutes 0–1440).
3. Her testin `severity` değeri: veri kaybı / çoğalma yaratanlar `error`, diğerleri `warn`. Gerekçeyi yorumla yaz.
4. `dbt test --select ${input:model}` çalıştır; başarısız test varsa nedenini açıkla ama VERİYİ DÜZELTME — sadece raporla.