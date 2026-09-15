# ADR-0001: Modüler monolit + hexagonal (ports & adapters) mimarisi kullan

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Tek kişilik, AI destekli geliştirme yapan bir ekip. Tek deploy hedefi. Domain kuralları (ölçü, stok, artık) ve solver algoritması ürünün özü; HTTP, veritabanı ve dosya formatları değiştirilebilir ayrıntı. Faz 2'de CAD modülü, Faz 3'te CNC post-processor'ler ve muhasebe entegrasyonu eklenecek; bunların çekirdeği bozmadan takılması gerekiyor.

## Karar

Tek deploy edilen modüler monolit. İç yapı hexagonal:

```
ingest adapters → domain core → solver → export adapters
                      ↑
              ports (storage, queue, auth, fiscal, country, file delivery, accounting)
```

- `packages/geppetto-domain` ve `packages/geppetto-solver` **saftır**: IO yapmaz, HTTP bilmez, tenant bilmez, veri alır veri döndürür.
- Adaptörler (`ingest`, `export`, `apps/api`, `apps/worker`) portları implemente eder ve çekirdeği çağırır.
- Bağımlılık yönü tek yönlüdür: `apps → ingest/export/contracts → domain`; `worker → solver`; `domain → hiçbir şey`.
- Mikroservis yok.

## Gerekçe

- Tek kişi birden fazla servisi işletemez; operasyon yükü ürünü öldürür.
- AI destekli geliştirmede en büyük risk sınır ihlalidir (domain'e SQL sızması). Paket sınırı + import kuralı bunu yapısal olarak engeller.
- Saf çekirdek test edilebilirliğin ön koşulu (ADR-0016).
- Solver'ın ileride başka dile taşınması yalnızca bir paket değişimi olur (ADR-0011).

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Mikroservisler | Operasyon yükü, dağıtık işlem karmaşıklığı; ölçek problemi yok. |
| Katmanlı anemik monolit (controller → service → repository) | Domain kuralları servis katmanına dağılır; solver ve domain saf kalmaz. |
| Django (batteries included) | ORM ve admin domain'i şekillendirir; hexagonal sınır zorlaşır. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** tek deploy, tek test koşusu, sınırları AI'a anlatılabilir tek cümle.
- **Bedel:** paket sınırlarını korumak disiplin ister; kısa yol her zaman caziptir.
- **Kodda zorlama:** import-linter (veya eşdeğeri) ile bağımlılık yönü CI'da doğrulanır; `domain` ve `solver` paketlerinin bağımlılık listesinde `sqlalchemy`, `fastapi`, `httpx`, `boto3` bulunamaz.

## Doğrulanmamış varsayımlar

Yok.

## İlgili ADR'ler

- ADR-0011 — solver paketi bu mimarinin saf çekirdeğidir
- ADR-0014 — teknoloji yığını
- ADR-0015 — yerel ajan bir port olarak tanımlanır
