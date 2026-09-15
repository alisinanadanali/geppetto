"""geppetto-solver: saf, izole, sürümlü giyotin kesim optimizasyonu (ADR-0011).

Tek genel giriş: ``optimize(request) -> result``. Saf: IO yok, saat yok (zaman sınırı
parametredir), rastgelelik varsa ``seed`` parametredir. Domain paketini import etmez.

Sürüm semver'dir; her koşuda ``OptimizeResult.solver_version`` olarak ``OptimizationRun``'a
yazılır (ADR-0005). Algoritma değişikliği = minor/major artışı.
"""

__version__ = "0.1.0"
