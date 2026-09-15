"""Domain hata kodları (ADR-0010; karar K3, 2026-09-15).

Domain `geppetto_contracts` paketini import edemez (ADR-0001). Bu yüzden domain'in ürettiği
kodlar burada **modül düzeyi `str` sabitleri** olarak durur:

- ad = değer (`PART_X = "PART_X"`),
- her değer `geppetto_contracts.error_codes.ErrorCode` içinde bulunmak zorundadır.

İkisi `packages/geppetto-contracts/tests/test_domain_codes.py` ile CI'da doğrulanır; yazım
hatası sessiz kalmaz. Sabitler ve `DomainError` bölüm 3'te, kullanan kural yazılırken eklenir.
"""
