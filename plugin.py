# -*- coding: utf-8 -*-
import pcbnew
import wx

from .config import DARK_ICON_FILE, ICON_FILE
from .i18n import tr
from .session import NetPainterSession


_ACTIVE_SESSION = None


def _clear_active_session():
    global _ACTIVE_SESSION
    _ACTIVE_SESSION = None


class NetPainterActionPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = tr("plugin_name")
        self.category = tr("plugin_category")
        self.description = tr("plugin_description")
        self.icon_file_name = ICON_FILE
        self.dark_icon_file_name = DARK_ICON_FILE
        self.show_toolbar_button = True

    def Run(self):
        global _ACTIVE_SESSION

        board = pcbnew.GetBoard()
        if board is None:
            wx.MessageBox(
                tr("message_open_board"),
                tr("window_title"),
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        if _ACTIVE_SESSION is not None:
            _ACTIVE_SESSION.present()
            return

        _ACTIVE_SESSION = NetPainterSession(on_close=_clear_active_session)
        _ACTIVE_SESSION.start()
