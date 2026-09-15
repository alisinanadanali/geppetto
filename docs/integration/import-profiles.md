# İthalat: Eşleme Profilleri ve `PartListDocument v1`

ADR-0012'nin operasyonel hali. Sabit adaptör yok; kullanıcı profil tanımlar, kaydeder, tekrar kullanır.

## 1. Akış

```
dosya (CSV/XLSX/DXF) → parser (ham tablo / katmanlar)
                     → ImportProfile uygula → PartListDocument v1 (+ satır uyarıları)
                     → ÖNİZLEME-DÜZELTME ekranı (kullanıcı onayı zorunlu)
                     → ImportBatch.COMMITTED → Part satırları
```

Onaysız `Part` yazan API ucu yoktur.

## 2. `ImportProfile`

| Alan | Tip | Not |
|---|---|---|
| `id`, `tenant_id`, `name` | | |
| `source_kind` | `CSV \| XLSX \| DXF` | |
| `parser_options` | JSONB | CSV: ayırıcı, kodlama, başlık satırı; XLSX: sayfa adı, başlık satırı; DXF: katman profili id |
| `unit` | `MM \| UM \| INCH` | ölçü kolonlarının birimi |
| `decimal_separator` | `.` veya `,` | Türkçe Excel `,` |
| `column_map` | JSONB | kaynak kolon → hedef alan (bölüm 3) |
| `edge_map` | JSONB | bant kolonlarının yorumu (bölüm 4) |
| `material_map` | JSONB | kaynak malzeme adı/kodu → `material_id`; eşleşmeyen → önizlemede seçilir |
| `dimension_basis_hint` | `FINISHED \| RAW \| null` | **yalnızca öneri**; onay ekranında kullanıcı seçer |
| `default_rotation`, `default_grain` | | kolon yoksa |
| `is_template` | bool | ürünle gelen şablon (kopyalanır, düzenlenemez) |

## 3. `PartListDocument v1` (`packages/geppetto-contracts`)

```
PartListDocument
  schema_version: "1"
  dimension_basis: FINISHED | RAW          # ZORUNLU, varsayılan yok
  unit_note: str                           # kaynaktaki birim (bilgi)
  source: {profile_id, file_name, file_hash, imported_at}
  rows: PartListRow[]

PartListRow
  row_index: int
  label: str
  material_ref: str                        # kaynaktaki ad/kod
  material_id: UUID | null                 # eşlendiyse
  length_um: int                           # dimension_basis'e göre bitmiş veya ham
  width_um: int
  thickness_um: int | null
  qty: int
  edges: {L1: EdgeRef|null, L2, W1, W2}   # EdgeRef = {material_ref, material_id|null}
  rotation: NONE|ROT_180|ROT_90|ANY | null
  grain: NONE|ALONG_LENGTH|ALONG_WIDTH | null
  project_ref: str | null                  # kaynaktaki proje/dolap adı
  notes: str | null
  warnings: [{code, params}]               # IMPORT_* hata kodları
```

Hedef alanlar `column_map`'te: `label, material_ref, length, width, thickness, qty, edge_L1, edge_L2, edge_W1, edge_W2, edge_count, grain, project_ref, notes`.

## 4. Kenar bandı yorumlama (`edge_map`)

Kaynak listelerde bant çoğunlukla dört ayrı kolonda (0/1 veya bant kodu) ya da tek "bant sayısı" kolonunda gelir.

| Kaynak biçimi | `edge_map` stratejisi | Uyarı |
|---|---|---|
| Dört kolon (L1, L2, W1, W2) | doğrudan eşleme; kaynak kenar adı → bizim kenar (örn. "Uzun1" → L1) | — |
| Tek sayı (0–4) | `edge_count_policy`: `2 → L1+L2`, `3 → L1+L2+W1`, `4 → hepsi`, `1 → L1` | `IMPORT_EDGE_COUNT_AMBIGUOUS` her satırda; kullanıcı önizlemede düzeltir |
| Bant kodu tek kolon ("PVC 0.8 beyaz") | `material_map` ile bant malzemesine eşle, kenar seçimi `edge_count_policy` | aynı |
| Bant bilgisi yok | `default_edge_band_id` (malzemeden) veya bantsız | `IMPORT_EDGES_MISSING` |

Kaynak kenar adlandırması bizimkiyle çakışırsa **konvansiyon değişmez** (ADR-0006); eşleme profilde yapılır.

## 5. Adeko — bilinmiyor

> ⚠️ DOĞRULANMADI: Adeko'nun dışa aktarma formatı elimizde değil. Bu bölümde **hiçbir alan adı uydurulmamıştır.**

Bilinmeyenler:
- Dosya tipi (CSV? XLSX? XML? kendi formatı? DXF parça çıktısı?)
- Kolon adları ve sırası; Türkçe/İngilizce
- Birim ve ondalık ayırıcı
- Ölçü esası (bitmiş mi ham mı; bant düşülmüş mü)
- Bant gösterimi (4 kolon mu, sayı mı, kod mu)
- Damar/döndürme bilgisi var mı
- Parça → dolap/modül referansı var mı
- Sürüm ve lisans farkları çıktıyı değiştiriyor mu

**Doğrulama planı:**
1. Referans müşteriden en az 3 örnek dışa aktarım al: küçük iş (1 dolap), orta iş (mutfak), bantlı/bantsız karışık. Adeko sürüm numarasıyla birlikte.
2. Aynı işlerin Adeko'da üretilmiş kesim planı çıktısını al (golden set ve ölçü esası tespiti için).
3. Bir parçanın ölçüsünü Adeko ekranında ve dosyada karşılaştırarak `dimension_basis`'i tespit et.
4. İlk "Adeko vX" profil şablonu bu dosyalardan yazılır; `is_template = true`.
5. Farklı sürüm/lisanslı ikinci bir Adeko kullanıcısı bulunursa şablon çeşitlenir.

## 6. Önizleme-düzeltme ekranı gereksinimleri

- `dimension_basis` seçimi ekranın en üstünde, onaysız geçilemez.
- Satır bazlı uyarılar (hata kodu + çeviri); satır içi düzenleme (ölçü, malzeme, kenar).
- Eşleşmeyen malzeme → seçim veya "yeni malzeme oluştur" (kademeli form).
- Türetilen ham ölçü sütunu canlı gösterilir (kullanıcı formülün etkisini görür).
- "Tümünü onayla" yalnızca sıfır hata (uyarı kabul) ile aktif.

## 7. DXF girişi

Katman → operasyon eşlemesi `DxfLayerProfile` ile (bkz. `dxf-conventions.md`). DXF'ten gelen parça: dış hat bounding box → ölçü; `outline` Faz 0'da yine null (dikdörtgen dışı DXF `IMPORT_NON_RECTANGULAR_OUTLINE` uyarısıyla reddedilir veya bounding box'a indirgenir — kullanıcı seçer).
