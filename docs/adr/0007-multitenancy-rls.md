# ADR-0007: Multi-tenancy için tek veritabanı + `tenant_id` + PostgreSQL Row Level Security kullan

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

SaaS; her atölye bir tenant. Tenant sızıntısı ürünü bitirir. Tek kişilik ekip; tenant başına operasyon (migration, yedek, bağlantı havuzu) taşınamaz. AI destekli geliştirmede en olası hata, `WHERE tenant_id = ...` filtresinin bir sorguda unutulmasıdır.

## Karar

- Tek PostgreSQL veritabanı, tek şema. Tenant'a ait her tabloda `tenant_id UUID NOT NULL`.
- İzolasyon **veritabanında**: her tenant tablosunda `ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY`; politika `tenant_id = current_setting('app.tenant_id')::uuid`.
- Uygulama tek bir middleware ile her istekte, işlem başında `SET LOCAL app.tenant_id = '<uuid>'` çalıştırır. `SET LOCAL` işlem sonunda düşer; bağlantı havuzunda sızıntı olmaz.
- Uygulama DB rolü (`geppetto_app`) **tablo sahibi değildir** ve superuser değildir; aksi halde RLS atlanır. Migration rolü (`geppetto_migrate`) ayrıdır ve uygulama çalışma zamanında kullanılmaz.
- Tenant'sız işlemler (kayıt, sistem görevleri) ayrı, açıkça işaretlenmiş bir yol kullanır (`app.tenant_id` boş → politika 0 satır döndürür; sistem görevleri `geppetto_system` rolüyle ve açık `tenant_id` iterasyonuyla çalışır).
- RLS test seti (ADR-0016): iki tenant, her tabloda çapraz okuma/yazma denemesi = 0 satır / hata.
- Birincil anahtarlar UUID (v7 tercih; sıralı, indeks dostu). Tenant'lar arası ID çakışması yapısal olarak yok.

## Gerekçe

- Filtre unutulursa uygulama değil veritabanı durdurur; hata sınıfı yapısal olarak kapanır.
- Tek DB = tek migration, tek yedek, tek havuz.
- `SET LOCAL` + havuz kombinasyonu bilinen ve test edilebilir bir kalıptır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Şema / tenant | Migration tenant sayısı kadar koşar; havuz şema başına bağlantı ister. |
| Veritabanı / tenant | En güçlü izolasyon ama operasyon yükü tek kişi için taşınmaz. |
| Yalnızca uygulama katmanı filtresi | Tek unutulan `WHERE` = sızıntı; AI destekli kodda en olası hata. |
| ORM global filter (SQLAlchemy `with_loader_criteria`) | Ek savunma olarak eklenebilir, tek savunma olamaz; ham SQL'i kapsamaz. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** sızıntı yapısal olarak engellenir; operasyon tek.
- **Bedel:** RLS politikası her sorguya predicate ekler (indekslerde `tenant_id` ilk kolon olmalı); rol/yetki kurulumu doğru yapılmazsa RLS sessizce devre dışı kalır — bu yüzden test seti zorunlu. Gürültülü komşu (performans) izolasyonu yok.
- **Kodda zorlama:** Alembic'te her yeni tablo için RLS politikası şablonu; CI'da "RLS'siz tenant tablosu" taraması; RLS test seti PR'da zorunlu.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: asyncpg + SQLAlchemy async havuzunda `SET LOCAL`'ın her işlem başında güvenilir çalıştığı, ilk implementasyonda entegrasyon testiyle kanıtlanacak.

## İlgili ADR'ler

- ADR-0003 — stok hareketleri tenant izoleli
- ADR-0014 — PostgreSQL seçimi
- ADR-0016 — RLS test seti
