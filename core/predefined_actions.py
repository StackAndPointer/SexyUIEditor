# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class PredefinedAction:
    id: str
    name: str
    description: str
    category: str
    code_template: str
    required_params: List[str] = field(default_factory=list)


PREDEFINED_ACTIONS: Dict[str, PredefinedAction] = {
    "close_dialog": PredefinedAction(
        id="close_dialog",
        name="关闭对话框",
        description="关闭当前对话框（调用Close方法）",
        category="dialog",
        code_template="Close();",
        required_params=[]
    ),
    "set_result_ok": PredefinedAction(
        id="set_result_ok",
        name="设置结果为确认",
        description="设置对话框结果为OK（Dialog::ID_OK）",
        category="dialog",
        code_template="mResult = Dialog::ID_OK;",
        required_params=[]
    ),
    "set_result_cancel": PredefinedAction(
        id="set_result_cancel",
        name="设置结果为取消",
        description="设置对话框结果为Cancel（Dialog::ID_CANCEL）",
        category="dialog",
        code_template="mResult = Dialog::ID_CANCEL;",
        required_params=[]
    ),
    "confirm_and_close": PredefinedAction(
        id="confirm_and_close",
        name="确认并关闭",
        description="设置结果为OK并关闭对话框",
        category="dialog",
        code_template="mResult = Dialog::ID_OK;\nClose();",
        required_params=[]
    ),
    "cancel_and_close": PredefinedAction(
        id="cancel_and_close",
        name="取消并关闭",
        description="设置结果为Cancel并关闭对话框",
        category="dialog",
        code_template="mResult = Dialog::ID_CANCEL;\nClose();",
        required_params=[]
    ),
    "set_custom_result": PredefinedAction(
        id="set_custom_result",
        name="设置自定义结果",
        description="设置对话框的自定义结果值",
        category="dialog",
        code_template="mResult = {result_value};",
        required_params=["result_value"]
    ),
    "show_lawn_dialog": PredefinedAction(
        id="show_lawn_dialog",
        name="显示LawnDialog",
        description="显示一个带有标题、内容和按钮的对话框（需要手动处理关闭）",
        category="dialog",
        code_template="mApp->DoDialog({dialog_id}, {is_modal}, \"{header}\", \"{content}\", \"{footer}\", Dialog::{button_mode});",
        required_params=["dialog_id", "is_modal", "header", "content", "footer", "button_mode"]
    ),
    "show_confirm_dialog": PredefinedAction(
        id="show_confirm_dialog",
        name="显示确认对话框(等待结果)",
        description="显示一个确认/取消对话框并等待用户响应，返回后自动关闭",
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"OK\", \"Cancel\", Dialog::BUTTONS_OK_CANCEL);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_yesno_dialog": PredefinedAction(
        id="show_yesno_dialog",
        name="显示是/否对话框(等待结果)",
        description="显示一个是/否对话框并等待用户响应，返回后自动关闭",
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"Yes\", \"No\", Dialog::BUTTONS_YES_NO);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_message_dialog": PredefinedAction(
        id="show_message_dialog",
        name="显示消息对话框(等待结果)",
        description="显示一个消息对话框并等待用户点击，返回后自动关闭",
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"OK\", \"\", Dialog::BUTTONS_FOOTER);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_simple_dialog": PredefinedAction(
        id="show_simple_dialog",
        name="显示简单对话框",
        description="显示一个简单对话框（不等待结果，需要手动关闭）",
        category="dialog",
        code_template="mApp->DoDialog({dialog_id}, true, \"{header}\", \"{content}\", \"\", Dialog::BUTTONS_NONE);",
        required_params=["dialog_id", "header", "content"]
    ),
    "play_sound": PredefinedAction(
        id="play_sound",
        name="播放音效",
        description="播放指定的音效",
        category="sound",
        code_template="mApp->PlaySample(Sexy::SOUND_{sound_id});",
        required_params=["sound_id"]
    ),
    "show_builtin_interface": PredefinedAction(
        id="show_builtin_interface",
        name="打开游戏内置界面",
        description="打开游戏原有的内置界面（如主菜单、商店等）",
        category="navigation",
        code_template="mApp->Show{interface_name}();",
        required_params=["interface_name"]
    ),
    "close_current_dialog": PredefinedAction(
        id="close_current_dialog",
        name="关闭当前Dialog界面",
        description="关闭当前所在的Dialog界面（仅适用于Dialog类型界面）",
        category="navigation",
        code_template="mApp->KillDialog(mId);",
        required_params=[]
    ),
    "close_current_widget": PredefinedAction(
        id="close_current_widget",
        name="关闭当前Widget界面",
        description="关闭当前所在的Widget界面（仅适用于Widget类型界面）",
        category="navigation",
        code_template="mWidgetManager->RemoveWidget(this);",
        required_params=[]
    ),
    "close_dialog_by_id": PredefinedAction(
        id="close_dialog_by_id",
        name="关闭指定ID的界面",
        description="根据界面ID关闭指定的Dialog界面",
        category="navigation",
        code_template="mApp->KillDialog({interface_id});",
        required_params=["interface_id"]
    ),
    "open_project_interface": PredefinedAction(
        id="open_project_interface",
        name="打开项目界面",
        description="打开项目中定义的其他界面（会叠加显示）",
        category="navigation",
        code_template="mApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));",
        required_params=["interface_class", "interface_id"]
    ),
    "switch_to_project_interface": PredefinedAction(
        id="switch_to_project_interface",
        name="切换到项目界面",
        description="关闭当前界面并打开项目中的另一个界面",
        category="navigation",
        code_template="mApp->KillDialog(mId);\nmApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));",
        required_params=["interface_class", "interface_id"]
    ),
    "open_project_widget": PredefinedAction(
        id="open_project_widget",
        name="打开项目Widget界面",
        description="打开项目中定义的Widget类型界面（会叠加显示）",
        category="navigation",
        code_template="mWidgetManager->AddWidget(new {interface_class}(mApp));",
        required_params=["interface_class"]
    ),
    "switch_to_project_widget": PredefinedAction(
        id="switch_to_project_widget",
        name="切换到项目Widget界面",
        description="关闭当前Widget界面并打开另一个Widget界面",
        category="navigation",
        code_template="mWidgetManager->RemoveWidget(this);\nmWidgetManager->AddWidget(new {interface_class}(mApp));",
        required_params=["interface_class"]
    ),
    "back_to_main_menu": PredefinedAction(
        id="back_to_main_menu",
        name="返回主菜单",
        description="返回游戏主菜单",
        category="navigation",
        code_template="mApp->DoBackToMain();",
        required_params=[]
    ),
    "show_game_board": PredefinedAction(
        id="show_game_board",
        name="显示游戏界面",
        description="显示游戏主界面（开始游戏）",
        category="navigation",
        code_template="mApp->ShowGameBoard();",
        required_params=[]
    ),
    "show_game_selector": PredefinedAction(
        id="show_game_selector",
        name="显示关卡选择",
        description="显示关卡选择界面",
        category="navigation",
        code_template="mApp->ShowGameSelector();",
        required_params=[]
    ),
    "show_store": PredefinedAction(
        id="show_store",
        name="显示商店",
        description="显示疯狂戴夫的商店",
        category="navigation",
        code_template="mApp->ShowStoreScreen()->WaitForResult(true);",
        required_params=[]
    ),
    "show_almanac": PredefinedAction(
        id="show_almanac",
        name="显示图鉴",
        description="显示植物图鉴",
        category="navigation",
        code_template="mApp->DoAlmanacDialog()->WaitForResult(true);",
        required_params=[]
    ),
    "show_chooser": PredefinedAction(
        id="show_chooser",
        name="显示选择器",
        description="显示植物选择界面",
        category="navigation",
        code_template="mApp->ShowSeedChooserScreen();",
        required_params=[]
    ),
    "show_options": PredefinedAction(
        id="show_options",
        name="显示选项",
        description="显示选项界面",
        category="navigation",
        code_template="mApp->DoNewOptions(true);",
        required_params=[]
    ),
    "show_challenge": PredefinedAction(
        id="show_challenge",
        name="显示挑战模式",
        description="显示挑战模式界面",
        category="navigation",
        code_template="mApp->ShowChallengeScreen(0);",
        required_params=[]
    ),
    "show_credits": PredefinedAction(
        id="show_credits",
        name="显示制作人员",
        description="显示制作人员名单",
        category="navigation",
        code_template="mApp->ShowCreditScreen();",
        required_params=[]
    ),
    "pause_game": PredefinedAction(
        id="pause_game",
        name="暂停游戏",
        description="显示暂停对话框",
        category="navigation",
        code_template="mApp->DoPauseDialog();",
        required_params=[]
    ),
    "set_widget_visible": PredefinedAction(
        id="set_widget_visible",
        name="设置控件可见性",
        description="设置控件的可见状态",
        category="widget",
        code_template="{widget_name}->mVisible = {visible};",
        required_params=["widget_name", "visible"]
    ),
    "set_widget_text": PredefinedAction(
        id="set_widget_text",
        name="设置控件文本",
        description="设置控件的文本内容",
        category="widget",
        code_template='{widget_name}->SetLabel("{text}");',
        required_params=["widget_name", "text"]
    ),
    "toggle_checkbox": PredefinedAction(
        id="toggle_checkbox",
        name="切换复选框状态",
        description="切换复选框的选中状态",
        category="widget",
        code_template="{widget_name}->mChecked = !{widget_name}->mChecked;",
        required_params=["widget_name"]
    ),
    "set_slider_value": PredefinedAction(
        id="set_slider_value",
        name="设置滑块值",
        description="设置滑块的当前值",
        category="widget",
        code_template="{widget_name}->mValue = {value};",
        required_params=["widget_name", "value"]
    ),
    "enable_widget": PredefinedAction(
        id="enable_widget",
        name="启用控件",
        description="设置控件的禁用状态",
        category="widget",
        code_template="{widget_name}->mDisabled = {disabled};",
        required_params=["widget_name", "disabled"]
    ),
    "add_list_item": PredefinedAction(
        id="add_list_item",
        name="添加列表项",
        description="向列表添加新项",
        category="widget",
        code_template='{widget_name}->AddLine("{text}", false);',
        required_params=["widget_name", "text"]
    ),
    "clear_list": PredefinedAction(
        id="clear_list",
        name="清空列表",
        description="清空列表中的所有项",
        category="widget",
        code_template="{widget_name}->Clear();",
        required_params=["widget_name"]
    ),
    "set_edit_text": PredefinedAction(
        id="set_edit_text",
        name="设置输入框文本",
        description="设置输入框的文本内容",
        category="widget",
        code_template='{widget_name}->SetText("{text}");',
        required_params=["widget_name", "text"]
    ),
    "log_message": PredefinedAction(
        id="log_message",
        name="输出日志",
        description="输出调试日志信息",
        category="debug",
        code_template='printf("{message}\\n");',
        required_params=["message"]
    ),

}


ACTION_CATEGORIES = {
    "dialog": "对话框操作",
    "navigation": "界面导航",
    "sound": "音效播放",
    "widget": "控件操作",
    "debug": "调试",
}

LEGACY_ACTION_ID_MAP = {
    "show_interface": "show_builtin_interface",
    "close_interface": "close_current_dialog",
    "close_interface_by_id": "close_dialog_by_id",
    "add_dialog": "open_project_interface",
    "show_project_interface": "open_project_interface",
    "close_and_show_project": "switch_to_project_interface",
    "accept_dialog": "confirm_and_close",
    "cancel_dialog": "cancel_and_close",
}


def get_actions_by_category(category: str) -> List[PredefinedAction]:
    return [a for a in PREDEFINED_ACTIONS.values() if a.category == category]


def get_all_categories() -> Dict[str, str]:
    return ACTION_CATEGORIES


def get_action(action_id: str) -> PredefinedAction:
    if action_id in LEGACY_ACTION_ID_MAP:
        action_id = LEGACY_ACTION_ID_MAP[action_id]
    return PREDEFINED_ACTIONS.get(action_id)


def generate_action_code(action_id: str, params: Dict[str, str]) -> str:
    action = get_action(action_id)
    if not action:
        return ""
    
    code = action.code_template
    for param, value in params.items():
        code = code.replace(f"{{{param}}}", value)
    
    return code
