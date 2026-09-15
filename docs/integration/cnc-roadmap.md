# CNC Yol Haritası: DXF → Post-Processor'ler → Yerel Ajan

## 1. Fazlara göre çıktı

| Faz | Çıktı | Teslim |
|---|---|---|
| 0 | Kesim planı PDF, parça etiketi (barkod), **R12 DXF** (parça başına), CSV | tarayıcı indirmesi (`FileDeliveryPort.DOWNLOAD`) |
| 1/2 | aynı | + yerel ajan klasöre yazar (`LOCAL_AGENT`) |
| 3 | marka post-processor'leri: MPR, BPP, CIX, HOP | yerel ajan |

## 2. Post-processor portu (Faz 3, bugünden imza)

```
PostProcessorPort
  supports(machine: Machine) -> bool
  render(part: PartSnapshot, ops: PartOperation[], profile: LayerProfile) -> bytes
  file_extension -> str
```

Tüm post-processor'ler **aynı** `PartOperation[]` listesini tüketir (ADR-0013). DXF R12 üreticisi bu portun ilk implementasyonudur; Faz 3'te yeni format = yeni implementasyon, çekirdek değişmez.

## 3. Format tablosu

> ⚠️ DOĞRULANMADI: Aşağıdaki eşleme genel sektör bilgisidir; her formatın sürüm ve makine kontrolcüsüne göre farkları vardır. Faz 3'te her biri için gerçek makine ve örnek dosya gerekir.

| Format | Üretici / kontrolcü | Not |
|---|---|---|
| MPR | Homag / WoodWOP | metin tabanlı, değişken ve makro destekli |
| BPP | Biesse / BiesseWorks | metin tabanlı |
| CIX | Biesse / bSolid | BPP'nin yenisi |
| HOP | ⚠️ kaynak belirsiz (muhtemelen Holz-Her); doğrulanacak | |
| DXF R12 | genel | Faz 0; birçok CAM yazılımı içe alır |

## 4. Yerel ajan (ADR-0015)

- Atölye PC'sinde küçük servis; bulutu poll eder (outbound HTTPS), bekleyen `ExportArtifact`'ları indirir, makine klasörüne yazar, makbuz gönderir.
- Klasör eşlemesi makine bazlı: `Machine.id → local_path`.
- Güvenlik: tenant'a özel iptal edilebilir API anahtarı; ajan yalnızca kendi tenant'ının artifact'larını görür (RLS + anahtar).
- Faz 0'da yalnızca `ExportArtifact.delivery_status` alanı ve port imzası var; kod yok.

## 5. Sıralama gerekçesi

DXF önce: en geniş uyumluluk, referans müşteri için yeterli ⚠️ (makinesinin DXF kabul ettiği doğrulanmadı). Marka formatları ancak ilgili makineye sahip müşteriyle test edilebilir; erişim yokken yazmak israftır.
