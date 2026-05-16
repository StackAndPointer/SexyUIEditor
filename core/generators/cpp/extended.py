# -*- coding: utf-8 -*-
from core.project import WidgetInstance
from ..base import CodeGeneratorBase


class CppExtendedGenerator(CodeGeneratorBase):
    def generate_widget_init(self, widget: WidgetInstance, class_listeners: list) -> str:
        if widget.class_name not in self.CUSTOM_WIDGETS:
            return ""
        if widget.class_name in ("Label", "ImageBox"):
            return ""
        return ""

    def generate_draw_code(self, widget: WidgetInstance) -> str:
        if widget.class_name == "Label":
            return self._generate_label_draw_code(widget)
        elif widget.class_name == "ImageBox":
            return self._generate_imagebox_draw_code(widget)
        return ""

    def _generate_label_draw_code(self, widget: WidgetInstance) -> str:
        props = widget.properties
        x = props.get("mX", 0)
        y = props.get("mY", 0)
        width = props.get("mWidth", 100)
        height = props.get("mHeight", 30)
        text = props.get("mText", "")
        font = props.get("mFont", "FONT_DWARVENTODCRAFT12")
        if not font:
            font = "FONT_DWARVENTODCRAFT12"
        color = props.get("mColor", "255,255,255")
        justify = props.get("mJustify", "LEFT")
        
        justify_map = {
            "LEFT": "DS_ALIGN_LEFT",
            "CENTER": "DS_ALIGN_CENTER",
            "RIGHT": "DS_ALIGN_RIGHT",
        }
        justify_val = justify_map.get(justify.upper(), "DS_ALIGN_LEFT")
        
        color_parts = color.split(",") if color else ["255", "255", "255"]
        r = color_parts[0].strip() if len(color_parts) > 0 else "255"
        g = color_parts[1].strip() if len(color_parts) > 1 else "255"
        b = color_parts[2].strip() if len(color_parts) > 2 else "255"
        
        font_ref = f"Sexy::{font}" if not font.startswith("Sexy::") else font
        
        lines = []
        lines.append(f"    // Label: {widget.instance_name or widget.id}\n")
        lines.append(f"    if ({font_ref})\n")
        lines.append(f'        TodDrawStringWrapped(g, "{text}", Rect({x}, {y}, {width}, {height}), {font_ref}, Color({r}, {g}, {b}), {justify_val});\n')
        return "".join(lines)

    def _generate_imagebox_draw_code(self, widget: WidgetInstance) -> str:
        props = widget.properties
        x = props.get("mX", 0)
        y = props.get("mY", 0)
        width = props.get("mWidth", 100)
        height = props.get("mHeight", 100)
        image = props.get("mImage", "")
        scale_x = props.get("mScaleX", 1.0)
        scale_y = props.get("mScaleY", 1.0)
        stretch = props.get("mStretch", False)
        
        if not image:
            return f"    // ImageBox: {widget.instance_name or widget.id} (no image)\n"
        
        img_ref = f"Sexy::{image}" if not image.startswith("Sexy::") else image
        
        lines = []
        lines.append(f"    // ImageBox: {widget.instance_name or widget.id}\n")
        lines.append(f"    if ({img_ref}) {{\n")
        if stretch:
            img_width = f"{img_ref}->GetWidth()"
            img_height = f"{img_ref}->GetHeight()"
            lines.append(f"        float scaleX = (float){width} / {img_width};\n")
            lines.append(f"        float scaleY = (float){height} / {img_height};\n")
            lines.append(f"        TodDrawImageScaledF(g, {img_ref}, (float){x}, (float){y}, scaleX, scaleY);\n")
        else:
            lines.append(f"        TodDrawImageScaledF(g, {img_ref}, (float){x}, (float){y}, {scale_x}f, {scale_y}f);\n")
        lines.append(f"    }}\n")
        return "".join(lines)
