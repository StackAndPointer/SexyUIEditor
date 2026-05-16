# -*- coding: utf-8 -*-
"""
C# Code Generator Module
Handles code generation for PlantsVsZombies.NET (C# version).
"""
from typing import List, Set
from core.project import Project, WidgetInstance, Interface
from .base import CodeGeneratorBase
from ui.image_picker import is_atlas_sub_image
from core.resource_groups import get_delay_load_call
from core.i18n import tr
import os

ATLAS_IMAGE_PREFIXES = (
    "IMAGE_REANIM_", "IMAGE_SELECTORSCREEN_", "IMAGE_SEEDCHOOSER_", 
    "IMAGE_ALMANAC_", "IMAGE_BLASTMARK", "IMAGE_ROCKSMALL", "IMAGE_DIRTBIG",
    "IMAGE_DIRTSMALL", "IMAGE_RAIN", "IMAGE_LANTERNSHINE", "IMAGE_AWARD",
    "IMAGE_VASE_", "IMAGE_IMITATERCLOUDS", "IMAGE_ZOMBOSS_", "IMAGE_BEGHOULED_",
    "IMAGE_DIALOG_", "IMAGE_BUTTON_", "IMAGE_EDITBOX", "IMAGE_OPTIONS_",
    "IMAGE_BLANK", "IMAGE_SCROLL_INDICATOR", "IMAGE_SELECTED_PACKET",
    "IMAGE_MINI_GAME_FRAME", "IMAGE_MINI_GAME_HIGHLIGHT_FRAME"
)


class CSharpGenerator(CodeGeneratorBase):
    SEXY_WIDGETS_CS = {"ButtonWidget", "EditWidget", "Checkbox", "Slider", "Dialog", "DialogButton",
                       "ListWidget", "ScrollWidget", "HyperlinkWidget", "ScrollbuttonWidget", "TextWidget"}
    PVZ_WIDGETS_CS = {"NewLawnButton", "LawnDialog", "LawnStoneButton", "LawnEditWidget", "GameButton"}
    CUSTOM_WIDGETS_CS = {"Label", "ImageBox"}
    NON_WIDGET_TYPES_CS = {"Label", "ImageBox"}
    PVZ_NON_WIDGET_TYPES_CS = {"GameButton"}
    
    JUSTIFY_MAP_CS = {
        "LEFT": "DrawStringJustification.Left",
        "CENTER": "DrawStringJustification.Center",
        "RIGHT": "DrawStringJustification.Right",
    }

    def __init__(self):
        super().__init__()

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

    def _parse_color_xna(self, color_str: str) -> str:
        if not color_str:
            return "Color.White"
        parts = color_str.split(",")
        if len(parts) >= 3:
            try:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                if len(parts) >= 4:
                    a = int(parts[3].strip())
                    return f"new Color({r}, {g}, {b}, {a})"
                return f"new Color({r}, {g}, {b})"
            except ValueError:
                pass
        return "Color.White"

    def _needs_store_listener(self, iface: Interface) -> bool:
        for widget in iface.widgets.values():
            for event_type, actions in widget.event_actions.items():
                for action in actions:
                    if hasattr(action, 'predefined_id') and action.predefined_id == "show_store":
                        return True
        return False

    def generate_widget_init(self, widget: WidgetInstance, class_listeners: List[str]) -> str:
        var_name = self._get_var_name(widget)
        props = widget.properties
        lines = []
        widget_id = props.get('mId', 0)
        skip_resize = False
        
        has_btn_listener = "ButtonListener" in class_listeners
        has_edit_listener = "EditListener" in class_listeners
        has_checkbox_listener = "CheckboxListener" in class_listeners
        has_slider_listener = "SliderListener" in class_listeners

        if widget.class_name == "GameButton":
            lines.append(f"        {var_name} = new GameButton({widget_id}, this);\n")
        elif widget.class_name == "NewLawnButton":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new NewLawnButton(null, {widget_id}, {listener});\n")
            lines.append(f"        {var_name}.SetColor(ButtonWidget.ColorType.Bkg, SexyColor.White);\n")
            lines.append(f"        {var_name}.SetColor(ButtonWidget.ColorType.Label, SexyColor.White);\n")
            lines.append(f"        {var_name}.SetColor(ButtonWidget.ColorType.LabelHilite, SexyColor.White);\n")
            font = props.get('mFont', 'FONT_DWARVENTODCRAFT12')
            if font:
                lines.append(f"        {var_name}.SetFont({self._get_font_ref(font)});\n")
            hilite_font = props.get('mHiliteFont', '')
            if hilite_font:
                lines.append(f"        {var_name}.mHiliteFont = {self._get_font_ref(hilite_font)};\n")
            uniform_img = props.get('mUniformImage', 'IMAGE_DIALOG')
            btn_img = props.get('mButtonImage', '')
            over_img = props.get('mOverImage', '')
            down_img = props.get('mDownImage', '')
            if not btn_img:
                btn_img = uniform_img
            if not over_img:
                over_img = uniform_img
            if not down_img:
                down_img = uniform_img
            if btn_img:
                lines.append(f"        {var_name}.mButtonImage = {self._get_image_ref(btn_img)};\n")
            if over_img:
                lines.append(f"        {var_name}.mOverImage = {self._get_image_ref(over_img)};\n")
            if down_img:
                lines.append(f"        {var_name}.mDownImage = {self._get_image_ref(down_img)};\n")
        elif widget.class_name == "LawnStoneButton":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new LawnStoneButton(null, {widget_id}, {listener});\n")
        elif widget.class_name == "LawnDialog":
            is_modal = str(props.get('mIsModal', False)).lower()
            header = props.get('mDialogHeader', '')
            lines_text = props.get('mDialogLines', '')
            footer = props.get('mDialogFooter', '')
            button_mode = props.get('mButtonMode', '0')
            if isinstance(button_mode, str) and not button_mode.isdigit():
                button_mode = '0'
            lines.append(f"        {var_name} = new LawnDialog(mApp, null, {widget_id}, {is_modal}, \"{header}\", \"{lines_text}\", \"{footer}\", {button_mode});\n")
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
        elif widget.class_name == "EditWidget":
            listener = "this" if has_edit_listener else "null"
            lines.append(f"        {var_name} = new EditWidget({widget_id}, {listener});\n")
        elif widget.class_name == "LawnEditWidget":
            listener = "this" if has_edit_listener else "null"
            title = props.get('mTitle', '')
            description = props.get('mDescription', '')
            lines.append(f"        {var_name} = new LawnEditWidget({widget_id}, {listener}, null, \"{title}\", \"{description}\");\n")
        elif widget.class_name == "ButtonWidget":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new ButtonWidget({widget_id}, {listener});\n")
        elif widget.class_name == "DialogButton":
            listener = "this" if has_btn_listener else "null"
            lines.append(f"        {var_name} = new DialogButton(null, {widget_id}, {listener});\n")
        elif widget.class_name == "Label":
            return ""
        elif widget.class_name == "ImageBox":
            return ""
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
                                        "mText", "mColor", "mJustify", "mStretch", "mScaleX", "mScaleY", "mHorizontal"}
        
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

    def generate_class_header_cs(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        class_name = s.class_name
        listeners = sorted(self._get_required_listeners_for_interface(iface))
        
        is_dialog_type = s.interface_type == "dialog"
        effective_listeners = [l for l in listeners if l != "ButtonListener"] if is_dialog_type else listeners
        
        needs_store_listener = self._needs_store_listener(iface)
        if needs_store_listener and "StoreListener" not in effective_listeners:
            effective_listeners.append("StoreListener")
        
        if is_dialog_type:
            base_class = "LawnDialog" if s.parent_class == "LawnDialog" else "Dialog"
            listener_interfaces = ", ".join([f"Sexy.{l}" if l in ("ButtonListener", "CheckboxListener", "SliderListener", "EditListener") else l for l in effective_listeners]) if effective_listeners else ""
            if listener_interfaces:
                class_decl = f"public class {class_name} : {base_class}, {listener_interfaces}"
            else:
                class_decl = f"public class {class_name} : {base_class}"
        else:
            base_class = "Widget"
            listener_interfaces = ", ".join([f"Sexy.{l}" if l in ("ButtonListener", "CheckboxListener", "SliderListener", "EditListener") else l for l in effective_listeners]) if effective_listeners else ""
            if listener_interfaces:
                class_decl = f"public class {class_name} : {base_class}, {listener_interfaces}"
            else:
                class_decl = f"public class {class_name} : {base_class}"
        
        usings = self._get_usings(iface)
        
        header = f"""// Auto-generated by SexyUI Editor
// Do not modify this file directly - changes may be overwritten

{usings}

namespace Lawn
{{
    {class_decl}
    {{
        public LawnApp mApp;

"""
        
        for wid in iface.widgets.values():
            if wid.class_name in self.NON_WIDGET_TYPES_CS:
                continue
            var_name = self._get_var_name(wid)
            type_name = self._get_csharp_type(wid.class_name)
            if wid.class_name in self.PVZ_WIDGETS_CS or type_name in ("Slider", "Checkbox"):
                header += f"        internal {type_name} {var_name};\n"
            else:
                header += f"        public {type_name} {var_name};\n"
        
        header += "\n        // [[[USER_DECLARATIONS]]]\n"
        if iface.user_code.declarations:
            header += iface.user_code.declarations + "\n"
        else:
            header += "        // " + tr("comment.declarations", "Add custom member declarations here") + "\n"
        header += "        // [[[END_USER_DECLARATIONS]]]\n"
        
        return header

    def _get_csharp_type(self, class_name: str) -> str:
        type_map = {
            "ButtonWidget": "ButtonWidget",
            "EditWidget": "EditWidget",
            "Checkbox": "Checkbox",
            "Slider": "Slider",
            "Dialog": "Dialog",
            "DialogButton": "DialogButton",
            "ListWidget": "ListWidget",
            "ScrollWidget": "ScrollWidget",
            "HyperlinkWidget": "HyperlinkWidget",
            "ScrollbuttonWidget": "ScrollbuttonWidget",
            "TextWidget": "TextWidget",
            "GameButton": "GameButton",
            "NewLawnButton": "NewLawnButton",
            "LawnDialog": "LawnDialog",
            "LawnStoneButton": "LawnStoneButton",
            "LawnEditWidget": "LawnEditWidget",
        }
        return type_map.get(class_name, class_name)

    def _get_usings(self, iface: Interface) -> str:
        usings = set()
        usings.add("using System;")
        usings.add("using Microsoft.Xna.Framework;")
        usings.add("using Sexy;")
        usings.add("using Sexy.TodLib;")
        
        for wid in iface.widgets.values():
            if wid.class_name in ("NewLawnButton", "LawnStoneButton", "GameButton", "LawnDialog"):
                pass
            if wid.class_name == "Label":
                pass
            if wid.class_name == "ImageBox":
                pass
        
        return "\n".join(sorted(usings))

    def generate_class_impl_cs(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        class_name = s.class_name
        listeners = sorted(self._get_required_listeners_for_interface(iface))
        
        is_dialog_type = s.interface_type == "dialog"
        effective_listeners = [l for l in listeners if l != "ButtonListener"] if is_dialog_type else listeners
        
        widget_listeners = listeners.copy()
        if is_dialog_type and "ButtonListener" not in widget_listeners:
            widget_listeners.append("ButtonListener")
        
        if is_dialog_type:
            interface_id = hash(class_name) % 10000 + 1000
            ctor = f"""        public {class_name}(LawnApp theApp, int theId, bool isModal, string theDialogHeader, string theDialogLines, string theDialogFooter, int theButtonMode)
            : base(theApp, null, theId, isModal, theDialogHeader, theDialogLines, theDialogFooter, theButtonMode)
        {{
            mApp = theApp;
            Resize(0, 0, {s.width}, {s.height});
"""
        else:
            ctor = f"""        public {class_name}(LawnApp theApp)
        {{
            mApp = theApp;
            Resize(0, 0, {s.width}, {s.height});
"""
        
        resource_load_calls = self._get_resource_load_calls(iface, project)
        if resource_load_calls:
            for call in resource_load_calls:
                ctor += f"            {call}\n"
        
        for wid in iface.widgets.values():
            init_code = self.generate_widget_init(wid, widget_listeners)
            ctor += init_code
        
        ctor += "\n            // [[[USER_INIT]]]\n"
        if iface.user_code.init_code:
            ctor += iface.user_code.init_code + "\n"
        else:
            ctor += "            // " + tr("comment.init", "Add custom initialization code here") + "\n"
        ctor += "            // [[[END_USER_INIT]]]\n"
        ctor += "        }\n\n"
        
        dtor = f"""        public override void Dispose()
        {{
"""
        for wid in iface.widgets.values():
            if wid.class_name not in self.NON_WIDGET_TYPES_CS:
                var_name = self._get_var_name(wid)
                dtor += f"            if ({var_name} != null) {var_name}.Dispose();\n"
        
        dtor += "\n            // [[[USER_DESTROY]]]\n"
        if iface.user_code.destroy_code:
            dtor += iface.user_code.destroy_code + "\n"
        else:
            dtor += "            // " + tr("comment.destroy", "Add custom cleanup code here") + "\n"
        dtor += "            // [[[END_USER_DESTROY]]]\n"
        dtor += "        }\n\n"
        
        draw_code = self._generate_draw_cs(iface)
        update_code = self._generate_update_cs(iface)
        added_removed = self._generate_added_removed_cs(iface)
        handlers = self._generate_handlers_cs(iface, project)
        
        impl = ctor + dtor + draw_code + update_code + added_removed + handlers
        
        footer = """        // [[[USER_FUNCTIONS]]]
"""
        if iface.user_code.functions:
            footer += iface.user_code.functions + "\n"
        else:
            footer += "        // " + tr("comment.functions", "Add custom function implementations here") + "\n"
        footer += """        // [[[END_USER_FUNCTIONS]]]
    }
}
"""
        
        return impl + footer

    def _get_resource_load_calls(self, iface: Interface, project: Project) -> List[str]:
        calls = []
        loaded_groups = set()
        
        resources_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      "Content", "resources.xml")
        
        if iface.settings.background_image:
            call = get_delay_load_call(iface.settings.background_image, resources_path)
            if call:
                group_name = call.split('"')[1]
                if group_name not in loaded_groups:
                    calls.append(call)
                    loaded_groups.add(group_name)
        
        for widget in iface.widgets.values():
            if widget.class_name == "ImageBox":
                img = widget.properties.get("mImage", "")
                if img:
                    call = get_delay_load_call(img, resources_path)
                    if call:
                        group_name = call.split('"')[1]
                        if group_name not in loaded_groups:
                            calls.append(call)
                            loaded_groups.add(group_name)
        
        return calls

    def _generate_draw_cs(self, iface: Interface) -> str:
        s = iface.settings
        class_name = s.class_name
        lines = [f"        public override void Draw(Graphics g)\n        {{\n"]
        
        if s.background_image:
            img_ref = self._get_image_ref(s.background_image)
            lines.append(f"            if ({img_ref} != null)\n")
            if s.background_stretch:
                lines.append(f"                LawnCommon.StretchImage(g, {img_ref}, 0, 0, mWidth, mHeight);\n")
            else:
                lines.append(f"                g.DrawImage({img_ref}, 0, 0);\n")
        
        for wid in iface.widgets.values():
            if wid.class_name == "Label":
                draw_code = self._generate_label_draw_cs(wid)
                lines.append(draw_code)
            elif wid.class_name == "ImageBox":
                draw_code = self._generate_imagebox_draw_cs(wid)
                lines.append(draw_code)
        
        lines.append("            base.Draw(g);\n")
        lines.append("\n            // [[[USER_DRAW]]]\n")
        if iface.user_code.draw_code:
            lines.append(iface.user_code.draw_code + "\n")
        else:
            lines.append("            // " + tr("comment.draw", "Add custom drawing code here") + "\n")
        lines.append("            // [[[END_USER_DRAW]]]\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_update_cs(self, iface: Interface) -> str:
        s = iface.settings
        lines = [f"        public override void Update()\n        {{\n"]
        lines.append("            base.Update();\n")
        lines.append("            MarkDirty();\n")
        lines.append("\n            // [[[USER_UPDATE]]]\n")
        if iface.user_code.update_code:
            lines.append(iface.user_code.update_code + "\n")
        else:
            lines.append("            // " + tr("comment.update", "Add custom update code here") + "\n")
        lines.append("            // [[[END_USER_UPDATE]]]\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_added_removed_cs(self, iface: Interface) -> str:
        lines = [f"        public override void AddedToManager(WidgetManager theWidgetManager)\n        {{\n"]
        lines.append("            base.AddedToManager(theWidgetManager);\n")
        
        for wid in iface.widgets.values():
            if wid.class_name not in self.NON_WIDGET_TYPES_CS and wid.class_name not in self.PVZ_NON_WIDGET_TYPES_CS:
                var_name = self._get_var_name(wid)
                lines.append(f"            AddWidget({var_name});\n")
        
        lines.append("        }\n\n")
        
        lines.append(f"        public override void RemovedFromManager(WidgetManager theWidgetManager)\n        {{\n")
        lines.append("            base.RemovedFromManager(theWidgetManager);\n")
        
        for wid in iface.widgets.values():
            if wid.class_name not in self.NON_WIDGET_TYPES_CS and wid.class_name not in self.PVZ_NON_WIDGET_TYPES_CS:
                var_name = self._get_var_name(wid)
                lines.append(f"            RemoveWidget({var_name});\n")
        
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_handlers_cs(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        class_name = s.class_name
        listeners = self._get_required_listeners_for_interface(iface)
        
        handlers = ""
        
        if "ButtonListener" in listeners:
            handlers += self._generate_button_handlers_cs(iface, project)
        
        if "CheckboxListener" in listeners:
            handlers += self._generate_checkbox_handlers_cs(iface)
        
        if "SliderListener" in listeners:
            handlers += self._generate_slider_handlers_cs(iface)
        
        if "EditListener" in listeners:
            handlers += self._generate_edit_handlers_cs(iface)
        
        if self._needs_store_listener(iface):
            handlers += self._generate_store_listener_cs(iface)
        
        return handlers

    def _generate_button_handlers_cs(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        class_name = s.class_name
        lines = []
        
        lines.append(f"        public virtual void ButtonPress(int theId)\n        {{\n")
        lines.append("            mApp.PlaySample(Resources.SOUND_TAP);\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonPress(int theId, int theClickCount)\n        {{\n")
        lines.append("            ButtonPress(theId);\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonDownTick(int theId)\n        {{\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonMouseEnter(int theId)\n        {{\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonMouseLeave(int theId)\n        {{\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonMouseMove(int theId, int theX, int theY)\n        {{\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual void ButtonDepress(int theId)\n        {{\n")
        lines.append("            switch (theId)\n")
        lines.append("            {\n")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.BUTTON_WIDGETS or widget.class_name in self.SCROLLBUTTON_WIDGETS or widget.class_name in self.PVZ_WIDGETS_CS:
                widget_id = widget.properties.get("mId", 0)
                var_name = self._get_var_name(widget)
                handler_key = f"HANDLER_{widget.id}"
                
                lines.append(f"                case {widget_id}:\n")
                lines.append(f"                    {{\n")
                lines.append(f"                    // {widget.instance_name or widget.id}\n")
                lines.append(f"                    // [[[{handler_key}]]]\n")
                
                event_actions = widget.event_actions.get("ButtonDepress", [])
                if event_actions:
                    for action in event_actions:
                        code = self._generate_action_code_cs(action, iface, project)
                        if code:
                            lines.append(f"                    {code}\n")
                else:
                    lines.append(f"                    // Click event handler\n")
                
                lines.append(f"                    // [[[END_{handler_key}]]]\n")
                lines.append(f"                    break;\n")
                lines.append(f"                    }}\n")
        
        lines.append("            }\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_action_code_cs(self, action, iface: Interface, project: Project) -> str:
        from core.predefined_actions import get_action
        
        if not hasattr(action, 'predefined_id'):
            return ""
        
        action_id = action.predefined_id
        params = action.params
        is_dialog_type = iface.settings.interface_type == "dialog"
        
        if action_id == "close_current_dialog":
            if is_dialog_type:
                return "mApp.KillDialog(mId);"
            else:
                return "mWidgetManager.RemoveWidget(this);"
        
        if action_id == "close_current_widget":
            if is_dialog_type:
                return "mApp.KillDialog(mId);"
            else:
                return "mWidgetManager.RemoveWidget(this);"
        
        if action_id in ["open_project_interface", "switch_to_project_interface"]:
            interface_class = params.get("interface_class", "")
            interface_id = params.get("interface_id", "")
            
            target_is_dialog = True
            if project and interface_class:
                for other_iface in project.interfaces.values():
                    if other_iface.settings.class_name == interface_class:
                        target_is_dialog = other_iface.settings.interface_type == "dialog"
                        break
            
            if action_id == "open_project_interface":
                if target_is_dialog:
                    return f"mApp.AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog.BUTTONS_NONE));"
                else:
                    return f"mWidgetManager.AddWidget(new {interface_class}(mApp));"
            else:
                if target_is_dialog:
                    close_code = "mApp.KillDialog(mId);" if is_dialog_type else "mWidgetManager.RemoveWidget(this);"
                    return f"{close_code}\n                    mApp.AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog.BUTTONS_NONE));"
                else:
                    return f"WidgetManager widgetManager = mWidgetManager;\n                    widgetManager.RemoveWidget(this);\n                    widgetManager.AddWidget(new {interface_class}(mApp));"
        
        if action_id == "show_store":
            return "mApp.ShowStoreScreen(this);"
        
        if action_id == "show_almanac":
            return "mApp.DoAlmanacDialog(SeedType.None, ZombieType.Invalid, this);"
        
        if action_id == "show_confirm_dialog":
            dialog_id = params.get("dialog_id", "1000")
            header = params.get("header", "")
            content = params.get("content", "")
            return f"mApp.LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"[OK]\", \"[CANCEL]\", (int)Dialog.DialogButtons.BUTTONS_OK_CANCEL, null);"
        
        if action_id == "back_to_main_menu":
            return "WidgetManager widgetManager = mWidgetManager;\n                    widgetManager.RemoveWidget(this);\n                    mApp.ShowGameSelector();"
        
        act = get_action(action_id)
        if act and act.code_template:
            code = act.code_template
            code = code.replace("mApp->", "mApp.")
            code = code.replace("->", ".")
            code = code.replace("nullptr", "null")
            code = code.replace("Sexy::", "")
            return code
        
        return ""

    def _generate_checkbox_handlers_cs(self, iface: Interface) -> str:
        lines = []
        lines.append(f"        public virtual void CheckboxChecked(int theId, bool isChecked)\n        {{\n")
        lines.append("            switch (theId)\n")
        lines.append("            {\n")
        
        for widget in iface.widgets.values():
            if widget.class_name == "Checkbox":
                widget_id = widget.properties.get("mId", 0)
                var_name = self._get_var_name(widget)
                handler_key = f"CHECKBOX_{widget_id}"
                
                lines.append(f"                case {widget_id}:\n")
                lines.append(f"                    // {widget.instance_name or widget.id}\n")
                lines.append(f"                    // [[[{handler_key}]]]\n")
                lines.append(f"                    // {var_name} checkbox state changed\n")
                lines.append(f"                    // [[[END_{handler_key}]]]\n")
                lines.append(f"                    break;\n")
        
        lines.append("            }\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_slider_handlers_cs(self, iface: Interface) -> str:
        lines = []
        lines.append(f"        public virtual void SliderVal(int theId, double theVal)\n        {{\n")
        lines.append("            switch (theId)\n")
        lines.append("            {\n")
        
        for widget in iface.widgets.values():
            if widget.class_name == "Slider":
                widget_id = widget.properties.get("mId", 0)
                var_name = self._get_var_name(widget)
                handler_key = f"SLIDER_{widget_id}"
                
                lines.append(f"                case {widget_id}:\n")
                lines.append(f"                    // {widget.instance_name or widget.id}\n")
                lines.append(f"                    // [[[{handler_key}]]]\n")
                lines.append(f"                    // {var_name} slider value changed\n")
                lines.append(f"                    // [[[END_{handler_key}]]]\n")
                lines.append(f"                    break;\n")
        
        lines.append("            }\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_edit_handlers_cs(self, iface: Interface) -> str:
        lines = []
        
        lines.append(f"        public virtual void EditWidgetText(int theId, string theString)\n        {{\n")
        lines.append("            switch (theId)\n")
        lines.append("            {\n")
        
        for widget in iface.widgets.values():
            if widget.class_name in ("EditWidget", "LawnEditWidget"):
                widget_id = widget.properties.get("mId", 0)
                var_name = self._get_var_name(widget)
                handler_key = f"EDIT_{widget_id}"
                
                lines.append(f"                case {widget_id}:\n")
                lines.append(f"                    // {widget.instance_name or widget.id}\n")
                lines.append(f"                    // [[[{handler_key}]]]\n")
                lines.append(f"                    // {var_name} text changed\n")
                lines.append(f"                    // [[[END_{handler_key}]]]\n")
                lines.append(f"                    break;\n")
        
        lines.append("            }\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual bool AllowChar(int theId, char theChar)\n        {{\n")
        lines.append("            return true;\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual bool AllowText(int theId, ref string theText)\n        {{\n")
        lines.append("            return true;\n")
        lines.append("        }\n\n")
        
        lines.append(f"        public virtual bool ShouldClear()\n        {{\n")
        lines.append("            return false;\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def _generate_store_listener_cs(self, iface: Interface) -> str:
        lines = []
        lines.append(f"        public virtual void BackFromStore()\n        {{\n")
        lines.append("            // Called when returning from store screen\n")
        lines.append("        }\n\n")
        
        return "".join(lines)

    def generate_full_class_cs(self, iface: Interface, project: Project) -> str:
        header = self.generate_class_header_cs(iface, project)
        impl = self.generate_class_impl_cs(iface, project)
        return header + impl
