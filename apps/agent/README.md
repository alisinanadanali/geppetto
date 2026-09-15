# apps/agent — yerel ajan (Faz 1/2)

Kaynak: ADR-0015. Bu dizinde Faz 0'da kod **yoktur**; yalnızca tanım.

## Ne yapar

Atölyedeki makine PC'sinde çalışan küçük masaüstü servis (Windows öncelikli). Bulutu **poll eder**
(outbound HTTPS; atölye ağında inbound port açılmaz), bekleyen `ExportArtifact`'ları indirir,
yapılandırılmış klasöre yazar, teslim makbuzu gönderir.

## Sözleşme (bugünden tanımlı)

- `FileDeliveryPort.deliver(artifact_id, target: DeliveryTarget) -> DeliveryReceipt`
- `DeliveryTarget`: `DOWNLOAD` (Faz 0) | `LOCAL_AGENT` (Faz 1/2) | `EMAIL` (opsiyonel)
- `ExportArtifact.delivery_status`: `PENDING | DOWNLOADED | DELIVERED | FAILED`
- Ajan kimliği: tenant'a özel uzun ömürlü, iptal edilebilir API anahtarı (JWT değil).
- Bulut tarafı tablo: `agents(id, tenant_id, name, api_key_hash, last_seen_at, target_folders)`.

## Açık doğrulamalar

- V14: makine PC'si işletim sistemi ve ağ durumu.
- V23: Faz 1 mi Faz 2 mi.
