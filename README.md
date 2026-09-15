# Geppetto

Marangozhaneler için uçtan uca bulut SaaS. Stok defteri, parça listesi ithalatı (Adeko / Excel / CSV / DXF), giyotin kesim optimizasyonu, artık yönetimi, kesim planı çıktıları (PDF, etiket, R12 DXF, CSV), basit sipariş ve proje maliyeti.

Aylık abonelik; Türkiye'de başlar, çok dilli (tr/en) ve uluslararası. CNC'li veya CNC'siz atölye; ürün çeşidi fark etmez.

## Durum

2026-09-15: repo iskeleti hazır (todo bölüm 1). Paket ve uygulama dizinleri, uv/pnpm workspace,
lint/tip/import-linter/test hattı, docker-compose ve CI çalışıyor; iş mantığı henüz yok.
Faz planı: `docs/product/phases.md`; adımlar: `todo.md`.

## Fazlar

| Faz | Kapsam |
|---|---|
| 0 | Stok, ithalat, giyotin optimizasyon, artık, çıktılar, stok düşümü, sipariş/maliyet, batch nesting |
| 1 | Teklif/fiyatlandırma, planlama, müşteri onay portalı, atölye mobil, yerel ajan, 1D çözücü |
| 2 | Kendi parametrik CAD / kural motoru (Faz 0 şeması değişmeden) |
| 3+ | AI görselleştirme, CNC post-processor'ler, ön muhasebe entegrasyonu, CRM, true-shape nesting |

## Dokümantasyon haritası

| Yol | İçerik |
|---|---|
| `CLAUDE.md` | mimari kurallar, "asla yapma" listesi, sözlük özeti |
| `docs/adr/` | mimari karar kayıtları (17 ADR) + açık doğrulamalar |
| `docs/product/` | fazlar, hedef kullanıcılar |
| `docs/domain/` | sözlük, veri modeli, ölçü kuralı, malzeme modeli, Faz 2 dolap referansı |
| `docs/integration/` | ithalat profilleri, DXF konvansiyonu, CNC yol haritası |
| `docs/engineering/` | mimari genel bakış, repo düzeni, test stratejisi, i18n |
| `docs/ui/` | tasarım yönü |

## Teknoloji

FastAPI + SQLAlchemy + Alembic · PostgreSQL (RLS) · React + Vite + TypeScript · uv workspace · arq/Redis · S3 uyumlu depolama · kendi JWT · Pydantic → OpenAPI → üretilmiş TS istemci. Ayrıntı: ADR-0014.

## Kurulum

Gereksinimler: Python ≥ 3.12, uv, Node 24, pnpm 10, Docker.

```
cp .env.example .env
docker compose -f infra/docker-compose.yml --env-file .env up -d   # postgres, redis, minio
uv sync                                                             # tüm Python workspace
pnpm install                                                        # apps/web
```

Doğrulama (CI ile aynı):

```
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run lint-imports          # bağımlılık yönü (ADR-0001, ADR-0011)
uv run pytest                # -m "not rls" ile Docker'sız
pnpm lint && pnpm i18n:check && pnpm build
```

Geliştirme: `uv run uvicorn geppetto_api.main:app --reload --app-dir apps/api/src` ·
`uv run arq geppetto_worker.settings.WorkerSettings` · `pnpm --filter @geppetto/web dev`.

Postgres ilk açılışta üç rol oluşturur (ADR-0007): `geppetto_migrate` (şema sahibi, yalnızca Alembic),
`geppetto_app` (çalışma zamanı, sahip değil → RLS uygulanır), `geppetto_system` (tenant'sız görevler).
MinIO varsayılan 9000 portu doluysa `.env` içinde `MINIO_PORT` değiştirilir.
