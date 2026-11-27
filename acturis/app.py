"""Starting, logging in to and closing Acturis Assistant."""

import logging
import os
import time

from pywinauto import Application

from acturis import config, locators, ui

log = logging.getLogger("acturis")


def launch_and_log_in():
    username, password = config.get_credentials()

    if ui.main_window_exists():
        raise RuntimeError("Acturis is already open. Close it, then run the tests again.")

    start = time.monotonic()
    # Quotes around the path because it contains spaces; start it from its own folder.
    Application(backend="uia").start(
        f'"{config.APP_PATH}"',
        work_dir=os.path.dirname(config.APP_PATH),
        wait_for_idle=False,
    )

    # The first start can be slow, so keep checking until the login screen appears.
    ui.wait_for(locators.LOGIN_PANE, timeout=config.STARTUP_TIMEOUT)
    # Uncomment if "Log On to Acturis" isn't selected by default:
    # ui.click(locators.LOGIN_RB_LOGON)
    ui.set_text(locators.LOGIN_TXT_USERNAME, username)
    ui.set_text(locators.LOGIN_TXT_PASSWORD, password, secret=True)
    ui.click(locators.LOGIN_BTN_LOGIN)

    # Logged in once the login screen has closed and the module tabs are shown
    ui.wait_until_gone(locators.LOGIN_PANE, timeout=config.LOGIN_TIMEOUT)
    ui.wait_for(locators.TAB_UNDERWRITING, timeout=config.LOGIN_TIMEOUT)
    log.info("logged in after %.1fs", time.monotonic() - start)


def open_underwriting_tab():
    ui.click(locators.TAB_UNDERWRITING)
    # The tab is ready when its Search list (Locate Quote, Locate Policy...) is shown
    try:
        ui.wait_for(locators.NAV_SEARCH_LIST)
    except AssertionError:
        raise AssertionError(
            "The UNDERWRITING Search list (Locate Quote, Locate Policy...) didn't appear. "
            "If a quote or policy from an earlier step or test is still open, it has to be closed "
            "first: add those clicks to return_to_start_screen() in acturis/app.py."
        ) from None


def return_to_start_screen():
    """Runs after every test so the next one starts from a clean screen."""
    # TODO: add the clicks that close an opened quote / policy once you know them.
    for cancel_button in (locators.LQ_BTN_CANCEL, locators.LP_BTN_CANCEL):
        try:
            if ui.exists(cancel_button):
                ui.click(cancel_button)
        except Exception as error:
            log.warning("couldn't return to the start screen: %s", error)


def close_acturis():
    """Closes the main window; kills the process if it doesn't close within 15 seconds."""
    window = ui.main_window()
    if window is None:
        return
    process_id = window.element_info.process_id
    try:
        window.close()
        ui.wait_until_gone([], timeout=15)
    except Exception:
        try:
            Application(backend="uia").connect(process=process_id).kill()
        except Exception as error:
            log.warning("couldn't close Acturis: %s", error)
