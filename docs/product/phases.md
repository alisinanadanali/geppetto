# Faz Planı ve Kapsam Dışı Kararlar

## Faz 0 — kama (şimdi)

Referans müşterinin iki darboğazını çözen en küçük ürün: stok kaydı ve Adeko listesinden doğrudan optimizasyon.

| # | Kapsam | Ana doküman |
|---|---|---|
| 1 | Malzeme ve plaka stok kayıtları (append-only defter) | ADR-0003, material-model.md |
| 2 | Dışarıdan parça listesi alma: Adeko çıktısı + Excel/CSV + DXF, eşleme profili, önizleme-düzeltme | ADR-0012, import-profiles.md |
| 3 | Giyotin kesim optimizasyonu (saf solver) | ADR-0011 |
| 4 | Artık yönetimi (birinci sınıf stok kalemi) | ADR-0004 |
| 5 | Kesim planı çıktısı: PDF + parça etiketi/barkod + R12 DXF + CSV | ADR-0013, dxf-conventions.md |
| 6 | Stok düşümü (onaylı koşu → hareketler) | ADR-0003, ADR-0005 |
| 7 | Basit sipariş / müşteri kaydı ve proje maliyeti (tek para birimi) | data-model.md |
| 8 | Çok siparişli (batch) toplu nesting (`CutJob`) | data-model.md |
| 9 | Makine (kesim istasyonu) tanımı: kerf, trim | ADR-0017 |
| 10 | tr + en, Türkiye ülke portu | ADR-0010 |

Faz 0 bitiş kriteri: referans müşteri bir haftalık gerçek işini Geppetto'dan kesiyor; stok raporu gerçek rafla tutuyor; doluluk Adeko planından kötü değil (golden set).

## Faz 1

- Teklif / fiyatlandırma motoru (malzeme + işçilik + kâr kuralları)
- Planlama (iş sırası, makine takvimi)
- Müşteri onay portalı (teklif/çizim onayı)
- Atölye mobil ekranı (etiket okut → parça durumu)
- Yerel ajan ilk sürüm (ADR-0015) ⚠️ Faz 1 mi 2 mi: müşteri ihtiyacına göre
- 1D (LINEAR) çözücü
- Çoklu para birimi / kur

## Faz 2 — ödün verilmez

Kendi parametrik çizim/CAD modülümüz: Adeko'nun işlevini yapan kural motoru (`cabinet-model-reference.md`).
**Faz 0 veri modeli bu modülü şema değiştirmeden kabul edecek** — mimarinin birinci kısıtı. Bugünden açık alanlar: `Module`, `Part.module_id/outline`, `PartOperation`, `machining_ref`, koordinat konvansiyonu (ADR-0006).

## Faz 3+

- AI görselleştirme: difüzyon + ControlNet (LLM değil); çizimden fotogerçekçi render
- CNC marka post-processor'leri: MPR / BPP / CIX / HOP (cnc-roadmap.md)
- Ön muhasebe entegrasyonu (`AccountingPort`, `FiscalPort`)
- CRM
- Serbest (true-shape) nesting

## Kapsam dışı — bilinçli kararlar

| Karar | Gerekçe | Bırakılan port / alan |
|---|---|---|
| Tam muhasebe yazılmayacak | Ürün alanı değil; hazır çözümler var | `AccountingPort`, `FiscalPort` (Faz 3); `StockMovement.unit_cost_minor` mutabakat için |
| Dekor kataloğu yok (Kastamonu/AGT vb.) | Veri lisansı ve bakım; Faz 0 değeri düşük | `Material.catalog_ref` |
| Seed verisi yok | Şema hazır; kayıtları kullanıcı girer | — |
| True-shape nesting yok, v1 = giyotin | Panel testeresi pazarın çoğunluğu; algoritma karmaşıklığı | `Machine.capabilities.nesting`, `Part.outline` |
| Harici IdP yok | Faz 0 maliyet | `AuthPort` |
| Mikroservis yok | Tek kişilik ekip | — |
| Yerel ajan kodu yok (Faz 0) | Kapsam | `FileDeliveryPort`, `ExportArtifact.delivery_status` |
