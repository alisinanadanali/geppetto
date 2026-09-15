# Monorepo Düzeni

uv workspace (Python) + pnpm workspace (web). Tek kök, tek CI.

```
geppetto/
├── CLAUDE.md                      # AI ve insan için mimari kurallar
├── README.md
├── pyproject.toml                 # uv workspace kökü; ortak lint/test ayarı
├── uv.lock
├── package.json                   # pnpm workspace (apps/web)
├── docs/                          # bkz. README.md docs haritası
├── packages/                      # kütüphaneler — hiçbiri HTTP/DB/dosya sistemi bilmez
│   ├── geppetto-domain/
│   │   ├── pyproject.toml         # bağımlılık: pydantic yalnızca
│   │   ├── src/geppetto_domain/
│   │   │   ├── dimensions.py      # derive_raw_dimensions()
│   │   │   ├── stock.py           # projeksiyon ve durum geçiş kuralları
│   │   │   ├── parts.py, materials.py, machines.py, cutjobs.py
│   │   │   └── errors.py          # domain hata kodları (contracts ile aynı enum'a bağlanır)
│   │   └── tests/
│   ├── geppetto-solver/
│   │   ├── pyproject.toml         # bağımlılık: pydantic; or-tools [extra]
│   │   ├── src/geppetto_solver/
│   │   │   ├── __init__.py        # optimize(), __version__
│   │   │   ├── types.py           # OptimizeRequest / OptimizeResult
│   │   │   ├── guillotine/        # v1 algoritma
│   │   │   └── invariants.py      # ADR-0016 değişmez doğrulayıcı
│   │   └── tests/                 # Hypothesis property testleri
│   ├── geppetto-contracts/
│   │   └── src/geppetto_contracts/
│   │       ├── part_list.py       # PartListDocument v1
│   │       ├── api/               # request/response DTO'ları
│   │       └── error_codes.py     # tek katalog
│   ├── geppetto-ingest/
│   │   └── src/geppetto_ingest/   # csv.py, xlsx.py, dxf.py, profile.py
│   └── geppetto-export/
│       └── src/geppetto_export/   # pdf_plan.py, labels.py, dxf_r12.py, csv.py
├── apps/
│   ├── api/
│   │   ├── pyproject.toml
│   │   ├── alembic/               # migration'lar; her tenant tablosuna RLS şablonu
│   │   └── src/geppetto_api/
│   │       ├── main.py
│   │       ├── middleware/tenant.py   # SET LOCAL app.tenant_id
│   │       ├── auth/                  # AuthPort JWT implementasyonu
│   │       ├── db/                    # SQLAlchemy modelleri, repository'ler
│   │       ├── ports/                 # StoragePort, QueuePort, CountryPort, FileDeliveryPort impl.
│   │       └── routers/
│   ├── worker/
│   │   └── src/geppetto_worker/   # arq görevleri: run_optimization, build_exports
│   ├── web/
│   │   ├── package.json
│   │   └── src/
│   │       ├── api/generated/     # openapi'den üretilir; elle düzenlenmez
│   │       ├── i18n/{tr,en}/      # çeviri dosyaları
│   │       ├── design/tokens.ts   # renk/spacing/radius/tipografi
│   │       ├── modules/           # stock, materials, import, cutplan, orders, machines
│   │       └── shell/             # sol modül rayı, tek ekran iskeleti
│   └── agent/
│       └── README.md              # Faz 1/2; yalnızca tanım
├── infra/
│   └── docker-compose.yml         # postgres, redis, minio
└── tests/
    ├── golden/<kaynak>/<ad>/{input.json, expected.json}
    └── rls/                       # tenant izolasyon testleri (testcontainers)
```

## Bağımlılık yönü (import-linter ile CI'da zorlanır)

```
apps/api, apps/worker  →  geppetto-ingest, geppetto-export, geppetto-contracts  →  geppetto-domain
apps/worker            →  geppetto-solver
geppetto-solver        →  (yalnızca kendi tipleri; geppetto-domain YASAK)
geppetto-domain        →  hiçbir iç paket; dış: pydantic
apps/web               →  yalnızca üretilmiş OpenAPI istemcisi
```

## Her paketin "yapmaz" listesi

| Paket | Yasak import |
|---|---|
| domain, solver | `sqlalchemy`, `fastapi`, `httpx`, `boto3`, `arq`, `os.environ`, `datetime.now()` (saat parametredir) |
| contracts | iş kuralı; yalnızca şema |
| ingest, export | DB, HTTP, S3 istemcisi |
| web | elle yazılmış API tipi; sabit metin; sabit hex renk |

## Sürümleme

- `geppetto-solver` semver; her koşuda `solver_version` kaydedilir.
- Diğer paketler workspace ile birlikte sürümlenir.
- Alembic migration adı: `YYYYMMDD_HHMM_<kısa-ad>`.
