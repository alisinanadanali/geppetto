# Malzeme Modeli

Tek `Material` varlığı. `type` alanı üç şeyi belirler: `attrs` doğrulaması (Pydantic discriminated union), stok birimi mantığı ve hangi optimizer'a gideceği. Bkz. ADR-0008.

## 1. Tipler

| `type` | Örnek | Stok mantığı | Optimizer | Faz |
|---|---|---|---|---|
| `SHEET` | suntalam, MDF, kontrplak, OSB | adet plaka (lot) + m² projeksiyonu | 2D giyotin | Faz 0 |
| `EDGE_BAND` | PVC/ABS bant | metre; rulo ile alınır | yok, metraj | Faz 0 |
| `HARDWARE` | menteşe, ray, kulp, vida | adet | yok, sayım | Faz 0 (basit) |
| `LINEAR` | masif, profil, çıta | metre | 1D kesim | şema Faz 0, çözücü Faz 1 |
| `VENEER` | kaplama | m² | 2D | Faz 2 |
| `CONSUMABLE` | tutkal, lake | kg / lt, katsayılı | yok | Faz 2 |

`type` oluşturulduktan sonra **değiştirilemez** (`MATERIAL_TYPE_IMMUTABLE`). Tip değişikliği = yeni malzeme + eskisini pasifleştirme.

## 2. Ortak kolonlar (tablo kolonu, JSONB değil)

| Alan | Tip | Not |
|---|---|---|
| `id` | UUID | |
| `tenant_id` | UUID | RLS |
| `code` | text | tenant içinde tekil (`UNIQUE(tenant_id, code)`) |
| `name` | text | |
| `type` | enum | değişmez |
| `catalog_ref` | text, nullable | dekor kataloğu bağlantı noktası; Faz 0'da serbest metin |
| `supplier` | text, nullable | |
| `supplier_code` | text, nullable | |
| `purchase_unit` | enum `PIECE \| ROLL \| M \| M2 \| KG \| L \| PACK` | satın alma birimi |
| `stock_unit` | enum (aynı küme) | tüketim birimi |
| `conversion` | numeric | 1 purchase_unit = `conversion` stock_unit (rulo 100 m → 100) |
| `unit_cost_minor` | bigint | para minor unit (kuruş) |
| `currency` | char(3) | ISO 4217 |
| `vat_rate_bp` | int | basis point (2000 = %20) |
| `price_date` | date | |
| `cost_method` | enum `LAST_PURCHASE \| WEIGHTED_AVG \| MANUAL` | |
| `density` | numeric, nullable | kg/m³ |
| `color_hex` | text, nullable | UI önizleme |
| `texture_ref` | text, nullable | S3 anahtarı |
| `is_active` | bool | |
| `notes` | text | |
| `tags` | text[] | |
| `attrs` | JSONB | tipe özgü alanlar (bölüm 3) |
| `created_at / updated_at` | timestamptz | UTC |

> ⚠️ DOĞRULANMADI: `conversion` için `numeric` seçildi çünkü bant rulosu "100 m" gibi tam olmayabilir; ölçü µm kuralı yalnızca uzunluk alanlarına uygulanır, dönüşüm katsayılarına değil. Bu ayrım ADR-0002'de yazılı.

## 3. `attrs` şemaları (Pydantic discriminated union, `type` ayırıcı)

### `SHEET`

```json
{
  "thickness_um": 18000,
  "standard_sizes": [
    {"length_um": 2800000, "width_um": 2100000, "price_minor": null, "stock": null}
  ],
  "grain": "NONE | LENGTHWISE",
  "two_faced": true,
  "trim_edges_um": {"left": 10000, "right": 10000, "top": 10000, "bottom": 10000},
  "oversize_length_um": 0,
  "oversize_width_um": 0,
  "min_offcut_length_um": 200000,
  "min_offcut_width_um": 100000,
  "default_edge_band_id": null,
  "rotation_default": "NONE | ROT_180 | ROT_90 | ANY"
}
```

- `standard_sizes[].length_um` damar yönündeki ölçüdür (`grain = LENGTHWISE` ise).
- `oversize_*` plakada normalde 0; alan LINEAR/VENEER ile şema paylaşımı için burada da var.
- `min_offcut_*` malzeme bazlı eşik; yoksa `Tenant.settings.min_offcut_*` geçerli. Öncelik: malzeme > tenant.
- `rotation_default`: parçaya `rotation` verilmediğinde uygulanan varsayılan. Damarlı plakada `NONE` veya `ROT_180`.

### `EDGE_BAND`

```json
{
  "thickness_um": 800,
  "widths_um": [22000, 45000],
  "roll_length_um": 100000000,
  "edge_reduction_policy": "NONE | BY_THICKNESS",
  "length_allowance_per_part_um": 30000,
  "price_per_m_minor": 1250
}
```

Kabul edilen kalınlıklar serbesttir; yaygın değerler 400 / 800 / 1000 / 2000 µm. Doğrulama yalnızca `> 0`.

### `HARDWARE`

```json
{
  "brand": "…",
  "model": "…",
  "unit_price_minor": 4500,
  "pack_size": 50,
  "machining_ref": null
}
```

`machining_ref`: Faz 2 için bugünden açılan boş alan. İleride bir `MachiningTemplate` kaydına bağlanacak (örn. menteşe → 35 mm kap + 32 mm aralıklı 2×8 mm vida deliği). Faz 0'da her zaman null.

### `LINEAR`

```json
{
  "profile": "text",
  "cross_section_um": {"width": 60000, "height": 20000},
  "stock_lengths_um": [2000000, 3000000],
  "oversize_length_um": 20000,
  "grain": "LENGTHWISE"
}
```

### `VENEER`, `CONSUMABLE`

> ⚠️ DOĞRULANMADI: Faz 2 tipleri. Şema şimdilik boş nesne `{}`; discriminated union içinde yer ayrılır, alan eklenmez.

## 4. Stok davranışı tipe göre

| `type` | `StockItem` satırı | Hareket birimi |
|---|---|---|
| `SHEET` | her lot bir satır; her artık ayrı satır (`is_offcut`) | adet |
| `EDGE_BAND` | rulo başına satır opsiyonel; genelde tek havuz | µm (uzunluk) |
| `HARDWARE` | tek havuz | adet |
| `LINEAR` | boy başına lot | adet (boy) — Faz 1 |

## 5. UI notu

Malzeme oluşturma formu **kademeli açılım**: (1) tip seçilir, (2) ortak alanların zorunlu alt kümesi (`code`, `name`, birimler, fiyat), (3) tipin `attrs` alanları, (4) isteğe bağlı alanlar katlanabilir bölümde. 40 alanlı tek ekran yok.

## 6. Seed verisi

Yazılmayacak. Şema hazır; kayıtları kullanıcı girer veya ileride dekor kataloğu ithalatı doldurur.
