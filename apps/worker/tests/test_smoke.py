from geppetto_worker.settings import WorkerSettings


def test_worker_settings_has_functions() -> None:
    assert WorkerSettings.functions
