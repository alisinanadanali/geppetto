# ADR-0016: Test stratejisi — property-based solver değişmezleri, golden set, RLS testleri

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

AI destekli geliştirmede darboğaz token değil **doğrulanabilirliktir**. Model, makul görünen ama sessizce yanlış bir nesting algoritması üretmekte çok başarılıdır. Örnek tabanlı birim testleri bunu yakalayamaz; yalnızca yazarın aklına gelen durumu test eder. Tenant sızıntısı ve ölçü formülü hataları da aynı sınıftadır: sessiz ve pahalı.

## Karar

### 1. Solver değişmezleri (Hypothesis, rastgele girdi)

Her `optimize()` çıktısı için, üretilen her rastgele girdide:

| # | Değişmez | Hata kodu |
|---|---|---|
| I1 | Hiçbir iki yerleşim çakışmaz (kerf dahil) | `SOLVER_OVERLAP` |
| I2 | Her yerleşim plakanın kullanılabilir alanı (plaka − trim) içindedir | `SOLVER_OUT_OF_BOUNDS` |
| I3 | Kerf her kesikte uygulanmıştır (iki komşu arası ≥ kerf) | `SOLVER_KERF_MISSING` |
| I4 | Giyotin modunda her kesik, bulunduğu dikdörtgeni kenardan kenara böler | `SOLVER_NOT_GUILLOTINE` |
| I5 | `grain ≠ NONE` olan parça 90° döndürülmemiştir; `rotation = NONE` olan hiç döndürülmemiştir | `SOLVER_ROTATION_VIOLATION` |
| I6 | Girdi parça adedi (qty toplamı) = yerleştirilen + yerleştirilemeyen adedi | `SOLVER_PART_COUNT_MISMATCH` |
| I7 | Her plaka için: Σ parça alanı + Σ artık alanı + fire (kerf + trim + eşik altı) = plaka alanı | `SOLVER_AREA_CONSERVATION` |
| I8 | Determinizm: aynı girdi + aynı seed = aynı çıktı | `SOLVER_NONDETERMINISTIC` |

Bu değişmezler `packages/geppetto-solver/tests/invariants.py` içinde **tek bir doğrulayıcı** olarak yazılır ve üretimde de (opsiyonel, `validate=True`) çalıştırılabilir.

### 2. Golden set

- `tests/golden/<kaynak>/<ad>/{input.json, expected.json}`; `input.json` = `OptimizeRequest`, `expected.json` = kabul edilen metrikler (plaka sayısı, doluluk) ve referans yerleşim.
- Kaynak: referans müşteriden gerçek kesim listeleri + Adeko'nun kendi kesim planı sonucu.
- Her solver değişikliğinde CI, tüm golden set için doluluk tablosu üretir (`solver_version × case`). Gerileme = plaka sayısı artışı veya doluluk düşüşü > eşik → PR bloklanır.

### 3. RLS testleri

- İki tenant, her tenant tablosunda: A oturumu B satırını okuyamaz (0 satır), güncelleyemez, silemez; `INSERT` yanlış `tenant_id` ile reddedilir.
- Tablo listesi migration'dan otomatik türetilir; RLS'siz tenant tablosu test başarısızlığıdır.
- Test rolü uygulama rolüdür; superuser ile koşan RLS testi geçersizdir.

### 4. Domain kural testleri

- `derive_raw_dimensions()`: property testleri (bant ekle → ilgili eksen küçülür; `RAW` basis → düşüm yok; negatif ham → hata kodu).
- Stok projeksiyonu: rastgele hareket dizisi → projeksiyon = cebirsel toplam; `status` geçiş kuralları.

### 5. Sözleşme testleri

- OpenAPI snapshot; değişiklik bilinçli commit ister.
- Export round-trip: DXF yaz → oku → operasyon listesi eşit.

## Gerekçe

- Değişmezler, "makul görünen yanlış" sınıfını yapısal olarak yakalar.
- Golden set, doğruluğun ötesinde **kaliteyi** (doluluk) ölçer; AI'ın gerilemesini görünür kılar.
- RLS testi, ADR-0007'nin yanlış rol kurulumuyla sessizce devre dışı kalmasına karşı tek savunmadır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Yalnızca örnek tabanlı birim test | Aklına gelen durumu test eder; nesting hataları kombinatoryaldir. |
| Manuel görsel kontrol | Ölçeklenmez; AI iterasyon hızında imkânsız. |
| Solver'ı "doğru kabul edip" yalnızca UI test etmek | Ürünün çekirdeğini test dışı bırakır. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** solver değişikliği güvenle yapılabilir; tenant sızıntısı yapısal olarak yakalanır.
- **Bedel:** Hypothesis stratejileri yazmak ilk başta zaman alır; golden set müşteri verisine bağlı.
- **Kodda zorlama:** CI: property + RLS + sözleşme testleri PR'da zorunlu; golden tablo PR yorumuna yazılır.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Golden set henüz yok; referans müşteriden kesim listesi ve Adeko planı alınmadı. Alınana kadar golden bölümü yalnızca dizin düzeni ve kabul kriteridir.

## İlgili ADR'ler

- ADR-0005, ADR-0007, ADR-0009, ADR-0011, ADR-0013
