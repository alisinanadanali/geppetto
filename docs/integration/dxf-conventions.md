# DXF Katman Konvansiyonu (Giriş ve Çıkış)

ADR-0013'ün operasyonel hali. Katman adı = operasyon sözleşmesi; sabit kodlanmaz, `DxfLayerProfile` ile yapılandırılır.

## 1. `DxfLayerProfile`

| Alan | Not |
|---|---|
| `id`, `tenant_id`, `name` | |
| `direction` | `IMPORT \| EXPORT \| BOTH` |
| `dxf_version` | çıkışta `R12` (Faz 0 sabit) |
| `unit` | `MM` (float, çıkışta); giriş için `MM \| INCH` |
| `origin` | `BOTTOM_LEFT` (ADR-0006; giriş DXF'i farklıysa dönüşüm) |
| `rules[]` | katman kuralı listesi (bölüm 2) |
| `face2_strategy` | `SEPARATE_FILE \| LAYER_PREFIX \| MIRROR_X` ⚠️ |
| `is_template` | ürünle gelen şablon |

## 2. Katman kuralı (`rules[]`)

```
rule
  op_type: OUTLINE | DRILL | GROOVE | NOTCH | POCKET | SAW_CUT | CHAIN_COMP_IN | CHAIN_COMP_OUT | START_POINT | LABEL_TEXT
  layer_pattern: str        # çıkışta şablon, girişte regex
  params_from_name: {...}   # katman adından parametre çıkarma (regex grupları)
  entity: POLYLINE | CIRCLE | LINE | POINT | TEXT
  color: int | null
```

Örnek (genel konvansiyon, **ürünle gelen varsayılan şablon**; gerçek makineyle doğrulanacak ⚠️):

| op_type | layer_pattern (export) | import regex | entity |
|---|---|---|---|
| OUTLINE | `OUTLINE` | `^(OUTLINE\|CONTOUR\|0)$` | POLYLINE (kapalı) |
| DRILL | `D{diameter_mm}_{depth_mm}` | `^D(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)$` | CIRCLE |
| DRILL (through) | `DT{diameter_mm}` | `^DT(\d+(?:\.\d+)?)$` | CIRCLE |
| GROOVE | `G{width_mm}_{depth_mm}` | `^G(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)$` | LINE (merkez çizgisi) |
| NOTCH / POCKET | `P{depth_mm}` | `^P(\d+(?:\.\d+)?)$` | POLYLINE (kapalı) |
| CHAIN_COMP_IN | `COMPIN` | | POLYLINE |
| CHAIN_COMP_OUT | `COMPOUT` | | POLYLINE |
| START_POINT | `START` | | POINT |
| LABEL_TEXT | `LABEL` | | TEXT |

> ⚠️ DOĞRULANMADI: Sektörde `D8_15`, `BOHR8_15`, `DRILL_8_15`, `H8D15` gibi çok sayıda varyant vardır; referans müşterinin makinesi hangisini bekliyor bilinmiyor. Varsayılan şablon yalnızca bir başlangıç noktasıdır.

## 3. Çıkış üreticisi

- Girdi: `OptimizationRun.input_snapshot` içindeki parça + `PartOperation[]` (bitmiş ölçü referanslı) + profil.
- Her parça için: `OUTLINE` = ham ölçü dikdörtgeni (0,0)-(raw_length, raw_width). Operasyonlar bitmiş ölçüye göre yazıldığından ham dış hata **ofset** uygulanır: `x' = x − band(W1)`, `y' = y − band(L1)` ⚠️ DOĞRULANMADI (bazı atölyeler önce bantlayıp sonra deler; o zaman dış hat = bitmiş ölçü ve ofset 0. Profilde `machining_stage: BEFORE_BANDING | AFTER_BANDING` alanı ile seçilir).
- Face2 operasyonları: profil `face2_strategy`'ye göre ayrı dosya (`<label>_F2.dxf`) veya `F2_` katman öneki.
- µm → mm dönüşümü **yalnızca burada**, `Decimal` ile, `0.001` hassasiyet.
- R12: `LWPOLYLINE` yok → `POLYLINE` + `VERTEX` + `SEQEND`. Yay: `ARC` veya bulge'lu vertex. Spline yok.
- Dosya adı: `{order_number}_{part_label}_{seq}.dxf`; toplu: zip.
- Plaka düzeyinde DXF (yerleşim çizimi) ayrı bir `kind`: her parça bir blok, kesik çizgileri `CUT_{level}` katmanı ⚠️ makine (beam saw) formatı istiyorsa Faz 3 post-processor.

## 4. Giriş

- Her `INSERT`/blok veya her kapalı `OUTLINE` polyline = bir parça adayı.
- Bounding box → `length/width` (birim dönüşümü, µm'ye yuvarlama `round half up`).
- Dikdörtgen olmayan dış hat: Faz 0'da `IMPORT_NON_RECTANGULAR_OUTLINE`; kullanıcı bounding box'ı kabul eder veya satırı atar.
- Diğer katmanlar `rules[]` ile `PartOperation`'a çevrilir; eşleşmeyen katman `IMPORT_UNKNOWN_LAYER` uyarısı.

## 5. Round-trip testi

Export → import (aynı profil) → operasyon listesi ve ölçüler orijinale eşit (µm toleransı 1). ADR-0016 §5.
