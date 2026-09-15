# ADR-0013: DXF katman konvansiyonu yapılandırılabilir; ihracat "operasyon listesi → katman" dönüştürücüsüdür

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Sektörde CNC operasyon bilgisi DXF **katman adına** gömülür: dış hat, delik (çap ve derinlik katman adında), kanal merkez çizgisi, zincir frezeleme (comp in/out), başlangıç noktası. Her makine/yazılım farklı katman adı bekler. Faz 0 çıktısı R12 DXF; Faz 3'te marka post-processor'leri gelecek.

## Karar

- Katman konvansiyonu `DxfLayerProfile` ile yapılandırılır; hem giriş (katman → operasyon) hem çıkış (operasyon → katman) için.
- İhracat üreticisi `PartOperation[]` listesini katmanlı DXF varlıklarına dönüştürür. "Dikdörtgen çizici" olarak **yazılmaz**; dış hat da bir operasyondur (`OUTLINE`).
- Çıkış formatı R12 (AC1009). R12 kısıtları: `LWPOLYLINE` yok → `POLYLINE`/`VERTEX`; blok/öznitelik sınırlı; birim mm float (µm → mm dönüşümü tek noktada, `packages/geppetto-export`).
- Koordinat sistemi ADR-0006: origin sol-alt, +X uzunluk, +Y genişlik. Face2 operasyonları ayrı dosya veya ayrı katman öneki ile (profil belirler).
- Varsayılan profil ürünle gelir (genel konvansiyon); kullanıcı kopyalayıp düzenler.
- Ayrıntı: `docs/integration/dxf-conventions.md`.

## Gerekçe

- Katman adı = makine sözleşmesi; sabit kodlanırsa her makine için kod değişir.
- Operasyon listesi tek doğru kaynak; DXF, MPR, BPP hepsi aynı listeden türetilir (Faz 3).
- R12 en geniş uyumluluğa sahip sürümdür; eski nesting/CNC yazılımları yalnızca bunu okur.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Sabit katman adları | Makine değişince kod değişir. |
| DXF 2000+ (LWPOLYLINE) | Eski makineler okumaz; R12 hedef pazarda standart. |
| Yalnızca dış hat çizen basit export | Faz 3'te yeniden yazılır; operasyon modeli boşa gider. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** makine bağımsızlığı; Faz 3 post-processor'ler aynı operasyon listesini tüketir.
- **Bedel:** profil UI'ı; R12'nin kısıtlı varlık seti (yay/daire desteklenir, spline yok).
- **Kodda zorlama:** export testi: üretilen DXF'i yeniden okuyup katman → operasyon eşlemesi orijinal listeyi vermeli (round-trip).

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Referans müşterinin makinesinin beklediği katman adları ve delik derinliği/çap gösterimi (örn. `D8_15` mi `BOHR8_15` mi) bilinmiyor; örnek makine dosyası alınmalı.

> ⚠️ DOĞRULANMADI: ezdxf'in R12 yazma desteği ve `POLYLINE` üretimi ilk implementasyonda doğrulanacak.

## İlgili ADR'ler

- ADR-0006 — koordinat sistemi ve operasyon modeli
- ADR-0012 — giriş katman eşlemesi profil mekanizması
- ADR-0015 — üretilen dosya yerel ajanla teslim edilir
