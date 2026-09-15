# tests/ — paketler arası test setleri

Paket içi birim ve property testleri her paketin kendi `tests/` dizinindedir. Burada yalnızca
birden çok paketi veya gerçek Postgres'i gerektiren setler durur (ADR-0016, testing-strategy.md).

| Dizin | Ne | Ne zaman koşar |
|---|---|---|
| `golden/` | gerçek kesim listeleri + kabul edilen metrikler; doluluk tablosu | her PR (tablo yorumu) |
| `rls/` | tenant izolasyon testleri (testcontainers Postgres, uygulama rolü) | her PR |

Kökten `uv run pytest` hepsini toplar. `-m "not rls"` ile Postgres'siz koşulur.
