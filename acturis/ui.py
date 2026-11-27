"""Small helpers on top of pywinauto, so the flows read like plain steps.

Every function takes a locator from acturis/locators.py: a list of criteria dicts
chained from the Acturis main window down to the element.

Why this doesn't use pywinauto's child_window() to FIND elements:
child_window() fetches every element of a type in the whole window and then checks
each auto_id from Python, one cross-process call at a time, and wait() repeats that
up to three times per action. On a big WPF screen like Acturis that takes seconds
per step. Here the search runs inside Windows UI Automation instead (FindFirst with
auto_id / title / control_type conditions), which stops at the first match.
pywinauto is still used for the actions themselves (click_input, set_edit_text, select).

Failures raise an AssertionError that names the locator, so the report shows what
wasn't found. Each action is logged with how long it took to find the element.
"""

import ctypes
import logging
import re
import time
from datetime import datetime

from comtypes import COMError
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper
import pywinauto.controls.uia_controls  # noqa: F401  (registers the Edit / ComboBox / ... wrappers)
from pywinauto.uia_defines import IUIA
from pywinauto.uia_element_info import UIAElementInfo

from acturis import config, locators

log = logging.getLogger("acturis")

_UIA = IUIA()
_PROPERTY_IDS = {
    "auto_id": getattr(_UIA.UIA_dll, "UIA_AutomationIdPropertyId", 30011),
    "title": getattr(_UIA.UIA_dll, "UIA_NamePropertyId", 30005),
    "control_type": getattr(_UIA.UIA_dll, "UIA_ControlTypePropertyId", 30003),
    "class_name": getattr(_UIA.UIA_dll, "UIA_ClassNamePropertyId", 30012),
}
_CHILDREN = _UIA.tree_scope["children"]
_DESCENDANTS = _UIA.tree_scope["descendants"]
_ALLOWED_KEYS = set(_PROPERTY_IDS) | {"title_re", "found_index"}
_POLL_SECONDS = 0.25

_main_window_cache = None


# ==========================================================================
# Finding elements
# ==========================================================================
def _condition(criteria):
    unknown = set(criteria) - _ALLOWED_KEYS
    if unknown:
        raise ValueError(f"Unsupported locator key(s) {sorted(unknown)}. Use: {sorted(_ALLOWED_KEYS)}")
    conditions = []
    for key, property_id in _PROPERTY_IDS.items():
        if key in criteria:
            value = criteria[key]
            if key == "control_type":
                value = _UIA.known_control_types[value]
            conditions.append(_UIA.iuia.CreatePropertyCondition(property_id, value))
    if not conditions:
        return _UIA.true_condition
    if len(conditions) == 1:
        return conditions[0]
    return _UIA.iuia.CreateAndConditionFromArray(conditions)


def _find_in(parent, criteria, scope=_DESCENDANTS):
    """First element below parent matching criteria, or None."""
    condition = _condition(criteria)
    title_re = criteria.get("title_re")
    index = criteria.get("found_index", 0)

    if title_re is None and index == 0:
        element = parent.FindFirst(scope, condition)
        return element if element else None

    found = parent.FindAll(scope, condition)
    matches = 0
    for i in range(found.Length):
        element = found.GetElement(i)
        try:
            if title_re is None or re.search(title_re, element.CurrentName or ""):
                if matches == index:
                    return element
                matches += 1
        except COMError:
            continue
    return None


def _main_window_element():
    """The Acturis main window (cached until it closes or its title stops matching)."""
    global _main_window_cache
    title_re = locators.MAIN_WINDOW["title_re"]
    if _main_window_cache is not None:
        try:
            if re.search(title_re, _main_window_cache.CurrentName or ""):
                return _main_window_cache
        except (COMError, ValueError):
            pass
        _main_window_cache = None
    _main_window_cache = _find_in(_UIA.root, locators.MAIN_WINDOW, scope=_CHILDREN)
    return _main_window_cache


def _resolve(locator):
    element = _main_window_element()
    for criteria in locator:
        if element is None:
            return None
        element = _find_in(element, criteria)
    return element


def _wrap(element):
    return UIAWrapper(UIAElementInfo(element))


def describe(locator):
    if not locator:
        return f"main window {locators.MAIN_WINDOW}"
    return " > ".join(
        ", ".join(f"{key}={value!r}" for key, value in criteria.items()) for criteria in locator
    )


def short_name(locator):
    if not locator:
        return "main window"
    last = locator[-1]
    return str(last.get("auto_id") or last.get("title") or last.get("title_re") or last.get("control_type"))


def find(locator, timeout=config.SCREEN_TIMEOUT, enabled=False):
    """Waits until the element exists (and is enabled, if asked) and returns its pywinauto wrapper."""
    start = time.monotonic()
    while True:
        try:
            element = _resolve(locator)
            if element is not None and (not enabled or element.CurrentIsEnabled):
                return _wrap(element)
        except (COMError, ValueError):
            pass  # the screen changed while searching: try again
        if time.monotonic() - start >= timeout:
            raise AssertionError(f"Not found within {timeout}s: {describe(locator)}")
        time.sleep(_POLL_SECONDS)


def wait_for(locator, timeout=config.SCREEN_TIMEOUT):
    start = time.monotonic()
    control = find(locator, timeout)
    log.info("found   %-45s %5.1fs", short_name(locator), time.monotonic() - start)
    return control


def exists(locator, timeout=0):
    start = time.monotonic()
    while True:
        try:
            if _resolve(locator) is not None:
                return True
        except (COMError, ValueError):
            pass
        if time.monotonic() - start >= timeout:
            return False
        time.sleep(_POLL_SECONDS)


def wait_until_gone(locator, timeout=config.SCREEN_TIMEOUT):
    start = time.monotonic()
    while exists(locator):
        if time.monotonic() - start >= timeout:
            raise AssertionError(f"Still shown after {timeout}s: {describe(locator)}")
        time.sleep(_POLL_SECONDS)
    log.info("gone    %-45s %5.1fs", short_name(locator), time.monotonic() - start)


def child_names(locator):
    """Names of the element's direct children, e.g. every item in a list."""
    parent = _resolve(locator)
    if parent is None:
        return []
    found = parent.FindAll(_CHILDREN, _UIA.true_condition)
    names = []
    for i in range(found.Length):
        try:
            names.append(found.GetElement(i).CurrentName)
        except COMError:
            continue
    return names


# ==========================================================================
# Main window
# ==========================================================================
def main_window_exists(timeout=0):
    return exists([], timeout)


def main_window_title():
    try:
        element = _main_window_element()
        return element.CurrentName if element is not None else ""
    except COMError:
        return ""


def main_window():
    """The main window's pywinauto wrapper, or None if Acturis isn't open."""
    element = _main_window_element()
    return _wrap(element) if element is not None else None


def main_window_spec():
    """pywinauto's own WindowSpecification (slow searches; used by tools/print_controls.py)."""
    return Desktop(backend="uia").window(**locators.MAIN_WINDOW)


def _bring_acturis_to_front():
    """Mouse clicks land on whatever is on top, e.g. FlaUInspect: make sure Acturis is."""
    try:
        element = _main_window_element()
        if element is None:
            return
        user32 = ctypes.windll.user32
        foreground_pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(foreground_pid))
        if foreground_pid.value != element.CurrentProcessId:
            _wrap(element).set_focus()
    except Exception:
        pass  # never fail a step just because focusing didn't work


# ==========================================================================
# Actions
# ==========================================================================
def click(locator, timeout=config.SCREEN_TIMEOUT):
    """A real mouse click in the middle of the element."""
    start = time.monotonic()
    control = find(locator, timeout, enabled=True)
    log.info("click   %-45s %5.1fs", short_name(locator), time.monotonic() - start)
    _bring_acturis_to_front()
    control.click_input()


def scroll_into_view(locator, timeout=config.SCREEN_TIMEOUT):
    """Scrolls the containing pane until the UIA item is visible."""
    start = time.monotonic()
    control = find(locator, timeout)
    log.info("scroll  %-45s %5.1fs", short_name(locator), time.monotonic() - start)
    control.iface_scroll_item.ScrollIntoView()


def set_text(locator, value, timeout=config.SCREEN_TIMEOUT, secret=False):
    start = time.monotonic()
    control = find(locator, timeout, enabled=True)
    log.info("type    %-45s %5.1fs  %s", short_name(locator), time.monotonic() - start,
             "***" if secret else value)
    try:
        control.set_edit_text(value)
    except Exception:
        # Some fields (e.g. masked password boxes) refuse direct setting: type the text instead.
        _bring_acturis_to_front()
        control.click_input()
        control.type_keys("^a{BACKSPACE}", set_foreground=True)
        control.type_keys(_escape_keys(value), with_spaces=True, set_foreground=True)


def select_combo_item(locator, item_name, timeout=config.SCREEN_TIMEOUT):
    """Picks an item from a drop-down by its Name, e.g. 'Insurer Quote No.'.
    If the item isn't there, the error lists every option the drop-down has."""
    start = time.monotonic()
    combo = find(locator, timeout, enabled=True)
    log.info("select  %-45s %5.1fs  %s", short_name(locator), time.monotonic() - start, item_name)
    try:
        combo.select(item_name)
        return
    except Exception:
        pass
    # Fallback: open the drop-down and click the item
    try:
        _bring_acturis_to_front()
        combo.click_input()
        click(locator + [{"title": item_name, "control_type": "ListItem"}], timeout=5)
    except AssertionError:
        raise AssertionError(
            f"'{item_name}' isn't in the drop-down {short_name(locator)}. "
            f"Options: {', '.join(item_names(locator))}"
        ) from None


def item_names(locator):
    """Names of every list item inside an element, e.g. a drop-down's options."""
    parent = _resolve(locator)
    if parent is None:
        return []
    found = parent.FindAll(_DESCENDANTS, _condition({"control_type": "ListItem"}))
    names = []
    for i in range(found.Length):
        try:
            names.append(found.GetElement(i).CurrentName)
        except COMError:
            continue
    return names


def screenshot(name):
    """Saves a screenshot of all screens to results/screenshots and returns its path.
    A failed screenshot only logs a warning, so it never fails a test."""
    try:
        from PIL import ImageGrab

        config.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^\w.-]+", "_", name)
        path = config.SCREENSHOT_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{safe_name}.png"
        ImageGrab.grab(all_screens=True).save(path)
        return path
    except Exception as error:
        log.warning("screenshot '%s' failed: %s", name, error)
        return None


def _escape_keys(text):
    """type_keys treats + ^ % ~ ( ) { } as special keys; wrap them in {} to type them literally."""
    return re.sub(r"([+^%~(){}\[\]])", r"{\1}", text)
