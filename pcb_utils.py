# -*- coding: utf-8 -*-
import pcbnew
import wx

from .i18n import tr


def _looks_like_pcb_editor(window):
    if window is None:
        return False

    try:
        class_name = window.GetClassName() or ""
    except Exception:
        class_name = ""

    title = window.GetTitle() or ""
    name = window.GetName() or ""
    haystack = " ".join((title, name, class_name)).lower()
    return any(token in haystack for token in ("pcbnew", "pcb editor", "board editor"))


def find_pcb_editor_window():
    if not wx.GetApp():
        return None

    active = wx.GetActiveWindow()
    if active and _looks_like_pcb_editor(active):
        return active

    try:
        windows = list(wx.GetTopLevelWindows())
    except Exception:
        windows = []

    matching = [window for window in windows if _looks_like_pcb_editor(window)]

    for window in matching:
        try:
            if window.IsActive():
                return window
        except Exception:
            pass

    for window in matching:
        try:
            if window.IsShown():
                return window
        except Exception:
            pass

    return matching[0] if matching else None


def normalize_item(item):
    if item is None:
        return None

    try:
        return item.Cast()
    except Exception:
        return item


def item_key(item):
    item = normalize_item(item)

    try:
        return item.m_Uuid.AsString()
    except Exception:
        return "{0}:{1}".format(item.GetClass(), id(item))


def item_friendly_name(item):
    item = normalize_item(item)

    try:
        return item.GetFriendlyName()
    except Exception:
        try:
            return item.GetClass()
        except Exception:
            return type(item).__name__


def item_net_name(item):
    item = normalize_item(item)

    if item is None or not hasattr(item, "GetNetCode"):
        return tr("na")

    try:
        if item.GetNetCode() <= 0:
            return tr("no_net")
    except Exception:
        return tr("na")

    try:
        name = item.GetNetname()
    except Exception:
        name = ""

    return name or tr("unnamed_net")


def describe_item(item):
    item = normalize_item(item)
    return "{0} [{1}]".format(item_friendly_name(item), item_net_name(item))


def supports_net_assignment(item):
    item = normalize_item(item)
    required_methods = ("GetNet", "GetNetCode", "GetNetname", "SetNet", "SetNetCode")
    return all(hasattr(item, method_name) for method_name in required_methods)


def is_zone_item(item):
    item = normalize_item(item)
    return isinstance(item, pcbnew.ZONE)
