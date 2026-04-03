# -*- coding: utf-8 -*-
import os


PLUGIN_VERSION = "0.3.0"
POLL_INTERVAL_MS = 50
UI_WRAP_WIDTH = 520
WINDOW_MIN_WIDTH = 580
WINDOW_MIN_HEIGHT = 280
WINDOW_MAX_WIDTH = 720

# 留空时自动跟随 KiCad 语言；可选值："zh" / "en"
LANGUAGE_OVERRIDE = ""

SCRIPT_DIR = os.path.dirname(__file__)
ICON_FILE = os.path.join(SCRIPT_DIR, "net_painter_icon.png")
DARK_ICON_FILE = os.path.join(SCRIPT_DIR, "net_painter_icon_dark.png")
