# Hedef Kullanıcılar

## Ürün

Geppetto: marangozhaneler için uçtan uca bulut SaaS. Aylık abonelik. Türkiye'de başlar, çok dilli ve uluslararası olur. CNC'li veya CNC'siz atölye; ürün çeşidi fark etmez (mutfak, kapı, sundurma, dolap, mobilya).

## Referans müşteri

Erişimimiz olan gerçek bir üretici. Darboğazları:

| # | Darboğaz | Faz 0 cevabı |
|---|---|---|
| a | Stok kayıtları tutulamıyor | append-only stok defteri, artık stoğu, barkodlu etiket |
| b | Adeko çizimleri doğrudan optimize edilemiyor | eşleme profili ile ithalat → giyotin solver → kesim planı |

> ⚠️ DOĞRULANMADI: Referans müşterinin makine parkı (panel testere modeli, CNC var mı), Adeko sürümü, günlük parça hacmi, atölye PC'sinin ağ durumu. İlk saha görüşmesinde toplanacak.

## Personalar (Faz 0)

| Persona | Rol | Ekran | Temel iş |
|---|---|---|---|
| Atölye sahibi / usta | `OWNER` | masaüstü + telefon | sipariş girer, maliyeti görür, planı onaylar |
| Kesimci | `OPERATOR` | atölye PC'si / tablet | kesim planını açar, etiket basar, kesimi "tamamlandı" işaretler, artığı raflar |
| Çizimci (Adeko kullanan) | `OPERATOR` | masaüstü | listeyi dışa aktarır, Geppetto'ya alır, önizlemede düzeltir |
| Depo sorumlusu (küçük atölyede usta) | `OPERATOR` | tablet | mal kabul, sayım düzeltme, artık hurdaya ayırma |
| Muhasebeci (Faz 3) | `VIEWER` | masaüstü | maliyet/fatura dışa aktarımı |

Küçük atölyede tek kişi tüm rolleri üstlenir; roller yetki sınırıdır, ekran ayrımı değil.

## Ortam kısıtları → tasarım gereksinimi

| Kısıt | Gereksinim |
|---|---|
| Tozlu ekran, gündüz ışığı | yüksek kontrast, büyük tipografi (min 16 px gövde, 14 px yardımcı) |
| Eldivenli parmak, dokunmatik | dokunma hedefi ≥ 44 px; sürükle-bırak + klavye alternatifi |
| Gürültü | ses bildirimi yok; görsel durum |
| Kesintili internet | ithalat ve plan görüntüleme çevrimdışı toleranslı (önbellek) ⚠️ Faz 0'da yalnızca "kaydedilmemiş veri kaybetme" |
| mm ile düşünen kullanıcı | tüm giriş/gösterim mm; µm yalnızca depolama |

Bkz. `docs/ui/design-direction.md`.
