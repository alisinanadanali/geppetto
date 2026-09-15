import geppetto_solver


def test_version_is_semver() -> None:
    major, minor, patch = geppetto_solver.__version__.split(".")
    assert all(p.isdigit() for p in (major, minor, patch))
