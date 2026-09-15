"""RLS test fixture iskeleti (ADR-0007, ADR-0016 §3).

Bölüm 5.4'te tamamlanır. Şimdiden sabitlenen kural: test superuser ile koşuyorsa geçersizdir.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    """Testcontainers Postgres; Docker yoksa set atlanır."""
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:  # pragma: no cover
        pytest.skip("testcontainers kurulu değil")
    try:
        container = PostgresContainer("postgres:16-alpine")
        container.start()
    except Exception as exc:
        pytest.skip(f"Postgres container başlatılamadı: {exc}")
    try:
        yield container.get_connection_url()
    finally:
        container.stop()


def assert_not_superuser(is_superuser: bool, bypass_rls: bool) -> None:
    """Superuser veya BYPASSRLS ile koşan RLS testi kendini geçersiz sayar (T1)."""
    if is_superuser or bypass_rls:
        pytest.fail("RLS testi superuser/BYPASSRLS rolüyle koşuyor; sonuç geçersiz (ADR-0016 §3)")
