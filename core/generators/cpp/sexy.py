# -*- coding: utf-8 -*-
from typing import List
from core.project import WidgetInstance, Interface
from ..base import CodeGeneratorBase


class CppSexyGenerator(CodeGeneratorBase):
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
        has_dialog_listener = "DialogListener" in class_listeners
        has_list_listener = "ListListener" in class_listeners

        if widget.class_name == "ButtonWidget":
            listener = "this" if has_btn_listener else "nullptr"
            lines.append(f"    {var_name} = new ButtonWidget({widget_id}, {listener});\n")
        elif widget.class_name == "EditWidget":
            listener = "this" if has_edit_listener else "nullptr"
            lines.append(f"    {var_name} = new EditWidget({widget_id}, {listener});\n")
        elif widget.class_name == "Checkbox":
            listener = "this" if has_checkbox_listener else "nullptr"
            unchecked_img = props.get('mUncheckedImage', 'nullptr')
            checked_img = props.get('mCheckedImage', 'nullptr')
            if not unchecked_img or unchecked_img == 'nullptr':
                unchecked_img = 'nullptr'
            if not checked_img or checked_img == 'nullptr':
                checked_img = 'nullptr'
            lines.append(f"    {var_name} = new Checkbox({unchecked_img}, {checked_img}, {widget_id}, {listener});\n")
        elif widget.class_name == "Slider":
            listener = "this" if has_slider_listener else "nullptr"
            lines.append(f"    {var_name} = new Slider(nullptr, nullptr, {widget_id}, {listener});\n")
        elif widget.class_name == "Dialog":
            listener = "this" if has_dialog_listener else "nullptr"
            header_text = props.get('mDialogHeader', '')
            lines_text = props.get('mDialogLines', '')
            lines.append(f"    {var_name} = new Dialog({listener}, \"{header_text}\", \"{lines_text}\", {widget_id});\n")
            stretch_image = props.get('mStretchImage', True)
            if stretch_image:
                comp_img = props.get('mComponentImage', '')
                if comp_img:
                    img_ref = f"Sexy::{comp_img}" if not comp_img.startswith("Sexy::") else comp_img
                    lines.append(f"    if ({img_ref})\n")
                    lines.append(f"        {var_name}->mComponentImageRect = Rect(0, 0, {img_ref}->GetWidth(), {img_ref}->GetHeight());\n")
        elif widget.class_name == "DialogButton":
            listener = "this" if has_btn_listener else "nullptr"
            lines.append(f"    {var_name} = new DialogButton(nullptr, {widget_id}, {listener});\n")
            stretch_image = props.get('mStretchImage', True)
            if stretch_image:
                comp_img = props.get('mComponentImage', '')
                if comp_img:
                    img_ref = f"Sexy::{comp_img}" if not comp_img.startswith("Sexy::") else comp_img
                    lines.append(f"    if ({img_ref})\n")
                    lines.append(f"        {var_name}->mNormalRect = Rect(0, 0, {img_ref}->GetWidth(), {img_ref}->GetHeight());\n")
        elif widget.class_name == "ScrollbuttonWidget":
            listener = "this" if has_btn_listener else "nullptr"
            scroll_type = props.get('mType', '0')
            lines.append(f"    {var_name} = new ScrollbuttonWidget({widget_id}, {listener}, {scroll_type});\n")
        elif widget.class_name == "HyperlinkWidget":
            listener = "this" if has_btn_listener else "nullptr"
            lines.append(f"    {var_name} = new HyperlinkWidget({widget_id}, {listener});\n")
        elif widget.class_name == "ListWidget":
            listener = "this" if has_list_listener else "nullptr"
            font = props.get('mFont', 'FONT_DWARVENTODCRAFT12')
            if not font:
                font = 'FONT_DWARVENTODCRAFT12'
            lines.append(f"    {var_name} = new ListWidget({widget_id}, {font}, {listener});\n")
            item_height = props.get('mItemHeight', 20)
            lines.append(f"    {var_name}->mItemHeight = {item_height};\n")
        elif widget.class_name == "TextWidget":
            lines.append(f"    {var_name} = new TextWidget();\n")
            font = props.get('mFont', 'FONT_DWARVENTODCRAFT12')
            if not font:
                font = 'FONT_DWARVENTODCRAFT12'
            lines.append(f"    {var_name}->mFont = {font};\n")
            lines.append(f"    {var_name}->mDisabled = true;\n")
            x = props.get("mX", 0)
            y = props.get("mY", 0)
            w = props.get("mWidth", 100)
            h = props.get("mHeight", 30)
            lines.append(f"    {var_name}->mX = {x};\n")
            lines.append(f"    {var_name}->mY = {y};\n")
            lines.append(f"    {var_name}->mWidth = {w};\n")
            lines.append(f"    {var_name}->mHeight = {h};\n")
            skip_resize = True
        else:
            return ""

        if not skip_resize:
            x = props.get("mX", 0)
            y = props.get("mY", 0)
            w = props.get("mWidth", 100)
            h = props.get("mHeight", 30)
            lines.append(f"    {var_name}->Resize({x}, {y}, {w}, {h});\n")

        lines.append(self._generate_property_assignments(widget, var_name))

        if widget.class_name == "TextWidget":
            mlines = props.get("mLines", "")
            if mlines:
                line_list = [l.strip() for l in mlines.split("\\n") if l.strip()]
                if line_list:
                    lines.append(f"    {{\n")
                    lines.append(f"        SexyStringVector lines;\n")
                    for l in line_list:
                        lines.append(f'        lines.push_back("{l}");\n')
                    lines.append(f"        {var_name}->SetLines(lines);\n")
                    lines.append(f"    }}\n")

        if widget.class_name == "ListWidget":
            mlines = props.get("mLines", "")
            if mlines:
                line_list = [l.strip() for l in mlines.split("\\n") if l.strip()]
                for l in line_list:
                    lines.append(f'    {var_name}->AddLine("{l}", false);\n')

        return "".join(lines)

    def _generate_property_assignments(self, widget: WidgetInstance, var_name: str) -> str:
        props = widget.properties
        lines = []
        
        for pname, pval in props.items():
            if pname in self.SKIP_PROPS:
                continue
            if pname == "mItemHeight":
                continue
            if pname == "mFont" and widget.class_name in ("ListWidget", "TextWidget"):
                continue
            if pname == "mDisabled" and widget.class_name == "TextWidget":
                continue
            if pname == "mLines":
                continue
            if pname == "mStretchImage":
                continue
            if pname.startswith("m") and pname not in ("mX", "mY", "mWidth", "mHeight", "mId", "_listeners"):
                if isinstance(pval, bool):
                    lines.append(f"    {var_name}->{pname} = {'true' if pval else 'false'};\n")
                elif isinstance(pval, str):
                    if not pval:
                        if pname in ("mString", "mLabel", "mDialogHeader", "mDialogLines", "mDialogFooter"):
                            lines.append(f"    {var_name}->{pname} = \"\";\n")
                        elif pname == "mFont":
                            lines.append(f"    {var_name}->{pname} = Sexy::FONT_DWARVENTODCRAFT12;\n")
                    elif pval.startswith("IMAGE_"):
                        lines.append(f"    {var_name}->{pname} = Sexy::{pval};\n")
                    elif pval.startswith("FONT_"):
                        lines.append(f"    {var_name}->{pname} = Sexy::{pval};\n")
                    elif pname in self.WIDGET_PROPS:
                        lines.append(f"    {var_name}->{pname} = {'true' if pval == 'true' or pval == True else 'false'};\n")
                    elif pname == "mJustify":
                        justify_val = self.JUSTIFY_MAP.get(pval.upper(), "ListWidget::JUSTIFY_LEFT")
                        lines.append(f"    {var_name}->{pname} = {justify_val};\n")
                    elif pname == "mButtonMode":
                        mode_val = self.BUTTON_MODE_MAP.get(pval, "Dialog::BUTTONS_NONE")
                        lines.append(f"    {var_name}->{pname} = {mode_val};\n")
                    elif pname in self.COLOR_PROPS:
                        color_val = self._parse_color(pval)
                        lines.append(f"    {var_name}->{pname} = {color_val};\n")
                    elif pval.isdigit() or (pval.replace('.', '', 1).isdigit() and pval.count('.') <= 1):
                        lines.append(f"    {var_name}->{pname} = {pval};\n")
                    else:
                        lines.append(f"    {var_name}->{pname} = \"{pval}\";\n")
                elif isinstance(pval, (int, float)):
                    lines.append(f"    {var_name}->{pname} = {pval};\n")
        
        return "".join(lines)

    def get_widget_includes(self, iface: Interface) -> str:
        includes = set()
        for wid in iface.widgets.values():
            if wid.class_name == "ButtonWidget":
                includes.add('#include "widget/ButtonWidget.h"')
            elif wid.class_name == "EditWidget":
                includes.add('#include "widget/EditWidget.h"')
            elif wid.class_name == "Checkbox":
                includes.add('#include "widget/Checkbox.h"')
            elif wid.class_name == "Slider":
                includes.add('#include "widget/Slider.h"')
            elif wid.class_name == "Dialog":
                includes.add('#include "widget/Dialog.h"')
            elif wid.class_name == "DialogButton":
                includes.add('#include "widget/DialogButton.h"')
            elif wid.class_name == "ListWidget":
                includes.add('#include "widget/ListWidget.h"')
            elif wid.class_name == "ScrollWidget":
                includes.add('#include "widget/ScrollWidget.h"')
            elif wid.class_name == "HyperlinkWidget":
                includes.add('#include "widget/HyperlinkWidget.h"')
            elif wid.class_name == "ScrollbuttonWidget":
                includes.add('#include "widget/ScrollbuttonWidget.h"')
            elif wid.class_name == "TextWidget":
                includes.add('#include "widget/TextWidget.h"')
        return "\n".join(includes)
