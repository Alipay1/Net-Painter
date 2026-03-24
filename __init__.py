import traceback

import wx

try:
    from .plugin import NetPainterActionPlugin

    NetPainterActionPlugin().register()
except Exception as exc:
    wx.LogMessage(
        "net_painter plugin error\n{0}\n{1}".format(
            exc, traceback.format_exc()
        )
    )
