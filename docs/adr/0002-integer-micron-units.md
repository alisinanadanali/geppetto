# ADR-0002: Tüm uzunlukları tam sayı mikron (µm) olarak sakla

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Kesim ölçüsü = bitmiş ölçü − bant − ... + pay şeklinde birçok terimin toplamıdır. Float ile 0,8 mm bant üç kez düşüldüğünde 2,4000000000000004 çıkar; yuvarlama yönü testere başında fiziksel hataya dönüşür. Kullanıcılar mm ile düşünür, bazı pazarlar inç ister.

## Karar

- Kanonik uzunluk birimi **µm**, tipi **tam sayı** (PostgreSQL `BIGINT`, Python `int`, TypeScript `number` ancak API sınırında güvenli tam sayı kontrolü). 18 mm = `18000`.
- Alan adları `_um` sonekiyle biter; alan hesapları `_um2`.
- Float uzunluk kodda, şemada ve API'de **yasaktır**.
- mm/inç yalnızca sunum katmanında dönüşümdür; girdi alındığı anda µm'ye çevrilir, tek bir yerde (`contracts` paketi).
- Uzunluk olmayan katsayılar (`conversion`, `density`, döviz kuru) bu kuralın dışındadır; onlar `numeric`.

## Gerekçe

- Toplama/çıkarma tam sayıda kesindir; kerf + bant + trim zinciri yuvarlama üretmez.
- µm çözünürlüğü sektörün en hassas makinesinden (0,01 mm) daha incedir; kayıp yok.
- 2800 mm × 2100 mm plaka alanı = 5,88 × 10¹² µm²; `BIGINT` (9,2 × 10¹⁸) rahatça yeter. `INTEGER` (2,1 × 10⁹) alan için yetmez; bu yüzden tüm uzunluk kolonları da `BIGINT`.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Float mm | Yuvarlama; eşitlik karşılaştırması güvensiz; solver'da epsilon yönetimi. |
| `Decimal` mm | Kesin ama yavaş, JSON'da string, TS tarafında native tip yok. |
| Tam sayı 0,1 mm | 0,4 mm bant kalınlığı ve 0,05 mm CNC hassasiyeti temsil edilemez. |
| Tam sayı nm | Alan hesabı `BIGINT` sınırını zorlar (10¹⁸). |

## Sonuçlar ve ödünleşimler

- **Kazanç:** deterministik hesap, kesin eşitlik, solver'da epsilon yok.
- **Bedel:** her UI alanı dönüşüm ister; büyük sayılar okunaksız (bu yüzden log/debug çıktıları mm gösterir).
- **Kodda zorlama:** SQLAlchemy'de uzunluk kolonları için `BigInteger` tipinde ortak tip alias; Pydantic'te `Micron = Annotated[int, ...]`; lint kuralı: `_um` soneki olmayan uzunluk alanı reddedilir (kod incelemesi listesinde).

## Doğrulanmamış varsayımlar

Yok.

## İlgili ADR'ler

- ADR-0009 — ölçü formülü bu birimle yazılır
- ADR-0010 — birim biçimlendirme sunum katmanında (i18n)
- ADR-0011 — solver µm tam sayı ile çalışır
