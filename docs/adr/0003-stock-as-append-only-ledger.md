# ADR-0003: Stoğu append-only hareket defteri olarak modelle

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Referans müşterinin birinci darboğazı stok kaydının tutulamaması. Stok yalnızca "kaç plaka var" değildir: kesim işi için rezervasyon, iptal, kesim sonrası artık üretimi, hurdaya ayırma ve ileride muhasebe mutabakatı gerekir. Tek bir `quantity` kolonu bu olayların izini kaybeder.

## Karar

- `stock_movements` tablosu **append-only**: satır güncellenmez, silinmez. Yanlış kayıt ters hareketle düzeltilir.
- Mevcut stok = hareketlerin projeksiyonu (SQL view; performans gerekince materialized view veya özet tablo, yine hareketlerden türetilir).
- Herhangi bir tabloda **`quantity` kolonu yasaktır**.
- Hareket tipleri:

| `movement_type` | İşaret | Anlam |
|---|---|---|
| `RECEIPT` | + | satın alma girişi |
| `RESERVE` | − (kullanılabilir) | kesim işi için ayırma; fiziksel değil |
| `RELEASE` | + (kullanılabilir) | rezervasyon iptali |
| `CONSUME` | − | kesim gerçekleşti, plaka tüketildi |
| `OFFCUT_IN` | + | kesimden artık üretildi (yeni `StockItem`) |
| `SCRAP` | − | hurdaya ayrıldı |
| `ADJUST` | ± | sayım düzeltmesi; gerekçe zorunlu |

- Her hareket: `tenant_id`, `stock_item_id`, `material_id`, `movement_type`, `qty` (birim malzeme tipine göre), `reference_type/reference_id` (order, cut_job, optimization_run), `reason`, `created_by`, `created_at`.
- Artık durumu (`available / reserved / consumed / scrapped`) da bu hareketlerden projeksiyondur; ayrı `status` kolonu **yoktur** (kullanıcı kararı, 2026-09-13).

## Gerekçe

- Rezervasyon ve iptal, sayaç modelinde yarış koşulu üretir; defterde iki satırdır.
- Her hareketin referansı vardır → "bu plaka hangi işte gitti" sorusu sorgudur, araştırma değil.
- Muhasebe mutabakatı (Faz 3) hareket bazlıdır; sayaç modelinden geri türetilemez.
- Solver kıyaslaması ve destek için "o gün stok neydi" sorusu zaman damgalı projeksiyonla cevaplanır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| `materials.quantity` sayaç kolonu | Geçmiş yok, rezervasyon yok, yarış koşulu. |
| Sayaç + ayrı audit log | İki doğru kaynak; log ile sayaç ayrışır. |
| Event sourcing (tüm domain) | Aşırı; yalnızca stok için defter yeterli. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** tam izlenebilirlik, rezervasyon doğal, mutabakat mümkün.
- **Bedel:** "şu an kaç plaka var" bir toplama sorgusudur; büyük tenant'larda özet tablo gerekir. Projeksiyon SQL'i tek yerde tutulmalı.
- **Kodda zorlama:** `stock_movements` üzerinde `UPDATE`/`DELETE` yetkisi uygulama rolünden alınır; migration testi `quantity` adında kolon bulursa başarısız olur.

## Doğrulanmamış varsayımlar

Yok.

## İlgili ADR'ler

- ADR-0004 — artık bu defterin bir kalemidir
- ADR-0005 — `CONSUME` ve `OFFCUT_IN` hareketleri `OptimizationRun`'a referans verir
- ADR-0007 — hareketler tenant izoleli
