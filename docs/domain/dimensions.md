# Ham Ölçü / Bitmiş Ölçü Kuralı

Bu doküman ADR-0009'un operasyonel halidir. Kod bu dokümandan sapamaz; sapma gerekiyorsa önce ADR güncellenir.

## 1. Tanımlar

| Kavram | Ne | Nerede saklanır |
|---|---|---|
| **Bitmiş ölçü (finished)** | Montajdaki nihai ölçü, bant dahil | `Part.finished_length_um`, `Part.finished_width_um` — **tek doğru kaynak** |
| **Ham ölçü (raw / cutting)** | Plakadan kesilecek ölçü | Hesaplanır; yalnızca `OptimizationRun.input_snapshot` içinde donmuş kopya |
| Kenar bandı kalınlığı | Bandın kenara eklediği kalınlık | `Material(EDGE_BAND).attrs.thickness_um` |
| İşleme payı (oversize) | Sonradan tıraşlanacak fazlalık | `Material.attrs.oversize_length_um / oversize_width_um` |
| Kerf | Testerenin yok ettiği genişlik | `Machine.kerf_um` |
| Tıraş payı (trim) | Plaka kenarından atılan pay | `Material(SHEET).attrs.trim_edges` ve/veya `Machine.default_trim_um` |

## 2. Formül

Tüm değerler tam sayı µm. Bölme yok; formül yalnızca toplama ve çıkarma içerir, yuvarlama oluşmaz.

```
raw_length_um = finished_length_um
              − band_thickness(W1)      # W1 kenarı X=0'da, uzunluğa dik → uzunluğu kısaltır
              − band_thickness(W2)
              + oversize_length_um

raw_width_um  = finished_width_um
              − band_thickness(L1)      # L1 kenarı Y=0'da, genişliğe dik → genişliği kısaltır
              − band_thickness(L2)
              + oversize_width_um
```

`band_thickness(edge)` = o kenara atanmış bandın `thickness_um` değeri; bant yoksa 0.
`edge_reduction_policy = NONE` olan bant için değer 0 kabul edilir (bant vurulur ama düşüm yapılmaz).

## 3. Kurallar

1. **Bant düşer, işleme payı ekler.** İki terim ters işaretlidir; asla tek bir "pay" alanında birleştirilmez.
2. **Düşüm bitmiş ölçü üzerinden yapılır.** Ham ölçüden tekrar düşüm yapılmaz.
3. **Kenarlar tek sayı değil, dört ayrı tanımdır.** `edges: {L1, L2, W1, W2}`; her biri nullable `edge_band_material_id`. "3 kenar bantlı" diye bir girdi yoktur; hangi 3 kenar olduğu yazılır.
4. **Bant metrajı bitmiş kenar boyundan hesaplanır.** L1 bantlıysa metraj `finished_length_um`, W1 bantlıysa `finished_width_um` kadardır.
5. **Bantlama fire payı stok tüketimine eklenir, parça ölçüsüne değil.** `length_allowance_per_part_um` her bantlı kenar için bant tüketimine eklenir.
6. **Kerf bunların hiçbiri değildir.** Kerf, yerleşimde iki parça arasındaki kayıptır ve yalnızca solver'da kullanılır. Parça ölçüsüne asla girmez. Kerf **makine** özelliğidir, malzeme özelliği değil.
7. **Tıraş payı plaka kenarına uygulanır**, parçaya değil. Solver kullanılabilir plaka alanını `sheet − trim` olarak alır.
8. **`OptimizationRun` ham ölçüleri donmuş saklar.** Malzeme veya bant parametresi sonradan değişse bile geçmiş koşu değişmez.
9. Ham ölçü ≤ 0 çıkarsa bu bir hata kodudur: `PART_RAW_DIMENSION_NON_POSITIVE`. Sessizce 0'a çekilmez.

## 4. Sayısal örnekler

Bant kalınlığı 800 µm (0,8 mm) varsayılır. Kerf 4000 µm (4 mm) — örneklerde ölçüye girmediği görülsün diye yazıldı.

### Örnek A — bantsız plaka parçası (arkalık)

| Alan | Değer |
|---|---|
| finished | 600 000 × 400 000 |
| edges | hepsi null |
| oversize | 0 / 0 |
| **raw** | **600 000 × 400 000** |
| bant metrajı | 0 |

### Örnek B — iki uzun kenarı bantlı raf (L1, L2)

| Alan | Değer |
|---|---|
| finished | 800 000 × 500 000 |
| edges | L1=800 µm, L2=800 µm, W1=null, W2=null |
| oversize | 0 / 0 |
| raw_length | 800 000 − 0 − 0 = **800 000** |
| raw_width | 500 000 − 800 − 800 = **498 400** |
| bant metrajı | 2 × 800 000 = 1 600 000 µm = 1,6 m (+ 2 × allowance stok tüketimine) |

Uzun kenarlar (L1/L2) genişliğe dik olduğu için **genişlik** kısalır; uzunluk değişmez. En sık yapılan hata tersidir.

### Örnek C — dört kenar bantlı kapak

| Alan | Değer |
|---|---|
| finished | 715 000 × 396 000 |
| edges | L1=L2=W1=W2=800 µm |
| raw | (715 000 − 1 600) × (396 000 − 1 600) = **713 400 × 394 400** |
| bant metrajı | 2×715 000 + 2×396 000 = 2 222 000 µm = 2,222 m |

### Örnek D — masif çıta, işleme payı

| Alan | Değer |
|---|---|
| finished | 2 000 000 × 60 000 |
| edges | null (masifte bant yok) |
| oversize | length 20 000, width 5 000 |
| raw | **2 020 000 × 65 000** |

## 5. İthalat tuzağı: `dimension_basis`

Gelen listedeki ölçünün bitmiş mi ham mı olduğu dosyadan anlaşılamaz. `PartListDocument` şemasında zorunlu alan:

```
dimension_basis: FINISHED | RAW
```

- Eşleme profilinde varsayılan **yoktur**; kullanıcı ithalat önizlemesinde açıkça seçer ve onaylar.
- `FINISHED`: ölçüler doğrudan `finished_*` alanına yazılır; ham ölçü bölüm 2 formülüyle türetilir.
- `RAW`: bant düşümü **tekrar uygulanmaz**. Bitmiş ölçü şöyle geri türetilir:
  - Kenar bant bilgisi listede varsa: `finished = raw + Σ band_thickness − oversize`. Parça `finished_is_derived = true` işaretlenir.
  - Kenar bant bilgisi yoksa: `finished = raw` kabul edilir, parça `finished_is_derived = true` ve uyarı kodu `PART_FINISHED_ASSUMED_FROM_RAW` ile önizlemede gösterilir.

> ⚠️ DOĞRULANMADI: Adeko'nun dışa aktardığı liste ham mı bitmiş mi ölçü içeriyor, bant bilgisi hangi biçimde geliyor — örnek dosya alınmadan bilinmiyor. İlk profil bu doğrulamadan sonra yazılacak. Bkz. `docs/integration/import-profiles.md`.

## 6. Etkilenen hesaplar (özet)

| Hesap | Girdi |
|---|---|
| Kesim / yerleşim | ham ölçü + kerf (makine) + trim (plaka) |
| Bant stok tüketimi | bitmiş kenar boyu + allowance |
| Proje maliyeti (plaka) | kullanılan plaka alanı (run metriği) |
| Etiket üzerindeki ölçü | bitmiş ölçü (montajcı bunu görür); ham ölçü ayrıca küçük yazılır |
| DXF çıktısı | ham ölçü dış hat; operasyonlar bitmiş ölçüye göre konumlanır → bant düşümü kadar ofset ⚠️ DOĞRULANMADI (CNC pratiğine göre kararlaştırılacak, bkz. dxf-conventions.md) |
