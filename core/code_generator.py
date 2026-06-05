# -*- coding: utf-8 -*-
"""
Code Generator Main Module
Integrates Sexy, PVZ, Custom and CSharp generators for complete code generation.
"""
from typing import List, Optional, Set, Dict, Tuple
from core.project import Project, WidgetInstance, Interface
from core.generators.base import CodeGeneratorBase
from core.generators.cpp.sexy import CppSexyGenerator
from core.generators.cpp.pvz import CppPvzGenerator
from core.generators.cpp.extended import CppExtendedGenerator
from core.generators.csharp_legacy import CSharpGenerator
from core.header_includes import HeaderIncludeManager


class CodeGenerator(CodeGeneratorBase):
    _instance = None

    def __init__(self):
        super().__init__()
        self._sexy_gen = CppSexyGenerator()
        self._pvz_gen = CppPvzGenerator()
        self._custom_gen = CppExtendedGenerator()
        self._csharp_gen = CSharpGenerator()
        self._output_language = "cpp"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_output_language(self, language: str):
        self._output_language = language.lower()

    def get_output_language(self) -> str:
        return self._output_language

    def generate_all_interfaces(self, project: Project, language: str = "cpp") -> Dict[str, Tuple[str, str]]:
        if language == "csharp":
            result = {}
            for iface_id, iface in project.interfaces.items():
                cs_code = self.generate_csharp_for_interface(iface, project)
                result[iface.settings.class_name] = (cs_code, "")
            return result
        else:
            result = {}
            for iface_id, iface in project.interfaces.items():
                header = self.generate_header_for_interface(iface, project)
                cpp = self.generate_cpp_for_interface(iface, project)
                result[iface.settings.class_name] = (header, cpp)
            return result

    def generate_header_for_interface(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        guard = f"{s.class_name.upper()}_H"
        listeners = sorted(self._get_required_listeners_for_interface(iface))
        structure = getattr(project.settings, 'cpp_structure', 'portable')
        listener_includes = self._listener_includes(listeners, structure)
        is_dialog_type = s.interface_type == "dialog"
        if is_dialog_type:
            listeners = [l for l in listeners if l != "ButtonListener"]
        listener_bases = "".join(f", public Sexy::{l}" for l in listeners) if listeners else ""
        
        base_class = "Sexy::Dialog" if is_dialog_type else "Sexy::Widget"
        
        widget_include = HeaderIncludeManager.get_include("Widget", structure)
        dialog_include = HeaderIncludeManager.get_include("Dialog", structure)
        
        header = f"""#ifndef {guard}
#define {guard}

#include "{widget_include}"
#include "{dialog_include}"
{listener_includes}

#include <string>
#include <vector>

// [[[USER_INCLUDES]]]
// Add custom header includes here
{iface.user_code.header_includes}// [[[END_USER_INCLUDES]]]

class LawnApp;

namespace Sexy
{{
    class ButtonWidget;
    class EditWidget;
    class Checkbox;
    class Slider;
    class DialogButton;
    class ScrollbuttonWidget;
    class HyperlinkWidget;
    class ListWidget;
    class TextWidget;
}}

class GameButton;
class LawnStoneButton;
class NewLawnButton;
class LawnDialog;
class LawnEditWidget;

// [[[USER_FORWARD_DECLARATIONS]]]
// Add forward declarations and enums here
{iface.user_code.forward_declarations}// [[[END_USER_FORWARD_DECLARATIONS]]]

class {s.class_name} : public {base_class}{listener_bases}
{{
public:
    LawnApp* mApp;
"""
        
        if is_dialog_type:
            header += f"""
    static const int INTERFACE_ID = {hash(s.class_name) % 10000 + 1000};

    {s.class_name}(LawnApp* theApp, int theId, bool isModal, const std::string& theDialogHeader, const std::string& theDialogLines, const std::string& theDialogFooter, int theButtonMode);
"""
        else:
            header += f"""
    {s.class_name}(LawnApp* theApp);
"""
        
        header += f"""    virtual ~{s.class_name}();

    virtual void Draw(Sexy::Graphics* g) override;
    virtual void Update() override;
    virtual void AddedToManager(Sexy::WidgetManager* theWidgetManager) override;
    virtual void RemovedFromManager(Sexy::WidgetManager* theWidgetManager) override;
"""
        if self._has_non_widget_types(iface):
            header += "    virtual void MouseMove(int x, int y) override;\n"
            header += "    virtual void MouseDown(int x, int y, int theBtnNum, int theClickCount) override;\n"
            header += "    virtual void MouseUp(int x, int y, int theBtnNum, int theClickCount) override;\n"

        for listener in listeners:
            if listener == "ButtonListener":
                header += "    virtual void ButtonPress(int theId) override;\n"
                header += "    virtual void ButtonDepress(int theId) override;\n"
                header += "    virtual void ButtonDownTick(int theId) override {}\n"
                header += "    virtual void ButtonMouseEnter(int theId) override {}\n"
                header += "    virtual void ButtonMouseLeave(int theId) override {}\n"
                header += "    virtual void ButtonMouseMove(int theId, int x, int y) override {}\n"
            elif listener == "DialogListener":
                header += "    virtual void DialogButtonPress(int theDialogId, int theButtonId) override;\n"
                header += "    virtual void DialogButtonDepress(int theDialogId, int theButtonId) override {}\n"
            elif listener == "EditListener":
                header += "    virtual void EditWidgetText(int theId, const std::string& theString) override;\n"
            elif listener == "ListListener":
                header += "    virtual void ListClicked(int theId, int theIndex, int theClickCount) override;\n"
                header += "    virtual void ListClosed(int theId) override {}\n"
                header += "    virtual void ListHiliteChanged(int theId, int theOldIndex, int theNewIndex) override {}\n"
            elif listener == "CheckboxListener":
                header += "    virtual void CheckboxChecked(int theId, bool checked) override;\n"
            elif listener == "SliderListener":
                header += "    virtual void SliderVal(int theId, double theVal) override;\n"
            elif listener == "ScrollListener":
                header += "    virtual void ScrollPosition(int theId, double thePosition) override;\n"
        
        if is_dialog_type and "ButtonListener" not in listeners:
            has_buttons = any(
                w.class_name in self.BUTTON_WIDGETS or w.class_name in self.NON_WIDGET_TYPES
                for w in iface.widgets.values()
            )
            if has_buttons:
                header += "    virtual void ButtonPress(int theId) override;\n"
                header += "    virtual void ButtonDepress(int theId) override;\n"

        header += "\n    // [[[USER_DECLARATIONS]]]\n"
        header += "    // 在此标记区域内添加你的成员声明\n"
        header += iface.user_code.declarations
        header += "    // [[[END_USER_DECLARATIONS]]]\n"

        header += "\nprivate:\n"
        header += "    std::vector<std::string> mLoadedResourceNames;\n"
        for wid in iface.widgets.values():
            if wid.class_name in self.NON_WIDGET_TYPES:
                continue
            var_name = self._get_var_name(wid)
            ns = self._get_widget_namespace(wid.class_name)
            header += f"    {ns}{wid.class_name}* {var_name};\n"

        header += "};\n\n"
        
        if iface.user_code.post_class:
            header += f"// [[[USER_POST_CLASS]]]\n"
            header += iface.user_code.post_class
            header += "// [[[END_USER_POST_CLASS]]]\n\n"
        
        header += "#endif // " + guard + "\n"
        return header

    def generate_header(self, project: Project) -> str:
        iface = project.current_interface
        if iface:
            return self.generate_header_for_interface(iface, project)
        return ""

    def generate_cpp_for_interface(self, iface: Interface, project: Project) -> str:
        s = iface.settings
        listeners = sorted(self._get_required_listeners_for_interface(iface))
        structure = getattr(project.settings, 'cpp_structure', 'portable')
        
        widget_includes = self._sexy_gen.get_widget_includes(iface, structure)
        lawn_includes = self._pvz_gen.get_lawn_includes(iface, structure)
        has_non_widget = self._has_non_widget_types(iface)
        interface_includes = self._get_interface_includes(iface, project)
        action_includes = self._get_action_includes(iface)
        
        is_dialog_type = s.interface_type == "dialog"
        effective_listeners = [l for l in listeners if l != "ButtonListener"] if is_dialog_type else listeners
        listener_init = "".join(f", Sexy::{l}()" for l in effective_listeners) if effective_listeners else ""
        
        widget_listeners = listeners.copy()
        if is_dialog_type and "ButtonListener" not in widget_listeners:
            widget_listeners.append("ButtonListener")
        
        required_resources = self._collect_required_resources(iface)
        resource_load_code = ""
        if required_resources:
            for res in sorted(required_resources):
                resource_load_code += f'    mLoadedResourceNames.push_back("{res}");\n'
            resource_load_code += '    for (std::string& resource : mLoadedResourceNames)\n'
            resource_load_code += '        TodLoadResources(resource.c_str());\n\n'
        
        graphics_include = HeaderIncludeManager.get_include("Graphics", structure)
        widget_manager_include = HeaderIncludeManager.get_include("WidgetManager", structure)
        
        cpp = f"""#include "{s.class_name}.h"
#include "../../LawnApp.h"
#include "../../Resources.h"
#include "../../GameConstants.h"
#include "../../Sexy.TodLib/TodCommon.h"
#include "../../Sexy.TodLib/TodStringFile.h"
#include "{graphics_include}"
#include "{widget_manager_include}"
{widget_includes}
{lawn_includes}
{interface_includes}
{action_includes}

// [[[USER_INCLUDES]]]
// Add custom header includes here
{iface.user_code.cpp_includes}// [[[END_USER_INCLUDES]]]

using namespace Sexy;

"""
        
        if is_dialog_type:
            interface_id = hash(s.class_name) % 10000 + 1000
            cpp += f"""{s.class_name}::{s.class_name}(LawnApp* theApp, int theId, bool isModal, const std::string& theDialogHeader, const std::string& theDialogLines, const std::string& theDialogFooter, int theButtonMode)
    : Dialog(nullptr, nullptr, theId, isModal, theDialogHeader, theDialogLines, theDialogFooter, theButtonMode){listener_init}
{{
    mApp = theApp;
    mWidth = {s.width};
    mHeight = {s.height};
"""
        else:
            cpp += f"""{s.class_name}::{s.class_name}(LawnApp* theApp)
    : Widget(){listener_init}
{{
    mApp = theApp;
    Resize(0, 0, {s.width}, {s.height});
"""

        if resource_load_code:
            cpp += "\n" + resource_load_code

        for wid in iface.widgets.values():
            init_code = self._generate_widget_init(wid, widget_listeners)
            cpp += init_code

        if iface.user_code.init_code:
            cpp += f"\n    // [[[USER_INIT]]]\n"
            cpp += iface.user_code.init_code
            cpp += "\n    // [[[END_USER_INIT]]]\n"
        else:
            cpp += "\n    // [[[USER_INIT]]]\n"
            cpp += "    // 在此添加自定义初始化代码\n"
            cpp += "    // [[[END_USER_INIT]]]\n"

        cpp += "}\n\n"
        
        cpp += f"{s.class_name}::~{s.class_name}()\n{{\n"
        # Remove all child widgets from the container before deletion to satisfy WidgetContainer assertion
        cpp += "    RemoveAllWidgets(false, false);\n"
        for wid in iface.widgets.values():
            if wid.class_name not in self.NON_WIDGET_TYPES:
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name}) delete {var_name};\n"

        if iface.user_code.destroy_code:
            cpp += f"\n    // [[[USER_DESTROY]]]\n"
            cpp += iface.user_code.destroy_code
            cpp += "\n    // [[[END_USER_DESTROY]]]\n"
        else:
            cpp += "\n    // [[[USER_DESTROY]]]\n"
            cpp += "    // 在此添加清理代码\n"
            cpp += "    // [[[END_USER_DESTROY]]]\n"

        cpp += "}\n\n"

        cpp += f"void {s.class_name}::Draw(Graphics* g)\n{{\n"
        if s.background_image:
            bg_img = f"Sexy::{s.background_image}" if not s.background_image.startswith("Sexy::") else s.background_image
            cpp += f'    if ({bg_img})\n'
            if s.background_stretch:
                cpp += f'        g->DrawImage({bg_img}, Rect(0, 0, mWidth, mHeight), Rect(0, 0, {bg_img}->GetWidth(), {bg_img}->GetHeight()));\n'
            else:
                cpp += f'        g->DrawImage({bg_img}, 0, 0);\n'
        elif s.background_color and s.background_color != "0,0,0":
            parts = s.background_color.split(",")
            r = parts[0].strip() if len(parts) > 0 else "0"
            gr = parts[1].strip() if len(parts) > 1 else "0"
            b = parts[2].strip() if len(parts) > 2 else "0"
            cpp += f'    g->SetColor(Color({r}, {gr}, {b}));\n'
            cpp += f'    g->FillRect(0, 0, mWidth, mHeight);\n'
        
        for wid in iface.widgets.values():
            if wid.class_name in self.CUSTOM_WIDGETS:
                draw_code = self._custom_gen.generate_draw_code(wid)
                cpp += draw_code
            elif wid.class_name in self.NON_WIDGET_TYPES:
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name}) {var_name}->Draw(g);\n"
        
        cpp += f"    Widget::Draw(g);\n"

        if iface.user_code.draw_code:
            cpp += f"\n    // [[[USER_DRAW]]]\n"
            cpp += iface.user_code.draw_code
            cpp += "\n    // [[[END_USER_DRAW]]]\n"
        else:
            cpp += "\n    // [[[USER_DRAW]]]\n"
            cpp += "    // 在此添加自定义绘制代码\n"
            cpp += "    // [[[END_USER_DRAW]]]\n"

        cpp += "}\n\n"

        cpp += f"void {s.class_name}::Update()\n{{\n"
        cpp += f"    Widget::Update();\n"
        
        for wid in iface.widgets.values():
            if wid.class_name == "GameButton":
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name}) {var_name}->Update();\n"
        
        cpp += f"    MarkDirty();\n"

        if iface.user_code.update_code:
            cpp += f"\n    // [[[USER_UPDATE]]]\n"
            cpp += iface.user_code.update_code
            cpp += "\n    // [[[END_USER_UPDATE]]]\n"
        else:
            cpp += "\n    // [[[USER_UPDATE]]]\n"
            cpp += "    // 在此添加自定义更新代码\n"
            cpp += "    // [[[END_USER_UPDATE]]]\n"

        cpp += "}\n\n"

        if has_non_widget:
            cpp += self._generate_non_widget_mouse_handlers(iface, s.class_name)

        cpp += f"void {s.class_name}::AddedToManager(WidgetManager* theWidgetManager)\n{{\n"
        base_class_call = "Dialog" if is_dialog_type else "Widget"
        cpp += f"    {base_class_call}::AddedToManager(theWidgetManager);\n"
        for wid_id in iface.root_widget_ids:
            wid = iface.widgets.get(wid_id)
            if wid:
                var_name = self._get_var_name(wid)
                if self._is_widget_type(wid.class_name):
                    cpp += f"    AddWidget({var_name});\n"
        cpp += "}\n\n"

        cpp += f"void {s.class_name}::RemovedFromManager(WidgetManager* theWidgetManager)\n{{\n"
        for wid_id in iface.root_widget_ids:
            wid = iface.widgets.get(wid_id)
            if wid:
                var_name = self._get_var_name(wid)
                if self._is_widget_type(wid.class_name):
                    cpp += f"    RemoveWidget({var_name});\n"
        cpp += f"    {base_class_call}::RemovedFromManager(theWidgetManager);\n}}\n\n"

        for listener in listeners:
            if listener == "ButtonListener":
                cpp += f"void {s.class_name}::ButtonPress(int theId)\n{{\n    mApp->PlaySample(Sexy::SOUND_TAP);\n}}\n\n"
                cpp += self._generate_button_depress_handler_for_interface(iface, project)
            elif listener == "DialogListener":
                cpp += self._generate_dialog_button_handler_for_interface(iface, "DialogButtonPress")
            elif listener == "EditListener":
                cpp += self._generate_edit_handler_for_interface(iface)
            elif listener == "CheckboxListener":
                cpp += self._generate_checkbox_handler_for_interface(iface)
            elif listener == "SliderListener":
                cpp += self._generate_slider_handler_for_interface(iface)
            elif listener == "ListListener":
                cpp += self._generate_list_handler_for_interface(iface)
        
        if is_dialog_type and "ButtonListener" not in listeners:
            has_buttons = any(
                w.class_name in self.BUTTON_WIDGETS or w.class_name in self.NON_WIDGET_TYPES
                for w in iface.widgets.values()
            )
            if has_buttons:
                cpp += f"void {s.class_name}::ButtonPress(int theId)\n{{\n    mApp->PlaySample(Sexy::SOUND_TAP);\n}}\n\n"
                cpp += self._generate_button_depress_handler_for_interface(iface, project)

        if iface.user_code.functions:
            cpp += "\n// [[[USER_FUNCTIONS]]]\n"
            cpp += iface.user_code.functions
            cpp += "\n// [[[END_USER_FUNCTIONS]]]\n"
        else:
            cpp += "\n// [[[USER_FUNCTIONS]]]\n"
            cpp += "// 在此添加自定义函数实现\n"
            cpp += "// [[[END_USER_FUNCTIONS]]]\n"

        return cpp

    def generate_cpp(self, project: Project) -> str:
        iface = project.current_interface
        if iface:
            return self.generate_cpp_for_interface(iface, project)
        return ""

    def _generate_widget_init(self, widget: WidgetInstance, class_listeners: List[str]) -> str:
        if widget.class_name in self.SEXY_WIDGETS:
            return self._sexy_gen.generate_widget_init(widget, class_listeners)
        elif widget.class_name in self.PVZ_WIDGETS:
            return self._pvz_gen.generate_widget_init(widget, class_listeners)
        elif widget.class_name in self.CUSTOM_WIDGETS:
            return self._custom_gen.generate_widget_init(widget, class_listeners)
        else:
            var_name = self._get_var_name(widget)
            props = widget.properties
            lines = []
            lines.append(f"    {var_name} = new {widget.class_name}();\n")
            x = props.get("mX", 0)
            y = props.get("mY", 0)
            w = props.get("mWidth", 100)
            h = props.get("mHeight", 30)
            lines.append(f"    {var_name}->Resize({x}, {y}, {w}, {h});\n")
            return "".join(lines)

    def _get_interface_includes(self, iface: Interface, project: Project) -> str:
        includes = set()
        current_class = iface.settings.class_name
        
        for other_iface in project.interfaces.values():
            if other_iface.settings.class_name != current_class:
                includes.add(f'#include "{other_iface.settings.class_name}.h"')
        
        return "\n".join(includes)

    def _get_action_includes(self, iface: Interface) -> str:
        includes = set()
        
        ACTION_INCLUDES = {
            "show_store": '#include "StoreScreen.h"',
            "show_almanac": '#include "AlmanacDialog.h"',
        }
        
        for widget in iface.widgets.values():
            for event_type, actions in widget.event_actions.items():
                for action in actions:
                    if hasattr(action, 'predefined_id') and action.predefined_id in ACTION_INCLUDES:
                        includes.add(ACTION_INCLUDES[action.predefined_id])
        
        return "\n".join(sorted(includes))

    def _generate_non_widget_mouse_handlers(self, iface: Interface, class_name: str) -> str:
        cpp = f"void {class_name}::MouseMove(int x, int y)\n{{\n"
        cpp += f"    Widget::MouseMove(x, y);\n"
        for wid in iface.widgets.values():
            if wid.class_name == "GameButton":
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name} && x >= {var_name}->mX && x < {var_name}->mX + {var_name}->mWidth && y >= {var_name}->mY && y < {var_name}->mY + {var_name}->mHeight)\n"
                cpp += f"        {var_name}->mIsOver = true;\n"
                cpp += f"    else if ({var_name})\n"
                cpp += f"        {var_name}->mIsOver = false;\n"
        cpp += "}\n\n"
        
        cpp += f"void {class_name}::MouseDown(int x, int y, int theBtnNum, int theClickCount)\n{{\n"
        cpp += f"    Widget::MouseDown(x, y, theBtnNum, theClickCount);\n"
        for wid in iface.widgets.values():
            if wid.class_name == "GameButton":
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name} && {var_name}->mIsOver && !{var_name}->mDisabled)\n"
                cpp += f"        {var_name}->mIsDown = true;\n"
        cpp += "}\n\n"
        
        cpp += f"void {class_name}::MouseUp(int x, int y, int theBtnNum, int theClickCount)\n{{\n"
        cpp += f"    Widget::MouseUp(x, y, theBtnNum, theClickCount);\n"
        for wid in iface.widgets.values():
            if wid.class_name == "GameButton":
                var_name = self._get_var_name(wid)
                cpp += f"    if ({var_name} && {var_name}->mIsDown && {var_name}->mIsOver && !{var_name}->mDisabled)\n"
                cpp += f"        ButtonDepress({var_name}->mId);\n"
                cpp += f"    if ({var_name})\n"
                cpp += f"        {var_name}->mIsDown = false;\n"
        cpp += "}\n\n"
        return cpp

    def _generate_button_depress_handler_for_interface(self, iface: Interface, project: Project = None) -> str:
        s = iface.settings
        is_dialog_type = s.interface_type == "dialog"
        lines = [f"void {s.class_name}::ButtonDepress(int theId)"]
        lines.append("{")
        lines.append("    switch (theId) {")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.BUTTON_WIDGETS or widget.class_name == "GameButton":
                widget_id = widget.properties.get("mId", 0)
                handler_key = f"HANDLER_{widget.id}"
                var_name = self._get_var_name(widget)
                
                lines.append(f"    case {widget_id}:")
                lines.append("        {")
                lines.append(f"        // {widget.instance_name or widget.id}")
                
                user_handler = iface.user_code.event_handlers.get(handler_key, "")
                event_actions = widget.event_actions.get("ButtonDepress", [])
                
                if user_handler:
                    lines.append(f"        // [[[{handler_key}]]]")
                    lines.append(f"        {user_handler}")
                    lines.append(f"        // [[[END_{handler_key}]]]")
                elif event_actions:
                    lines.append(f"        // [[[{handler_key}]]]")
                    for action in event_actions:
                        if action.action_type == "predefined":
                            code = self._generate_predefined_action_code(action, is_dialog_type, project)
                            if code:
                                lines.append(f"        {code}")
                    lines.append(f"        // [[[END_{handler_key}]]]")
                else:
                    lines.append(f"        // [[[{handler_key}]]]")
                    lines.append(f"        // {var_name} 点击事件处理")
                    lines.append(f"        // [[[END_{handler_key}]]]")
                
                lines.append("        break;")
                lines.append("        }")
        
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n\n"

    def generate_csharp_for_interface(self, iface: Interface, project: Project) -> str:
        return self._csharp_gen.generate_full_class_cs(iface, project)

    def generate_csharp(self, project: Project) -> str:
        iface = project.current_interface
        if iface:
            return self.generate_csharp_for_interface(iface, project)
        return ""

    def generate_code(self, project: Project, language: str = None) -> Tuple[str, str]:
        lang = language or self._output_language
        if lang == "csharp":
            return (self.generate_csharp(project), "")
        else:
            return (self.generate_header(project), self.generate_cpp(project))

    def _generate_predefined_action_code(self, action, is_dialog_type: bool = True, project: Project = None) -> str:
        from core.predefined_actions import generate_action_code, get_action
        act = get_action(action.predefined_id)
        if not act:
            return ""
        
        action_id = action.predefined_id
        params = action.params
        
        if action_id == "close_current_dialog":
            if is_dialog_type:
                return "mApp->KillDialog(mId);"
            else:
                return "mWidgetManager->RemoveWidget(this);"
        
        if action_id == "close_current_widget":
            if is_dialog_type:
                return "mApp->KillDialog(mId);"
            else:
                return "mWidgetManager->RemoveWidget(this);"
        
        if action_id in ["open_project_interface", "switch_to_project_interface", "open_project_widget", "switch_to_project_widget"]:
            interface_class = params.get("interface_class", "")
            interface_id = params.get("interface_id", "")
            
            target_is_dialog = True
            if project and interface_class:
                for iface in project.interfaces.values():
                    if iface.settings.class_name == interface_class:
                        target_is_dialog = iface.settings.interface_type == "dialog"
                        break
            
            if action_id == "open_project_interface" or action_id == "open_project_widget":
                if target_is_dialog:
                    return f"mApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));"
                else:
                    return f"mWidgetManager->AddWidget(new {interface_class}(mApp));"
            else:
                if target_is_dialog:
                    if is_dialog_type:
                        return f"mApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));\n        mApp->KillDialog(mId);"
                    else:
                        return f"mApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));\n        mWidgetManager->RemoveWidget(this);"
                else:
                    if is_dialog_type:
                        return f"mApp->KillDialog(mId);\n        mWidgetManager->AddWidget(new {interface_class}(mApp));"
                    else:
                        return f"WidgetManager* wmgr = mWidgetManager;\n        wmgr->AddWidget(new {interface_class}(mApp));\n        wmgr->RemoveWidget(this);"
        
        return generate_action_code(action.predefined_id, params)

    def _generate_dialog_button_handler_for_interface(self, iface: Interface, method_name: str) -> str:
        s = iface.settings
        lines = [f"void {s.class_name}::{method_name}(int theDialogId, int theButtonId)"]
        lines.append("{")
        lines.append("    // [[[DIALOG_HANDLER]]]")
        lines.append("    // 对话框按钮事件处理")
        lines.append("    // [[[END_DIALOG_HANDLER]]]")
        lines.append("}")
        return "\n".join(lines) + "\n\n"

    def _generate_edit_handler_for_interface(self, iface: Interface) -> str:
        s = iface.settings
        lines = [f"void {s.class_name}::EditWidgetText(int theId, const std::string& theString)"]
        lines.append("{")
        lines.append("    switch (theId) {")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.EDIT_WIDGETS:
                widget_id = widget.properties.get("mId", 0)
                handler_key = f"EDIT_{widget_id}"
                var_name = self._get_var_name(widget)
                
                lines.append(f"    case {widget_id}:")
                lines.append(f"        // {widget.instance_name or widget.id}")
                lines.append(f"        // [[[{handler_key}]]]")
                lines.append(f"        // {var_name} 文本变化事件")
                lines.append(f"        // [[[END_{handler_key}]]]")
                lines.append("        break;")
        
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n\n"

    def _generate_checkbox_handler_for_interface(self, iface: Interface) -> str:
        s = iface.settings
        lines = [f"void {s.class_name}::CheckboxChecked(int theId, bool checked)"]
        lines.append("{")
        lines.append("    switch (theId) {")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.CHECKBOX_WIDGETS:
                widget_id = widget.properties.get("mId", 0)
                handler_key = f"CHECKBOX_{widget_id}"
                var_name = self._get_var_name(widget)
                
                lines.append(f"    case {widget_id}:")
                lines.append(f"        // {widget.instance_name or widget.id}")
                lines.append(f"        // [[[{handler_key}]]]")
                lines.append(f"        // {var_name} 复选框状态变化")
                lines.append(f"        // [[[END_{handler_key}]]]")
                lines.append("        break;")
        
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n\n"

    def _generate_slider_handler_for_interface(self, iface: Interface) -> str:
        s = iface.settings
        lines = [f"void {s.class_name}::SliderVal(int theId, double theVal)"]
        lines.append("{")
        lines.append("    switch (theId) {")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.SLIDER_WIDGETS:
                widget_id = widget.properties.get("mId", 0)
                handler_key = f"SLIDER_{widget_id}"
                var_name = self._get_var_name(widget)
                
                lines.append(f"    case {widget_id}:")
                lines.append(f"        // {widget.instance_name or widget.id}")
                lines.append(f"        // [[[{handler_key}]]]")
                lines.append(f"        // {var_name} 滑块值变化")
                lines.append(f"        // [[[END_{handler_key}]]]")
                lines.append("        break;")
        
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n\n"

    def _generate_list_handler_for_interface(self, iface: Interface) -> str:
        s = iface.settings
        lines = [f"void {s.class_name}::ListClicked(int theId, int theIndex, int theClickCount)"]
        lines.append("{")
        lines.append("    switch (theId) {")
        
        for widget in iface.widgets.values():
            if widget.class_name in self.LIST_WIDGETS:
                widget_id = widget.properties.get("mId", 0)
                handler_key = f"LIST_{widget_id}"
                var_name = self._get_var_name(widget)
                
                lines.append(f"    case {widget_id}:")
                lines.append(f"        // {widget.instance_name or widget.id}")
                lines.append(f"        // [[[{handler_key}]]]")
                lines.append(f"        // {var_name} 列表项点击")
                lines.append(f"        // [[[END_{handler_key}]]]")
                lines.append("        break;")
        
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n\n"
