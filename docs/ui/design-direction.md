# UI Tasarım Yönü

## 1. Görsel dil

- **Sıcak, malzeme hissi.** Ahşap, talaş, kontrplak dokusu. Palet: koyu ceviz (birincil koyu), açık meşe (yüzey), doğal keten (zemin), talaş sarısı (vurgu), demir grisi (metin). Steril kurumsal SaaS mavisi **değil**.
- Yüzeyler hafif doku/gölge ile "levha" gibi; düz beyaz kart yok.
- Tipografi: net, geniş x-yüksekliği olan sans (örn. Inter/IBM Plex Sans ⚠️ lisans ve Türkçe glif kontrolü); gövde ≥ 16 px; sayısal ölçüler tabular rakam.
- Kontrast: WCAG AA en az; ölçü ve durum metinlerinde AAA hedef (atölye ışığı).
- Dokunma hedefi ≥ 44 × 44 px; birincil eylemler ≥ 56 px.

## 2. Design token'ları

`apps/web/src/design/tokens.ts` tek kaynak: renk (semantik adlar: `surface.sheet`, `text.primary`, `accent.sawdust`, `state.reserved`), spacing (4 px ölçeği), radius, gölge, tipografi ölçeği, dokunma hedefi boyutu. **Bileşenlerde elle hex, px spacing yazılmaz** (lint). Açık/koyu tema token seviyesinde.

## 3. Ana yerleşim

- **Sol modül rayı:** her modül oradan açılır; ikon + etiket; dar ekranda ikon-only, dokunmatikte alt bar.
- Faz 0 modülleri: Sipariş/Müşteri, Malzeme, Stok (plaka + artık + bant + donanım), İthalat, Kesim Planı, Makineler, Ayarlar.
- Üst bant: tenant adı, dil, kullanıcı; küresel arama (parça etiketi / barkod / sipariş no).

## 4. Tek ekran ilkesi

Bir modülün **tüm** işlevleri tek ekranda; geçişler o ekranın içinde (sekme, yan panel, çekmece, satır içi düzenleme). Kullanıcı sayfadan sayfaya savrulmaz. Örnek — Kesim Planı ekranı:

```
┌ sol rayı ┬──────────────────────────────────────────────┬ sağ çekmece ┐
│          │ [Kesim işi: MUT-0142 ▾] [Makine ▾] [Optimize] │ parça listesi│
│          │ ┌────────────┐ ┌────────────┐                │ (sürüklenir) │
│          │ │ plaka 1    │ │ plaka 2    │  ← plakalar    │ ───────────  │
│          │ │ ▭ ▭ ▭      │ │ ▭▭ ▭       │    fiziksel    │ artık havuzu │
│          │ └────────────┘ └────────────┘    nesne gibi  │ (sürüklenir) │
│          │ sekmeler: Yerleşim | Kesik sırası | Metrik | Çıktılar        │
└──────────┴──────────────────────────────────────────────┴──────────────┘
```

## 5. Sürükle-bırak: "kalıbı giyotine sürmek"

| Eylem | Sürükle | Bırak |
|---|---|---|
| Siparişe proje ekle | proje kartı | sipariş |
| Projeye parça ekle | parça satırı / ithalat önizleme satırı | proje |
| Kesim işine sipariş/parça at | sipariş veya parça | kesim işi kuyruğu |
| Plakayı/artığı işe dahil et | stok kalemi | kesim işi plaka listesi |
| Parçayı plakada yeniden konumlandır (manuel düzeltme) | yerleşim | plaka ⚠️ giyotin kısıtı canlı doğrulanır; ihlal kırmızı |

Parçalar ve plakalar fiziksel nesne gibi davranır: ölçek sadık (aynı ekranda aynı oran), damar yönü doku ile görünür, artık kendi ölçüsüyle çizilir, tutunca hafif kalkar, bırakınca oturur.

## 6. Erişilebilirlik ve klavye

Her sürükle-bırak eylemi için klavye eşdeğeri zorunlu: satır seç → `Enter` menü → hedef seç. Odak halkası görünür; ARIA canlı bölge ile "parça X plaka 2'ye taşındı". Dokunmatik ve masaüstü ikisi de birinci sınıf.

## 7. Ekran envanteri (Faz 0)

| Modül | Ana görünüm | İç geçişler |
|---|---|---|
| Sipariş/Müşteri | sipariş listesi + seçili sipariş paneli | projeler, parçalar, maliyet, çıktılar |
| Malzeme | liste + kademeli oluşturma formu | tip seç → alanlar |
| Stok | seviye tablosu (projeksiyon) | hareket defteri, artık havuzu (görsel kart), mal kabul, sayım |
| İthalat | profil seç/oluştur → önizleme-düzeltme | kolon eşleme çekmecesi, `dimension_basis` onayı |
| Kesim Planı | bölüm 4 | koşular arası kıyas, onay, çıktı üretimi |
| Makineler | tek form | kerf, trim, kabiliyet |
| Ayarlar | tenant, kullanıcı, dil, para birimi, artık eşiği | |

## 8. Yapılmayacaklar

- Modal üstüne modal.
- 40 alanlı tek form.
- Sayfa yönlendirmesiyle iş akışı.
- Sabit metin, sabit renk.
