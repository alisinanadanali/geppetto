# Test Stratejisi (Operasyonel)

ADR-0016'nın uygulama rehberi. Kural: PR, aşağıdaki setlerin tamamı geçmeden birleşmez.

## 1. Solver değişmezleri → test fonksiyonları

`packages/geppetto-solver/tests/test_invariants.py`, Hypothesis ile:

| Değişmez | Test | Strateji notu |
|---|---|---|
| I1 çakışma yok | `test_no_overlap` | kerf'i dahil ederek dikdörtgen kesişim kontrolü |
| I2 sınır içi | `test_within_usable_area` | plaka − trim |
| I3 kerf uygulanmış | `test_kerf_between_neighbours` | aynı kesik hattını paylaşan komşular |
| I4 giyotin | `test_cuts_are_guillotine` | kesik ağacı: her düğüm tam bölme |
| I5 döndürme/damar | `test_rotation_respects_constraints` | `grain≠NONE` → 90° yok |
| I6 adet korunumu | `test_part_count_conserved` | yerleşen + yerleşemeyen = qty toplamı |
| I7 alan korunumu | `test_area_conservation` | parça + artık + fire = plaka |
| I8 determinizm | `test_deterministic_with_seed` | iki çağrı, aynı çıktı |

Hypothesis stratejileri (`strategies.py`):
- `parts()`: length/width 50 000–2 800 000 µm, qty 1–20, rotation/grain rastgele tutarlı (grain≠NONE → rotation ∈ {NONE, ROT_180}).
- `sheets()`: standart ölçüler + rastgele artıklar (`is_offcut`), trim 0–20 000.
- `machine()`: kerf 0–6 000.
- `request()`: 1–60 parça (CI hızı); gecelik koşuda 500'e kadar.

Doğrulayıcı `invariants.validate(request, result) -> list[Violation]` üretimde `validate=True` ile de çağrılabilir; hata kodu `SOLVER_*`.

## 2. Golden set

```
tests/golden/
  <kaynak>/                # örn. reference-customer
    <case>/
      input.json           # OptimizeRequest
      expected.json        # {sheets_used, yield_ratio_min, reference: "adeko" | "manual", notes}
```

- CI her case için koşar; tablo: `case | solver_version | sheets | yield | Δ vs expected`.
- Gerileme kuralı: `sheets_used > expected` veya `yield < yield_ratio_min − 0.01` → PR bloklanır (override etiketi ile bilinçli kabul).
- Kaynak: referans müşteri gerçek listeleri + Adeko planı. ⚠️ Henüz yok; dizin ve kural hazır.

## 3. RLS testleri

`tests/rls/test_isolation.py` (testcontainers Postgres, **uygulama rolüyle**):

- Tablo listesi `information_schema` + `tenant_id` kolonu olanlardan otomatik.
- Her tablo için: tenant A oturumunda B satırı `SELECT` → 0; `UPDATE/DELETE` → 0 etkilenen; `INSERT` yanlış `tenant_id` → hata.
- `app.tenant_id` set edilmemiş oturum → tüm sorgular 0 satır.
- RLS etkin olmayan tenant tablosu → test başarısız.
- Superuser ile koşarsa test kendini geçersiz sayar (`pytest.fail`).

## 4. Domain testleri

- `derive_raw_dimensions`: property: bant ekle → yalnızca dik eksen küçülür; `edge_reduction_policy=NONE` → değişmez; ham ≤ 0 → `PART_RAW_DIMENSION_NON_POSITIVE`. Örnek testler dimensions.md A–D.
- Stok projeksiyonu: rastgele hareket dizisi → toplam = cebirsel toplam; artık durum geçişleri; geçersiz geçiş (`CONSUME` after `SCRAP`) → hata.

## 5. Sözleşme ve export

- OpenAPI snapshot (`apps/api/tests/openapi.snapshot.json`); diff → bilinçli güncelleme.
- Üretilmiş TS istemci CI'da yeniden üretilir; diff varsa hata.
- DXF round-trip: export → import → eşitlik (µm toleransı 1).
- PDF/etiket: içerik testi (parça sayısı, barkod değeri); görsel snapshot yok.

## 6. Koşu düzeni

| Set | Ne zaman | Süre hedefi |
|---|---|---|
| domain + solver property (küçük) + contracts | her PR | < 2 dk |
| RLS + API entegrasyon | her PR | < 5 dk |
| golden | her PR (tablo yorumu) | < 5 dk |
| solver property (büyük, 500 parça) | gecelik | — |
