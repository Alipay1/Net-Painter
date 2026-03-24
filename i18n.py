# -*- coding: utf-8 -*-
import locale

import pcbnew

from . import config


TRANSLATIONS = {
    "en": {
        "plugin_name": "Net Painter",
        "plugin_category": "Modify PCB",
        "plugin_description": "Copy the net from one PCB object to another with two clicks.",
        "window_title": "Net Painter",
        "headline": "Copy a net in two clicks",
        "instructions": (
            "1. Click the source object to be changed.\n"
            "2. Click the target object whose net should be copied."
        ),
        "source_waiting": "Source: waiting",
        "target_waiting": "Target: waiting",
        "source_value": "Source: {description}",
        "target_value": "Target: {description}",
        "button_reset": "Reset",
        "button_close": "Close",
        "step_source": "Step 1/2: click the source object",
        "step_target": "Step 2/2: click the target object",
        "step_error": "Error",
        "status_wait_source": (
            "Waiting for a net-capable PCB item such as a track, via, pad, zone, or copper graphic."
        ),
        "status_wait_target": "Waiting for the target object's net.",
        "status_source_captured": "Source captured. Waiting for the target object's net.",
        "status_target_no_net": "The target item has no assigned net.",
        "status_target_unresolved": "Unable to resolve the target net.",
        "status_success_ready": (
            "Copied net {target_net} to the source item (was {source_net}). "
            "Net Painter is still active. Click the next source object to continue."
        ),
        "status_unsupported": (
            "The selected item does not carry a net. Choose a track, via, pad, zone, or copper graphic."
        ),
        "status_same_item": "The target must be a different object from the source.",
        "status_ambiguous": "Selection is ambiguous. Single-click one object.",
        "status_unexpected_error": "Unexpected error: {error}",
        "message_open_board": "Open a board in the PCB Editor before running Net Painter.",
        "no_net": "<no net>",
        "unnamed_net": "<unnamed net>",
        "na": "n/a",
    },
    "zh": {
        "plugin_name": "网络吸管",
        "plugin_category": "PCB 修改",
        "plugin_description": "通过两次点击，把一个 PCB 对象的网络复制到另一个对象。",
        "window_title": "网络吸管",
        "headline": "两次点击复制网络",
        "instructions": (
            "1. 点击要被修改网络的源对象。\n"
            "2. 点击要吸取网络的目标对象。"
        ),
        "source_waiting": "源对象：等待选择",
        "target_waiting": "目标对象：等待选择",
        "source_value": "源对象：{description}",
        "target_value": "目标对象：{description}",
        "button_reset": "重置",
        "button_close": "关闭",
        "step_source": "第 1/2 步：点击源对象",
        "step_target": "第 2/2 步：点击目标对象",
        "step_error": "错误",
        "status_wait_source": "等待选择一个带网络的 PCB 对象，例如走线、过孔、焊盘、区域或铜图形。",
        "status_wait_target": "等待目标对象的网络。",
        "status_source_captured": "已记录源对象，等待目标对象的网络。",
        "status_target_no_net": "目标对象没有分配网络。",
        "status_target_unresolved": "无法解析目标对象的网络。",
        "status_success_ready": (
            "已将源对象的网络从 {source_net} 改为 {target_net}。"
            "网络吸管仍然处于激活状态，请继续点击下一个源对象。"
        ),
        "status_unsupported": "当前选择的对象不携带网络，请选择走线、过孔、焊盘、区域或铜图形。",
        "status_same_item": "目标对象必须与源对象不同。",
        "status_ambiguous": "当前选择不唯一，请单击一个对象。",
        "status_unexpected_error": "发生未预期错误：{error}",
        "message_open_board": "请先在 PCB 编辑器中打开一个板文件，再运行网络吸管。",
        "no_net": "<无网络>",
        "unnamed_net": "<未命名网络>",
        "na": "无",
    },
}


def current_language():
    override = (config.LANGUAGE_OVERRIDE or "").strip().lower()
    if override in TRANSLATIONS:
        return override

    language = ""

    if hasattr(pcbnew, "GetLanguage"):
        try:
            language = str(pcbnew.GetLanguage() or "")
        except Exception:
            language = ""

    if not language:
        try:
            language = locale.getdefaultlocale()[0] or ""
        except Exception:
            language = ""

    normalized = language.replace("-", "_").lower().strip()

    if (
        normalized.startswith("zh")
        or "chinese" in normalized
        or "simplified" in normalized
        or "hans" in normalized
        or "中文" in normalized
        or "简体" in normalized
    ):
        return "zh"

    if normalized.startswith("en") or "english" in normalized:
        return "en"

    return "en"


def tr(key, **kwargs):
    language = current_language()
    text = TRANSLATIONS.get(language, TRANSLATIONS["en"]).get(
        key,
        TRANSLATIONS["en"].get(key, key),
    )
    return text.format(**kwargs)
