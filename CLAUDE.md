# Geppetto — Mimari Kurallar

Marangozhaneler için bulut SaaS: stok defteri, parça listesi ithalatı, giyotin kesim optimizasyonu, artık yönetimi, kesim planı çıktıları. Modüler monolit, hexagonal. Tek kişilik AI destekli ekip. Dokümanlar Türkçe, kod/şema/alan adları İngilizce.

## Önce oku

Herhangi bir tasarım veya kod kararından önce: `docs/adr/README.md` (indeks + açık doğrulamalar), ilgili ADR, `docs/domain/glossary.md`. Ölçü kodu yazmadan `docs/domain/dimensions.md`; şema yazmadan `docs/domain/data-model.md`; test yazmadan `docs/engineering/testing-strategy.md`.

## Mimari kurallar (ADR'lerden)

1. **Bağımlılık yönü tek yönlü:** `apps → ingest/export/contracts → domain`; `worker → solver`; `domain` ve `solver` hiçbir iç pakete ve hiçbir IO kütüphanesine bağlı değildir. (ADR-0001)
2. **Uzunluk = tam sayı µm, `_um` soneki, BIGINT.** 18 mm = 18000. mm/inç yalnızca sunumda. (ADR-0002)
3. **Stok = `stock_movements` append-only defteri; mevcut stok projeksiyon.** Artık durumu da projeksiyon. (ADR-0003, 0004)
4. **`OptimizationRun` değişmez:** girdi anlık görüntüsü + `solver_version` + çıktı + metrikler. Stok düşümü ayrı hareket, `reference_id = run.id`. (ADR-0005)
5. **Koordinat konvansiyonu sabit:** origin Face1'e bakarken sol-alt; +X uzunluk/damar, +Y genişlik, +Z içeri; Face1 = görünen yüz; L1 (Y=0), L2 (Y=width), W1 (X=0), W2 (X=length). `rotation: NONE|ROT_180|ROT_90|ANY`, `grain: NONE|ALONG_LENGTH|ALONG_WIDTH`. (ADR-0006)
6. **Tenant izolasyonu DB'de:** her tenant tablosunda `tenant_id` + RLS; middleware `SET LOCAL app.tenant_id`; uygulama rolü tablo sahibi değil. (ADR-0007)
7. **Malzeme tek tablo + `attrs JSONB`,** Pydantic discriminated union; `type` değişmez. (ADR-0008)
8. **Bitmiş ölçü saklanır, ham türetilir:** `raw = finished − Σbant(dik kenarlar) + oversize`. Bant düşer, pay ekler; kerf ve trim formülün dışındadır. İthalatta `dimension_basis` zorunlu ve kullanıcı onaylı. (ADR-0009)
9. **i18n ilk günden:** UI'da sabit metin yok; backend hata **kodu** döndürür (`PART_EXCEEDS_SHEET`); para minor unit + ISO; zaman UTC; ülke kuralları `CountryPort`. (ADR-0010)
10. **Solver saf ve sürümlü:** `optimize(request) -> result`; determinist (seed); domain'i import etmez. (ADR-0011)
11. **İthalat = eşleme profili + önizleme-düzeltme;** onaysız `Part` yazılmaz. (ADR-0012)
12. **DXF export = operasyon listesi → katman;** katman adları profilden. R12. (ADR-0013)
13. **Kerf/trim/kabiliyet sahibi `Machine`.** `CutJob.machine_id` zorunlu. (ADR-0017)
14. **Portlar:** Storage, Queue, Auth, Country, FileDelivery, PostProcessor, Accounting, Fiscal. Doğrudan S3/Redis/JWT çağrısı yalnızca port implementasyonunda. (ADR-0001, 0015)

## Asla yapma

- Float uzunluk; `_um` soneksiz uzunluk alanı; `raw_*` DB kolonu.
- Herhangi bir tabloda `quantity` kolonu; `stock_movements` üzerinde UPDATE/DELETE; artıkta `status` kolonu.
- `OptimizationRun.input_snapshot / output` güncellemek.
- `tenant_id` filtresine güvenmek yerine RLS'siz tenant tablosu; superuser ile çalışan uygulama; RLS testi olmadan yeni tenant tablosu.
- `domain` veya `solver` içinde IO, `datetime.now()`, `os.environ`, SQLAlchemy, FastAPI, httpx, boto3.
- JSX'te çıplak metin; bileşende elle hex/px; `HTTPException(detail="metin")`.
- `AdekoAdapter` gibi sabit kodlanmış ithalat sınıfı; `dimension_basis` için varsayılan değer.
- Sabit DXF katman adı; "dikdörtgen çizen" export.
- Kerf'i malzemeye veya tenant ayarına koymak.
- Elle yazılmış API istemci tipi (OpenAPI'den üretilir).
- Mikroservis, PostGIS, TimescaleDB, Dagster, Django, Next.js.
- Uydurma alan adı: Adeko formatı bilinmiyor; bilinmeyeni `> ⚠️ DOĞRULANMADI:` ile işaretle, tahmin etme.
- Kabul edilmiş ADR'yi düzenlemek; çelişki varsa yeni ADR.

## Domain sözlüğü (özet; tam liste `docs/domain/glossary.md`)

| TR | EN / kod | |
|---|---|---|
| plaka | `SHEET` | dikdörtgen levha |
| artık | offcut, `is_offcut` | yeniden kullanılabilir kalan; birinci sınıf stok kalemi |
| kerf / testere payı | `Machine.kerf_um` | testerenin yok ettiği genişlik; makine özelliği |
| tıraş payı | trim | plaka kenarından atılan pay |
| kenar bandı | `EDGE_BAND` | bitmiş ölçüden düşer; metraj bitmiş kenardan |
| işleme payı | oversize | ham ölçüye eklenir (masif/kaplama) |
| damar | grain | +X boyunca; 90° dönüşü yasaklar |
| giyotin | `GUILLOTINE` | her kesik kenardan kenara; v1 tek mod |
| bitmiş / ham ölçü | finished / raw | saklanan / türetilen |
| kesim işi | `CutJob` | batch; N sipariş → 1 iş → N koşu |
| koşu | `OptimizationRun` | değişmez belge |
| Face1 / Face2 | | görünen / arka yüz |
| L1 L2 W1 W2 | | Y=0, Y=width, X=0, X=length kenarları |

## Dizin yapısı (özet; tam: `docs/engineering/repo-structure.md`)

```
packages/geppetto-{domain,solver,contracts,ingest,export}   # saf kütüphaneler
apps/{api,worker,web,agent}                                 # adaptörler ve uygulamalar
infra/docker-compose.yml                                    # postgres, redis, minio
tests/{golden,rls}
docs/{adr,product,domain,integration,engineering,ui}
```

## Doğrulanmamış varsayım kuralı

Emin olmadığın her nokta `> ⚠️ DOĞRULANMADI: <ne> — <nasıl doğrulanır>` biçiminde yazılır ve `docs/adr/README.md` "Açık doğrulamalar" tablosuna eklenir. Tahmin, doğrulanmış bilgi gibi sunulmaz.

## Durum

2026-09-15: repo iskeleti hazır (todo bölüm 1): workspace, lint/mypy/import-linter/test hattı, docker-compose (rol init), CI. İş mantığı yok; sıradaki adım bölüm 2 (`geppetto-contracts`). Faz 0 kapsamı `docs/product/phases.md`.
