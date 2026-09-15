# ADR-0014: Teknoloji yığını

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Tek kişilik, AI destekli ekip; tek deploy; saf Python çekirdek; sözleşme öncelikli API; çok dilli React arayüz.

## Karar

| Katman | Seçim | Not |
|---|---|---|
| API | FastAPI + SQLAlchemy 2 (async) + Alembic | Pydantic v2 modelleri OpenAPI'yi üretir |
| Veritabanı | PostgreSQL 16+ | **PostGIS yok**, **TimescaleDB yok** |
| Web | React + Vite + TypeScript, react-i18next | üretilmiş OpenAPI istemcisi (openapi-typescript veya eşdeğeri) |
| Monorepo | uv workspace (Python), pnpm workspace (web) | tek `pyproject.toml` kökü |
| İş kuyruğu | **arq** (Redis) | kullanıcı kararı 2026-09-13; **Dagster yok** |
| Dosya depolama | S3 uyumlu; geliştirmede MinIO, üretimde bulut | `StoragePort` arkasında |
| Auth | Kendi JWT'miz (access + refresh), `AuthPort` arkasında | harici IdP (OIDC) sonra takılabilir |
| Sözleşme | Pydantic → OpenAPI → TypeScript istemci | el yazımı istemci tipi yasak |
| Test | pytest, Hypothesis, testcontainers (Postgres) | bkz. ADR-0016 |
| Solver | Python; OR-Tools opsiyonel extra | bkz. ADR-0011 |
| PDF/etiket | ⚠️ kütüphane seçimi ilk implementasyonda (WeasyPrint veya ReportLab adayları) | |
| DXF | ezdxf | R12 yazımı doğrulanacak (ADR-0013) |

## Gerekçe

- FastAPI + Pydantic: sözleşme öncelikli akış doğal; tip güvenliği Python tarafında.
- PostgreSQL: RLS (ADR-0007), JSONB (ADR-0008), tek DB. PostGIS geometri için cazip ama µm tam sayı poligonları için gereksiz ve deploy yükü; TimescaleDB stok hareketleri için gereksiz (hacim küçük).
- arq: asyncio, FastAPI ile aynı çalışma modeli, küçük yüzey. Redis zaten önbellek/oturum için gelecekti.
- Dagster reddi: veri hattı orkestratörüdür; burada "bir solver işi kuyruğa at, sonucu yaz" gerekir.
- Kendi JWT: Faz 0'da harici IdP maliyeti gereksiz; port sayesinde sonra takılır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Django + DRF | ORM/admin domain'i şekillendirir; async ve Pydantic entegrasyonu ikinci sınıf. |
| Next.js | SSR gereksiz; SaaS uygulaması SPA; Vite daha sade. |
| Celery | Olgun ama sync model, ağır konfigürasyon; arq yeterli. |
| procrastinate (Postgres kuyruk) | Redis'siz cazip; topluluk küçük. arq tercih edildi; Redis kabul. |
| Dagster | Yanlış araç sınıfı. |
| PostGIS | Faz 3 true-shape nesting'de bile geometri saf Python/Rust'ta; DB'de geometri sorgusu ihtiyacı yok. |
| Auth0/Clerk/Keycloak | Faz 0'da maliyet ve bağımlılık; `AuthPort` ile sonra. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** tek dil çekirdek (Python), tek DB, sözleşmeden üretilen istemci.
- **Bedel:** Redis ek servis; kendi JWT'de güvenlik sorumluluğu bizde (refresh rotasyonu, iptal listesi).
- **Kodda zorlama:** CI'da OpenAPI snapshot ve üretilmiş istemci diff kontrolü; `apps/web` içinde elle yazılmış API tipi lint ile reddedilir.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: PDF/etiket kütüphanesi. Barkod (Code128) ve Türkçe karakter desteği kriter.

## İlgili ADR'ler

- ADR-0001, ADR-0007, ADR-0010, ADR-0011, ADR-0016
