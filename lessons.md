# Geppetto — Dersler (lessons)

Bu dosya projede yapılan hataların, kök nedenlerinin ve düzeltme adımlarının kaydıdır. Amaç: aynı hatayı ikinci kez yapmamak ve AI destekli oturumlara rehber olmak.

## Nasıl kullanılır

- Bir hata fark edildiğinde (test kırıldı, yanlış hesap, dokümanla çelişki, geri alınan karar) **aynı gün** kayıt açılır.
- Her kayıt aşağıdaki şablonu kullanır. Kısa yaz; her cümle bir olgu, bir neden veya bir kural.
- Bir ders üç kez tekrarlanırsa `CLAUDE.md` "asla yapma" listesine veya bir ADR'ye taşınır ve buraya "→ taşındı" notu düşülür.
- Kayıtlar silinmez; geçersizleşen kayıt `[geçersiz: neden]` ile işaretlenir.
- Her oturum başında bölüm 3 (kontrol listesi) okunur.

## Kayıt şablonu

```
### L-NNN · YYYY-MM-DD · <kısa başlık>
**Alan:** domain | solver | db/rls | api | ithalat | export | web | süreç | doküman
**Belirti:** ne görüldü (test adı, hata kodu, yanlış çıktı)
**Kök neden:** neden oldu
**Düzeltme:** ne yapıldı (commit / dosya)
**Kural:** bundan sonra ne yapılır / yapılmaz
**Bağlantı:** ADR-XXXX, todo adımı, V-madde
```

---

## 1. Kayıtlar

### L-001 · 2026-09-13 · Kerf'in şemada sahibi yoktu
**Alan:** doküman
**Belirti:** Tasarım oturumu "kerf makine özelliğidir" dedi ama veri modelinde `Machine` varlığı yoktu; kerf tenant ayarına veya koşu parametresine düşecekti.
**Kök neden:** Kural cümle olarak yazıldı, şemaya izdüşümü kontrol edilmedi.
**Düzeltme:** ADR-0017 `Machine`; `CutJob.machine_id` zorunlu.
**Kural:** Her "X, Y'nin özelliğidir" cümlesi için veri modelinde Y'nin tablosu ve X'in kolonu gösterilir. Gösterilemiyorsa karar eksiktir.
**Bağlantı:** ADR-0009, ADR-0017

### L-002 · 2026-09-13 · Ledger ile artık yaşam döngüsü çelişiyordu
**Alan:** doküman
**Belirti:** ADR-0003 "tek quantity kolonu yasak, her şey projeksiyon" derken ADR-0004 artık için `available → reserved → consumed → scrapped` durum alanı ima ediyordu.
**Kök neden:** İki karar ayrı ayrı doğru, birlikte okunmamıştı.
**Düzeltme:** Artık durumu hareketlerden projeksiyon; `status` kolonu yok (kullanıcı kararı).
**Kural:** Aynı varlığa dokunan iki ADR birlikte okunur; "durum" alanı görülen her yerde "bu bir projeksiyon mu, kolon mu" sorulur.
**Bağlantı:** ADR-0003, ADR-0004

### L-003 · 2026-09-13 · `allow_rotation: bool` iki farklı kısıtı karıştırıyordu
**Alan:** domain
**Belirti:** Damar 90° dönüşü yasaklar; dengesiz panel 180° dönüşü yasaklar. Tek bool ikisini ayıramıyordu; Faz 2 CAM'de migration gerekecekti.
**Kök neden:** Faz 0 ihtiyacı (dikdörtgen nesting) ile Faz 2 ihtiyacı (delik deseni) aynı alana sıkıştırıldı.
**Düzeltme:** `rotation: NONE|ROT_180|ROT_90|ANY` + `grain: NONE|ALONG_LENGTH|ALONG_WIDTH`.
**Kural:** Bir bool alanı iki farklı fiziksel nedenle false olabiliyorsa enum'dur.
**Bağlantı:** ADR-0006, cabinet-model-reference.md §3

### L-004 · 2026-09-13 · Bant düşümü yanlış eksene uygulanma riski
**Alan:** domain
**Belirti:** Sezgi "uzun kenar bantlı → uzunluk kısalır" der; doğrusu tersi. L1/L2 (X'e paralel) kenarlar **genişliği** kısaltır.
**Kök neden:** Kenarın adı ("uzun") ile etkilediği eksen farklı.
**Düzeltme:** dimensions.md Örnek B bu durumu açıkça gösteriyor; ADR-0006 tablosunda "etkiler" sütunu.
**Kural:** `derive_raw_dimensions` testlerinde Örnek B zorunlu; kod incelemesinde bant düşümü gören kişi ekseni sorar.
**Bağlantı:** ADR-0009, dimensions.md §4

### L-005 · 2026-09-13 · Bilinmeyen formata alan adı uydurma cazibesi
**Alan:** süreç
**Belirti:** Adeko formatı elde yokken "muhtemelen şu kolonlar vardır" diye örnek yazmak kolay ve zararlı.
**Kök neden:** Doküman boş bırakmak rahatsız edici; AI makul görünen tahmini doğru gibi sunar.
**Düzeltme:** import-profiles.md §5 bilinçli boş; doğrulama planı yazıldı.
**Kural:** Kaynak dosya görülmeden alan adı yazılmaz. Boşluk `⚠️ DOĞRULANMADI` + doğrulama planı ile bırakılır.
**Bağlantı:** ADR-0012, V1

### L-006 · 2026-09-13 · Batch nesting için varlık yoktu
**Alan:** doküman
**Belirti:** "Çok siparişli toplu nesting" kapsamda ama `OptimizationRun`'ı siparişlere bağlayan varlık tanımsızdı.
**Kök neden:** Özellik listesi ile veri modeli ayrı yazıldı.
**Düzeltme:** `CutJob` + `cut_job_orders` + `cut_job_parts`; N sipariş → 1 iş → N koşu.
**Kural:** Her kapsam maddesi için "hangi tabloya yazılır" sorusu cevaplanır.
**Bağlantı:** data-model.md, phases.md §Faz 0 #8

### L-007 · 2026-09-15 · Paket başına `tests/` dizini pytest'te ad çakıştı
**Alan:** süreç
**Belirti:** Kökten `pytest` koşunca `ModuleNotFoundError: tests.test_smoke`; yedi paketin `tests/__init__.py` dosyası aynı `tests` modül adını paylaşıyordu.
**Kök neden:** repo-structure.md her pakete kendi `tests/` dizinini verir; pytest'in varsayılan `prepend` import modu aynı adlı paketleri ayıramaz.
**Düzeltme:** `--import-mode=importlib` (kök pyproject) ve test dizinlerinde `__init__.py` yok. `tests/rls/conftest.py` gibi paylaşılan fixture'lar conftest ile taşınır.
**Kural:** Test dizinlerine `__init__.py` konmaz; testler birbirini import etmez, paylaşılan kod `conftest.py` veya bir src paketinde durur.
**Bağlantı:** todo 1.2, 1.8; ADR-0016

---

## 2. Beklenen tuzaklar (henüz olmadı, olursa kayıt açılır)

Bu liste dokümanlardan türetildi; her biri gerçekleşirse yukarıya L-kaydı olarak taşınır.

| # | Tuzak | Nerede yakalanır |
|---|---|---|
| T1 | RLS sessizce devre dışı (app rolü tablo sahibi, superuser bağlantı, `SET LOCAL` işlem dışında) | RLS test seti; superuser'da test kendini geçersiz sayar |
| T2 | Solver "makul görünen yanlış" yerleşim (çakışma, kerf eksik, giyotin ihlali) | Hypothesis I1–I8; algoritmadan **önce** yazılır |
| T3 | Float uzunluk sızması (JSON `18.0`, TS `number` bölmesi, PDF ölçek) | Pydantic `Micron` tipi; export'ta µm→mm tek nokta |
| T4 | `RAW` gelen listeye ikinci kez bant düşümü | `finished_is_derived`; önizlemede ham ölçü canlı |
| T5 | Koşu onayı olmadan stok düşümü / koşu içinde stok yazma | hareketler yalnızca onay eyleminde; `reference_id = run.id` |
| T6 | Eşik altı artığın stoğa girmesi (gürültü) | malzeme > tenant eşik önceliği; I7 alan korunumu |
| T7 | Sabit metin / sabit hex / elle yazılmış API tipi | ESLint kuralları, CI diff |
| T8 | Operasyon koordinatlarında ham/bitmiş ofset karışıklığı (DXF) | round-trip testi; V5 doğrulaması |
| T9 | JSONB `attrs` doğrulanmadan yazılması | repository yalnızca Pydantic modelinden kabul eder |
| T10 | Alembic'te RLS şablonu unutulan yeni tablo | migration testi tablo listesini otomatik tarar |
| T11 | Domain/solver'a `datetime.now()` veya env sızması | import-linter + kod incelemesi |
| T12 | Kabul edilmiş ADR'yi "küçük düzeltme" diye değiştirmek | ADR README kuralı: yeni ADR |

---

## 3. Oturum başı kontrol listesi

- [ ] `docs/adr/README.md` açık doğrulamalar tablosuna bak; bugün kapanabilecek var mı?
- [ ] Bu dosyanın bölüm 1'ini oku; son 3 kaydın kuralı bugünkü işe uygulanıyor mu?
- [ ] Yazılacak kod hangi ADR'ye dayanıyor? Numarasını PR açıklamasına yaz.
- [ ] Ölçü kodu → dimensions.md Örnek A–D testleri var mı?
- [ ] Yeni tablo → `tenant_id`, RLS şablonu, migration testi.
- [ ] Yeni hata → metin değil kod; `error_codes.py`'ye eklendi mi?
- [ ] Emin olmadığın şey → `⚠️ DOĞRULANMADI` + README tablosuna V-madde.

## 4. Oturum sonu kontrol listesi

- [ ] Kırılan test / geri alınan karar var mı? → L-kaydı.
- [ ] `todo.md` işaretlendi mi (tarihle)?
- [ ] Doküman ile kod çelişti mi? → önce doküman (ADR) sonra kod.
- [ ] Üç kez tekrarlanan ders var mı? → `CLAUDE.md` veya ADR'ye taşı.
