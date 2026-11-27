"""pytest setup: log in once for the whole run, tidy up after each test,
and save a screenshot when a test fails."""

import pytest

from acturis import app, ui


@pytest.fixture(scope="session")
def acturis():
    """Opens Acturis and logs in once for the whole run; closes it at the end."""
    try:
        app.launch_and_log_in()
    except Exception:
        ui.screenshot("FAILED_login")
        app.close_acturis()
        raise
    yield
    app.close_acturis()


@pytest.fixture
def logged_in(acturis):
    """Use in every test: makes sure we're logged in, and goes back to the start screen afterwards."""
    yield
    app.return_to_start_screen()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        path = ui.screenshot(f"FAILED_{item.name}")
        if path:
            report.sections.append(("Screenshot", str(path)))
