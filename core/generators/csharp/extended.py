# -*- coding: utf-8 -*-
from core.project import WidgetInstance
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


class CSharpExtendedGenerator(CodeGeneratorBase):
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

    def generate_widget_init(self, widget: WidgetInstance, class_listeners: list) -> str:
        if widget.class_name not in self.CUSTOM_WIDGETS:
            return ""
        if widget.class_name in ("Label", "ImageBox"):
            return ""
        return ""

    def generate_draw_code(self, widget: WidgetInstance) -> str:
        if widget.class_name == "Label":
            return self._generate_label_draw_cs(widget)
        elif widget.class_name == "ImageBox":
            return self._generate_imagebox_draw_cs(widget)
        return ""

    def _generate_label_draw_cs(self, widget: WidgetInstance) -> str:
        props = widget.properties
        x = props.get("mX", 0)
        y = props.get("mY", 0)
        w = props.get("mWidth", 100)
        h = props.get("mHeight", 30)
        text = props.get('mText', '')
        font = props.get('mFont', 'FONT_DWARVENTODCRAFT12')
        color = props.get('mColor', '255,255,255')
        justify = props.get('mJustify', 'LEFT')
        justify_val = self.JUSTIFY_MAP_CS.get(justify.upper(), "DrawStringJustification.Left")
        
        lines = f"            // Label: {widget.instance_name or widget.id}\n"
        lines += f"            if ({self._get_font_ref(font)} != null)\n"
        lines += f"                TodStringFile.TodDrawStringWrapped(g, \"{text}\", new TRect({x}, {y}, {w}, {h}), {self._get_font_ref(font)}, {self._parse_color_cs(color)}, {justify_val});\n"
        return lines

    def _generate_imagebox_draw_cs(self, widget: WidgetInstance) -> str:
        props = widget.properties
        x = props.get("mX", 0)
        y = props.get("mY", 0)
        w = props.get("mWidth", 100)
        h = props.get("mHeight", 100)
        img = props.get('mImage', '')
        stretch = props.get('mStretch', False)
        scale_x = props.get('mScaleX', 1.0)
        scale_y = props.get('mScaleY', 1.0)
        
        lines = f"            // ImageBox: {widget.instance_name or widget.id}\n"
        if stretch:
            lines += f"            if ({self._get_image_ref(img)} != null)\n"
            lines += f"            {{\n"
            lines += f"                TRect srcRect = new TRect(0, 0, {self._get_image_ref(img)}.mWidth, {self._get_image_ref(img)}.mHeight);\n"
            lines += f"                TRect destRect = new TRect({x}, {y}, {w}, {h});\n"
            lines += f"                g.DrawImage({self._get_image_ref(img)}, destRect, srcRect);\n"
            lines += f"            }}\n"
        elif scale_x != 1.0 or scale_y != 1.0:
            lines += f"            if ({self._get_image_ref(img)} != null)\n"
            lines += f"                TodCommon.TodDrawImageScaledF(g, {self._get_image_ref(img)}, {x}, {y}, {scale_x}f, {scale_y}f);\n"
        else:
            lines += f"            if ({self._get_image_ref(img)} != null)\n"
            lines += f"                g.DrawImage({self._get_image_ref(img)}, {x}, {y});\n"
        return lines
