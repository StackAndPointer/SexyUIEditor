# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from typing import List, Dict
from core.i18n import tr


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
        name=tr("action.close_dialog", "Close Dialog"),
        description=tr("action.close_dialog.desc", "Close the current dialog (calls Close method)"),
        category="dialog",
        code_template="Close();",
        required_params=[]
    ),
    "set_result_ok": PredefinedAction(
        id="set_result_ok",
        name=tr("action.set_result_ok", "Set Result OK"),
        description=tr("action.set_result_ok.desc", "Set dialog result to OK (Dialog::ID_OK)"),
        category="dialog",
        code_template="mResult = Dialog::ID_OK;",
        required_params=[]
    ),
    "set_result_cancel": PredefinedAction(
        id="set_result_cancel",
        name=tr("action.set_result_cancel", "Set Result Cancel"),
        description=tr("action.set_result_cancel.desc", "Set dialog result to Cancel (Dialog::ID_CANCEL)"),
        category="dialog",
        code_template="mResult = Dialog::ID_CANCEL;",
        required_params=[]
    ),
    "confirm_and_close": PredefinedAction(
        id="confirm_and_close",
        name=tr("action.confirm_and_close", "Confirm and Close"),
        description=tr("action.confirm_and_close.desc", "Set result to OK and close dialog"),
        category="dialog",
        code_template="mResult = Dialog::ID_OK;\nClose();",
        required_params=[]
    ),
    "cancel_and_close": PredefinedAction(
        id="cancel_and_close",
        name=tr("action.cancel_and_close", "Cancel and Close"),
        description=tr("action.cancel_and_close.desc", "Set result to Cancel and close dialog"),
        category="dialog",
        code_template="mResult = Dialog::ID_CANCEL;\nClose();",
        required_params=[]
    ),
    "set_custom_result": PredefinedAction(
        id="set_custom_result",
        name=tr("action.set_custom_result", "Set Custom Result"),
        description=tr("action.set_custom_result.desc", "Set a custom result value for the dialog"),
        category="dialog",
        code_template="mResult = {result_value};",
        required_params=["result_value"]
    ),
    "show_lawn_dialog": PredefinedAction(
        id="show_lawn_dialog",
        name=tr("action.show_lawn_dialog", "Show LawnDialog"),
        description=tr("action.show_lawn_dialog.desc", "Show a dialog with title, content and buttons (requires manual close)"),
        category="dialog",
        code_template="mApp->DoDialog({dialog_id}, {is_modal}, \"{header}\", \"{content}\", \"{footer}\", Dialog::{button_mode});",
        required_params=["dialog_id", "is_modal", "header", "content", "footer", "button_mode"]
    ),
    "show_confirm_dialog": PredefinedAction(
        id="show_confirm_dialog",
        name=tr("action.show_confirm_dialog", "Show Confirm Dialog (Wait)"),
        description=tr("action.show_confirm_dialog.desc", "Show a confirm/cancel dialog and wait for response, auto-closes on return"),
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"OK\", \"Cancel\", Dialog::BUTTONS_OK_CANCEL);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_yesno_dialog": PredefinedAction(
        id="show_yesno_dialog",
        name=tr("action.show_yesno_dialog", "Show Yes/No Dialog (Wait)"),
        description=tr("action.show_yesno_dialog.desc", "Show a yes/no dialog and wait for response, auto-closes on return"),
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"Yes\", \"No\", Dialog::BUTTONS_YES_NO);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_message_dialog": PredefinedAction(
        id="show_message_dialog",
        name=tr("action.show_message_dialog", "Show Message Dialog (Wait)"),
        description=tr("action.show_message_dialog.desc", "Show a message dialog and wait for click, auto-closes on return"),
        category="dialog",
        code_template="mApp->LawnMessageBox({dialog_id}, \"{header}\", \"{content}\", \"OK\", \"\", Dialog::BUTTONS_FOOTER);",
        required_params=["dialog_id", "header", "content"]
    ),
    "show_simple_dialog": PredefinedAction(
        id="show_simple_dialog",
        name=tr("action.show_simple_dialog", "Show Simple Dialog"),
        description=tr("action.show_simple_dialog.desc", "Show a simple dialog (does not wait, requires manual close)"),
        category="dialog",
        code_template="mApp->DoDialog({dialog_id}, true, \"{header}\", \"{content}\", \"\", Dialog::BUTTONS_NONE);",
        required_params=["dialog_id", "header", "content"]
    ),
    "play_sound": PredefinedAction(
        id="play_sound",
        name=tr("action.play_sound", "Play Sound"),
        description=tr("action.play_sound.desc", "Play the specified sound effect"),
        category="sound",
        code_template="mApp->PlaySample(Sexy::SOUND_{sound_id});",
        required_params=["sound_id"]
    ),
    "show_builtin_interface": PredefinedAction(
        id="show_builtin_interface",
        name=tr("action.show_builtin_interface", "Open Built-in Interface"),
        description=tr("action.show_builtin_interface.desc", "Open a game built-in interface (e.g. main menu, store)"),
        category="navigation",
        code_template="mApp->Show{interface_name}();",
        required_params=["interface_name"]
    ),
    "close_current_dialog": PredefinedAction(
        id="close_current_dialog",
        name=tr("action.close_current_dialog", "Close Current Dialog"),
        description=tr("action.close_current_dialog.desc", "Close the current Dialog interface (only for Dialog type)"),
        category="navigation",
        code_template="mApp->KillDialog(mId);",
        required_params=[]
    ),
    "close_current_widget": PredefinedAction(
        id="close_current_widget",
        name=tr("action.close_current_widget", "Close Current Widget"),
        description=tr("action.close_current_widget.desc", "Close the current Widget interface (only for Widget type)"),
        category="navigation",
        code_template="mWidgetManager->RemoveWidget(this);",
        required_params=[]
    ),
    "close_dialog_by_id": PredefinedAction(
        id="close_dialog_by_id",
        name=tr("action.close_dialog_by_id", "Close Interface by ID"),
        description=tr("action.close_dialog_by_id.desc", "Close a specific Dialog interface by ID"),
        category="navigation",
        code_template="mApp->KillDialog({interface_id});",
        required_params=["interface_id"]
    ),
    "open_project_interface": PredefinedAction(
        id="open_project_interface",
        name=tr("action.open_project_interface", "Open Project Interface"),
        description=tr("action.open_project_interface.desc", "Open another interface defined in the project (overlays on top)"),
        category="navigation",
        code_template="mApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));",
        required_params=["interface_class", "interface_id"]
    ),
    "switch_to_project_interface": PredefinedAction(
        id="switch_to_project_interface",
        name=tr("action.switch_to_project_interface", "Switch to Project Interface"),
        description=tr("action.switch_to_project_interface.desc", "Close current interface and open another project interface"),
        category="navigation",
        code_template="mApp->KillDialog(mId);\nmApp->AddDialog(new {interface_class}(mApp, {interface_id}, true, \"\", \"\", \"\", Dialog::BUTTONS_NONE));",
        required_params=["interface_class", "interface_id"]
    ),
    "open_project_widget": PredefinedAction(
        id="open_project_widget",
        name=tr("action.open_project_widget", "Open Project Widget"),
        description=tr("action.open_project_widget.desc", "Open a Widget type interface defined in the project (overlays on top)"),
        category="navigation",
        code_template="mWidgetManager->AddWidget(new {interface_class}(mApp));",
        required_params=["interface_class"]
    ),
    "switch_to_project_widget": PredefinedAction(
        id="switch_to_project_widget",
        name=tr("action.switch_to_project_widget", "Switch to Project Widget"),
        description=tr("action.switch_to_project_widget.desc", "Close current Widget and open another Widget interface"),
        category="navigation",
        code_template="mWidgetManager->RemoveWidget(this);\nmWidgetManager->AddWidget(new {interface_class}(mApp));",
        required_params=["interface_class"]
    ),
    "back_to_main_menu": PredefinedAction(
        id="back_to_main_menu",
        name=tr("action.back_to_main_menu", "Back to Main Menu"),
        description=tr("action.back_to_main_menu.desc", "Return to the game main menu"),
        category="navigation",
        code_template="mApp->DoBackToMain();",
        required_params=[]
    ),
    "show_game_board": PredefinedAction(
        id="show_game_board",
        name=tr("action.show_game_board", "Show Game Board"),
        description=tr("action.show_game_board.desc", "Show the game main interface (start game)"),
        category="navigation",
        code_template="mApp->ShowGameBoard();",
        required_params=[]
    ),
    "show_game_selector": PredefinedAction(
        id="show_game_selector",
        name=tr("action.show_game_selector", "Show Level Selector"),
        description=tr("action.show_game_selector.desc", "Show the level selection interface"),
        category="navigation",
        code_template="mApp->ShowGameSelector();",
        required_params=[]
    ),
    "show_store": PredefinedAction(
        id="show_store",
        name=tr("action.show_store", "Show Store"),
        description=tr("action.show_store.desc", "Show Crazy Dave's shop"),
        category="navigation",
        code_template="mApp->ShowStoreScreen()->WaitForResult(true);",
        required_params=[]
    ),
    "show_almanac": PredefinedAction(
        id="show_almanac",
        name=tr("action.show_almanac", "Show Almanac"),
        description=tr("action.show_almanac.desc", "Show the plant almanac"),
        category="navigation",
        code_template="mApp->DoAlmanacDialog()->WaitForResult(true);",
        required_params=[]
    ),
    "show_chooser": PredefinedAction(
        id="show_chooser",
        name=tr("action.show_chooser", "Show Chooser"),
        description=tr("action.show_chooser.desc", "Show the plant selection interface"),
        category="navigation",
        code_template="mApp->ShowSeedChooserScreen();",
        required_params=[]
    ),
    "show_options": PredefinedAction(
        id="show_options",
        name=tr("action.show_options", "Show Options"),
        description=tr("action.show_options.desc", "Show the options interface"),
        category="navigation",
        code_template="mApp->DoNewOptions(true);",
        required_params=[]
    ),
    "show_challenge": PredefinedAction(
        id="show_challenge",
        name=tr("action.show_challenge", "Show Challenge Mode"),
        description=tr("action.show_challenge.desc", "Show the challenge mode interface"),
        category="navigation",
        code_template="mApp->ShowChallengeScreen(0);",
        required_params=[]
    ),
    "show_credits": PredefinedAction(
        id="show_credits",
        name=tr("action.show_credits", "Show Credits"),
        description=tr("action.show_credits.desc", "Show the credits screen"),
        category="navigation",
        code_template="mApp->ShowCreditScreen();",
        required_params=[]
    ),
    "pause_game": PredefinedAction(
        id="pause_game",
        name=tr("action.pause_game", "Pause Game"),
        description=tr("action.pause_game.desc", "Show the pause dialog"),
        category="navigation",
        code_template="mApp->DoPauseDialog();",
        required_params=[]
    ),
    "set_widget_visible": PredefinedAction(
        id="set_widget_visible",
        name=tr("action.set_widget_visible", "Set Widget Visibility"),
        description=tr("action.set_widget_visible.desc", "Set the visibility state of a widget"),
        category="widget",
        code_template="{widget_name}->mVisible = {visible};",
        required_params=["widget_name", "visible"]
    ),
    "set_widget_text": PredefinedAction(
        id="set_widget_text",
        name=tr("action.set_widget_text", "Set Widget Text"),
        description=tr("action.set_widget_text.desc", "Set the text content of a widget"),
        category="widget",
        code_template='{widget_name}->SetLabel("{text}");',
        required_params=["widget_name", "text"]
    ),
    "toggle_checkbox": PredefinedAction(
        id="toggle_checkbox",
        name=tr("action.toggle_checkbox", "Toggle Checkbox"),
        description=tr("action.toggle_checkbox.desc", "Toggle the checked state of a checkbox"),
        category="widget",
        code_template="{widget_name}->mChecked = !{widget_name}->mChecked;",
        required_params=["widget_name"]
    ),
    "set_slider_value": PredefinedAction(
        id="set_slider_value",
        name=tr("action.set_slider_value", "Set Slider Value"),
        description=tr("action.set_slider_value.desc", "Set the current value of a slider"),
        category="widget",
        code_template="{widget_name}->mValue = {value};",
        required_params=["widget_name", "value"]
    ),
    "enable_widget": PredefinedAction(
        id="enable_widget",
        name=tr("action.enable_widget", "Enable Widget"),
        description=tr("action.enable_widget.desc", "Set the disabled state of a widget"),
        category="widget",
        code_template="{widget_name}->mDisabled = {disabled};",
        required_params=["widget_name", "disabled"]
    ),
    "add_list_item": PredefinedAction(
        id="add_list_item",
        name=tr("action.add_list_item", "Add List Item"),
        description=tr("action.add_list_item.desc", "Add a new item to a list"),
        category="widget",
        code_template='{widget_name}->AddLine("{text}", false);',
        required_params=["widget_name", "text"]
    ),
    "clear_list": PredefinedAction(
        id="clear_list",
        name=tr("action.clear_list", "Clear List"),
        description=tr("action.clear_list.desc", "Clear all items from a list"),
        category="widget",
        code_template="{widget_name}->Clear();",
        required_params=["widget_name"]
    ),
    "set_edit_text": PredefinedAction(
        id="set_edit_text",
        name=tr("action.set_edit_text", "Set Edit Text"),
        description=tr("action.set_edit_text.desc", "Set the text content of an edit widget"),
        category="widget",
        code_template='{widget_name}->SetText("{text}");',
        required_params=["widget_name", "text"]
    ),
    "log_message": PredefinedAction(
        id="log_message",
        name=tr("action.log_message", "Log Message"),
        description=tr("action.log_message.desc", "Output a debug log message"),
        category="debug",
        code_template='printf("{message}\\n");',
        required_params=["message"]
    ),

}


ACTION_CATEGORIES = {
    "dialog": tr("category.dialog", "Dialog"),
    "navigation": tr("category.navigation", "Navigation"),
    "sound": tr("category.sound", "Sound"),
    "widget": tr("category.widget", "Widget"),
    "debug": tr("category.debug", "Debug"),
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
