# ADR-0012: Sabit ithalat adaptörü değil, kullanıcı tanımlı eşleme profili kullan

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Referans müşteri Adeko'da çizip kesim listesini dışarı veriyor. Adeko'nun dışa aktarma formatı **elimizde değil**; sürüm ve lisansa göre kolonlar değişebilir. Diğer atölyeler Excel/CSV veya başka CAD kullanıyor. "Adeko adaptörü" diye sabit kodlanmış bir şey ilk sürüm değişikliğinde kırılır.

## Karar

- `ImportProfile` varlığı: kaynak tipi (`CSV | XLSX | DXF`), kolon/katman → `PartListDocument` alanı eşlemesi, birim (`MM | UM | INCH`), ondalık ayırıcı, başlık satırı, kenar bant kolonlarının yorumu, varsayılan malzeme, `dimension_basis` **önerisi** (varsayılan değil).
- Kullanıcı profili kaydeder, adlandırır, tekrar kullanır. "Adeko v?" bir profil şablonudur, kod değil.
- Ayrıştırıcılar (`packages/geppetto-ingest`) yalnızca ham tabloyu/katmanları üretir; anlamlandırma profil ile olur.
- Çıktı her zaman `PartListDocument v1` (`packages/geppetto-contracts`); `dimension_basis` zorunlu.
- **Önizleme-düzeltme zorunlu:** ithal edilen parçalar önce önizleme ekranına düşer; kullanıcı ölçü esasını, malzeme eşlemesini ve hatalı satırları onaylamadan `Part` tablosuna yazılmaz. Uyarılar hata koduyla satır bazında gösterilir.
- Tasarım ayrıntısı: `docs/integration/import-profiles.md`.

## Gerekçe

- Format bilinmiyor; bilinse de değişecek. Profil, sürüm farkını kullanıcı düzeyinde çözer.
- Önizleme, "sessizce yanlış ölçü" riskini (özellikle `dimension_basis`) kullanıcıya görünür kılar.
- Aynı mekanizma Excel, CSV ve ileride başka CAD'ler için çalışır.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Sabit `AdekoAdapter` sınıfı | Format bilinmiyor; sürüm değişince kod değişir. |
| Sadece "bizim CSV şablonumuzu doldurun" | Kullanıcıya iş yükler; Adeko çıktısını elle dönüştürmek hata kaynağı. |
| Doğrudan Adeko veritabanına/API'sine bağlanmak | Erişim ve lisans bilinmiyor; kapalı sistem. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** format bağımsızlığı; kullanıcı kendi kaynağını bağlar.
- **Bedel:** ilk kurulumda kullanıcı eşleme yapar (bir kez); profil UI'ı yazılacak.
- **Kodda zorlama:** `PartListDocument` şemasında `dimension_basis` zorunlu (Pydantic); ithalat API'si önizleme onayı olmadan `Part` yazan uç sunmaz.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Adeko'nun dışa aktarma formatı (dosya tipi, kolonlar, birim, bant gösterimi, ölçü esası). Doğrulama planı `docs/integration/import-profiles.md` §5.

## İlgili ADR'ler

- ADR-0009 — `dimension_basis`
- ADR-0006 — kenar eşlemesi (L1/L2/W1/W2)
- ADR-0013 — DXF girişte katman eşlemesi aynı profil mekanizmasını kullanır
