# Net Painter for KiCad 9

Net Painter 是一个 KiCad 9 `ActionPlugin`，用于把对象 2 的网络快速复制到对象 1。插件启动后会打开一个常驻悬浮窗，并保持连续工作，适合在 PCB 布线整理时反复“吸网”。

## 功能特性

- 两次点击完成网络复制：先点对象 1 ，再点对象 2 。
- 悬浮窗常驻，单次成功后会自动回到下一轮等待状态。
- 支持工具栏按钮和插件菜单两种入口。
- 支持中英文界面，并可手动强制指定语言。
- 源对象为 Zone 时，会在改网后自动重建连通性并重新填充。

## 目录结构

- `__init__.py`：KiCad 插件注册入口。
- `plugin.py`：`ActionPlugin` 入口与会话生命周期管理。
- `session.py`：网络吸管状态机与选择轮询逻辑。
- `ui.py`：悬浮窗界面。
- `pcb_utils.py`：PCB 编辑器窗口识别与对象辅助函数。
- `i18n.py`：多语言文本与语言识别。
- `config.py`：插件配置项。
- `net_painter_action.py`：兼容旧导入路径的轻量包装层。

## 安装方式

1. 将整个 `net_painter` 文件夹放到 KiCad 9 的插件目录中。
2. 重启 KiCad，或重新加载插件。
3. 在 PCB Editor 中通过工具栏按钮或插件菜单启动 `Net Painter / 网络吸管`。

当前目录示例：

```text
Documents/KiCad/9.0/3rdparty/plugins/net_painter
```

## 使用方法

1. 启动插件。
2. 点击要被修改网络的源对象。
3. 点击要吸取网络的目标对象。
4. 插件会立刻把源对象改成目标对象的网络。
5. 悬浮窗会继续保持激活，可以直接开始下一次操作。

## 语言切换

在 `config.py` 中修改 `LANGUAGE_OVERRIDE`：

- `LANGUAGE_OVERRIDE = ""`：自动跟随 KiCad 语言。
- `LANGUAGE_OVERRIDE = "zh"`：强制中文。
- `LANGUAGE_OVERRIDE = "en"`：强制英文。

修改后建议重启 KiCad，确保工具栏提示、菜单文字和悬浮窗文本一起刷新。

## 支持对象

当前主要面向带网络的 PCB 对象，例如：

- Track
- Via
- Pad
- Zone
- 带网络的铜图形

目标对象本身必须已经带有有效网络。

## 说明与限制

- 插件当前基于 KiCad Python 插件能力和当前选区变化来识别点击对象，因此建议单击选择单个对象，不要框选多个对象。
- 如果当前选择不唯一，悬浮窗会给出错误提示，并继续等待下一次选择。
- 改网后插件会调用 `BuildConnectivity()`；源对象是 Zone 时还会执行重新填充。

## 开发备注

- 工具栏图标使用 `24x24` PNG。
- 如果需要调整轮询频率、窗口尺寸或语言策略，可直接编辑 `config.py`。
