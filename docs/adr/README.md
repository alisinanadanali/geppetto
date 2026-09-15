# Mimari Karar Kayıtları (ADR)

Format: `0000-adr-template.md` (MADR uyarlaması). Dil Türkçe; kod/şema/alan adları İngilizce.

## Kurallar

- Numara sıralı, asla yeniden kullanılmaz. Yeni ADR = sonraki numara.
- Durum yaşam döngüsü: `Önerildi → Kabul edildi → Kullanımdan kaldırıldı | Yerine geçen: ADR-XXXX`.
- Kabul edilmiş ADR **düzenlenmez**; değişiklik yeni ADR ile yapılır ve eskisi "Yerine geçen" alır. Yazım hatası ve bağlantı düzeltmesi serbest.
- Her ADR'de `Doğrulanmamış varsayımlar` bölümü zorunlu; boşsa "Yok."
- Kod bir ADR ile çelişiyorsa kod yanlıştır; ADR değişecekse önce ADR.

## İndeks

| No | Başlık | Durum | Tarih |
|---|---|---|---|
| [0001](0001-modular-monolith-hexagonal.md) | Modüler monolit + hexagonal (ports & adapters) | Kabul edildi | 2026-09-13 |
| [0002](0002-integer-micron-units.md) | Tüm uzunluklar tam sayı mikron (µm) | Kabul edildi | 2026-09-13 |
| [0003](0003-stock-as-append-only-ledger.md) | Stok append-only hareket defteri | Kabul edildi | 2026-09-13 |
| [0004](0004-offcut-first-class-entity.md) | Artık birinci sınıf stok kalemi | Kabul edildi | 2026-09-13 |
| [0005](0005-optimization-run-immutable.md) | `OptimizationRun` değişmez belge | Kabul edildi | 2026-09-13 |
| [0006](0006-part-geometry-and-coordinate-convention.md) | `Part` geometrisi; koordinat, origin, Face1/Face2, L1/L2/W1/W2 konvansiyonu | Kabul edildi | 2026-09-13 |
| [0007](0007-multitenancy-rls.md) | Multi-tenancy: tek DB + `tenant_id` + PostgreSQL RLS | Kabul edildi | 2026-09-13 |
| [0008](0008-material-single-table-jsonb.md) | Malzeme tek tablo + `attrs JSONB` | Kabul edildi | 2026-09-13 |
| [0009](0009-finished-dimension-source-of-truth.md) | Bitmiş ölçü tek doğru kaynak; ham türetilir | Kabul edildi | 2026-09-13 |
| [0010](0010-i18n-from-day-one.md) | i18n ilk günden; hata kodu; kanonik depolama | Kabul edildi | 2026-09-13 |
| [0011](0011-solver-pure-versioned-package.md) | Solver saf, izole, sürümlü paket | Kabul edildi | 2026-09-13 |
| [0012](0012-import-mapping-profiles.md) | İthalat: eşleme profili, önizleme-düzeltme | Kabul edildi | 2026-09-13 |
| [0013](0013-dxf-layer-convention-configurable.md) | DXF katman konvansiyonu yapılandırılabilir | Kabul edildi | 2026-09-13 |
| [0014](0014-technology-stack.md) | Teknoloji yığını (FastAPI, PostgreSQL, React, uv, arq, S3, JWT) | Kabul edildi | 2026-09-13 |
| [0015](0015-local-agent-port.md) | Yerel ajan portu bugünden tanımlı | Kabul edildi | 2026-09-13 |
| [0016](0016-testing-strategy.md) | Test stratejisi: property-based, golden set, RLS | Kabul edildi | 2026-09-13 |
| [0017](0017-machine-cut-station.md) | `Machine` (kesim istasyonu): kerf/trim/kabiliyet sahibi | Kabul edildi | 2026-09-13 |

## Açık doğrulamalar

Tüm `⚠️ DOĞRULANMADI` işaretlerinin toplu listesi. Kapanınca ilgili dokümandaki işaret kaldırılır ve burada tarih yazılır.

| # | Konu | Nerede | Nasıl doğrulanır |
|---|---|---|---|
| V1 | Adeko dışa aktarma formatı (dosya tipi, kolonlar, birim, bant, ölçü esası) | ADR-0012, import-profiles.md §5, dimensions.md §5, ADR-0009 | Referans müşteriden 3 örnek dosya + sürüm |
| V2 | Referans müşterinin yüz/kenar adlandırması ADR-0006 ile çakışıyor mu | ADR-0006 | Örnek dosya ve saha görüşmesi |
| V3 | Makinenin beklediği DXF katman adları, delik gösterimi, DXF kabul edip etmediği | ADR-0013, dxf-conventions.md, cnc-roadmap.md | Örnek makine dosyası |
| V4 | ezdxf R12 yazımı ve POLYLINE üretimi | ADR-0013 | İlk implementasyonda test |
| V5 | Operasyon koordinatlarında ham/bitmiş ofseti (bantlama öncesi mi sonrası mı işleniyor) | dimensions.md §6, dxf-conventions.md §3 | Müşteri iş akışı |
| V6 | OR-Tools'un giyotin için faydası; Python sezgiselinin 500 parça süresi | ADR-0011 | Golden set kıyası |
| V7 | Golden set yok | ADR-0016, testing-strategy.md | Müşteri listeleri + Adeko planı |
| V8 | asyncpg + SQLAlchemy async havuzunda `SET LOCAL` güvenilirliği | ADR-0007 | Entegrasyon testi |
| V9 | JSONB anlık görüntü boyutu (1000+ parça) | ADR-0005 | Ölçüm |
| V10 | Varsayılan kerf 4 mm; müşterinin gerçek testere payı | ADR-0017 | Ölçüm |
| V11 | PDF/etiket kütüphanesi (barkod, Türkçe glif) | ADR-0014 | İlk implementasyon |
| V12 | Çoklu para birimi Faz 0 dışı varsayımı | ADR-0010 | Ürün kararı |
| V13 | Artık raf/etiket pratiği; artık barkodu Faz 0'da mı | ADR-0004 | Saha görüşmesi |
| V14 | Makine PC'si işletim sistemi ve ağ durumu | ADR-0015, target-users.md | Saha görüşmesi |
| V15 | `conversion` katsayısının `numeric` olması (µm kuralı dışı) | material-model.md §2 | Tasarım onayı |
| V16 | VENEER/CONSUMABLE `attrs` şeması boş | material-model.md §3 | Faz 2 |
| V17 | `edges` JSONB ile `EDGE_BAND` operasyon satırlarının ilişkisi (tek kaynak) | data-model.md `PartOperation` | İlk implementasyon |
| V18 | m² birimli hareketlerde `qty` ölçeği | data-model.md `StockMovement` | İlk implementasyon |
| V19 | Face2 stratejisi (ayrı dosya / önek / ayna) | dxf-conventions.md §1 | Makine dosyası |
| V20 | Menteşe kap derinliği; dengesiz panelde 90° kısıtı | cabinet-model-reference.md §3 | Faz 2 |
| V21 | Adeko'dan modül düzeyinde ithalat | cabinet-model-reference.md §4 | V1 ile birlikte |
| V22 | HOP formatının kaynağı | cnc-roadmap.md §3 | Faz 3 |
| V23 | Yerel ajan Faz 1 mi 2 mi | phases.md | Müşteri ihtiyacı |
| V24 | Referans müşteri makine parkı, Adeko sürümü, hacim | target-users.md | Saha görüşmesi |
| V25 | Çevrimdışı tolerans kapsamı | target-users.md | Ürün kararı |
| V26 | Yazı tipi lisansı ve Türkçe glif | design-direction.md §1 | Seçimde |
| V27 | Manuel yerleşim düzeltmede giyotin doğrulaması | design-direction.md §5 | İlk implementasyon |
| V28 | µm/µm²/minor değerlerinin API'de JS güvenli tam sayı sınırında (2⁵³−1) kalması; toplu işte toplam alan (≈1500 plaka) sınırı aşabilir | `geppetto_domain/units.py`, ADR-0002 | Bölüm 4 metrikleri ve bölüm 5.9 üretilmiş TS istemcisinde ölçüm |
