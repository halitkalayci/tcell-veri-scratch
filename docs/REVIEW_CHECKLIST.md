# Copilot Çıktısı Review Checklist — her merge öncesi

Syntax hatasını Copilot yapmaz; anlam hatasını sık yapar. Bu liste anlam için.

| # | Soru | Nerede patlar |
|---|---|---|
| 1 | Grain nedir, tek cümlede? | Agregasyon katlanır |
| 2 | Join edilen dim, anahtarında tekil mi? (ROW_NUMBER, DISTINCT değil) | Fan-out, toplamlar şişer |
| 3 | LEFT JOIN + WHERE sağ kolon → INNER'a döndü mü? | Satır kaybı, sessiz |
| 4 | Tarih filtresi `>= / <` mi? BETWEEN var mı? | Ayın son günü kaybolur |
| 5 | COUNT(*) mı COUNT(DISTINCT) mı — gerekçesi yorumda mı? | Abone yerine olay sayılır |
| 6 | Tanım (aktif, churn, ARPU) instructions'takiyle aynı mı? | Uydurma tanım |
| 7 | Incremental: watermark ingested_at mı? lookback var mı? unique_key var mı? | Late data kaybı, duplicate |
| 8 | İki kez çalıştırınca sonuç aynı mı? | Retry veriyi katlar |
| 9 | SCD2 join tarih aralığı mı, is_current mı? | Geçmiş rapor bugünkü tarifeyi gösterir |
| 10 | Doğrulama sorguları çalıştırıldı mı, sonuç beklenen mi? | "Çalıştı" ≠ "doğru" |
| 11 | DAG: catchup=False, sabit start_date, retries, reschedule sensor, secret yok? | Deploy anında 365 paralel run |
| 12 | PII kolonları işaretli mi, maskeleme var mı? | KVKK |