# ADR-0011: Solver saf, izole ve sürümlü bir pakettir: `optimize(request) -> result`

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Giyotin kesim optimizasyonu ürünün çekirdek değeri ve en çok değişecek parçasıdır. Algoritma evrilecek, belki dil değişecek (Python performans duvarı). AI destekli geliştirmede en tehlikeli çıktı "makul görünen ama sessizce yanlış nesting"tir; solver'ın izole ve deterministik olması test edilebilirliğin ön koşuludur.

## Karar

- `packages/geppetto-solver`: tek genel giriş `optimize(request: OptimizeRequest) -> OptimizeResult`.
- **Saf:** IO yok, DB yok, tenant yok, saat yok (zaman sınırı parametredir), rastgelelik varsa `seed` parametredir. Aynı girdi + aynı sürüm = aynı çıktı.
- **Kendi tipleri:** `OptimizeRequest` (parçalar: ham ölçü, qty, rotation, grain; plakalar: ölçü, trim, `is_offcut`, adet; makine: kerf; parametreler: mod, artık tercihi, zaman sınırı, seed) ve `OptimizeResult` (plaka başına yerleşim + kesik ağacı, artıklar, metrikler). Domain tiplerine bağımlılık **yok**; dönüşüm `apps/worker` içinde.
- **Sürümlü:** paket semver; `OptimizeResult.solver_version` her koşuda `OptimizationRun`'a yazılır (ADR-0005). Algoritma değişikliği = minor/major artışı.
- v1 = **giyotin**, Python. Strateji: yapıcı sezgisel (level/strip veya guillotine-split tabanlı) + yerel arama; OR-Tools CP-SAT yalnızca küçük örnekler ve kıyas için değerlendirilir. Golden set karar verdirir.
- Performans duvarında yalnızca bu paket başka dile (Rust/Go) taşınır; `OptimizeRequest/Result` JSON sözleşmesi korunur, üstündeki hiçbir şey değişmez.

## Gerekçe

- Saflık = property-based test (Hypothesis) mümkün; her değişmez rastgele girdide doğrulanır.
- Determinizm = golden set kıyası anlamlı.
- Kendi tipleri = dil taşıma sınırı net; domain değişince solver kırılmaz.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Solver'ı domain paketinin içine koymak | Dil taşıma sınırı bulanıklaşır; domain tipleri solver'a sızar. |
| Baştan Rust/C++ | Tek kişilik ekipte iterasyon hızı düşer; performans sorunu henüz ölçülmedi. |
| Harici SaaS optimizer (API) | Vendor bağımlılığı; çekirdek değer dışarıda. |
| Yalnızca OR-Tools CP-SAT | 100–500 parçalık gerçek işlerde zaman aşımı riski; giyotin kısıtı CP-SAT'ta pahalı. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** test edilebilir, kıyaslanabilir, taşınabilir çekirdek.
- **Bedel:** worker'da domain ↔ solver tip dönüşümü (ince katman). Sezgisel çözüm optimalden uzak olabilir; golden set doluluk tablosu bunu görünür kılar.
- **Kodda zorlama:** paket bağımlılık listesi yalnızca stdlib + pydantic (+ or-tools opsiyonel extra); import-linter kuralı `geppetto_solver` → `geppetto_domain` yasak; property test seti PR'da zorunlu (ADR-0016).

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: OR-Tools'un giyotin problemi için pratik faydası ölçülmedi; "taban" ifadesi tasarım oturumundan geliyor. İlk golden set ile kıyaslanmadan OR-Tools'a bağımlılık eklenmeyecek.

> ⚠️ DOĞRULANMADI: Python sezgiselinin 500 parçalık işi kabul edilebilir sürede (hedef < 30 s) çözüp çözmediği ölçülmedi.

## İlgili ADR'ler

- ADR-0001 — saf çekirdek
- ADR-0005 — `solver_version` koşuda donar
- ADR-0006 — rotation/grain kısıtları
- ADR-0016 — değişmezler ve golden set
- ADR-0017 — kerf/trim makineden gelir
