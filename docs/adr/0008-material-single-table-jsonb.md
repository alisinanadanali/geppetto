# ADR-0008: Malzemeyi tek tablo + ortak kolonlar + `attrs JSONB` ile sakla

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Altı malzeme tipi (SHEET, EDGE_BAND, HARDWARE, LINEAR, VENEER, CONSUMABLE); ortak alanlar çok, tipe özgü alanlar farklı. Faz 2–3'te yeni tipler ve mevcut tiplere yeni alanlar gelecek. Yeni malzeme tipi eklemek migration gerektirmemeli.

## Karar

- Tek `materials` tablosu. Ortak alanlar (kod, ad, tip, tedarikçi, birimler, fiyat, para, KDV, aktiflik, etiketler) gerçek kolon.
- Tipe özgü alanlar `attrs JSONB`.
- Doğrulama Pydantic **discriminated union** (`type` ayırıcı) ile; DB'ye yazılmadan önce `attrs` ilgili modelle doğrulanır. Doğrulanmamış JSONB yazımı yasaktır.
- `type` değiştirilemez.
- `attrs` içinde sorgulanan alanlar (örn. `thickness_um`, `grain`) için gerektikçe expression index; GIN yalnızca gerçek ihtiyaçta.
- Alan listesi ve JSON şemaları: `docs/domain/material-model.md`.

## Gerekçe

- Yeni tip = yeni Pydantic sınıfı + UI formu; migration yok.
- Stok, fiyat ve raporlama ortak kolonlardan çalışır; JSONB'ye bakmaz.
- Tek tablo = `stock_items.material_id` tek FK.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Tip başına tablo (`sheets`, `edge_bands`, …) | Her yeni tip migration; polimorfik FK. |
| Class table inheritance (ortak + tip tablosu join) | Join maliyeti; yeni tip yine migration. |
| EAV (attribute tablosu) | Sorgu ve doğrulama kâbusu. |
| Her şey JSONB | Ortak alanlarda indeks/kısıt kaybı. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** esnek şema, tek FK, migration'sız tip ekleme.
- **Bedel:** JSONB alanlarında DB seviyesinde tip/kısıt yok; tüm doğrulama uygulama katmanında. `attrs` şeması değişince eski satırlar için geçiş kodu gerekir (`attrs_schema_version` alanı tutulur).
- **Kodda zorlama:** repository katmanı `attrs`'ı yalnızca doğrulanmış Pydantic modelinden kabul eder; test: her tip için geçersiz `attrs` reddi.

## Doğrulanmamış varsayımlar

Yok.

## İlgili ADR'ler

- ADR-0002 — `attrs` içindeki uzunluklar da µm tam sayı
- ADR-0004 — `min_offcut_*` malzeme override'ı `attrs`'ta
- ADR-0017 — kerf malzemede değil makinede
