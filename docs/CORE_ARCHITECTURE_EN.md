# SexyUI Editor - Core Architecture Document

## Overview

SexyUI Editor is a PyQt6-based visual UI editor for the Sexy framework used in Plants vs. Zombies (PvZ). It supports code generation for both C++ and C# (.NET) versions.

## Project Structure

```
SexyUIEditor/
├── core/                    # Core business logic
│   ├── generators/          # Code generation modules (organized by language and framework)
│   │   ├── __init__.py
│   │   ├── base.py          # Base class and common constants
│   │   ├── csharp_legacy.py # C# complete generator
│   │   ├── cpp/             # C++ modular generators
│   │   │   ├── __init__.py
│   │   │   ├── sexy.py      # C++ Sexy framework widgets
│   │   │   ├── pvz.py       # C++ PvZ-specific widgets
│   │   │   └── extended.py  # C++ extended widgets
│   │   └── csharp/          # C# modular generators
│   │       ├── __init__.py
│   │       ├── sexy.py      # C# Sexy framework widgets
│   │       ├── pvz.py       # C# PvZ-specific widgets
│   │       └── extended.py  # C# extended widgets
│   ├── __init__.py
│   ├── code_generator.py    # Main code generator (integrates all generators)
│   ├── code_parser.py       # Code parsing utilities
│   ├── code_sync.py         # Code synchronization
│   ├── component_registry.py # Widget component definitions
│   ├── extension_manager.py # Extension component management
│   ├── i18n.py              # Internationalization
│   ├── predefined_actions.py # Predefined action handlers
│   ├── project.py           # Project data model
│   ├── resource_manager.py  # Resource management
│   ├── resource_groups.py   # Lazy-loaded resource group parsing
│   ├── net_resources.py     # .NET resource management
│   └── undo_manager.py      # Undo/Redo functionality
├── ui/                      # User interface components
│   ├── canvas.py            # Visual editing canvas
│   ├── property_panel.py    # Property editing panel
│   ├── event_config.py      # Event configuration dialog
│   ├── image_picker.py      # Image/font resource picker
│   ├── code_view.py         # Code preview window
│   ├── preview_window.py    # Interface preview window
│   └── ...
├── Content/                 # .NET version game resources
│   ├── images/              # Image resources
│   ├── fonts/               # Font resources
│   ├── resources.xml        # Resource definitions
│   └── atlas_definitions.json # Atlas image slicing definitions
├── SexyUIExtensions/        # Extension components directory
│   ├── cpp/                 # C++ extensions
│   └── csharp/              # C# extensions
├── docs/                    # Documentation
│   ├── CORE_ARCHITECTURE.md # This file (Chinese)
│   └── CORE_ARCHITECTURE_EN.md # English version
├── main.py                  # Application entry point
└── test.sexyui              # Example project file
```

## Dual Platform Support

The editor supports two output targets:

### C++ Version (Default)
- Project file extension: `.sexyui`
- Resolution: 800x600
- Image references: `Sexy::IMAGE_xxx`

#### C++ Project Structures

C++ mode supports two project structures, differing mainly in header include paths:

**QE Structure** (Default):
```cpp
#include "../../SexyAppFramework/Widget.h"
#include "../../SexyAppFramework/ButtonListener.h"
#include "../../SexyAppFramework/ButtonWidget.h"
```

**Portable Structure**:
```cpp
#include "widget/Widget.h"
#include "widget/ButtonListener.h"
#include "widget/ButtonWidget.h"
```

Project structures are managed by the `HeaderIncludeManager` class in `core/header_includes.py`, supporting:
- Automatic generation of correct header include paths based on project structure
- Switching between QE/Portable structures in the toolbar
- Default to QE structure

### C# (.NET) Version
- Project file extension: `.cssexyui`
- Resolution: 800x480
- Image references: `Resources.IMAGE_xxx` or `AtlasResources.IMAGE_xxx`

## Atlas Image System (.NET Version)

The .NET version uses an Atlas (sprite sheet) system that packs multiple small images into one large image.

### Atlas Definition File

`Content/atlas_definitions.json` defines how to slice small images from large images:

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

### Atlas Sub-image Naming Rules

Images with the following prefixes are recognized as Atlas sub-images:
- `IMAGE_DIALOG_*` - Dialog components
- `IMAGE_BUTTON_*` - Button components
- `IMAGE_OPTIONS_*` - Option controls
- `IMAGE_REANIM_*` - Animation resources
- And more...

### Code Generation

Atlas sub-images use the `AtlasResources` prefix in C# code:
```csharp
// Normal images
Resources.IMAGE_BACKGROUND1

// Atlas sub-images
AtlasResources.IMAGE_DIALOG_TOPLEFT
AtlasResources.IMAGE_BUTTON_MIDDLE
```

### Image Picker

In C# mode, the image picker will:
1. Display all available resources (including Atlas sub-images)
2. Highlight Atlas sub-images in cyan
3. Correctly display sliced images in preview

## Lazy-Loaded Resources

The .NET version uses a lazy-loading mechanism where certain resources require explicit resource group loading.

### Resource Group Parsing

`core/resource_groups.py` parses the `Content/resources.xml` file to build a mapping from image IDs to resource groups:

```python
from core.resource_groups import get_delay_load_call

# Get resource loading call
call = get_delay_load_call("IMAGE_BACKGROUND_MUSHROOMGARDEN", resources_path)
# Returns: 'mApp.DelayLoadBackgroundResource("DelayLoad_MushroomGarden");'
```

### Code Generation

The generator automatically detects lazy-loaded resources and adds loading calls in the constructor:

```csharp
public MainWidget(LawnApp theApp)
{
    mApp = theApp;
    Resize(0, 0, 800, 480);
    mApp.DelayLoadBackgroundResource("DelayLoad_MushroomGarden");  // Auto-added
    // ...
}
```

## Code Generator Architecture

The code generators are organized hierarchically by language and widget source:

### Directory Structure
```
core/generators/
├── __init__.py          # Module exports
├── base.py              # Base class and common constants
├── csharp_legacy.py     # C# complete generator
├── cpp/                 # C++ modular generators
│   ├── __init__.py
│   ├── sexy.py          # C++ Sexy framework widgets
│   ├── pvz.py           # C++ PvZ-specific widgets
│   └── extended.py      # C++ extended widgets
└── csharp/              # C# modular generators
    ├── __init__.py
    ├── sexy.py          # C# Sexy framework widgets
    ├── pvz.py           # C# PvZ-specific widgets
    └── extended.py      # C# extended widgets
```

### 1. C++ Generator Modules

#### Sexy Framework Widgets (`generators/cpp/sexy.py`)
Handles standard Sexy framework widgets:
- `ButtonWidget` - Basic button
- `EditWidget` - Text input box
- `Checkbox` - Checkbox
- `Slider` - Slider
- `Dialog` - Dialog
- `DialogButton` - Dialog button (supports image stretching via DrawImageBox)
- `ListWidget` - List control
- `ScrollWidget` - Scroll container
- `HyperlinkWidget` - Hyperlink
- `ScrollbuttonWidget` - Scroll button
- `TextWidget` - Text display control

#### PVZ Widgets (`generators/cpp/pvz.py`)
Handles Plants vs. Zombies specific widgets:
- `GameButton` - PVZ game button (non-Widget type)
- `NewLawnButton` - PVZ new style button
- `LawnDialog` - PVZ dialog
- `LawnStoneButton` - PVZ stone button
- `LawnEditWidget` - PVZ edit control

#### Extended Widgets (`generators/cpp/extended.py`)
Handles custom extended widgets:
- `Label` - Custom text label (uses `TodDrawStringWrapped` for auto-wrapping)
- `ImageBox` - Custom image box (uses `TodDrawImageScaledF` for scaling)

### 2. C# Generator Modules

#### Sexy Framework Widgets (`generators/csharp/sexy.py`)
Handles .NET version Sexy framework widgets, generates C# syntax code.

#### PVZ Widgets (`generators/csharp/pvz.py`)
Handles .NET version PvZ-specific widgets, supports Atlas sub-image references.

#### Extended Widgets (`generators/csharp/extended.py`)
Handles .NET version custom extended widgets.

### Base Module (`generators/base.py`)
Contains:
- Common constants (SKIP_PROPS, WIDGET_PROPS, COLOR_PROPS, etc.)
- Widget type classifications (SEXY_WIDGETS, PVZ_WIDGETS, CUSTOM_WIDGETS, etc.)
- Utility methods (color parsing, variable naming, listener detection, etc.)

## Widget Type Classifications

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
    "GameButton", "Label", "ImageBox"  # Not managed by WidgetManager
}
```

## Key Features

### Image Stretching Support
- `DialogButton`, `Dialog`, `LawnDialog` support image stretching via `DrawImageBox`
- `NewLawnButton` does not support image stretching (uses `DrawButtonImage`)
- `ImageBox` supports custom scaling via `TodDrawImageScaledF`

### Font Handling
- `NewLawnButton` uses `SetFont()` method to set normal font
- `mHiliteFont` is set directly as a property
- `Label` uses `TodDrawStringWrapped` for auto-wrapping

### Uniform Image Property
- `NewLawnButton` has `mUniformImage` property
- When set, automatically applies to `mButtonImage`, `mOverImage`, `mDownImage`
- Individual image properties can override the uniform image

### Resource Management
- .NET version: Resources loaded from `Content/resources.xml`
- Atlas sub-images loaded from `Content/atlas_definitions.json`
- Automatic detection of resource groups for lazy-loaded resources

## Import/Export Functionality

### Export Interfaces
- Default export to the same directory as the config file
- Supports "Export All Interfaces" functionality
- Auto-syncs user code from code files in the same directory before export

### Import Interfaces
- Import interfaces from other project files
- File filter automatically adjusts based on current project type:
  - C++ projects: Only shows `.sexyui` files
  - C# projects: Only shows `.cssexyui` files
- Automatically skips interfaces with duplicate class names

### Auto Sync
Before export, automatically:
1. Detects existing code files in the same directory
2. Extracts user code from code files (`// [[[USER_xxx]]]` regions)
3. Merges user code into project data
4. Preserves user modifications when generating new code

### Auto Associate
When saving a project, automatically:
1. Detects code files in the same directory
2. Associates code file paths with interface settings

### Manual File Association
If auto-association doesn't work, you can manually associate via menu:
- **Menu Path**: Sync → Associate Source File...
- **C++ Mode**: Select .h and .cpp files
- **C# Mode**: Select .cs file
- File paths are saved in interface settings after association

## Extension Component System

### Extension Component Directory Structure
```
SexyUIExtensions/
├── cpp/                    # C++ extension components
│   ├── Label.json          # Label component definition
│   ├── Label.h             # Label header file
│   ├── Label.cpp           # Label source file
│   ├── ImageBox.json       # ImageBox component definition
│   ├── ImageBox.h          # ImageBox header file
│   └── ImageBox.cpp        # ImageBox source file
└── csharp/                 # C# extension components
    ├── Label.json          # Label component definition
    ├── Label.cs            # Label source file
    ├── ImageBox.json       # ImageBox component definition
    └── ImageBox.cs         # ImageBox source file
```

### Extension Component JSON Definition
```json
{
    "class_name": "Label",
    "display_name": "Text Label",
    "description": "Text label drawn using TodDrawStringWrapped",
    "parent_class": "Widget",
    "category": "extension",
    "is_container": false,
    "properties": [
        {
            "name": "mX",
            "display_name": "X Position",
            "type": "INT",
            "default": 0,
            "category": "geometry"
        },
        ...
    ]
}
```

### Extension Component Management
- `ExtensionManager` class handles loading and managing extension components
- Supports loading different extension components by platform (C++/C#)
- Extension components appear in the "Extension" category of the component panel
- Source files for extension components are automatically included when exporting code

## Event System

Events are configured through the widget's `event_actions` property:
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

## Event Management Considerations

### Widget vs Dialog Differences

- **Widget type interfaces**: Added via `mWidgetManager->AddWidget()`, removed via `mWidgetManager->RemoveWidget()`
- **Dialog type interfaces**: Added via `mApp->AddDialog()`, removed via `mApp->KillDialog()`

### Showing Built-in Interfaces (Store, Almanac, etc.)

Built-in interfaces (like store, almanac) are all **Dialog** types that display as overlays on the current interface.

**Important**: When showing built-in interfaces, you do **NOT** need to close the current Widget interface first!

```json
// Wrong configuration - will cause inability to return after store closes
"event_actions": {
    "ButtonDepress": [
        { "predefined_id": "close_current_widget" },  // Wrong!
        { "predefined_id": "show_store" }
    ]
}

// Correct configuration - store is a Dialog, overlays on Widget
"event_actions": {
    "ButtonDepress": [
        { "predefined_id": "show_store" }
    ]
}
```

### Interface Switching Actions

| Action | Description | Use Case |
|--------|-------------|----------|
| `open_project_interface` | Open project interface (overlay) | Doesn't close current interface |
| `switch_to_project_interface` | Switch to project interface | Closes current interface before opening new one |
| `close_current_dialog` | Close current Dialog | Dialog types only |
| `close_current_widget` | Close current Widget | Widget types only |

### User Code Priority

Priority of user code in event handlers:
1. **User-defined code** - Highest priority, preserved in `// [[[HANDLER_xxx]]]` regions
2. **Editor-configured event code** - Generated when no user code exists
3. **Empty placeholder** - Generated when neither exists

## Project File Format

### C++ Version (.sexyui)

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
                "name": "Display Name",
                "class_name": "ClassName",
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

### C# Version (.cssexyui)

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
                "name": "Display Name",
                "class_name": "ClassName",
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

## Code Generation Flow

### C++ Version

1. **Header File Generation** (`generate_header_for_interface`)
   - Determine required listeners
   - Generate class declaration with base class
   - Add virtual method declarations
   - Add member variables

2. **CPP File Generation** (`generate_cpp_for_interface`)
   - Generate include statements
   - Generate constructor and widget initialization
   - Generate Draw method (draw custom widgets first, then call Widget::Draw)
   - Generate Update method
   - Generate mouse handlers (for non-Widget types)
   - Generate event handlers
   - Add user code regions

### C# Version

1. **Single File Generation** (`generate_csharp`)
   - Generate using statements
   - Generate namespace and class declaration
   - Generate constructor and widget initialization
   - Generate Draw method
   - Generate Update method
   - Generate event handlers
   - Add user code regions

## User Code Regions

### C++ Version
- `// [[[USER_INCLUDES]]]` - Custom header includes
- `// [[[USER_FORWARD_DECLARATIONS]]]` - Forward declarations and enum definitions (before class definition)
- `// [[[USER_DECLARATIONS]]]` - Member declarations
- `// [[[USER_INIT]]]` - Initialization code
- `// [[[USER_DESTROY]]]` - Cleanup code
- `// [[[USER_DRAW]]]` - Custom drawing code
- `// [[[USER_UPDATE]]]` - Update logic
- `// [[[USER_FUNCTIONS]]]` - Custom functions
- `// [[[USER_POST_CLASS]]]` - Post-class definitions (helper classes, etc., after class definition)
- `// [[[HANDLER_widget_id]]]` - Event handler code

### C# Version
- `// [[[USER_INCLUDES]]]` - Custom using statements
- `// [[[USER_DECLARATIONS]]]` - Member declarations
- `// [[[USER_INIT]]]` - Initialization code
- `// [[[USER_DESTROY]]]` - Cleanup code
- `// [[[USER_DRAW]]]` - Custom drawing code
- `// [[[USER_UPDATE]]]` - Update logic
- `// [[[USER_FUNCTIONS]]]` - Custom functions
- `// [[[HANDLER_widget_id]]]` - Event handler code
- `// [[[EDIT_widget_id]]]` - Edit widget text changed handler
- `// [[[CHECKBOX_widget_id]]]` - Checkbox state changed handler
- `// [[[SLIDER_widget_id]]]` - Slider value changed handler

## Internationalization

The editor supports multiple languages through the i18n system:

### Translation Files
- `i18n/zh_CN.json` - Chinese (Simplified)
- `i18n/en.json` - English

### Usage in Code
```python
from core.i18n import tr

# Get translated text with fallback
text = tr("menu.file", "&File")
```

### Adding New Translations
1. Add translation key-value pairs to `i18n/zh_CN.json` and `i18n/en.json`
2. Use the `tr()` function in code to retrieve translations
3. The system automatically loads the appropriate language based on user settings

## Building and Distribution

### Build Script
The `build.bat` script uses Nuitka to create a standalone executable:

```batch
python -m nuitka ^
    --standalone ^
    --output-filename=SexyUIEditor.exe ^
    --include-data-dir=i18n=i18n ^
    --include-data-dir=resources=resources ^
    --include-data-dir=SexyUIExtensions=SexyUIExtensions ^
    ...
```

### Included Directories
- `i18n/` - Translation files
- `resources/` - Icons and UI resources
- `SexyUIExtensions/` - Extension components

### Manual Steps
After building, manually copy:
- `pak/` - Game resource files
- `Content/` - .NET game resources

## License

Copyright (C) 2026 StackAndPointer

This project is open-source software. Contributions are welcome!

## Acknowledgments

Special thanks to PopCap Games for open-sourcing the Sexy framework, which made this editor possible.
