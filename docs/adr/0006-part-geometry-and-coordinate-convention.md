# ADR-0006: `Part` bugünden geometri taşır; koordinat sistemi, origin ve yüz/kenar konvansiyonu sabittir

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Faz 0 yalnızca dikdörtgen parça keser. Faz 2 parametrik CAD, Faz 3 CNC post-processor ekleyecek; bunlar parça üzerinde delik, kanal, kertme ve poligon dış hat gerektirir. Bu bilgiler için **koordinat sisteminin, origin köşesinin ve yüz tanımının** bugünden sabitlenmesi zorunludur. CAM projelerini öldüren bir numaralı hata bu konvansiyonun sonradan değişmesidir: mevcut tüm delik verisi anlamını yitirir.

## Karar

### Alanlar (Faz 0'da açılır, çoğu null kalır)

| Alan | Tip | Faz 0 |
|---|---|---|
| `finished_length_um`, `finished_width_um`, `thickness_um` | bigint | dolu |
| `material_id` | FK | dolu |
| `edges` | `{L1, L2, W1, W2}` → nullable `edge_band_material_id` | dolu |
| `rotation` | `NONE \| ROT_180 \| ROT_90 \| ANY` | dolu (varsayılan malzemeden) |
| `grain` | `NONE \| ALONG_LENGTH \| ALONG_WIDTH` | dolu |
| `outline` | nullable poligon `[{x_um, y_um}]`, Face1 düzleminde, saat yönünün tersi | **null** |
| `operations[]` | `PartOperation` satırları | boş |
| `source` | `IMPORT \| MANUAL \| CAD` | dolu |
| `project_id` | FK | dolu |
| `module_id` | nullable FK → `modules` (Faz 2) | null |
| `finished_is_derived` | bool | ithalat `RAW` ise true |
| `label`, `qty`, `notes` | | dolu |

### Koordinat sistemi (değiştirilemez)

- **Origin:** parça Face1'e bakacak şekilde önde tutulduğunda **sol-alt köşe**.
- **+X:** uzunluk (`length`) yönü. Damar varsa damar daima +X boyuncadır. `length` damar yönündeki ölçüdür; `width`'ten büyük olmak zorunda değildir.
- **+Y:** genişlik (`width`) yönü.
- **+Z:** Face1'den parçanın içine doğru. Delik derinliği pozitif değerdir. Face2'den yapılan işlem `face = FACE2` ile belirtilir; koordinatı yine Face1 düzlemindeki (x, y) olarak yazılır (aynaya alınmaz).
- Sağ el kuralı bozulur (Z içeri); bu bilinçlidir: makinenin bakış açısı "üstten" değil "parçanın görünen yüzünden"dir.

### Yüzler

- **Face1** = görünen / dış / ön yüz. Kapakta oda tarafı, rafta üst yüz, yan panelde dolap içi olmayan yüz. Tek yüzlü plakada dekorlu yüz.
- **Face2** = arka yüz.
- Faz 2 kural motoru "hangi yüz görünür" bilgisini modülden türetir; Faz 0'da kullanıcı seçer, varsayılan Face1.

### Kenarlar

| Kenar | Konum | Bant düşümü etkiler |
|---|---|---|
| `L1` | Y = 0 (alt uzun kenar) | width |
| `L2` | Y = width (üst uzun kenar) | width |
| `W1` | X = 0 (sol kısa kenar) | length |
| `W2` | X = length (sağ kısa kenar) | length |

"Uzun/kısa" adlandırması alışkanlık içindir; L kenarları X eksenine paralel olanlardır, gerçek uzunluk sırası ne olursa olsun.

### `PartOperation`

| Alan | Not |
|---|---|
| `type` | `EDGE_BAND \| DRILL \| GROOVE \| NOTCH \| POCKET \| SAW_CUT` (Faz 0'da yalnızca `EDGE_BAND` üretilir) |
| `face` | `FACE1 \| FACE2 \| EDGE_L1 \| EDGE_L2 \| EDGE_W1 \| EDGE_W2` |
| `geometry` (JSONB) | tipe göre: drill `{x, y, diameter_um, depth_um}`; groove `{x1, y1, x2, y2, width_um, depth_um}`; notch `{x, y, length_um, width_um}` |
| `machining_ref` | nullable; Faz 2 donanım şablonuna bağ |
| `seq` | sıra |

Operasyon koordinatları **bitmiş ölçü** referansıyla yazılır (montajcının ölçtüğü parça). Ham → bitmiş ofseti export adaptörü uygular.

### Döndürme ve damar

- `grain = ALONG_LENGTH` veya `ALONG_WIDTH` ise solver 90° döndüremez; `rotation` en fazla `ROT_180` olabilir (`PART_ROTATION_CONFLICTS_GRAIN`).
- `ROT_180` yalnızca dengeli panelde (delik deseni 180° simetrik) anlamlıdır; dikdörtgen yerleşimini değiştirmez, CAM'i etkiler. Faz 0'da solver `ROT_180`'i `NONE` gibi işler.
- `ANY` = 90° ve 180° serbest.

## Gerekçe

- Konvansiyonu bugün yazmak Faz 2'de sıfır migration demektir.
- Face1-önden-sol-alt origin, DXF/CNC pratiğiyle (sol-alt origin, +Y yukarı) uyumludur.
- Dört ayrı kenar, bant düşümünün doğru eksene uygulanmasının tek yoludur (ADR-0009).
- `rotation` enum + `grain` ayrımı: damar 90°'yi, dengesiz panel 180°'yi yasaklar; bunlar farklı kısıtlardır. bool `allow_rotation` ikisini karıştırır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Faz 0'da yalnızca `length/width` alanları | Faz 2'de migration + eski parçaların anlamsızlaşması. |
| Origin sol-üst (ekran koordinatı) | DXF ve CNC ile ters düşer; her export'ta Y çevirisi. |
| Face1 = tezgaha bakan yüz | Bazı CNC yazılımlarının pratiği ama kullanıcı için sezgisel değil; "görünen yüz" atölye dilidir. Kullanıcı kararıyla reddedildi. |
| `allow_rotation: bool` | Damar ve panel dengesini ayıramaz. Kullanıcı kararıyla reddedildi. |
| Delikleri tek tek saklamak (Faz 2) | Kural motoru delikleri üretir (32 mm sistemi); saklama yalnızca sonuç görüntüsüdür. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** Faz 0 → Faz 2 geçişinde `Part` tablosu değişmez; CNC export tek konvansiyonla yazılır.
- **Bedel:** Faz 0 UI'ında kullanıcı Face1'i ve kenar adlarını öğrenmek zorunda; ithalat profili kenar eşlemesi ister.
- **Kodda zorlama:** `outline` verildiğinde bounding box = finished ölçü (check); `EDGE_L*` operasyonları `edges` ile tutarlı; `grain ≠ NONE` iken `rotation ∈ {ROT_90, ANY}` reddedilir.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Referans müşterinin Adeko/CNC iş akışındaki yüz ve kenar adlandırması bu konvansiyonla çakışabilir. İlk örnek DXF/liste dosyalarıyla doğrulanacak. Çakışırsa **konvansiyon değişmez**; ithalat/ihracat profilinde eşleme yapılır.

## İlgili ADR'ler

- ADR-0009 — bant düşümü kenar tanımına dayanır
- ADR-0012 — ithalat profili kenar eşlemesi
- ADR-0013 — DXF export bu koordinat sistemini kullanır
- ADR-0011 — solver `rotation` ve `grain`'i kısıt olarak alır
