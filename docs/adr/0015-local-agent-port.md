# ADR-0015: Yerel ajan portunu bugünden tanımla, kodunu Faz 1/2'de yaz

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Atölyedeki CNC ve kesim makineleri genellikle internete bağlı değildir; dosyalar USB veya yerel ağ paylaşımıyla taşınır. Bulutta üretilen DXF/MPR dosyasının makinenin okuduğu klasöre inmesi gerekir. Bu, ürünün "tıkla, makine hazır" vaadinin son halkasıdır.

## Karar

- `FileDeliveryPort` bugünden mimaride tanımlanır:
  - `deliver(artifact_id, target: DeliveryTarget) -> DeliveryReceipt`
  - `DeliveryTarget`: `DOWNLOAD` (Faz 0, tarayıcı indirmesi) | `LOCAL_AGENT` (Faz 1/2) | `EMAIL` (opsiyonel)
- Faz 0 implementasyonu yalnızca `DOWNLOAD` (S3 presigned URL).
- Faz 1/2: `apps/agent` — küçük masaüstü servis (Windows öncelikli). Bulutta tenant'a bağlı bir ajan kaydı (`agents` tablosu: `id, tenant_id, name, api_key_hash, last_seen_at, target_folders`), ajan bulutu **poll eder** (outbound HTTPS; atölye ağında inbound port açılmaz), bekleyen `ExportArtifact`'ları indirir, yapılandırılmış klasöre yazar, teslim makbuzu gönderir.
- Ajan kimliği: tenant'a özel API anahtarı; JWT değil (uzun ömürlü, iptal edilebilir).
- Bu ADR kod yazdırmaz; yalnızca port imzası ve `ExportArtifact.delivery_status` alanı Faz 0 şemasında yer alır.

## Gerekçe

- Port bugün tanımlanmazsa Faz 0 export kodu doğrudan "indir" düğmesine bağlanır ve Faz 1'de sökülür.
- Poll modeli atölye ağında yapılandırma gerektirmez.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi (veya ertelendi) |
|---|---|
| Faz 0'da ajanı yazmak | Kapsam; referans müşteri şimdilik USB ile yaşayabilir. |
| Bulut → atölye push (WebSocket/VPN) | Atölye ağında inbound/VPN kurulumu; destek yükü. |
| Tarayıcı File System Access API ile klasöre yazma | Yalnızca Chromium, izin her oturumda; makine PC'sinde tarayıcı olmayabilir. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** Faz 1/2'de yalnızca yeni bir port implementasyonu + küçük uygulama.
- **Bedel:** Faz 0'da kullanılmayan bir alan (`delivery_status`) ve arayüz.
- **Kodda zorlama:** export uçları `FileDeliveryPort` üzerinden çalışır; doğrudan presigned URL üreten uç yok.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Referans müşterinin makine PC'sinin işletim sistemi ve ağ durumu (tamamen izole mi, yerel ağda mı) bilinmiyor.

## İlgili ADR'ler

- ADR-0001 — port kavramı
- ADR-0013 — teslim edilen dosya DXF
- ADR-0014 — S3 depolama
