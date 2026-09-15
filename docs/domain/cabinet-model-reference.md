# Parametrik Dolap Modeli — Faz 2 Referansı

> Bu doküman **kod değildir**. Faz 2 CAD/kural motorunun tasarım referansıdır. Faz 0'da yalnızca `Part`, `Module` ve `PartOperation` şemasının bu modeli şema değişikliği olmadan kabul edebilmesi için okunur.

## 1. Kavramsal iskelet

Sektör liderlerinin (PolyBoard, Cabinet Vision, Mozaik, Adeko) ortaklaştığı model:

1. **Karkas (carcass):** parametrik kutu. Girdi: dış genişlik/yükseklik/derinlik, malzeme kalınlığı, arkalık tipi (kanal / bindirme / yok). Çıktı: yan ×2, alt, üst (veya üst kuşaklar), arkalık.
2. **Bölgeler (zones):** karkas içi hacimler (raf/çekmece bölgeleri) + karkas dışı bölgeler (baza/plinth, taç/cornice, yan dolgu/filler).
3. **Parçalar + konum kuralı:** raf, dikme, çekmece, kapak bir hacme yerleşir. Konum ya **oransal** (%50) ya da komşu panelden **sabit mesafe** (üstten 300 mm). Dolap yeniden boyutlandığında kural korunur, sayı yeniden hesaplanır.
4. **Bağlantı (link):** hangi panel diğerinin üstünden geçer (overpassing / underpassing); zıvana/kanal var mı; bant hangi kenara. Bağlantı, parça ölçüsünü belirler (üstten geçen yan panel tam yükseklik, alt panel yan kalınlıkları kadar kısa).
5. **İmalat yöntemi (stil şablonu):** malzeme karışımı, kenar bandı politikası, boşluk (gap) ve geçme payları, donanım bağlantıları. Topluca uygulanan alt yöntemler (kapak stili, çekmece stili, karkas stili).
6. **Donanım = fitting + konumlandırma kuralı:** nesne (menteşe modeli) ve "nereye konacağı" (kapak üst/alttan 100 mm, 3 adet > 900 mm) ayrı tanımlanır.

**Sistem şablon değil, kural motorudur.** Dolap 800'den 1200'e çıkınca: raf sayısı artmalı, orta dikme eklenmeli, kapak 1'den 2'ye çıkmalı, menteşe pozisyonu yeniden hesaplanmalı.

## 2. Faz 0 şemasıyla eşleme

| Kavram | Faz 0 karşılığı |
|---|---|
| Modül örneği (bir dolap) | `Module(template_ref, params)` |
| Üretilen panel | `Part(module_id, source=CAD)` |
| Bant kuralı | `Part.edges` (4 kenar) |
| Delik/kanal/kertme | `PartOperation` (DRILL/GROOVE/NOTCH), koordinat ADR-0006 |
| Donanım işleme şablonu | `Material(HARDWARE).attrs.machining_ref` |
| Yüz kuralı (görünen yüz) | `Part.face_reference` |
| Yeniden boyutlandırma | Module.params değişir → parçalar yeniden üretilir (eski parçalar yeni set ile değiştirilir; onaylı koşular etkilenmez, ADR-0005) |

## 3. 32 mm sistemi

Delikler **kuraldan üretilir**, tek tek saklanmaz. Kural motoru `PartOperation` satırlarını türetir; kullanıcı düzenlerse `source = MANUAL` ile override.

- Sistem delikleri: **5 mm çap**, **32 mm aralık**, panel iç yüzünde (Face2 veya face_reference'a göre) iki paralel sıra.
- Ön sıra panel ön kenarından **37 mm** içeride (37 = 32 + 5). Dengeli (balanced) panelde arka sıra da arka kenardan 37 mm.
- Montaj/dowel delikleri tipik **8 mm**; sistem ızgarasında olmak zorunda değil.
- Menteşe kap deliği **35 mm** (kapakta), derinlik tipik 12–13 mm ⚠️ menteşe modeline göre `machining_ref`'ten.
- Dikey konum: ilk delik alt kenardan tanımlı mesafe; delik merkezleri `y = y0 + 32·k`.

### Dengeli / dengesiz panel ve döndürme

- **Dengeli panel:** delik deseni parçanın merkezine göre 180° simetrik → panel ters çevrilebilir → `Part.rotation ⊇ ROT_180`.
- **Dengesiz panel:** yalnızca ön sıra veya asimetrik montaj delikleri → `rotation = NONE` (damar yoksa `ROT_90` yine yasak çünkü delik yüzeyi/yönü değişir ⚠️ makine kabiliyetine göre).
- Sonuç: **delik deseni ile nesting birbirine bağlıdır.** Kural motoru `rotation` alanını hesaplar; solver bunu kısıt olarak alır (ADR-0011).

## 4. Faz 2'de cevaplanacak açık sorular

- Şablon dili: JSON tabanlı parametre ağacı mı, küçük bir DSL mi?
- Bağlantı kurallarının (link) saklanma yeri: modül şablonunda mı, tenant "imalat yöntemi"nde mi?
- Adeko'dan modül düzeyinde ithalat mümkün mü (yalnızca parça listesi mi geliyor)? ⚠️ DOĞRULANMADI.
