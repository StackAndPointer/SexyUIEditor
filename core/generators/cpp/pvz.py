# -*- coding: utf-8 -*-
from typing import List
from core.project import WidgetInstance, Interface
from ..base import CodeGeneratorBase
from core.header_includes import HeaderIncludeManager


class CppPvzGenerator(CodeGeneratorBase):
    def generate_widget_init(self, widget: WidgetInstance, class_listeners: List[str]) -> str:
        if widget.class_name not in self.PVZ_WIDGETS:
            return ""
        
        var_name = self._get_var_name(widget)
        props = widget.properties
        lines = []
        widget_id = props.get('mId', 0)
        
        has_btn_listener = "ButtonListener" in class_listeners
        has_edit_listener = "EditListener" in class_listeners

        if widget.class_name == "GameButton":
            lines.append(f"    {var_name} = new GameButton({widget_id});\n")
            lines.append(f"    {var_name}->mApp = mApp;\n")
            lines.append(f"    {var_name}->mParentWidget = this;\n")
        elif widget.class_name == "NewLawnButton":
            listener = "this" if has_btn_listener else "nullptr"
            lines.append(f"    {var_name} = new NewLawnButton(nullptr, {widget_id}, {listener});\n")
            lines.append(f"    {var_name}->SetColor(ButtonWidget::COLOR_BKG, Color::White);\n")
            lines.append(f"    {var_name}->SetColor(ButtonWidget::COLOR_LABEL, Color::White);\n")
            lines.append(f"    {var_name}->SetColor(ButtonWidget::COLOR_LABEL_HILITE, Color::White);\n")
            font = props.get('mFont', 'FONT_DWARVENTODCRAFT12')
            if not font:
                font = 'FONT_DWARVENTODCRAFT12'
            lines.append(f"    {var_name}->SetFont(Sexy::{font});\n")
            hilite_font = props.get('mHiliteFont', '')
            if hilite_font:
                lines.append(f"    {var_name}->mHiliteFont = Sexy::{hilite_font};\n")
            uniform_img = props.get('mUniformImage', 'IMAGE_BUTTON_MIDDLE')
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
                img_ref = f"Sexy::{btn_img}" if not btn_img.startswith("Sexy::") else btn_img
                lines.append(f"    {var_name}->mButtonImage = {img_ref};\n")
            if over_img:
                img_ref = f"Sexy::{over_img}" if not over_img.startswith("Sexy::") else over_img
                lines.append(f"    {var_name}->mOverImage = {img_ref};\n")
            if down_img:
                img_ref = f"Sexy::{down_img}" if not down_img.startswith("Sexy::") else down_img
                lines.append(f"    {var_name}->mDownImage = {img_ref};\n")
        elif widget.class_name == "LawnStoneButton":
            listener = "this" if has_btn_listener else "nullptr"
            lines.append(f"    {var_name} = new LawnStoneButton(nullptr, {widget_id}, {listener});\n")
        elif widget.class_name == "LawnDialog":
            is_modal = props.get('mIsModal', 'false')
            header = props.get('mDialogHeader', '')
            lines_text = props.get('mDialogLines', '')
            footer = props.get('mDialogFooter', '')
            button_mode = props.get('mButtonMode', '0')
            if isinstance(button_mode, str) and not button_mode.isdigit():
                button_mode = '0'
            lines.append(f"    {var_name} = new LawnDialog(mApp, {widget_id}, {is_modal}, \"{header}\", \"{lines_text}\", \"{footer}\", {button_mode});\n")
        elif widget.class_name == "LawnEditWidget":
            listener = "this" if has_edit_listener else "nullptr"
            lines.append(f"    {var_name} = new LawnEditWidget({widget_id}, {listener}, nullptr);\n")
        else:
            return ""

        x = props.get("mX", 0)
        y = props.get("mY", 0)
        w = props.get("mWidth", 100)
        h = props.get("mHeight", 30)
        lines.append(f"    {var_name}->Resize({x}, {y}, {w}, {h});\n")

        lines.append(self._generate_property_assignments(widget, var_name))
        return "".join(lines)

    def _generate_property_assignments(self, widget: WidgetInstance, var_name: str) -> str:
        props = widget.properties
        lines = []
        
        for pname, pval in props.items():
            if pname in self.SKIP_PROPS:
                continue
            if pname == "mFont" and widget.class_name == "NewLawnButton":
                continue
            if pname == "mHiliteFont" and widget.class_name == "NewLawnButton":
                continue
            if pname in ("mButtonImage", "mOverImage", "mDownImage", "mUniformImage") and widget.class_name == "NewLawnButton":
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
                    elif pval.startswith("IMAGE_"):
                        lines.append(f"    {var_name}->{pname} = Sexy::{pval};\n")
                    elif pval.startswith("FONT_"):
                        lines.append(f"    {var_name}->{pname} = Sexy::{pval};\n")
                    elif pname in self.WIDGET_PROPS:
                        lines.append(f"    {var_name}->{pname} = {'true' if pval == 'true' or pval == True else 'false'};\n")
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

    def get_lawn_includes(self, iface: Interface, structure: str = "portable") -> str:
        includes = set()
        has_lawn_dialog = False
        for wid in iface.widgets.values():
            if wid.class_name in ("GameButton", "NewLawnButton", "LawnStoneButton"):
                include = HeaderIncludeManager.get_include("GameButton", structure)
                if include:
                    includes.add(f'#include "{include}"')
            if wid.class_name == "LawnDialog":
                include = HeaderIncludeManager.get_include("LawnDialog", structure)
                if include:
                    includes.add(f'#include "{include}"')
                has_lawn_dialog = True
            if wid.class_name == "LawnEditWidget":
                includes.add('#include "../LawnCommon.h"')
        if has_lawn_dialog or any(wid.class_name == "HyperlinkWidget" for wid in iface.widgets.values()):
            include = HeaderIncludeManager.get_include("Color", structure)
            if include:
                includes.add(f'#include "{include}"')
        return "\n".join(sorted(includes))
