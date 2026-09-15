#!/bin/bash
# Rol kurulumu (ADR-0007). Yalnızca ilk açılışta (boş veri dizini) çalışır.
#
#   geppetto_migrate : tablo sahibi; yalnızca Alembic kullanır, çalışma zamanında KULLANILMAZ.
#   geppetto_app     : uygulama rolü; sahip DEĞİL, superuser DEĞİL -> RLS uygulanır.
#   geppetto_system  : tenant'sız sistem görevleri; RLS'yi atlamaz, tenant'ları açıkça iterasyon eder.
#
# Rol oluşturmak superuser ister; bu yüzden Alembic'te değil burada yapılır.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
    CREATE ROLE geppetto_migrate LOGIN PASSWORD '${GEPPETTO_MIGRATE_PASSWORD}' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    CREATE ROLE geppetto_app     LOGIN PASSWORD '${GEPPETTO_APP_PASSWORD}'     NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    CREATE ROLE geppetto_system  LOGIN PASSWORD '${GEPPETTO_SYSTEM_PASSWORD}'  NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;

    -- Şema sahibi migration rolüdür; app rolü nesne yaratamaz.
    ALTER SCHEMA public OWNER TO geppetto_migrate;
    REVOKE CREATE ON SCHEMA public FROM PUBLIC;
    GRANT USAGE ON SCHEMA public TO geppetto_app, geppetto_system;

    -- migrate rolünün ileride yaratacağı tablolarda app/system için varsayılan yetkiler.
    -- stock_movements üzerinde UPDATE/DELETE bölüm 5.6'da açıkça geri alınır.
    ALTER DEFAULT PRIVILEGES FOR ROLE geppetto_migrate IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO geppetto_app, geppetto_system;
    ALTER DEFAULT PRIVILEGES FOR ROLE geppetto_migrate IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO geppetto_app, geppetto_system;
SQL
