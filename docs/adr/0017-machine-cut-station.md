# ADR-0017: Kerf, trim ve kesim kabiliyetlerinin sahibi olarak `Machine` (kesim istasyonu) varlığını tanımla

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

ADR-0009 "kerf makine özelliğidir, malzeme özelliği değil" der; ancak tasarım oturumunun veri modelinde kerf'i taşıyan bir varlık yoktu. Kerf tenant ayarına veya koşu parametresine konursa, ikinci makine (örn. yatay panel testeresi + CNC router) geldiğinde taşınmak zorunda kalır. Ayrıca maksimum plaka ölçüsü ve giyotin/nesting kabiliyeti de makineye aittir.

## Karar

- `machines` tablosu (tenant izoleli):

| Alan | Tip | Not |
|---|---|---|
| `id`, `tenant_id` | UUID | |
| `name` | text | "Panel testere 1" |
| `kind` | `PANEL_SAW \| CNC_ROUTER \| BEAM_SAW \| MANUAL` | |
| `kerf_um` | bigint | testere payı |
| `default_trim_um` | `{left, right, top, bottom}` | plaka bazlı trim yoksa bu |
| `max_sheet_length_um`, `max_sheet_width_um` | bigint | tezgah sınırı |
| `capabilities` | `{guillotine: bool, nesting: bool, drilling: bool}` | hangi solver modu |
| `post_processor` | nullable enum | Faz 3: `DXF_R12 \| MPR \| BPP \| CIX \| HOP` |
| `layer_profile_id` | nullable FK | ADR-0013 |
| `is_default` | bool | tenant başına bir |
| `is_active` | bool | |

- Faz 0: tenant kayıt olurken bir varsayılan makine oluşturulur (kullanıcı kerf'i girer; varsayılan öneri 4000 µm ⚠️).
- `CutJob.machine_id` zorunlu; solver kerf/trim/mod/max ölçüyü buradan alır ve `OptimizationRun.input_snapshot` içinde dondurur.
- Trim önceliği: `Material(SHEET).attrs.trim_edges_um` (plakaya özgü) > `Machine.default_trim_um`.

## Gerekçe

- Kerf'in doğru sahibi; ikinci makine migration'sız eklenir.
- Post-processor ve katman profili doğal olarak makineye bağlanır (Faz 3 hazırlığı).
- Koşu anlık görüntüsünde makine parametreleri donduğu için geçmiş plan değişmez.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Kerf tenant ayarında | Çok makineli atölyede yanlış; ikinci makinede taşınır. |
| Kerf koşu parametresinde (kullanıcı her seferinde girer) | Hata kaynağı; parametre sahibi yok. |
| Kerf malzemede | Testere değişince tüm malzemeler güncellenir; yanlış model. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** kerf/trim/kabiliyet tek yerde; Faz 3 post-processor makineye bağlanır.
- **Bedel:** Faz 0'da bir ekran daha (makine ayarları; tek makine için basit form).
- **Kodda zorlama:** `CutJob.machine_id NOT NULL`; solver request'te `kerf_um` zorunlu alan; malzemede `kerf` adında alan migration testinde reddedilir.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Varsayılan kerf önerisi (4 mm) yaygın panel testeresi değeridir; referans müşterinin gerçek testere payı ölçülmeli.

## İlgili ADR'ler

- ADR-0009 — kerf formülün dışında
- ADR-0011 — solver kerf'i request'ten alır
- ADR-0013 — katman profili makineye bağlı
- ADR-0005 — makine parametreleri koşuda donar
