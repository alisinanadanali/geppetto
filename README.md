# Geppetto

Marangozhaneler için uçtan uca bulut SaaS. Stok defteri, parça listesi ithalatı (Adeko / Excel / CSV / DXF), giyotin kesim optimizasyonu, artık yönetimi, kesim planı çıktıları (PDF, etiket, R12 DXF, CSV), basit sipariş ve proje maliyeti.

Aylık abonelik; Türkiye'de başlar, çok dilli (tr/en) ve uluslararası. CNC'li veya CNC'siz atölye; ürün çeşidi fark etmez.

## Durum

Yalnızca mimari dokümantasyon (2026-09-13). Uygulama kodu henüz yok. Faz planı: `docs/product/phases.md`.

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

Kod gelince yazılacak. Planlanan: `infra/docker-compose.yml` (postgres, redis, minio) + `uv sync` + `pnpm install`.
