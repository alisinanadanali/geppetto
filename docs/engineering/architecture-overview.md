# Mimari Genel Bakış

ADR-0001'in operasyonel hali. Modüler monolit, hexagonal.

## 1. Katmanlar

```mermaid
flowchart LR
    subgraph adapters_in [Giriş adaptörleri]
        CSV[CSV/XLSX parser]
        DXFin[DXF parser]
        API[FastAPI HTTP]
    end
    subgraph core [Saf çekirdek]
        DOM[geppetto-domain<br/>ölçü kuralları, stok projeksiyonu, varlıklar]
        SOL[geppetto-solver<br/>optimize(request)->result]
    end
    subgraph adapters_out [Çıkış adaptörleri]
        PDF[PDF/etiket]
        DXFout[DXF R12]
        CSVout[CSV]
    end
    subgraph ports [Portlar]
        ST[StoragePort S3]
        Q[QueuePort arq]
        AU[AuthPort JWT]
        CO[CountryPort TR]
        FD[FileDeliveryPort]
        AC[AccountingPort F3]
        FI[FiscalPort F3]
    end
    CSV --> DOM
    DXFin --> DOM
    API --> DOM
    DOM --> SOL
    SOL --> DOM
    DOM --> PDF
    DOM --> DXFout
    DOM --> CSVout
    API --- ports
```

## 2. Uçtan uca veri akışı (Faz 0)

1. **İthalat:** dosya → `StoragePort` → parser → `ImportProfile` → `PartListDocument` → önizleme (`ImportBatch.PREVIEW`) → onay → `Part` satırları.
2. **Kesim işi:** kullanıcı siparişleri/parçaları `CutJob`'a sürükler; makine seçer; `params`.
3. **Optimizasyon:** API `CutJob`'u `QueuePort`'a atar → worker: domain'den anlık görüntü (ham ölçüler türetilir, stok/artık listesi, makine) → `OptimizeRequest` → `solver.optimize()` → `OptimizationRun` yazılır (değişmez).
4. **İnceleme:** kullanıcı planı görür; başka parametreyle yeni koşu; birini onaylar (`approved_run_id`).
5. **Onay = stok:** `RESERVE` hareketleri (kesim öncesi); kesim tamamlandı → `CONSUME` + `OFFCUT_IN` (yeni `StockItem`, `is_offcut`).
6. **Export:** `input_snapshot + output` → PDF/etiket/DXF/CSV → `ExportArtifact` → `FileDeliveryPort`.
7. **Maliyet:** onaylı koşunun hareketleri + bant metrajı + donanım → proje maliyeti (sorgu).

## 3. Sınır kuralları

| Paket | Yapabilir | Yapamaz |
|---|---|---|
| `geppetto-domain` | saf hesap, doğrulama, varlık tipleri, projeksiyon mantığı | IO, HTTP, SQL, tenant, saat, env |
| `geppetto-solver` | `optimize()`, kendi tipleri, değişmez doğrulayıcı | domain import, IO, saat (zaman sınırı parametredir) |
| `geppetto-contracts` | Pydantic DTO, hata kodu enumu, `PartListDocument` | iş kuralı |
| `geppetto-ingest` | dosya → tablo/katman, profil uygulama | DB, HTTP |
| `geppetto-export` | koşu → dosya bytes | DB, HTTP, S3 (bytes döner; yazan API/worker) |
| `apps/api` | HTTP, auth, RLS middleware, repository, port implementasyonları | iş kuralı (domain'e delege) |
| `apps/worker` | kuyruk, solver çağrısı, koşu yazımı, export tetikleme | HTTP |
| `apps/web` | UI, i18n, üretilmiş istemci | ölçü/stok hesabı (backend'den gelir; yalnızca görüntü dönüşümü) |

## 4. Port listesi

| Port | Faz 0 implementasyonu | Sonra |
|---|---|---|
| `StoragePort` | S3 (MinIO) | bulut S3 |
| `QueuePort` | arq/Redis | — |
| `AuthPort` | kendi JWT | OIDC |
| `CountryPort` | TR (KDV, plaka ölçüleri, biçim) | diğer ülkeler |
| `FileDeliveryPort` | DOWNLOAD | LOCAL_AGENT (F1/2) |
| `PostProcessorPort` | DXF R12 | MPR/BPP/CIX/HOP (F3) |
| `AccountingPort` | yok (arayüz tanımlı) | Defteran/Paraşüt benzeri (F3) |
| `FiscalPort` | yok | GİB özel entegratör (F3) |

## 5. Çalışma zamanı

Tek deploy: `api` + `worker` + Postgres + Redis + MinIO. Geliştirmede `infra/docker-compose.yml`. Ölçekleme gerekirse `worker` kopyası artırılır; kod değişmez.
