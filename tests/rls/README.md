# RLS (tenant izolasyon) testleri

Kaynak: ADR-0007, ADR-0016 §3, testing-strategy.md §3. Lessons T1: RLS sessizce devre dışı kalabilir;
bu set tek savunmadır.

## Kurallar

- Test **uygulama rolüyle** (`geppetto_app`) koşar. Superuser veya `BYPASSRLS` ile koşarsa
  `conftest.py` testi geçersiz sayar (`pytest.fail`).
- Tablo listesi `information_schema`'dan, `tenant_id` kolonu olanlardan **otomatik** türetilir;
  RLS'si etkin/forced olmayan tenant tablosu test başarısızlığıdır.
- Her tablo için: tenant A oturumunda B satırı `SELECT` → 0; `UPDATE/DELETE` → 0 etkilenen;
  `INSERT` yanlış `tenant_id` → hata; `app.tenant_id` set edilmemiş oturum → 0 satır.

## Çalıştırma

Postgres testcontainer'ı Docker ister. `uv run pytest -m rls`. Docker yoksa set atlanır (skip),
CI'da ise zorunludur.

Testin kendisi (`test_isolation.py`) bölüm 5.4'te yazılır; burada yalnızca fixture iskeleti var.
