# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMenu, QComboBox, QLineEdit, QFormLayout,
    QWidget, QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
from core.i18n import tr
from core.project import WidgetInstance, EventAction, Project
from core.predefined_actions import (
    PREDEFINED_ACTIONS, ACTION_CATEGORIES, get_action, generate_action_code
)


def _calculate_interface_id(class_name: str) -> int:
    return hash(class_name) % 10000 + 1000


class ActionParamDialog(QDialog):
    def __init__(self, action_id: str, project: Project, parent=None, existing_params: dict = None):
        super().__init__(parent)
        self._action = get_action(action_id)
        self._project = project
        self._existing_params = existing_params or {}
        self._param_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self._action.name if self._action else tr("event.config", "Configure Action"))
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        if not self._action:
            layout.addWidget(QLabel(tr("event.action_not_found", "Action not found")))
            return

        title = QLabel(f"<b>{self._action.name}</b>")
        layout.addWidget(title)

        desc = QLabel(self._action.description)
        desc.setStyleSheet("color: #888;")
        layout.addWidget(desc)

        form = QFormLayout()

        for param in self._action.required_params:
            widget = self._create_param_widget(param)
            if widget:
                label = QLabel(self._get_param_label(param))
                form.addRow(label, widget)
                self._param_widgets[param] = widget

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(tr("btn.ok", "OK"))
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _create_param_widget(self, param: str) -> QWidget:
        existing = self._existing_params.get(param, "")
        
        if param == "sound_id":
            combo = QComboBox()
            combo.addItems([
                "TAP", "TAP2", "SHOVEL", "SEEDLIFT",
                "PLANT", "PLANT2", "SPLAT", "SHOOT",
                "BUTTONCLICK", "CHIME", "MONEYFALL", "GENTLEMEN"
            ])
            combo.setEditable(True)
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "interface_name":
            combo = QComboBox()
            combo.addItems([
                "GameBoard", "StoreScreen", "Almanac", 
                "SeedChooserScreen", "OptionsScreen", "MainMenu"
            ])
            combo.setEditable(True)
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "interface_class":
            combo = QComboBox()
            for iface in self._project.interfaces.values():
                combo.addItem(f"{iface.settings.class_name} ({iface.settings.name})")
                combo.setItemData(combo.count() - 1, iface.settings.class_name)
            combo.currentIndexChanged.connect(self._on_interface_class_index_changed)
            combo.setEditable(False)
            if existing:
                for i in range(combo.count()):
                    if combo.itemData(i) == existing:
                        combo.setCurrentIndex(i)
                        break
            elif combo.count() > 0:
                combo.setCurrentIndex(0)
                QTimer.singleShot(0, lambda: self._on_interface_class_index_changed(0))
            return combo

        elif param == "interface_id":
            edit = QLineEdit()
            edit.setReadOnly(True)
            edit.setPlaceholderText(tr("param.interface_id_hint", "Auto-filled when interface selected"))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "dialog_class":
            combo = QComboBox()
            for iface in self._project.interfaces.values():
                combo.addItem(iface.settings.class_name)
            combo.setEditable(True)
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "dialog_id":
            edit = QLineEdit()
            edit.setPlaceholderText(tr("param.dialog_id_hint", "e.g., 1001, Dialogs::DIALOG_CUSTOM"))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "is_modal":
            combo = QComboBox()
            combo.addItems(["true", "false"])
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "header":
            edit = QLineEdit()
            edit.setPlaceholderText(tr("param.header_hint", "Dialog header/title"))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "content":
            edit = QLineEdit()
            edit.setPlaceholderText(tr("param.content_hint", "Dialog content text"))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "footer":
            edit = QLineEdit()
            edit.setPlaceholderText(tr("param.footer_hint", "Dialog footer text (optional)"))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "button_mode":
            combo = QComboBox()
            combo.addItems([
                "BUTTONS_NONE",
                "BUTTONS_YES_NO",
                "BUTTONS_OK_CANCEL",
                "BUTTONS_FOOTER"
            ])
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "widget_name":
            combo = QComboBox()
            iface = self._project.current_interface
            if iface:
                combo.addItems([
                    w.instance_name for w in iface.widgets.values()
                    if w.instance_name
                ])
            combo.setEditable(True)
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "visible":
            combo = QComboBox()
            combo.addItems(["true", "false"])
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "disabled":
            combo = QComboBox()
            combo.addItems(["false", "true"])
            if existing:
                combo.setCurrentText(existing)
            return combo

        elif param == "text" or param == "message":
            edit = QLineEdit()
            edit.setPlaceholderText(tr("param.text_hint", "Enter text..."))
            if existing:
                edit.setText(existing)
            return edit

        elif param == "value":
            edit = QLineEdit()
            edit.setPlaceholderText("0.0")
            if existing:
                edit.setText(existing)
            return edit

        elif param == "result_value":
            combo = QComboBox()
            combo.addItems([
                "Dialog::ID_OK",
                "Dialog::ID_CANCEL",
                "Dialog::ID_YES",
                "Dialog::ID_NO",
                "1000",
                "1001",
                "0"
            ])
            combo.setEditable(True)
            if existing:
                combo.setCurrentText(existing)
            return combo

        edit = QLineEdit()
        if existing:
            edit.setText(existing)
        return edit

    def _on_interface_class_index_changed(self, index: int):
        if "interface_id" in self._param_widgets and "interface_class" in self._param_widgets:
            combo = self._param_widgets["interface_class"]
            class_name = combo.itemData(index)
            if class_name:
                self._param_widgets["interface_id"].setText(f"{class_name}::INTERFACE_ID")
            else:
                self._param_widgets["interface_id"].clear()

    def _get_param_label(self, param: str) -> str:
        labels = {
            "sound_id": tr("param.sound_id", "Sound ID"),
            "interface_name": tr("param.interface_name", "Interface Name"),
            "interface_class": tr("param.interface_class", "Interface Class"),
            "interface_id": tr("param.interface_id", "Interface ID"),
            "dialog_class": tr("param.dialog_class", "Dialog Class"),
            "dialog_id": tr("param.dialog_id", "Dialog ID"),
            "is_modal": tr("param.is_modal", "Modal"),
            "header": tr("param.header", "Header"),
            "content": tr("param.content", "Content"),
            "footer": tr("param.footer", "Footer"),
            "button_mode": tr("param.button_mode", "Button Mode"),
            "widget_name": tr("param.widget_name", "Widget Name"),
            "visible": tr("param.visible", "Visible"),
            "disabled": tr("param.disabled", "Disabled"),
            "text": tr("param.text", "Text"),
            "message": tr("param.message", "Message"),
            "value": tr("param.value", "Value"),
            "result_value": tr("param.result_value", "Result Value"),
        }
        return labels.get(param, param)

    def get_params(self) -> dict:
        result = {}
        for param, widget in self._param_widgets.items():
            if param == "interface_class":
                index = widget.currentIndex()
                class_name = widget.itemData(index)
                result[param] = class_name if class_name else widget.currentText()
            elif hasattr(widget, 'currentText'):
                result[param] = widget.currentText()
            elif hasattr(widget, 'text'):
                result[param] = widget.text()
        return result


class EventConfigDialog(QDialog):
    def __init__(self, widget: WidgetInstance, event_name: str, project: Project, parent=None):
        super().__init__(parent)
        self._widget = widget
        self._event_name = event_name
        self._project = project
        self._actions = list(widget.event_actions.get(event_name, []))
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("event.config_title", "Configure Event: {}").format(self._event_name))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)

        info_label = QLabel(f"{tr('event.widget', 'Widget')}: {self._widget.instance_name or self._widget.id}")
        info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(info_label)

        event_label = QLabel(f"{tr('event.event', 'Event')}: {self._event_name}")
        layout.addWidget(event_label)

        self._action_list = QListWidget()
        self._action_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._action_list.currentRowChanged.connect(self._on_selection_changed)
        for action in self._actions:
            self._add_action_item(action)
        layout.addWidget(self._action_list)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton(tr("event.add_action", "Add Action"))
        add_btn.clicked.connect(self._show_action_menu)
        btn_layout.addWidget(add_btn)

        self._edit_btn = QPushButton(tr("event.edit", "Edit"))
        self._edit_btn.clicked.connect(self._edit_selected)
        self._edit_btn.setEnabled(False)
        btn_layout.addWidget(self._edit_btn)

        self._remove_btn = QPushButton(tr("event.remove", "Remove"))
        self._remove_btn.clicked.connect(self._remove_selected)
        self._remove_btn.setEnabled(False)
        btn_layout.addWidget(self._remove_btn)

        layout.addLayout(btn_layout)

        dialog_btn_layout = QHBoxLayout()
        ok_btn = QPushButton(tr("btn.ok", "OK"))
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        dialog_btn_layout.addWidget(ok_btn)
        dialog_btn_layout.addWidget(cancel_btn)
        layout.addLayout(dialog_btn_layout)

    def _show_action_menu(self):
        menu = QMenu(self)

        for cat_id, cat_name in ACTION_CATEGORIES.items():
            cat_menu = menu.addMenu(cat_name)
            for action_id, action in PREDEFINED_ACTIONS.items():
                if action.category == cat_id:
                    act = cat_menu.addAction(action.name)
                    act.triggered.connect(
                        lambda checked, a=action: self._add_action(a)
                    )

        menu.exec(QCursor.pos())

    def _add_action(self, action):
        if action.required_params:
            dlg = ActionParamDialog(action.id, self._project, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                params = dlg.get_params()
                event_action = EventAction(
                    action_type="predefined",
                    predefined_id=action.id,
                    params=params
                )
                self._actions.append(event_action)
                self._add_action_item(event_action)
        else:
            event_action = EventAction(
                action_type="predefined",
                predefined_id=action.id
            )
            self._actions.append(event_action)
            self._add_action_item(event_action)

    def _add_action_item(self, action: EventAction):
        action_def = get_action(action.predefined_id)
        if action_def:
            display_text = action_def.name
            if action.params:
                param_str = ", ".join(f"{k}={v}" for k, v in action.params.items())
                display_text += f" ({param_str})"
        else:
            display_text = action.predefined_id

        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, action)
        self._action_list.addItem(item)

    def _on_selection_changed(self, row: int):
        has_selection = row >= 0
        self._edit_btn.setEnabled(has_selection)
        self._remove_btn.setEnabled(has_selection)

    def _edit_selected(self):
        row = self._action_list.currentRow()
        if row < 0:
            return

        action = self._actions[row]
        action_def = get_action(action.predefined_id)
        if not action_def or not action_def.required_params:
            return

        dlg = ActionParamDialog(action.predefined_id, self._project, self, action.params)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            action.params = dlg.get_params()
            self._action_list.takeItem(row)
            self._add_action_item(action)
            self._action_list.setCurrentRow(self._action_list.count() - 1)

    def _remove_selected(self):
        row = self._action_list.currentRow()
        if row < 0:
            return

        del self._actions[row]
        self._action_list.takeItem(row)

    def _on_ok(self):
        if self._event_name not in self._widget.event_actions:
            self._widget.event_actions[self._event_name] = []
        self._widget.event_actions[self._event_name] = self._actions.copy()
        self._project.modified = True
        self.accept()

    def get_actions(self) -> list:
        return self._actions.copy()
