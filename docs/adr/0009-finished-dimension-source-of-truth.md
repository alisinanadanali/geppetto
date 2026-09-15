# ADR-0009: Bitmiş ölçü tek doğru kaynaktır; ham ölçü türetilir

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Bir parçanın iki ölçüsü vardır: montajdaki bitmiş ölçü ve plakadan kesilecek ham ölçü. Aralarındaki fark kenar bandı (düşer) ve işleme payı (ekler). İkisini de saklamak tutarsızlık üretir; yalnızca hamı saklamak bant metrajını ve montaj ölçüsünü kaybettirir.

## Karar

- `Part` yalnızca **bitmiş ölçüyü** saklar (`finished_length_um`, `finished_width_um`).
- Ham ölçü `geppetto-domain` içindeki tek saf fonksiyonla türetilir:

```
raw_length = finished_length − band(W1) − band(W2) + oversize_length
raw_width  = finished_width  − band(L1) − band(L2) + oversize_width
```

- Bant düşümü **bitmiş ölçü üzerinden**, kenar bazında (`edges: {L1, L2, W1, W2}`).
- Bant metrajı bitmiş kenar boyundan; bantlama fire payı bant **stok tüketimine** eklenir, parça ölçüsüne değil.
- Kerf ve trim bu formülün parçası değildir; kerf makinenin, trim plakanın özelliğidir ve yalnızca solver'da kullanılır.
- Ham ölçüler `OptimizationRun.input_snapshot` içinde donar (ADR-0005).
- İthalatta `dimension_basis: FINISHED | RAW` **zorunlu** ve kullanıcı onaylı; `RAW` gelince düşüm tekrar uygulanmaz, bitmiş ölçü geri türetilir ve `finished_is_derived = true` işaretlenir.
- Kurallar, örnekler ve ithalat tuzağı: `docs/domain/dimensions.md`.

## Gerekçe

- Kullanıcının bildiği ve montajcının ölçtüğü değer bitmiş ölçüdür.
- Bant değişince (0,8 → 2 mm) ham ölçü otomatik güncellenir; iki alanı senkron tutma sorunu yok.
- Tek fonksiyon = tek test yüzeyi; formül hatası tek yerde yakalanır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Ham ölçüyü saklamak | Bant metrajı ve montaj ölçüsü türetilemez; bant değişince ham yanlış kalır. |
| İkisini de saklamak | İki doğru kaynak; ithalatta hangisinin geldiği belirsizken tutarsızlık garantili. |
| Tek `band_count` alanı | Düşümün hangi eksene gideceği bilinemez. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** tek kaynak, otomatik tutarlılık, bant metrajı doğru.
- **Bedel:** her kesim listesi görüntüsü bir hesap ister (ucuz, saf fonksiyon). `RAW` ithalatta bilgi kaybı olabilir (bant bilgisi yoksa bitmiş = ham varsayımı).
- **Kodda zorlama:** `raw_*` adında DB kolonu yasak (migration testi); `derive_raw_dimensions()` property testleri (bant ekle → ham küçülür, doğru eksende).

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Adeko listesinin ölçü esası (bkz. dimensions.md §5).

## İlgili ADR'ler

- ADR-0002 — birim
- ADR-0005 — donmuş ham ölçü
- ADR-0006 — kenar tanımı
- ADR-0012 — `dimension_basis` ithalat şemasında
- ADR-0017 — kerf makinede
