# Geppetto — Proje Adımları (todo)

Sıra bağımlılığa göredir; bir adım bitmeden sonrakine geçilmez. Her adımın kaynağı `docs/` altındaki dokümandır; kod dokümanla çelişirse kod yanlıştır.
İşaretleme: `[ ]` yapılmadı · `[~]` sürüyor · `[x]` bitti (tarih) · `[!]` bloke (neden)

Kural: bir adım bitince (1) ilgili test geçer, (2) `docs/adr/README.md` açık doğrulama tablosu güncellenir, (3) öğrenilen varsa `lessons.md`'ye yazılır.

---

## 0. Saha doğrulaması (kod öncesi, referans müşteri)

Kaynak: `docs/adr/README.md` açık doğrulamalar V1–V3, V7, V10, V13, V14, V24

- [ ] 0.1 Adeko dışa aktarım örneği ×3 (küçük iş, mutfak, bantlı/bantsız karışık) + Adeko sürüm numarası → V1
- [ ] 0.2 Aynı işlerin Adeko kesim planı çıktısı (golden set tabanı) → V7
- [ ] 0.3 Bir parçanın Adeko ekran ölçüsü ile dosya ölçüsünü karşılaştır → `dimension_basis` tespiti → V1
- [ ] 0.4 Müşterinin yüz/kenar adlandırması ile ADR-0006 konvansiyonunu karşılaştır → V2 (konvansiyon değişmez; fark profile yazılır)
- [ ] 0.5 Makine parkı: panel testere modeli, CNC var mı, DXF kabul ediyor mu, beklediği katman adları, örnek makine dosyası → V3, V24
- [ ] 0.6 Gerçek kerf ölçümü → V10
- [ ] 0.7 Artık raf/etiket pratiği → V13
- [ ] 0.8 Makine PC'si işletim sistemi ve ağ durumu → V14
- [ ] 0.9 Bulguları ilgili dokümanlara işle; kapanan V maddelerine tarih yaz

## 1. Repo iskeleti

Kaynak: `docs/engineering/repo-structure.md`, ADR-0001, ADR-0014

- [x] (2026-09-15) 1.1 `git init`, ilk commit (dokümanlar)
- [x] (2026-09-15) 1.2 uv workspace kökü: `pyproject.toml`, ortak ruff/mypy/pytest ayarı
- [x] (2026-09-15) 1.3 Paket iskeletleri: `packages/geppetto-{domain,solver,contracts,ingest,export}` (boş `src/`, `tests/`, kendi `pyproject.toml`)
- [x] (2026-09-15) 1.4 Uygulama iskeletleri: `apps/{api,worker}`; `apps/web` (Vite + React + TS + pnpm; react-i18next + `no-literal-string` lint + eksik anahtar kontrolü öne alındı); `apps/agent/README.md`
- [x] (2026-09-15) 1.5 `infra/docker-compose.yml`: postgres, redis, minio (+ rol init: migrate/app/system, ADR-0007)
- [x] (2026-09-15) 1.6 import-linter kuralları: bağımlılık yönü (domain/solver → IO kütüphanesi yasak, solver → domain yasak)
- [x] (2026-09-15) 1.7 CI: lint + test + import-linter; PR şablonunda "ilgili ADR" alanı
- [x] (2026-09-15) 1.8 `tests/golden/`, `tests/rls/` dizinleri ve README

## 2. Sözleşmeler (`geppetto-contracts`)

Kaynak: ADR-0010, `docs/engineering/i18n.md`, `docs/integration/import-profiles.md` §3

- [x] (2026-09-15) 2.1 `error_codes.py`: tek enum; önekler `PART_ STOCK_ IMPORT_ SOLVER_ AUTH_ TENANT_ MATERIAL_ MACHINE_ EXPORT_`
- [x] (2026-09-15) 2.2 Ortak tipler (tanım `geppetto-domain`, contracts yeniden dışa aktarır; L-008): `Micron = Annotated[int]`, `Money(minor, currency)`, enum'lar (`MaterialType, Rotation, Grain, EdgeRef, FaceRef, MovementType, DimensionBasis`)
- [x] (2026-09-15) 2.3 `PartListDocument v1` + `PartListRow` (`dimension_basis` zorunlu, varsayılan yok)
- [x] (2026-09-15) 2.4 Şema testleri: geçersiz `dimension_basis` reddi, µm tam sayı zorunluluğu (+ katalog/JSON şema snapshot, round-trip; domain kod sabiti testi bölüm 3'te aktifleşir)

## 3. Domain çekirdeği (`geppetto-domain`)

Kaynak: ADR-0002, 0003, 0004, 0006, 0009; `docs/domain/dimensions.md`, `data-model.md`

- [ ] 3.1 Varlık tipleri (Pydantic, IO'suz): `Part, PartOperation, Material(+attrs union), Machine, StockItem, StockMovement, CutJob`
- [ ] 3.2 `dimensions.derive_raw_dimensions()` — formül; `PART_RAW_DIMENSION_NON_POSITIVE`
- [ ] 3.3 Örnek testleri: dimensions.md A–D birebir
- [ ] 3.4 Property testleri: bant ekle → yalnızca dik eksen küçülür; `edge_reduction_policy=NONE` → değişmez
- [ ] 3.5 Bant metrajı hesabı (bitmiş kenar + allowance stok tüketimine)
- [ ] 3.6 `stock.project()` — hareket listesi → seviye; artık durum geçişleri; geçersiz geçiş hatası
- [ ] 3.7 Material `attrs` discriminated union (SHEET, EDGE_BAND, HARDWARE, LINEAR; VENEER/CONSUMABLE boş)
- [ ] 3.8 `rotation`/`grain` tutarlılık doğrulaması (`PART_ROTATION_CONFLICTS_GRAIN`)
- [ ] 3.9 Paket bağımlılık kontrolü: yalnızca pydantic

## 4. Solver (`geppetto-solver`)

Kaynak: ADR-0011, ADR-0016, `docs/engineering/testing-strategy.md`

- [ ] 4.1 `types.py`: `OptimizeRequest / OptimizeResult` (kendi tipleri; domain import yok)
- [ ] 4.2 `invariants.py`: I1–I8 doğrulayıcı (`validate(request, result) -> [Violation]`)
- [ ] 4.3 Hypothesis stratejileri (`parts, sheets, machine, request`)
- [ ] 4.4 Property test seti — **algoritmadan önce** yazılır; ilk "solver" her şeyi tek plakaya sıralı koyan naif sürüm olabilir, testler onunla çalışmalı
- [ ] 4.5 v1 giyotin sezgiseli (level/strip veya guillotine-split) + artık üretimi + kerf/trim
- [ ] 4.6 Yerel arama / iyileştirme turu
- [ ] 4.7 Determinizm (seed), zaman sınırı parametresi
- [ ] 4.8 Semver ve `__version__`; `OptimizeResult.solver_version`
- [ ] 4.9 Golden set koşucusu + doluluk tablosu üretimi (CI yorumu)
- [ ] 4.10 (0.2 geldiyse) ilk golden case'ler; Adeko doluluğu ile kıyas
- [ ] 4.11 OR-Tools kıyası yalnızca golden set üzerinde; bağımlılık eklenmez → V6 kararı
- [ ] 4.12 500 parça süre ölçümü → V6

## 5. Veritabanı ve API temeli (`apps/api`)

Kaynak: ADR-0007, 0008, 0014, 0017; `docs/domain/data-model.md`

- [ ] 5.1 SQLAlchemy modelleri (UUID v7, `tenant_id`, UTC zaman damgaları, `BigInteger` µm alias)
- [ ] 5.2 Alembic: roller (`geppetto_migrate` sahip, `geppetto_app` sahip değil), her tenant tablosuna RLS + FORCE şablonu
- [ ] 5.3 Tenant middleware: `SET LOCAL app.tenant_id` işlem başında → V8 entegrasyon testi
- [ ] 5.4 RLS test seti (`tests/rls`): tablo listesi otomatik, iki tenant çapraz erişim, superuser koruması
- [ ] 5.5 Migration testi: `quantity` kolonu yasak, `raw_*` kolonu yasak, malzemede `kerf` yasak, RLS'siz tenant tablosu yasak
- [ ] 5.6 `stock_movements` üzerinde app rolüne UPDATE/DELETE yok; `optimization_runs` içerik değişimi trigger ile red
- [ ] 5.7 Auth: kendi JWT (`AuthPort`), access+refresh, tenant/kullanıcı kaydı, roller
- [ ] 5.8 Portlar: `StoragePort` (MinIO), `QueuePort` (arq), `CountryPort` (TR), `FileDeliveryPort` (DOWNLOAD)
- [ ] 5.9 OpenAPI snapshot testi; TS istemci üretim scripti

## 6. Faz 0 modülleri — backend

Sıra: malzeme → makine → stok → sipariş → ithalat → kesim işi → koşu → export → maliyet

- [ ] 6.1 Malzeme CRUD (`attrs` doğrulama, `type` değişmez, `code` tenant içinde tekil)
- [ ] 6.2 Makine CRUD; tenant kaydında varsayılan makine
- [ ] 6.3 Stok: mal kabul (`RECEIPT`), sayım (`ADJUST` + gerekçe), hurda (`SCRAP`), seviye ve artık projeksiyon view'ları
- [ ] 6.4 Müşteri / Sipariş / Proje / Parça CRUD (bitmiş ölçü, 4 kenar, rotation, grain)
- [ ] 6.5 `ImportProfile` CRUD; CSV/XLSX parser (`geppetto-ingest`); profil uygulama → `PartListDocument`
- [ ] 6.6 `ImportBatch`: önizleme (uyarılar, ham ölçü canlı), `dimension_basis` onayı, commit → `Part`; RAW akışında `finished_is_derived`
- [ ] 6.7 DXF girişi (katman profili, bounding box, `IMPORT_NON_RECTANGULAR_OUTLINE`)
- [ ] 6.8 `CutJob`: sipariş/parça bağlama (batch), plaka/artık seçimi, makine, params
- [ ] 6.9 Worker: anlık görüntü oluştur → `OptimizeRequest` → solver → `OptimizationRun` (değişmez) ; hata durumları
- [ ] 6.10 Koşu onayı: `approved_run_id`; `RESERVE`; kesim tamamlandı → `CONSUME` + `OFFCUT_IN` (eşik: malzeme > tenant)
- [ ] 6.11 Export (`geppetto-export`): PDF kesim planı, etiket/barkod (kütüphane seçimi → V11), R12 DXF (ezdxf → V4, operasyon→katman, round-trip testi), CSV
- [ ] 6.12 `ExportArtifact` + `FileDeliveryPort.DOWNLOAD` (presigned URL)
- [ ] 6.13 Proje maliyeti sorgusu (tek para birimi; `MATERIAL_CURRENCY_MISMATCH` uyarısı)

## 7. Faz 0 — frontend (`apps/web`)

Kaynak: `docs/ui/design-direction.md`, `docs/engineering/i18n.md`

- [ ] 7.1 Design token'ları (`design/tokens.ts`); lint: elle hex/px yasak
- [ ] 7.2 i18n altyapısı (tr/en, namespace'ler, `errors`, `glossary`); lint: çıplak metin yasak; CI: eksik anahtar
- [ ] 7.3 Biçimlendirme katmanı (`formatLength/Money/Date`)
- [ ] 7.4 Kabuk: sol modül rayı, üst bant, tek ekran iskeleti, klavye/erişilebilirlik temeli
- [ ] 7.5 Üretilmiş API istemcisi bağlantısı; auth akışı
- [ ] 7.6 Malzeme modülü (kademeli form)
- [ ] 7.7 Makineler modülü
- [ ] 7.8 Stok modülü (seviye, defter, artık havuzu kartları, mal kabul, sayım)
- [ ] 7.9 Sipariş/Müşteri modülü (sürükle-bırak: proje → sipariş, parça → proje)
- [ ] 7.10 İthalat modülü (profil, kolon eşleme çekmecesi, önizleme-düzeltme, `dimension_basis` onayı)
- [ ] 7.11 Kesim Planı modülü (plaka görselleştirme ölçek sadık, sürükle-bırak, koşu kıyası, onay, çıktılar)
- [ ] 7.12 Ayarlar (tenant, kullanıcı, dil, para birimi, artık eşiği)
- [ ] 7.13 Dokunmatik ve masaüstü testi; kontrast denetimi

## 8. Faz 0 kapanış

- [ ] 8.1 Referans müşteri bir haftalık gerçek işi Geppetto'dan keser
- [ ] 8.2 Stok raporu ile raf sayımı karşılaştırması
- [ ] 8.3 Golden tablo: doluluk Adeko'dan kötü değil
- [ ] 8.4 Açık doğrulamalar tablosu gözden geçirilir; kalanlar Faz 1'e taşınır
- [ ] 8.5 `lessons.md` özeti → gerekiyorsa yeni ADR

## 9. Faz 1 (başlıklar; ayrıntı Faz 0 sonunda planlanır)

- [ ] Teklif / fiyatlandırma motoru
- [ ] Planlama
- [ ] Müşteri onay portalı
- [ ] Atölye mobil ekranı (barkod okut)
- [ ] Yerel ajan (`apps/agent`, `FileDeliveryPort.LOCAL_AGENT`) → V23
- [ ] 1D (LINEAR) çözücü
- [ ] Çoklu para birimi / kur

## 10. Faz 2 — parametrik CAD / kural motoru

Kaynak: `docs/domain/cabinet-model-reference.md`

- [ ] `Module` şablon dili kararı (ADR)
- [ ] Karkas → bölge → parça → bağlantı → stil → donanım kural motoru
- [ ] 32 mm sistemi delik üretimi → `PartOperation`; `rotation` hesaplama
- [ ] Şema değişikliği **sıfır** olduğu doğrulanır

## 11. Faz 3+

- [ ] Post-processor'ler (MPR/BPP/CIX/HOP) → `PostProcessorPort`
- [ ] `AccountingPort`, `FiscalPort` (Türkiye)
- [ ] AI görselleştirme (difüzyon + ControlNet)
- [ ] CRM
- [ ] True-shape nesting (`Machine.capabilities.nesting`)
