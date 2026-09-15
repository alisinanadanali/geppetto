# ADR-0005: `OptimizationRun`'ı değişmez bir belge olarak sakla

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Kesim planı üretildikten sonra malzeme parametreleri (bant kalınlığı, trim, kerf), parça listesi veya stok değişebilir. Atölye geçmiş planı yeniden basmak, destek ekibi "neden böyle yerleşti" sorusunu cevaplamak, geliştirici solver sürümlerini kıyaslamak ister. Bunların hepsi girdinin ve çıktının o anki haliyle korunmasını gerektirir.

## Karar

`optimization_runs` satırı oluşturulduktan sonra **güncellenmez**. İçeriği:

| Alan | İçerik |
|---|---|
| `cut_job_id` | hangi kesim işi |
| `input_snapshot` (JSONB) | parçalar (bitmiş **ve** hesaplanmış ham ölçüler, kenar bantları, rotation, grain), plaka/artık listesi (ölçü, trim, `stock_item_id`), makine (kerf), koşu parametreleri (mod, artık tercihi, zaman sınırı) |
| `solver_name`, `solver_version` | semver, paketten okunur |
| `output` (JSONB) | plaka başına yerleşimler, kesik sırası, üretilen artıklar |
| `metrics` (JSONB) | plaka sayısı, doluluk, fire alanı, artık alanı, kesik sayısı, süre |
| `status` | `QUEUED \| RUNNING \| SUCCEEDED \| FAILED \| CANCELLED` — koşunun **kendi** yaşam döngüsü; içerik değil |
| `error_code` | başarısızlıkta |
| `created_by`, `created_at`, `finished_at` | |

- `status`, `finished_at`, `output`, `metrics` yalnızca `QUEUED/RUNNING → terminal` geçişinde bir kez yazılır; sonrası salt okunur.
- Bir `CutJob` birden çok koşu üretebilir (farklı parametre, farklı solver sürümü); biri `approved_run_id` olarak işaretlenir.
- Stok düşümü koşunun içinde değil, **onay** eylemindedir: `CONSUME` / `OFFCUT_IN` hareketleri `reference_id = run.id` ile ayrı yazılır (ADR-0003).
- Export çıktıları (PDF/DXF/CSV) `input_snapshot + output`'tan üretilir; canlı tablolardan değil.

## Gerekçe

- Tekrar üretilebilirlik: aynı `input_snapshot` + aynı `solver_version` = aynı çıktı; bu golden test tabanıdır.
- Destek yükü: "plan değişti" şikayeti yapısal olarak imkânsız.
- Solver kıyaslaması: aynı girdi, iki sürüm, metrik tablosu.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Koşuyu canlı parça/stok tablolarına FK ile bağlamak | Kaynak değişince plan anlamını yitirir. |
| Yalnızca çıktıyı saklamak | Girdi olmadan yeniden üretim ve kıyas imkânsız. |
| Her koşuda parça tablosunun kopyasını almak (ayrı tablolar) | JSONB anlık görüntü aynı işi tek satırda yapar; şema büyümez. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** determinizm, denetlenebilirlik, güvenli solver evrimi.
- **Bedel:** JSONB büyüklüğü (500 parçalık iş ≈ yüzlerce KB); eski koşuların arşivlenmesi Faz 1+ konusu. Anlık görüntü şemasının sürümlenmesi gerekir (`snapshot_schema_version`).
- **Kodda zorlama:** uygulama rolünde `optimization_runs` üzerinde yalnızca terminal geçiş kolonlarını hedefleyen `UPDATE`; trigger ile `input_snapshot`/`output` değişimi reddedilir.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: JSONB anlık görüntü boyutunun büyük batch işlerinde (1000+ parça) pratik sınırı ölçülmedi.

## İlgili ADR'ler

- ADR-0003 — stok düşümü ayrı hareket
- ADR-0009 — ham ölçüler anlık görüntüde donar
- ADR-0011 — `solver_version` kaynağı
- ADR-0016 — golden testler bu belgeyi kullanır
