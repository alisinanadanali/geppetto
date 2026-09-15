# ADR-0010: i18n ilk günden; backend hata kodu döndürür, kanonik depolama birimleri sabittir

**Durum:** Kabul edildi
**Tarih:** 2026-09-13

## Bağlam

Ürün Türkiye'de başlayıp uluslararası olacak. Sonradan eklenen i18n, her ekranı ve her hata mesajını yeniden yazmak demektir. Ülkeye özgü kurallar (vergi, fiscal entegrasyon, plaka standart ölçüleri, sayı/tarih biçimi) çekirdeğe sızarsa ikinci ülke çekirdeği değiştirmek zorunda kalır.

## Karar

- Arayüz `tr` + `en` aynı anda; react-i18next. Bileşenlerde **sabit metin yoktur**; her metin bir çeviri anahtarıdır.
- Backend **metin döndürmez**, hata kodu döndürür: `{"code": "PART_EXCEEDS_SHEET", "params": {...}}`. Kod `SCREAMING_SNAKE`, ilk kelime domain alanı (`PART_`, `STOCK_`, `IMPORT_`, `SOLVER_`, `AUTH_`, `TENANT_`). Katalog `packages/geppetto-contracts` içinde tek enum; çeviri metinleri `apps/web` çeviri dosyalarında.
- Kanonik depolama: uzunluk µm tam sayı (ADR-0002); para minor unit (bigint) + ISO 4217 kodu; zaman UTC `timestamptz`; tarih biçimi, ondalık ayırıcı, birim gösterimi yalnızca sunumda.
- Domain terimleri enum (`SHEET`, `L1`, `GUILLOTINE`); etiketleri çeviri anahtarıdır.
- Ülkeye özgü her şey `CountryPort` arkasında: KDV oranları, fiscal/e-fatura entegratörü, standart plaka ölçüleri, para birimi varsayılanı, adres biçimi. Türkiye ilk implementasyon.
- Tenant'ın `locale`, `base_currency`, `country_code` alanları vardır; kullanıcının `locale` tenant'ı override edebilir.

## Gerekçe

- Sonradan i18n maliyeti baştan i18n maliyetinin katıdır.
- Hata kodu = API sözleşmesinin parçası; çeviri istemcide, test edilebilir.
- Ülke portu: ikinci pazar bir port implementasyonu, çekirdek değişikliği değil.

## Değerlendirilen alternatifler

| Alternatif | Neden reddedildi |
|---|---|
| Önce tr, sonra en | Sabit metinler kodun her yerine dağılır; geri toplanamaz. |
| Backend'de çevrilmiş mesaj (`Accept-Language`) | Backend sunum bilgisi taşır; mesaj değişikliği deploy ister. |
| Ülke kurallarını `if country == "TR"` ile | İkinci ülkede çekirdek dallanır. |

## Sonuçlar ve ödünleşimler

- **Kazanç:** ikinci dil/ülke ekleme maliyeti düşük; hata kodları test ve destek için aranabilir.
- **Bedel:** her metin için anahtar disiplini; hata kodu kataloğu bakımı; çoğul/cins kuralları çeviri katmanında çözülür.
- **Kodda zorlama:** ESLint kuralı JSX içinde çıplak metni reddeder (`i18next/no-literal-string`); backend testinde `HTTPException(detail=str)` yasak; çeviri dosyalarında eksik anahtar CI'da hata.

## Doğrulanmamış varsayımlar

> ⚠️ DOĞRULANMADI: Çoklu para birimi (kur dönüşümü) Faz 0 kapsamı dışı varsayıldı; proje maliyeti tenant `base_currency` ile sınırlı. Farklı para biriminde malzeme girilirse `MATERIAL_CURRENCY_MISMATCH` uyarısı.

## İlgili ADR'ler

- ADR-0002 — birim
- ADR-0014 — react-i18next, Pydantic → OpenAPI
