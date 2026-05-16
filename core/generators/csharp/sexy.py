# -*- coding: utf-8 -*-
from typing import List
from core.project import WidgetInstance, Interface
from ..base import CodeGeneratorBase
from ui.image_picker import is_atlas_sub_image


ATLAS_IMAGE_PREFIXES = (
    "IMAGE_REANIM_", "IMAGE_SELECTORSCREEN_", "IMAGE_SEEDCHOOSER_", 
    "IMAGE_ALMANAC_", "IMAGE_BLASTMARK", "IMAGE_ROCKSMALL", "IMAGE_DIRTBIG",
    "IMAGE_DIRTSMALL", "IMAGE_RAIN", "IMAGE_LANTERNSHINE", "IMAGE_AWARD",
    "IMAGE_VASE_", "IMAGE_IMITATERCLOUDS", "IMAGE_ZOMBOSS_", "IMAGE_BEGHOULED_",
    "IMAGE_DIALOG_", "IMAGE_BUTTON_", "IMAGE_EDITBOX", "IMAGE_OPTIONS_",
    "IMAGE_BLANK", "IMAGE_SCROLL_INDICATOR", "IMAGE_SELECTED_PACKET",
    "IMAGE_MINI_GAME_FRAME", "IMAGE_MINI_GAME_HIGHLIGHT_FRAME"
)


class CSharpSexyGenerator(CodeGeneratorBase):
    JUSTIFY_MAP_CS = {
        "LEFT": "DrawStringJustification.Left",
        "CENTER": "DrawStringJustification.Center",
        "RIGHT": "DrawStringJustification.Right",
    }

    def _get_image_ref(self, image_name: str) -> str:
        if not image_name:
            return "null"
        if image_name.startswith("IMAGE_"):
            if is_atlas_sub_image(image_name):
                return f"AtlasResources.{image_name}"
            if any(image_name.startswith(prefix) or image_name == prefix for prefix in ATLAS_IMAGE_PREFIXES):
                return f"AtlasResources.{image_name}"
            return f"Resources.{image_name}"
        elif image_name.startswith("IMAGE_REANIM_") or image_name.startswith("IMAGE_SELECTORSCREEN_"):
            return f"AtlasResources.{image_name}"
        return f"Resources.{image_name}"

    def _get_font_ref(self, font_name: str) -> str:
        if not font_name:
            return "Resources.FONT_DWARVENTODCRAFT12"
        if font_name.startswith("FONT_"):
            return f"Resources.{font_name}"
        return f"Resources.{font_name}"

    def _parse_color_cs(self, color_str: str) -> str:
        if not color_str:
            return "SexyColor.White"
        parts = color_str.split(",")
        if len(parts) >= 3:
            try:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                if len(parts) >= 4:
                    a = int(parts[3].strip())
                    return f"new SexyColor({r}, {g}, {b}, {a})"
                return f"new SexyColor({r}, {g}, {b})"
            except ValueError:
                pass
        return "SexyColor.White"

    def generate_widget_init(self, widget: WidgetInstance, class_listeners: List[str]) -> str:
        if widget.class_name not in self.SEXY_WIDGETS:
            return ""
        
        var_name = self._get_var_name(widget)
        props = widget.properties
        lines = []
        widget_id = props.get('mId', 0)
        skip_resize = False
        
        has_btn_listener = "ButtonListener" in class_listeners
        has_edit_listener = "EditListener" in class_listeners
        has_checkbox_listener = "CheckboxListener" in class_listeners
        has_slider_listener = "SliderListener" in class_listeners

        if widget.class_name == "ButtonWidget":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new ButtonWidget({widget_id}, {listener});\n")
        elif widget.class_name == "EditWidget":
            listener = "this" if has_edit_listener else "null"
            lines.append(f"        {var_name} = new EditWidget({widget_id}, {listener});\n")
        elif widget.class_name == "Checkbox":
            listener = "this" if has_checkbox_listener else "null"
            unchecked_img = props.get('mUncheckedImage', '')
            checked_img = props.get('mCheckedImage', '')
            lines.append(f"        {var_name} = new Checkbox({self._get_image_ref(unchecked_img)}, {self._get_image_ref(checked_img)}, {widget_id}, {listener});\n")
        elif widget.class_name == "Slider":
            listener = "this" if has_slider_listener else "null"
            track_img = props.get('mTrackImage', '')
            thumb_img = props.get('mThumbImage', '')
            lines.append(f"        {var_name} = new Slider({self._get_image_ref(track_img)}, {self._get_image_ref(thumb_img)}, {widget_id}, {listener});\n")
        elif widget.class_name == "DialogButton":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new DialogButton(null, {widget_id}, {listener});\n")
        else:
            return ""

        if not skip_resize:
            x = props.get("mX", 0)
            y = props.get("mY", 0)
            w = props.get("mWidth", 100)
            h = props.get("mHeight", 30)
            lines.append(f"        {var_name}.Resize({x}, {y}, {w}, {h});\n")

        lines.append(self._generate_property_assignments_cs(widget, var_name))
        return "".join(lines)

    def _generate_property_assignments_cs(self, widget: WidgetInstance, var_name: str) -> str:
        props = widget.properties
        lines = []
        
        skip_props = self.SKIP_PROPS | {"mFont", "mHiliteFont", "mButtonImage", "mOverImage", "mDownImage", "mUniformImage",
                                        "mUncheckedImage", "mCheckedImage", "mTrackImage", "mThumbImage", "mImage",
                                        "mText", "mColor", "mJustify", "mStretch", "mScaleX", "mScaleY"}
        
        for pname, pval in props.items():
            if pname in skip_props:
                continue
            if pname == "mItemHeight":
                continue
            if pname == "mStretchImage":
                continue
            if pname.startswith("m") and pname not in ("mX", "mY", "mWidth", "mHeight", "mId", "_listeners"):
                if isinstance(pval, bool):
                    lines.append(f"        {var_name}.{pname} = {str(pval).lower()};\n")
                elif isinstance(pval, str):
                    if not pval:
                        if pname in ("mString", "mLabel", "mDialogHeader", "mDialogLines", "mDialogFooter"):
                            lines.append(f"        {var_name}.{pname} = \"\";\n")
                    elif pname in self.WIDGET_PROPS:
                        lines.append(f"        {var_name}.{pname} = {str(pval).lower()};\n")
                    elif pname == "mJustify":
                        justify_val = self.JUSTIFY_MAP_CS.get(pval.upper(), "DrawStringJustification.Left")
                        lines.append(f"        {var_name}.{pname} = {justify_val};\n")
                    elif pname in self.COLOR_PROPS:
                        color_val = self._parse_color_cs(pval)
                        lines.append(f"        {var_name}.{pname} = {color_val};\n")
                    elif pname == "mVal":
                        lines.append(f"        {var_name}.{pname} = {pval}f;\n")
                    elif pval.replace('.', '', 1).isdigit() and pval.count('.') <= 1:
                        if '.' in pval:
                            lines.append(f"        {var_name}.{pname} = {pval}f;\n")
                        else:
                            lines.append(f"        {var_name}.{pname} = {pval};\n")
                    else:
                        lines.append(f"        {var_name}.{pname} = \"{pval}\";\n")
                elif isinstance(pval, (int, float)):
                    if isinstance(pval, float):
                        lines.append(f"        {var_name}.{pname} = {pval}f;\n")
                    else:
                        lines.append(f"        {var_name}.{pname} = {pval};\n")
        
        return "".join(lines)

    def get_widget_includes(self, iface: Interface) -> str:
        usings = set()
        usings.add("using Sexy;")
        usings.add("using Sexy.TodLib;")
        return "\n".join(sorted(usings))
