# Golden set

Kaynak: ADR-0016 §2, testing-strategy.md §2.

```
tests/golden/
  <kaynak>/                # örn. reference-customer
    <case>/
      input.json           # OptimizeRequest (geppetto_solver.types)
      expected.json        # {"sheets_used": int, "yield_ratio_min": float,
                           #  "reference": "adeko" | "manual", "notes": str}
```

## Kurallar

- CI her case için koşar; tablo: `case | solver_version | sheets | yield | Δ vs expected`.
- Gerileme: `sheets_used > expected` veya `yield < yield_ratio_min − 0.01` → PR bloklanır
  (override etiketi ile bilinçli kabul).
- Koşucu bölüm 4.9'da yazılır; ilk case'ler todo 0.2 (Adeko kesim planı) geldikten sonra eklenir.

> ⚠️ DOĞRULANMADI (V7): Golden set henüz yok. Bu dizin yalnızca düzen ve kabul kriteridir.
