# -*- coding: utf-8 -*-
import wx

from .config import UI_WRAP_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from .i18n import tr
from .pcb_utils import describe_item


class NetPainterWindow(wx.Frame):
    def __init__(self, controller):
        style = (
            wx.CAPTION
            | wx.CLOSE_BOX
            | wx.FRAME_NO_TASKBAR
            | wx.FRAME_TOOL_WINDOW
            | wx.STAY_ON_TOP
        )
        super().__init__(None, title=tr("window_title"), style=style)

        self.controller = controller
        self._preferred_width = WINDOW_MIN_WIDTH
        self._wrap_width = UI_WRAP_WIDTH

        self.panel = wx.Panel(self)
        self.root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self.panel, label=tr("headline"))
        title_font = title.GetFont()
        title_font.MakeBold()
        title.SetFont(title_font)

        self.instructions_label = wx.StaticText(self.panel, label=tr("instructions"))
        self.phase_label = wx.StaticText(self.panel, label="")
        self.source_label = wx.StaticText(self.panel, label=tr("source_waiting"))
        self.target_label = wx.StaticText(self.panel, label=tr("target_waiting"))
        self.status_label = wx.StaticText(self.panel, label="")

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        reset_button = wx.Button(self.panel, label=tr("button_reset"))
        close_button = wx.Button(self.panel, label=tr("button_close"))
        reset_button.SetMinSize(wx.Size(108, 36))
        close_button.SetMinSize(wx.Size(108, 36))
        reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        close_button.Bind(wx.EVT_BUTTON, self._on_close_button)

        button_sizer.Add(reset_button, 0, wx.RIGHT, 10)
        button_sizer.Add(close_button, 0)

        self.panel_sizer.Add(title, 0, wx.BOTTOM, 8)
        self.panel_sizer.Add(self.instructions_label, 0, wx.EXPAND | wx.BOTTOM, 12)
        self.panel_sizer.Add(self.phase_label, 0, wx.BOTTOM, 8)
        self.panel_sizer.Add(self.source_label, 0, wx.BOTTOM, 6)
        self.panel_sizer.Add(self.target_label, 0, wx.BOTTOM, 10)
        self.panel_sizer.Add(self.status_label, 0, wx.EXPAND | wx.BOTTOM, 14)
        self.panel_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT)

        self.panel.SetSizer(self.panel_sizer)
        self.root_sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND, 14)
        self.SetSizer(self.root_sizer)

        self._apply_wrapping()
        self.root_sizer.Fit(self)
        self._preferred_width = max(WINDOW_MIN_WIDTH, self.GetSize().width)
        self.SetMinSize(wx.Size(self._preferred_width, WINDOW_MIN_HEIGHT))
        self._refresh_window_size()

        self.Bind(wx.EVT_CLOSE, self._on_close)

    def set_phase(self, text):
        self.phase_label.SetLabel(text)
        self._refresh_window_size()

    def set_source(self, item):
        label = tr("source_value", description=describe_item(item)) if item else tr("source_waiting")
        self.source_label.SetLabel(label)
        self._refresh_window_size()

    def set_target(self, item):
        label = tr("target_value", description=describe_item(item)) if item else tr("target_waiting")
        self.target_label.SetLabel(label)
        self._refresh_window_size()

    def set_status(self, text, tone="info"):
        if tone == "error":
            color = wx.Colour(170, 45, 45)
        elif tone == "success":
            color = wx.Colour(42, 112, 62)
        else:
            color = wx.Colour(35, 82, 124)

        self.status_label.SetForegroundColour(color)
        self.status_label.SetLabel(text)
        self._refresh_window_size()

    def _apply_wrapping(self):
        for label in (
            self.instructions_label,
            self.source_label,
            self.target_label,
            self.status_label,
        ):
            label.Wrap(self._wrap_width)

    def _refresh_window_size(self):
        self._apply_wrapping()
        self.panel_sizer.Layout()
        self.root_sizer.Layout()

        best_size = self.root_sizer.CalcMin()
        width = max(self._preferred_width, best_size.width + 28)
        height = max(WINDOW_MIN_HEIGHT, best_size.height + 28)

        self.SetMinSize(wx.Size(self._preferred_width, WINDOW_MIN_HEIGHT))
        self.SetSize(wx.Size(width, height))
        self.Layout()

    def _on_reset(self, _event):
        self.controller.restart()

    def _on_close_button(self, _event):
        self.controller.cancel()

    def _on_close(self, _event):
        self.controller.cancel()
