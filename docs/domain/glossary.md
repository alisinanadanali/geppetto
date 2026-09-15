# Domain Sözlüğü (TR / EN)

Kural: kodda, şemada ve API'de yalnızca **EN** sütunundaki ad kullanılır. TR karşılıklar yalnızca çeviri dosyalarında yaşar.
Enum değerleri `SCREAMING_SNAKE`, alan adları `snake_case`, uzunluk alanları `_um` sonekiyle biter.

## Malzeme ve stok

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Malzeme | Material | `Material` | Stoklanan ve tüketilen her şey. `type` alanı davranışı belirler (bkz. material-model.md). |
| Plaka | Sheet | `Material.type = SHEET` | Dikdörtgen levha (suntalam, MDF, kontrplak, OSB). 2D giyotin optimizasyonuna girer. |
| Kenar bandı | Edge band | `EDGE_BAND` | Parça kenarına yapıştırılan şerit. Metre ile tüketilir, ruloyla alınır. |
| Donanım | Hardware | `HARDWARE` | Menteşe, ray, kulp, vida. Adetle sayılır. |
| Masif / profil / çıta | Linear stock | `LINEAR` | Tek boyutlu kesilen malzeme. 1D optimizasyon (Faz 1). |
| Kaplama | Veneer | `VENEER` | m² ile tüketilen ince yüzey malzemesi (Faz 2). |
| Sarf | Consumable | `CONSUMABLE` | Tutkal, lake, vernik; katsayılı tüketim (Faz 2). |
| Stok kalemi | Stock item | `StockItem` | Fiziksel bir plaka lotu veya tek bir artık. Hareketlerin referans aldığı satır. |
| Stok hareketi | Stock movement | `StockMovement` | Append-only defter kaydı. Mevcut stok bunların toplamıdır. |
| Rezervasyon | Reservation | `MovementType.RESERVE` | Bir kesim işi için stoğu ayırma; fiziksel tüketim değil. |
| Artık | Offcut | `StockItem.is_offcut = true` | Kesim sonrası kalan, yeniden kullanılabilir parça plaka. Birinci sınıf stok kalemi. |
| Hurda | Scrap | `MovementType.SCRAP` | Kullanılamayacak kadar küçük veya hasarlı artık; stoktan düşer. |
| Minimum artık eşiği | Min offcut threshold | `min_offcut_length_um / width_um` | Bu ölçünün altındaki artık stoklanmaz, fire sayılır. |
| Dekor / desen | Decor | `Material.catalog_ref` | Üretici kataloğundaki renk/desen kodu. Faz 0'da yalnızca serbest referans. |
| Damar | Grain | `grain` | Malzeme yüzeyindeki yön. Damarlı parça 90° döndürülemez. |
| Çift yüzlü | Two-faced | `two_faced` | Her iki yüzü dekorlu plaka. |

## Ölçü

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Mikron | Micron | `_um` | Kanonik uzunluk birimi. 1 mm = 1000 µm. Tam sayı. |
| Bitmiş ölçü | Finished dimension | `finished_length_um / finished_width_um` | Montajdaki nihai ölçü, bant dahil. **Saklanan tek doğru kaynak.** |
| Ham ölçü / kesim ölçüsü | Raw (cutting) dimension | `raw_length_um / raw_width_um` | Plakadan kesilecek ölçü. Türetilir, `OptimizationRun` içinde dondurulur. |
| Kalınlık | Thickness | `thickness_um` | Plaka veya bant kalınlığı. |
| Uzunluk | Length | `length_um` | Parçanın +X eksenindeki ölçüsü (damar yönü). Genişlikten büyük olmak zorunda değildir. |
| Genişlik | Width | `width_um` | Parçanın +Y eksenindeki ölçüsü. |
| Kerf / testere payı | Kerf | `Machine.kerf_um` | Testerenin yok ettiği malzeme genişliği. **Makine özelliği.** |
| Tıraş payı | Trim | `trim_*_um` | Plaka kenarından atılan pay (fabrika kenarı düzgün değildir). |
| İşleme payı / fazlalık | Oversize | `oversize_length_um / width_um` | Masif ve kaplamada sonradan tıraşlanmak üzere eklenen pay. Plakada 0. |
| Bant düşümü | Edge reduction | `edge_reduction_policy` | Bant kalınlığının bitmiş ölçüden düşülmesi. |
| Bantlama fire payı | Banding allowance | `length_allowance_per_part_um` | Bant stok tüketimine eklenen pay; parça ölçüsünü etkilemez. |
| Ölçü esası | Dimension basis | `dimension_basis: FINISHED \| RAW` | İthal edilen listedeki ölçünün hangisi olduğu. Zorunlu, kullanıcı onaylar. |

## Parça ve geometri

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Parça | Part | `Part` | Kesilecek tek bir dikdörtgen (Faz 0) veya poligon (Faz 2). |
| Yüz 1 / Yüz 2 | Face1 / Face2 | `FaceRef.FACE1 \| FACE2` | Face1 = görünen yüz. Face2 = arka yüz. Bkz. ADR-0006. |
| Kenar L1, L2, W1, W2 | Edges | `EdgeRef.L1 \| L2 \| W1 \| W2` | L1: Y=0 uzun kenar, L2: Y=width, W1: X=0 kısa kenar, W2: X=length. |
| Dış hat | Outline | `Part.outline` | Nullable poligon. Faz 0'da null (dikdörtgen varsayılır). |
| Operasyon | Operation | `PartOperation` | Bant, delik, kanal, kertme gibi parça üzerindeki işlem. |
| Delik | Drill / hole | `OperationType.DRILL` | Çap + derinlik + yüz + konum. |
| Kanal | Groove | `OperationType.GROOVE` | Yüzeyde açılan doğrusal oluk (arkalık kanalı). |
| Kertme | Notch | `OperationType.NOTCH` | Kenardan alınan dikdörtgen çıkıntı boşluğu. |
| Bant operasyonu | Edge banding | `OperationType.EDGE_BAND` | Hangi kenara hangi bant. |
| Döndürme izni | Rotation | `Part.rotation: NONE \| ROT_180 \| ROT_90 \| ANY` | Yerleşimde izin verilen dönüşler. |
| Dengeli panel | Balanced panel | `rotation ⊇ ROT_180` | Delik deseni 180° simetrik; ters çevrilebilir. |
| Modül | Module | `Module` | Faz 2: parametrik dolap. Faz 0'da yalnızca nullable FK. |
| Proje | Project | `Project` | Bir siparişin içindeki iş birimi (örn. "mutfak alt dolaplar"). |

## Optimizasyon ve kesim

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Yerleşim | Nesting / layout | `Placement` | Bir parçanın bir plaka üzerindeki konumu ve dönüşü. |
| Giyotin kesim | Guillotine cut | `CutMode.GUILLOTINE` | Her kesik plakayı kenardan kenara ikiye böler. v1'in tek modu. |
| Serbest yerleşim | True-shape nesting | `CutMode.NESTING` | Poligon yerleşimi; CNC router. Faz 3+. |
| Kesim işi | Cut job | `CutJob` | Birlikte optimize edilecek parça havuzu. Bir veya birden çok siparişten oluşur (batch). |
| Optimizasyon koşusu | Optimization run | `OptimizationRun` | Bir kesim işinin tek bir çözüm denemesi. Değişmez belge. |
| Kesim planı | Cut plan | `CutPlanSheet[]` | Koşunun çıktısı: her plaka için yerleşim ve kesik sırası. |
| Kesik | Cut | `Cut` | Bir plaka üzerindeki tek testere hareketi (yön, konum, seviye). |
| Doluluk | Yield / utilization | `metrics.yield_ratio` | Parça alanı / kullanılan plaka alanı. |
| Fire | Waste | `metrics.waste_area_um2` | Kerf + trim + eşik altı artık. |
| Kesim istasyonu / makine | Machine / cut station | `Machine` | Kerf, trim, maks. plaka ve kabiliyetlerin sahibi. |
| Etiket | Label | `ExportKind.LABEL` | Parça başına barkodlu yapışkan etiket çıktısı. |

## Ticari

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Kiracı / hesap | Tenant | `Tenant` | Bir atölye. Tüm veri `tenant_id` ile izole (RLS). |
| Müşteri | Customer | `Customer` | Atölyenin müşterisi. |
| Sipariş | Order | `Order` | Müşteriden alınan iş. Projeleri içerir. |
| Proje maliyeti | Project cost | `ProjectCost` | Malzeme + bant + donanım tüketiminden hesaplanan maliyet. Faz 0 basit. |
| Ön muhasebe | Pre-accounting | `AccountingPort` | Fatura/cari dış sisteme aktarım. Faz 3, port arkasında. |

## Dolap (Faz 2 referansı)

| TR | EN | Kod | Tanım |
|---|---|---|---|
| Karkas | Carcass | — | Dolabın parametrik kutusu (yan, alt, üst, arkalık). |
| Dikme | Divider / partition | — | Karkas içini bölen dikey panel. |
| Raf | Shelf | — | Yatay panel; sabit veya ayarlı. |
| Kapak | Door | — | Menteşeli ön panel. |
| Çekmece | Drawer | — | Ray üzerinde kutu. |
| Baza | Plinth | — | Karkas altı, karkas dışı bölge. |
| Taç | Cornice / crown | — | Karkas üstü dış bölge. |
| 32 mm sistemi | System 32 | — | 5 mm çap, 32 mm aralıklı delik ızgarası. Bkz. cabinet-model-reference.md. |
| Bağlantı | Link / joint | — | İki panel arasındaki geçme ilişkisi (overpassing/underpassing). |
