from unittest.mock import Mock

from acturis import ui


def test_scroll_into_view_uses_scroll_item_pattern(monkeypatch):
    control = Mock()
    monkeypatch.setattr(ui, "find", lambda locator, timeout: control)

    ui.scroll_into_view([{"title": "Authorise Refer", "control_type": "ListItem"}])

    control.iface_scroll_item.ScrollIntoView.assert_called_once_with()
