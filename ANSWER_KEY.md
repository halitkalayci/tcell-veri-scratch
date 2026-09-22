# ANSWER KEY — eğitmen kopyası, repoya girmez

Üretim: quick | seed=42

## Veri kirliliği
- raw.cdr_events satır: 305942 | tekil event_id: 300000 | duplicate satır: 5942
- late-arriving (ingested_at - event_ts > 24 saat): 6014
- geçersiz event_type ('mms'): 968
- raw.subscribers satır: 10150 | tekil msisdn: 10000 | iki kaydı olan msisdn: 150
- status tam olarak 'ACTIVE' yazan satır: 4904 (varyantlar dahil değil!)

## Ağustos 2026 aktif abone (>=1 geçerli CDR ve güncel kaydın statüsü ACTIVE)
- YOUTH: 1676
- MASS: 4486
- PREMIUM: 1249
- CORPORATE: 826
- TOPLAM: 8237
- (Sadece 'Ağustos'ta CDR üreten' tekil msisdn, statü bakılmadan: 9995)

## Kanal bazında toplam yükleme (TRY), tüm dönem
| channel | DOĞRU toplam | fan-out'lu (subscribers'a naif join) |
|---|---|---|
| APP | 5455653.01 | 5536152.53 |
| WEB | 1827327.60 | 1856170.34 |
| DEALER | 3050608.53 | 3097914.97 |
| BANK | 1219328.79 | 1240595.98 |
| IVR | 613989.50 | 622854.42 |

- msisdn normalize ETMEDEN subscribers'a inner join yapılırsa kaybolan yükleme satırı: 25169

## plan_changes satır: 1000
