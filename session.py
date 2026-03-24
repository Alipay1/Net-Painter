# -*- coding: utf-8 -*-
import pcbnew
import wx

from .config import POLL_INTERVAL_MS
from .i18n import tr
from .pcb_utils import (
    find_pcb_editor_window,
    is_zone_item,
    item_friendly_name,
    item_key,
    item_net_name,
    normalize_item,
    supports_net_assignment,
)
from .ui import NetPainterWindow


class NetPainterSession:
    def __init__(self, on_close=None):
        self.board = pcbnew.GetBoard()
        self.parent_window = find_pcb_editor_window()
        self.dialog = NetPainterWindow(self)
        self.timer = wx.Timer(self.dialog)
        self.dialog.Bind(wx.EVT_TIMER, self.on_timer)

        self.on_close_callback = on_close
        self.source_item = None
        self.target_item = None
        self.source_id = None
        self.previous_supported_ids = set()
        self.baseline_supported_ids = set()
        self.last_feedback = None
        self.keep_status_until_selection = False
        self.closed = False

    def start(self):
        self._reset_state(clear_selection=True)
        self._position_dialog()
        self._show_dialog()
        self.timer.Start(POLL_INTERVAL_MS)
        self._focus_editor()

    def restart(self):
        if self.closed:
            return

        self._reset_state(clear_selection=True)

        if not self.timer.IsRunning():
            self.timer.Start(POLL_INTERVAL_MS)

        self._show_dialog()
        self._focus_editor()

    def cancel(self):
        if self.closed:
            return

        self.closed = True

        if self.timer.IsRunning():
            self.timer.Stop()

        if self.dialog:
            self.dialog.Hide()
            self.dialog.Destroy()
            self.dialog = None

        if self.on_close_callback is not None:
            self.on_close_callback()

    def present(self):
        if self.closed or not self.dialog:
            return

        self._show_dialog()
        self._focus_editor()

    def on_timer(self, _event):
        if self.closed:
            return

        try:
            snapshot = self._selection_snapshot()
            current_supported_ids = set(snapshot["supported"].keys())
            new_supported_ids = current_supported_ids - self.previous_supported_ids

            if self.source_item is None:
                self._handle_source_phase(snapshot, current_supported_ids, new_supported_ids)
            else:
                self._handle_target_phase(snapshot, new_supported_ids)

            self.previous_supported_ids = current_supported_ids
        except Exception as exc:
            if self.timer.IsRunning():
                self.timer.Stop()

            self.dialog.set_phase(tr("step_error"))
            self.dialog.set_status(tr("status_unexpected_error", error=exc), tone="error")

    def _reset_state(self, clear_selection, status_text=None, status_tone="info", sticky=False):
        if clear_selection:
            self._clear_selection()

        supported = self._selection_snapshot()["supported"]
        supported_ids = set(supported.keys())

        self.source_item = None
        self.target_item = None
        self.source_id = None
        self.previous_supported_ids = set(supported_ids)
        self.baseline_supported_ids = set(supported_ids)
        self.last_feedback = None
        self.keep_status_until_selection = sticky

        self.dialog.set_phase(tr("step_source"))
        self.dialog.set_source(None)
        self.dialog.set_target(None)
        self.dialog.set_status(status_text or tr("status_wait_source"), tone=status_tone)

    def _handle_source_phase(self, snapshot, current_supported_ids, new_supported_ids):
        candidate = None

        if len(snapshot["supported"]) == 1 and current_supported_ids != self.baseline_supported_ids:
            candidate = next(iter(snapshot["supported"].values()))
        elif len(new_supported_ids) == 1:
            candidate = snapshot["supported"][next(iter(new_supported_ids))]

        if candidate:
            self._capture_source(candidate)
            return

        self._update_feedback(snapshot, target_phase=False)

    def _handle_target_phase(self, snapshot, new_supported_ids):
        candidate = None

        if len(snapshot["supported"]) == 1:
            only_id, only_item = next(iter(snapshot["supported"].items()))
            if only_id != self.source_id:
                candidate = only_item
        elif len(new_supported_ids) == 1:
            new_id = next(iter(new_supported_ids))
            if new_id != self.source_id:
                candidate = snapshot["supported"][new_id]

        if candidate:
            self._capture_target(candidate)
            return

        self._update_feedback(snapshot, target_phase=True)

    def _capture_source(self, item):
        self.source_item = normalize_item(item)
        self.source_id = item_key(self.source_item)
        self.keep_status_until_selection = False

        self.dialog.set_source(self.source_item)
        self.dialog.set_phase(tr("step_target"))
        self.dialog.set_status(tr("status_source_captured"))
        self.last_feedback = None

        self._clear_selection()
        self._focus_editor()

    def _capture_target(self, item):
        self.target_item = normalize_item(item)
        self.dialog.set_target(self.target_item)
        self.keep_status_until_selection = False
        self.last_feedback = None

        self._apply_net_copy()

    def _apply_net_copy(self):
        target_net_code = self.target_item.GetNetCode()

        if target_net_code <= 0:
            self.dialog.set_status(tr("status_target_no_net"), tone="error")
            return False

        target_net = self.target_item.GetNet() or self.board.FindNet(target_net_code)
        if target_net is None:
            self.dialog.set_status(tr("status_target_unresolved"), tone="error")
            return False

        source_before = item_net_name(self.source_item)
        target_name = item_net_name(self.target_item)

        self.source_item.SetNet(target_net)
        self.source_item.SetNetCode(target_net_code)

        self.board.BuildConnectivity()

        if is_zone_item(self.source_item):
            zones = pcbnew.ZONES()
            zones.append(self.source_item)
            pcbnew.ZONE_FILLER(self.board).Fill(zones, False, self.parent_window)

        pcbnew.Refresh()
        pcbnew.UpdateUserInterface()

        try:
            pcbnew.FocusOnItem(self.source_item)
        except Exception:
            pass

        self._reset_state(
            clear_selection=True,
            status_text=tr(
                "status_success_ready",
                target_net=target_name,
                source_net=source_before,
            ),
            status_tone="success",
            sticky=True,
        )
        return True

    def _update_feedback(self, snapshot, target_phase):
        if self.keep_status_until_selection and not snapshot["raw"]:
            return

        waiting_message = tr("status_wait_target") if target_phase else tr("status_wait_source")

        token = None
        message = waiting_message

        if len(snapshot["raw"]) == 1:
            self.keep_status_until_selection = False
            only_item = normalize_item(snapshot["raw"][0])

            if not supports_net_assignment(only_item):
                token = "unsupported:{0}".format(item_friendly_name(only_item))
                message = tr("status_unsupported")
                tone = "error"
            elif target_phase and item_key(only_item) == self.source_id:
                token = "same-item"
                message = tr("status_same_item")
                tone = "error"
            else:
                tone = "info"
        elif len(snapshot["raw"]) > 1:
            self.keep_status_until_selection = False
            token = "ambiguous:{0}".format(len(snapshot["raw"]))
            message = tr("status_ambiguous")
            tone = "error"
        else:
            tone = "info"

        if token != self.last_feedback:
            self.dialog.set_status(message, tone=tone)
            self.last_feedback = token

    def _selection_snapshot(self):
        raw_items = [normalize_item(item) for item in pcbnew.GetCurrentSelection()]
        supported = {}

        for item in raw_items:
            if supports_net_assignment(item):
                supported[item_key(item)] = item

        return {"raw": raw_items, "supported": supported}

    def _clear_selection(self):
        try:
            for item in list(pcbnew.GetCurrentSelection()):
                normalize_item(item).ClearSelected()
        except Exception:
            return

        self.previous_supported_ids = set()
        pcbnew.Refresh()
        pcbnew.UpdateUserInterface()

    def _show_dialog(self):
        if hasattr(self.dialog, "ShowWithoutActivating"):
            self.dialog.ShowWithoutActivating()
        else:
            self.dialog.Show()

        try:
            self.dialog.Raise()
        except Exception:
            pass

    def _focus_editor(self):
        if self.parent_window is None:
            return

        try:
            self.parent_window.SetFocus()
        except Exception:
            pass

    def _position_dialog(self):
        if self.parent_window is None:
            self.dialog.CentreOnScreen()
            return

        rect = self.parent_window.GetScreenRect()
        size = self.dialog.GetSize()
        x = max(0, rect.x + rect.width - size.width - 32)
        y = max(0, rect.y + 96)
        self.dialog.Move(wx.Point(x, y))
