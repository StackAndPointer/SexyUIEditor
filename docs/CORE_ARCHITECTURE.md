# SexyUI Editor - 核心架构文档

## 概述

SexyUI Editor 是一个基于 PyQt6 的可视化 UI 编辑器，用于 Plants vs. Zombies (PvZ) 中使用的 Sexy 框架。它支持为 C++ 和 C# (.NET) 版本生成代码。

## 项目结构

```
SexyUIEditor/
├── core/                    # 核心业务逻辑
│   ├── generators/          # 代码生成模块（按语言和框架拆分）
│   │   ├── __init__.py
│   │   ├── base.py          # 基类和公共常量
│   │   ├── csharp_legacy.py # C# 完整生成器
│   │   ├── cpp/             # C++ 模块化生成器
│   │   │   ├── __init__.py
│   │   │   ├── sexy.py      # C++ Sexy框架控件
│   │   │   ├── pvz.py       # C++ PvZ特定控件
│   │   │   └── extended.py  # C++ 扩展控件
│   │   └── csharp/          # C# 模块化生成器
│   │       ├── __init__.py
│   │       ├── sexy.py      # C# Sexy框架控件
│   │       ├── pvz.py       # C# PvZ特定控件
│   │       └── extended.py  # C# 扩展控件
│   ├── __init__.py
│   ├── code_generator.py    # 主代码生成器（整合所有生成器）
│   ├── code_parser.py       # 代码解析工具
│   ├── code_sync.py         # 代码同步
│   ├── component_registry.py # 控件组件定义
│   ├── i18n.py              # 国际化
│   ├── predefined_actions.py # 预定义动作处理器
│   ├── project.py           # 项目数据模型
│   ├── resource_manager.py  # 资源管理
│   ├── resource_groups.py   # 延迟加载资源组解析
│   ├── net_resources.py     # .NET 资源管理
│   └── undo_manager.py      # 撤销/重做功能
├── ui/                      # 用户界面组件
│   ├── canvas.py            # 可视化编辑画布
│   ├── property_panel.py    # 属性编辑面板
│   ├── event_config.py      # 事件配置对话框
│   ├── image_picker.py      # 图片/字体资源选择器
│   ├── code_view.py         # 代码预览窗口
│   ├── preview_window.py    # 界面预览窗口
│   └── ...
├── Content/                 # .NET 版本游戏资源文件
│   ├── images/              # 图片资源
│   ├── fonts/               # 字体资源
│   ├── resources.xml        # 资源定义
│   └── atlas_definitions.json # Atlas 图片切分定义
├── docs/                    # 文档
│   └── CORE_ARCHITECTURE.md # 本文件
├── main.py                  # 应用程序入口
└── test.sexyui              # 示例项目文件
```

## 双平台支持

编辑器支持两种输出目标：

### C++ 版本 (默认)
- 项目文件后缀：`.sexyui`
- 分辨率：800x600
- 图片引用：`Sexy::IMAGE_xxx`

#### C++ 项目结构

C++ 模式支持两种项目结构，主要区别在于头文件包含路径：

**QE 结构** (默认)：
```cpp
#include "../../SexyAppFramework/Widget.h"
#include "../../SexyAppFramework/ButtonListener.h"
#include "../../SexyAppFramework/ButtonWidget.h"
```

**Portable 结构**：
```cpp
#include "widget/Widget.h"
#include "widget/ButtonListener.h"
#include "widget/ButtonWidget.h"
```

项目结构通过 `core/header_includes.py` 中的 `HeaderIncludeManager` 类管理，支持：
- 自动根据项目结构生成正确的头文件包含路径
- 在工具栏中切换 QE/Portable 结构
- 默认使用 QE 结构

### C# (.NET) 版本
- 项目文件后缀：`.cssexyui`
- 分辨率：800x480
- 图片引用：`Resources.IMAGE_xxx` 或 `AtlasResources.IMAGE_xxx`

## Atlas 图片系统 (.NET 版本)

.NET 版本使用 Atlas（精灵图）系统，将多个小图片打包到一张大图中。

### Atlas 定义文件

`Content/atlas_definitions.json` 定义了如何从大图中切分小图：

```json
{
    "IMAGE_DIALOG": {
        "sub_images": {
            "IMAGE_DIALOG_TOPLEFT": {"x": 515, "y": 185, "width": 57, "height": 52},
            "IMAGE_BUTTON_MIDDLE": {"x": 624, "y": 185, "width": 25, "height": 30},
            ...
        }
    }
}
```

### Atlas 子图片命名规则

以下前缀的图片会被识别为 Atlas 子图片：
- `IMAGE_DIALOG_*` - 对话框组件
- `IMAGE_BUTTON_*` - 按钮组件
- `IMAGE_OPTIONS_*` - 选项控件
- `IMAGE_REANIM_*` - 动画资源
- 等等...

### 代码生成

Atlas 子图片在 C# 代码中使用 `AtlasResources` 前缀：
```csharp
// 普通图片
Resources.IMAGE_BACKGROUND1

// Atlas 子图片
AtlasResources.IMAGE_DIALOG_TOPLEFT
AtlasResources.IMAGE_BUTTON_MIDDLE
```

### 图片选择器

在 C# 模式下，图片选择器会：
1. 显示所有可用资源（包括 Atlas 子图片）
2. Atlas 子图片以青色高亮显示
3. 预览时正确显示切分后的图片

## 延迟加载资源

.NET 版本使用延迟加载机制，某些资源需要显式加载资源组才能使用。

### 资源组解析

`core/resource_groups.py` 解析 `Content/resources.xml` 文件，建立图片ID到资源组的映射：

```python
from core.resource_groups import get_delay_load_call

# 获取资源加载调用
call = get_delay_load_call("IMAGE_BACKGROUND_MUSHROOMGARDEN", resources_path)
# 返回: 'mApp.DelayLoadBackgroundResource("DelayLoad_MushroomGarden");'
```

### 代码生成

生成器会自动检测延迟加载资源，并在构造函数中添加加载调用：

```csharp
public MainWidget(LawnApp theApp)
{
    mApp = theApp;
    Resize(0, 0, 800, 480);
    mApp.DelayLoadBackgroundResource("DelayLoad_MushroomGarden");  // 自动添加
    // ...
}
```

## 代码生成器架构

代码生成器按语言和控件来源分层组织：

### 目录结构
```
core/generators/
├── __init__.py          # 模块导出
├── base.py              # 基础类和公共常量
├── csharp_legacy.py     # C# 完整生成器
├── cpp/                 # C++ 模块化生成器
│   ├── __init__.py
│   ├── sexy.py          # C++ Sexy框架控件
│   ├── pvz.py           # C++ PvZ特定控件
│   └── extended.py      # C++ 扩展控件
└── csharp/              # C# 模块化生成器
    ├── __init__.py
    ├── sexy.py          # C# Sexy框架控件
    ├── pvz.py           # C# PvZ特定控件
    └── extended.py      # C# 扩展控件
```

### 1. C++ 生成器模块

#### Sexy 框架控件 (`generators/cpp/sexy.py`)
处理标准 Sexy 框架控件：
- `ButtonWidget` - 基本按钮
- `EditWidget` - 文本输入框
- `Checkbox` - 复选框
- `Slider` - 滑块
- `Dialog` - 对话框
- `DialogButton` - 对话框按钮（支持通过 DrawImageBox 拉伸图片）
- `ListWidget` - 列表控件
- `ScrollWidget` - 滚动容器
- `HyperlinkWidget` - 超链接
- `ScrollbuttonWidget` - 滚动按钮
- `TextWidget` - 文本显示控件

#### PVZ 控件 (`generators/cpp/pvz.py`)
处理 Plants vs. Zombies 特定控件：
- `GameButton` - PVZ 游戏按钮（非 Widget 类型）
- `NewLawnButton` - PVZ 新风格按钮
- `LawnDialog` - PVZ 对话框
- `LawnStoneButton` - PVZ 石头按钮
- `LawnEditWidget` - PVZ 编辑控件

#### 扩展控件 (`generators/cpp/extended.py`)
处理自定义扩展控件：
- `Label` - 自定义文本标签（使用 `TodDrawStringWrapped` 实现自动换行）
- `ImageBox` - 自定义图片框（使用 `TodDrawImageScaledF` 实现缩放）

### 2. C# 生成器模块

#### Sexy 框架控件 (`generators/csharp/sexy.py`)
处理 .NET 版本的 Sexy 框架控件，生成 C# 语法代码。

#### PVZ 控件 (`generators/csharp/pvz.py`)
处理 .NET 版本的 PvZ 特定控件，支持 Atlas 子图片引用。

#### 扩展控件 (`generators/csharp/extended.py`)
处理 .NET 版本的自定义扩展控件。

### 基础模块 (`generators/base.py`)
包含：
- 公共常量（SKIP_PROPS, WIDGET_PROPS, COLOR_PROPS 等）
- 控件类型分类（SEXY_WIDGETS, PVZ_WIDGETS, CUSTOM_WIDGETS 等）
- 工具方法（颜色解析、变量命名、监听器检测等）

## 控件类型分类

```python
SEXY_WIDGETS = {
    "ButtonWidget", "EditWidget", "Checkbox", "Slider", "Dialog", 
    "DialogButton", "ListWidget", "ScrollWidget", "HyperlinkWidget", 
    "ScrollbuttonWidget", "TextWidget"
}

PVZ_WIDGETS = {
    "NewLawnButton", "LawnDialog", "LawnStoneButton", 
    "LawnEditWidget", "GameButton"
}

CUSTOM_WIDGETS = {
    "Label", "ImageBox"
}

NON_WIDGET_TYPES = {
    "GameButton", "Label", "ImageBox"  # 不由 WidgetManager 管理
}
```

## 关键功能

### 图片拉伸支持
- `DialogButton`、`Dialog`、`LawnDialog` 支持通过 `DrawImageBox` 进行图片拉伸
- `NewLawnButton` 不支持图片拉伸（使用 `DrawButtonImage`）
- `ImageBox` 支持通过 `TodDrawImageScaledF` 进行自定义缩放

### 字体处理
- `NewLawnButton` 使用 `SetFont()` 方法设置正常字体
- `mHiliteFont` 直接作为属性设置
- `Label` 使用 `TodDrawStringWrapped` 实现自动换行

### 统一图片属性
- `NewLawnButton` 有 `mUniformImage` 属性
- 设置后自动应用到 `mButtonImage`、`mOverImage`、`mDownImage`
- 单独的图片属性可以覆盖统一图片

### 资源管理
- .NET 版本：资源从 `Content/resources.xml` 加载
- Atlas 子图片从 `Content/atlas_definitions.json` 加载
- 自动检测延迟加载资源的资源组

## 导入导出功能

### 导出界面
- 默认导出到配置文件所在目录
- 支持"导出所有界面"功能
- 导出前自动同步同目录下的代码文件中的用户代码

### 导入界面
- 从其他项目文件导入界面
- 文件过滤器根据当前项目类型自动调整：
  - C++ 项目：只显示 `.sexyui` 文件
  - C# 项目：只显示 `.cssexyui` 文件
- 自动跳过重复类名的界面

### 自动同步
导出前会自动：
1. 检测同目录下已存在的代码文件
2. 从代码文件中提取用户代码（`// [[[USER_xxx]]]` 区域）
3. 将用户代码合并到项目数据中
4. 生成新代码时保留用户修改

### 自动关联
保存项目时自动：
1. 检测同目录下的代码文件
2. 将代码文件路径关联到界面设置中

### 手动关联文件
如果自动关联未生效，可以通过菜单手动关联：
- **菜单路径**：Sync → Associate Source File...
- **C++ 模式**：选择 .h 和 .cpp 文件
- **C# 模式**：选择 .cs 文件
- 关联后会在界面设置中保存文件路径

## 扩展组件系统

### 扩展组件目录结构
```
SexyUIExtensions/
├── cpp/                    # C++ 扩展组件
│   ├── Label.json          # Label 组件定义
│   ├── Label.h             # Label 头文件
│   ├── Label.cpp           # Label 源文件
│   ├── ImageBox.json       # ImageBox 组件定义
│   ├── ImageBox.h          # ImageBox 头文件
│   └── ImageBox.cpp        # ImageBox 源文件
└── csharp/                 # C# 扩展组件
    ├── Label.json          # Label 组件定义
    ├── Label.cs            # Label 源文件
    ├── ImageBox.json       # ImageBox 组件定义
    └── ImageBox.cs         # ImageBox 源文件
```

### 扩展组件 JSON 定义
```json
{
    "class_name": "Label",
    "display_name": "文本标签",
    "description": "使用TodDrawStringWrapped绘制的文本标签",
    "parent_class": "Widget",
    "category": "extension",
    "is_container": false,
    "properties": [
        {
            "name": "mX",
            "display_name": "X坐标",
            "type": "INT",
            "default": 0,
            "category": "geometry"
        },
        ...
    ]
}
```

### 扩展组件管理
- `ExtensionManager` 类负责加载和管理扩展组件
- 支持按平台（C++/C#）加载不同的扩展组件
- 扩展组件会在组件面板的"扩展"分类中显示
- 导出代码时自动包含扩展组件的源文件

## 事件系统

事件通过控件的 `event_actions` 属性配置：
```json
"event_actions": {
    "ButtonDepress": [
        {
            "action_type": "predefined",
            "predefined_id": "switch_to_project_interface",
            "params": {
                "interface_class": "testWidget",
                "interface_id": "testWidget::INTERFACE_ID"
            }
        }
    ]
}
```

## 事件管理机制注意事项

### Widget 与 Dialog 的区别

- **Widget 类型界面**：使用 `mWidgetManager->AddWidget()` 添加，`mWidgetManager->RemoveWidget()` 移除
- **Dialog 类型界面**：使用 `mApp->AddDialog()` 添加，`mApp->KillDialog()` 移除

### 显示内置界面（商店、图鉴等）

内置界面（如商店、图鉴）都是 **Dialog** 类型，会叠加在当前界面上显示。

**重要**：显示内置界面时，**不需要**先关闭当前 Widget 界面！

```json
// 错误配置 - 会导致商店关闭后无法返回
"event_actions": {
    "ButtonDepress": [
        { "predefined_id": "close_current_widget" },  // 错误！
        { "predefined_id": "show_store" }
    ]
}

// 正确配置 - 商店是 Dialog，会叠加在 Widget 上
"event_actions": {
    "ButtonDepress": [
        { "predefined_id": "show_store" }
    ]
}
```

### 界面切换动作

| 动作 | 说明 | 适用场景 |
|------|------|----------|
| `open_project_interface` | 打开项目界面（叠加） | 不关闭当前界面 |
| `switch_to_project_interface` | 切换到项目界面 | 先关闭当前界面再打开新界面 |
| `close_current_dialog` | 关闭当前 Dialog | 仅 Dialog 类型 |
| `close_current_widget` | 关闭当前 Widget | 仅 Widget 类型 |

### 用户代码优先级

事件处理器中的用户代码优先级：
1. **用户自定义代码** - 最高优先级，保留在 `// [[[HANDLER_xxx]]]` 区域内
2. **编辑器配置的事件代码** - 当没有用户代码时生成
3. **空占位符** - 当两者都没有时生成

## 项目文件格式

### C++ 版本 (.sexyui)

```json
{
    "settings": {
        "namespace": "",
        "header_include": "",
        "target_platform": "cpp"
    },
    "interfaces": {
        "interface_id": {
            "settings": {
                "id": "interface_id",
                "name": "显示名称",
                "class_name": "类名",
                "parent_class": "Widget",
                "interface_type": "main|dialog|widget",
                "width": 800,
                "height": 600,
                "background_image": "IMAGE_NAME",
                "background_stretch": false,
                "background_color": "0,0,0",
                "listeners": ["ButtonListener"]
            },
            "widgets": { ... },
            "root_widget_ids": [...],
            "user_code": { ... }
        }
    },
    "main_interface_id": "interface_id",
    "current_interface_id": "interface_id"
}
```

### C# 版本 (.cssexyui)

```json
{
    "settings": {
        "namespace": "",
        "header_include": "",
        "target_platform": "csharp"
    },
    "interfaces": {
        "interface_id": {
            "settings": {
                "id": "interface_id",
                "name": "显示名称",
                "class_name": "类名",
                "parent_class": "Widget",
                "interface_type": "main|dialog|widget",
                "width": 800,
                "height": 480,
                "background_image": "IMAGE_NAME",
                "background_stretch": false,
                "background_color": "0,0,0",
                "listeners": ["ButtonListener"]
            },
            "widgets": { ... },
            "root_widget_ids": [...],
            "user_code": { ... }
        }
    },
    "main_interface_id": "interface_id",
    "current_interface_id": "interface_id"
}
```

## 代码生成流程

### C++ 版本

1. **头文件生成** (`generate_header_for_interface`)
   - 确定所需的监听器
   - 生成带有基类的类声明
   - 添加虚方法声明
   - 添加成员变量

2. **CPP 文件生成** (`generate_cpp_for_interface`)
   - 生成包含语句
   - 生成构造函数和控件初始化
   - 生成 Draw 方法（先绘制自定义控件，然后调用 Widget::Draw）
   - 生成 Update 方法
   - 生成鼠标处理器（针对非 Widget 类型）
   - 生成事件处理器
   - 添加用户代码区域

### C# 版本

1. **单一文件生成** (`generate_csharp`)
   - 生成 using 语句
   - 生成命名空间和类声明
   - 生成构造函数和控件初始化
   - 生成 Draw 方法
   - 生成 Update 方法
   - 生成事件处理器
   - 添加用户代码区域

## 用户代码区域

### C++ 版本
- `// [[[USER_DECLARATIONS]]]` - 成员声明
- `// [[[USER_INIT]]]` - 初始化代码
- `// [[[USER_DESTROY]]]` - 清理代码
- `// [[[USER_DRAW]]]` - 自定义绘制代码
- `// [[[USER_UPDATE]]]` - 更新逻辑
- `// [[[USER_FUNCTIONS]]]` - 自定义函数
- `// [[[HANDLER_widget_id]]]` - 事件处理器代码

### C# 版本
- `// [[[USER_DECLARATIONS]]]` - 成员声明
- `// [[[USER_INIT]]]` - 初始化代码
- `// [[[USER_DESTROY]]]` - 清理代码
- `// [[[USER_DRAW]]]` - 自定义绘制代码
- `// [[[USER_UPDATE]]]` - 更新逻辑
- `// [[[USER_FUNCTIONS]]]` - 自定义函数
- `// [[[HANDLER_widget_id]]]` - 事件处理器代码

