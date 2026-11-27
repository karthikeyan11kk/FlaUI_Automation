"""Settings: app path, test data, timeouts, and the login read from testdata/credentials.env."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TESTDATA_DIR = BASE_DIR / "testdata"
RESULTS_DIR = BASE_DIR / "results"
SCREENSHOT_DIR = RESULTS_DIR / "screenshots"

# A raw string (r"...") keeps the backslashes as they are, so no doubling is needed.
APP_PATH = r"C:\Program Files (x86)\Acturis\Installation\ActurisAssistant.exe"

# Test data: one row per test case, matched on the TestCaseName column (.xls or .xlsx)
TESTDATA_FILE = TESTDATA_DIR / "TestData.xls"
TESTDATA_SHEET = "Execution"
CREDENTIALS_FILE = TESTDATA_DIR / "credentials.env"

# Timeouts in seconds
STARTUP_TIMEOUT = 120
LOGIN_TIMEOUT = 60
SCREEN_TIMEOUT = 30


def load_env_file(path):
    """Reads KEY=value lines (# starts a comment line). Values are used exactly as written.
    A Windows environment variable with the same name overrides the file."""
    if not Path(path).is_file():
        raise FileNotFoundError(f"File not found: {path}")
    values = {}
    with open(path, encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"{path}, line {line_number}: expected KEY=value, got '{line}'")
            key, value = (part.strip() for part in line.split("=", 1))
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            values[key] = os.environ.get(key, value)
    return values


def get_credentials():
    """Returns (username, password) from credentials.env, failing clearly if either is empty."""
    values = load_env_file(CREDENTIALS_FILE)
    username = values.get("ACTURIS_USERNAME", "")
    password = values.get("ACTURIS_PASSWORD", "")
    if not username:
        raise ValueError("ACTURIS_USERNAME is empty in testdata/credentials.env")
    if not password:
        raise ValueError("ACTURIS_PASSWORD is empty in testdata/credentials.env")
    return username, password


def get_authorisation_code():
    """The code typed into Authorise Refer, from ACTURIS_AUTH_CODE in credentials.env."""
    code = load_env_file(CREDENTIALS_FILE).get("ACTURIS_AUTH_CODE", "")
    if not code:
        raise ValueError("ACTURIS_AUTH_CODE is empty or missing in testdata/credentials.env")
    return code
