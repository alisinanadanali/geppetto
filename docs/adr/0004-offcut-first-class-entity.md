# ADR-0004: Artığı (offcut) birinci sınıf stok kalemi olarak modelle

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Giyotin kesimde her plakadan kullanılabilir artıklar kalır. Atölyeler bunları köşede biriktirir ve çoğunlukla kaybeder. Artığı sonraki kesim işinde plaka olarak sunmak doluluk oranını doğrudan artırır. Artık, tam plakadan farklı olarak **tekil**dir: her birinin kendi ölçüsü vardır ve bir kez kullanılır.

## Karar

- Artık, plaka stoğuyla **aynı tabloda** (`stock_items`) saklanır: `is_offcut = true`, `origin_cut_plan_id` (hangi `OptimizationRun` / plaka üretti), `length_um`, `width_um`, `material_id`.
- Tam plaka lotu da `stock_items` satırıdır (`is_offcut = false`, ölçü = standart plaka ölçüsü, adet hareketlerden).
- Artık her zaman `qty = 1`'lik tek kalemdir.
- Yaşam döngüsü `available → reserved → consumed → scrapped`, **hareketlerden projeksiyon** (ADR-0003). Geçişler:
  - `OFFCUT_IN` → available
  - `RESERVE` → reserved; `RELEASE` → available
  - `CONSUME` → consumed (bu artıktan yine artık çıkabilir: yeni satır, `origin_cut_plan_id` yeni koşu)
  - `SCRAP` → scrapped
- Minimum kullanılabilirlik eşiği: `Tenant.settings.min_offcut_length_um / width_um` varsayılan; `Material(SHEET).attrs.min_offcut_*` malzeme bazlı override. Öncelik: malzeme > tenant. Eşik altı artık `OFFCUT_IN` üretmez; fire sayılır.
- Solver'a artıklar plaka listesinde `is_offcut` bayrağıyla verilir; tercih politikası (önce artık / önce tam plaka) koşu parametresidir.

## Gerekçe

- Aynı tablo: solver için "kesilebilir dikdörtgen" tek tiptir; artık/plaka ayrımı yalnızca bayraktır.
- Tekil kalem: artığın ölçüsü ve kökeni kendine özgü; sayaç modeli anlamsız.
- Durumun projeksiyon olması ledger ilkesini korur; `status` kolonu ile hareketlerin ayrışma riski sıfırlanır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Ayrı `offcuts` tablosu | Solver iki kaynaktan plaka toplar; stok raporu birleşim ister. |
| `status` kolonu (denormalize) | İki doğru kaynak; tutarsızlık riski. Kullanıcı kararıyla reddedildi. |
| Artığı stoklamamak (fire say) | Ürünün temel değer önerisini yok eder. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** artık otomatik olarak sonraki işe girer; izlenebilirlik tam.
- **Bedel:** `stock_items` tablosu artık sayısı kadar büyür; eşik doğru ayarlanmazsa gürültü. "Şu an kullanılabilir artıklar" sorgusu projeksiyon view'ından gelir.
- **Kodda zorlama:** `stock_items.is_offcut = true` iken `origin_cut_plan_id NOT NULL` check constraint; property testi "artık alanı + parça alanı + fire = plaka alanı" (ADR-0016).

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Referans müşterinin artık için fiziksel raf/etiket pratiği bilinmiyor. Etiket çıktısına artık barkodu eklenmesi (artığı rafta bulmak için) Faz 0 kapsamında varsayıldı; müşteriyle doğrulanacak.

## İlgili ADR'ler

- ADR-0003 — durum projeksiyonu ve hareket tipleri
- ADR-0005 — `origin_cut_plan_id` donmuş koşuya işaret eder
- ADR-0016 — alan korunumu değişmezi
