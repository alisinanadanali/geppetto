# Alembic

Bölüm 5.2'de kurulur. Kurallar:

- Migration rolü `geppetto_migrate` tablo sahibidir; uygulama rolü `geppetto_app` sahip değildir (ADR-0007).
- Her tenant tablosu: `tenant_id UUID NOT NULL` + `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY` şablonu.
- Migration adı: `YYYYMMDD_HHMM_<kısa-ad>`.
- Yasak kolonlar migration testiyle taranır: `quantity`, `raw_*`, malzemede `kerf`, artıkta `status`.
