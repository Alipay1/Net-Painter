# -*- coding: utf-8 -*-
import wx

from .config import (
    UI_WRAP_WIDTH,
    WINDOW_MAX_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
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
        self._wrapped_labels = ()

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

        self.button_panel = wx.Panel(self.panel)
        button_sizer = wx.StdDialogButtonSizer()
        self.reset_button = wx.Button(self.button_panel, label=tr("button_reset"))
        self.close_button = wx.Button(self.button_panel, label=tr("button_close"))
        self.reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        self.close_button.Bind(wx.EVT_BUTTON, self._on_close_button)

        self._wrapped_labels = (
            self.instructions_label,
            self.source_label,
            self.target_label,
            self.status_label,
        )
        self._update_metrics()

        button_sizer.AddButton(self.reset_button)
        button_sizer.AddButton(self.close_button)
        button_sizer.Realize()
        button_row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_row_sizer.AddStretchSpacer()
        button_row_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        button_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        button_panel_sizer.Add(
            button_row_sizer,
            1,
            wx.EXPAND | wx.TOP | wx.BOTTOM,
            self._spacing["button_panel_padding_v"],
        )
        self.button_panel.SetSizer(button_panel_sizer)

        self.panel_sizer.Add(title, 0, wx.BOTTOM, self._spacing["title_bottom"])
        self.panel_sizer.Add(
            self.instructions_label,
            0,
            wx.EXPAND | wx.BOTTOM,
            self._spacing["instructions_bottom"],
        )
        self.panel_sizer.Add(
            self.phase_label,
            0,
            wx.BOTTOM,
            self._spacing["phase_bottom"],
        )
        self.panel_sizer.Add(
            self.source_label,
            0,
            wx.BOTTOM,
            self._spacing["source_bottom"],
        )
        self.panel_sizer.Add(
            self.target_label,
            0,
            wx.BOTTOM,
            self._spacing["target_bottom"],
        )
        self.panel_sizer.Add(
            self.status_label,
            0,
            wx.EXPAND | wx.BOTTOM,
            self._spacing["status_bottom"],
        )
        self.panel_sizer.Add(self.button_panel, 0, wx.EXPAND)

        self.panel.SetSizer(self.panel_sizer)
        self.root_sizer.Add(self.panel, 1, wx.ALL | wx.EXPAND, self._spacing["panel_border"])
        self.SetSizerAndFit(self.root_sizer)

        self._apply_wrapping()
        self._refresh_window_size()

        self.Bind(wx.EVT_CLOSE, self._on_close)
        if hasattr(wx, "EVT_DPI_CHANGED"):
            self.Bind(wx.EVT_DPI_CHANGED, self._on_dpi_changed)

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

    def _update_metrics(self):
        self._preferred_width = self.FromDIP(WINDOW_MIN_WIDTH)
        self._maximum_width = self.FromDIP(WINDOW_MAX_WIDTH)
        self._minimum_size = self.FromDIP(wx.Size(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT))
        self._base_wrap_width = min(self.FromDIP(UI_WRAP_WIDTH), self._maximum_width)
        self._spacing = {
            "panel_border": self.FromDIP(14),
            "title_bottom": self.FromDIP(8),
            "instructions_bottom": self.FromDIP(12),
            "phase_bottom": self.FromDIP(8),
            "source_bottom": self.FromDIP(6),
            "target_bottom": self.FromDIP(10),
            "status_bottom": self.FromDIP(14),
            "button_min_width": self.FromDIP(108),
            "button_min_height": self.FromDIP(40),
            "button_panel_padding_v": self.FromDIP(6),
        }
        self._configure_button_min_size(self.reset_button)
        self._configure_button_min_size(self.close_button)
        self._configure_button_panel_min_size()

    def _configure_button_min_size(self, button):
        best_size = button.GetBestSize()
        default_size = self.FromDIP(wx.Button.GetDefaultSize())
        button.SetMinSize(
            wx.Size(
                max(best_size.width, self._spacing["button_min_width"]),
                max(
                    best_size.height,
                    default_size.height,
                    self._spacing["button_min_height"],
                ),
            )
        )
        button.SetInitialSize(button.GetMinSize())

    def _configure_button_panel_min_size(self):
        best_height = max(
            self.reset_button.GetMinSize().height,
            self.close_button.GetMinSize().height,
        )
        panel_min_height = best_height + self._spacing["button_panel_padding_v"] * 2
        self.button_panel.SetMinSize(wx.Size(-1, panel_min_height))
        self.button_panel.SetInitialSize(wx.Size(-1, panel_min_height))

    def _apply_wrapping(self):
        for label in self._wrapped_labels:
            label.Wrap(self._base_wrap_width)
            label.InvalidateBestSize()

    def _refresh_window_size(self):
        frozen_here = False

        if not self.IsFrozen():
            self.Freeze()
            frozen_here = True

        try:
            self._apply_wrapping()
            self.button_panel.Layout()
            self.panel_sizer.Fit(self.panel)
            self.root_sizer.SetSizeHints(self)
            self.SetSizeHints(
                self._preferred_width,
                self._minimum_size.height,
                self._maximum_width,
                -1,
            )
            self.Fit()
            size = self.GetSize()
            clamped_width = min(max(size.width, self._preferred_width), self._maximum_width)
            if clamped_width != size.width:
                self.SetSize(wx.Size(clamped_width, size.height))
            self.Layout()
        finally:
            if frozen_here:
                self.Thaw()

    def _on_dpi_changed(self, event):
        self._update_metrics()
        self._refresh_window_size()
        event.Skip()

    def _on_reset(self, _event):
        self.controller.restart()

    def _on_close_button(self, _event):
        self.controller.cancel()

    def _on_close(self, _event):
        self.controller.cancel()
