# -*- coding: utf-8 -*-
"""
Code Generator Base Module
Contains common constants, types, and base functionality for code generation.
"""
from typing import List, Optional, Set, Dict, Tuple
from core.project import Project, WidgetInstance, Interface
from core.component_registry import ComponentRegistry
from ui.image_picker import get_resource_group


class CodeGeneratorBase:
    SKIP_PROPS = {
        "mNormalRect", "mOverRect", "mDownRect", "mDisabledRect",
        "mLabelJustify", "mRect", "mBounds",
        "mOverlay",
        "mUncheckedRect", "mCheckedRect",
    }

    WIDGET_PROPS = {
        "mVisible", "mDisabled", "mHasTransparencies", "mClip",
        "mHasAlpha", "mDoFinger", "mWantsFocus", "mMouseVisible",
    }

    COLOR_PROPS = {
        "mOverColor", "mColor", "mOutlineColor", "mBkgColor", "mCheckColor",
    }

    JUSTIFY_MAP = {
        "LEFT": "ListWidget::JUSTIFY_LEFT",
        "CENTER": "ListWidget::JUSTIFY_CENTER",
        "RIGHT": "ListWidget::JUSTIFY_RIGHT",
    }

    BUTTON_MODE_MAP = {
        "BUTTONS_NONE": "Dialog::BUTTONS_NONE",
        "BUTTONS_YES_NO": "Dialog::BUTTONS_YES_NO",
        "BUTTONS_OK_CANCEL": "Dialog::BUTTONS_OK_CANCEL",
        "BUTTONS_FOOTER": "Dialog::BUTTONS_FOOTER",
    }

    BUTTON_WIDGETS = {"ButtonWidget", "DialogButton", "NewLawnButton", "LawnStoneButton"}
    EDIT_WIDGETS = {"EditWidget", "LawnEditWidget"}
    CHECKBOX_WIDGETS = {"Checkbox"}
    SLIDER_WIDGETS = {"Slider"}
    DIALOG_WIDGETS = {"Dialog", "LawnDialog"}
    SCROLLBUTTON_WIDGETS = {"ScrollbuttonWidget"}
    LIST_WIDGETS = {"ListWidget"}
    NON_WIDGET_TYPES = {"GameButton", "Label", "ImageBox"}

    SEXY_WIDGETS = {"ButtonWidget", "EditWidget", "Checkbox", "Slider", "Dialog", "DialogButton", 
                    "ListWidget", "ScrollWidget", "HyperlinkWidget", "ScrollbuttonWidget", "TextWidget"}

    PVZ_WIDGETS = {"NewLawnButton", "LawnDialog", "LawnStoneButton", "LawnEditWidget", "GameButton"}
    CUSTOM_WIDGETS = {"Label", "ImageBox"}

    def __init__(self):
        self._registry = ComponentRegistry.instance()

    def _get_widget_namespace(self, class_name: str) -> str:
        return "Sexy::" if class_name in self.SEXY_WIDGETS else ""

    def _get_var_name(self, widget: WidgetInstance) -> str:
        name = widget.instance_name or widget.id
        if name:
            name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
        return f"m{name}"

    def _is_widget_type(self, class_name: str) -> bool:
        return class_name not in self.NON_WIDGET_TYPES

    def _parse_color(self, color_str: str) -> str:
        if not color_str:
            return "Color(255, 255, 255)"
        parts = color_str.split(",")
        if len(parts) >= 3:
            try:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                return f"Color({r}, {g}, {b})"
            except ValueError:
                pass
        return "Color(255, 255, 255)"

    def _listener_includes(self, listeners: List[str]) -> str:
        includes = []
        for l in listeners:
            inc_map = {
                "ButtonListener": "widget/ButtonListener.h",
                "DialogListener": "widget/DialogListener.h",
                "EditListener": "widget/EditListener.h",
                "ListListener": "widget/ListListener.h",
                "CheckboxListener": "widget/CheckboxListener.h",
                "SliderListener": "widget/SliderListener.h",
                "ScrollListener": "widget/ScrollListener.h",
            }
            if l in inc_map:
                includes.append(f'#include "{inc_map[l]}"')
        return "\n".join(includes)

    def _collect_required_resources(self, iface: Interface) -> Set[str]:
        resources = set()
        
        if iface.settings.background_image:
            group = get_resource_group(iface.settings.background_image)
            if group:
                resources.add(group)
        
        for widget in iface.widgets.values():
            for prop_name, prop_value in widget.properties.items():
                if prop_name in ("mButtonImage", "mOverImage", "mDownImage", "mDisabledImage",
                                 "mComponentImage", "mUncheckedImage", "mTrackImage", "mImage"):
                    if prop_value:
                        group = get_resource_group(prop_value)
                        if group:
                            resources.add(group)
        
        return resources

    def _get_required_listeners_for_interface(self, iface: Interface) -> Set[str]:
        required = set(iface.settings.listeners or [])
        for wid in iface.widgets.values():
            if wid.class_name in self.BUTTON_WIDGETS or wid.class_name in self.SCROLLBUTTON_WIDGETS:
                required.add("ButtonListener")
            if wid.class_name in self.EDIT_WIDGETS:
                required.add("EditListener")
            if wid.class_name in self.CHECKBOX_WIDGETS:
                required.add("CheckboxListener")
            if wid.class_name in self.SLIDER_WIDGETS:
                required.add("SliderListener")
            if wid.class_name in self.DIALOG_WIDGETS:
                required.add("DialogListener")
            if wid.class_name in self.LIST_WIDGETS:
                required.add("ListListener")
        return required

    def _has_non_widget_types(self, iface: Interface) -> bool:
        for wid in iface.widgets.values():
            if wid.class_name == "GameButton":
                return True
        return False
