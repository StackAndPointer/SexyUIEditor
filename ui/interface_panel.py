# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QInputDialog, QMessageBox, QMenu, QDialog, QFormLayout,
    QLineEdit, QComboBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from core.i18n import tr
from core.project import Project


class AddInterfaceDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._project = project
        self._result_name = ""
        self._result_type = "dialog"
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("interface.add_title", "Add Interface"))
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText(tr("interface.name_hint", "e.g., Settings, Help"))
        form.addRow(QLabel(tr("interface.name_prompt", "Interface name:")), self._name_edit)

        self._type_combo = QComboBox()
        self._type_combo.addItem(tr("interface.type_dialog", "Dialog (弹出界面)"), "dialog")
        self._type_combo.addItem(tr("interface.type_widget", "Widget (嵌入式界面)"), "widget")
        form.addRow(QLabel(tr("interface.type_prompt", "Interface type:")), self._type_combo)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton(tr("btn.ok", "OK"))
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, tr("error.title", "Error"), tr("interface.name_required", "Interface name is required"))
            return
        self._result_name = name
        self._result_type = self._type_combo.currentData()
        self.accept()

    def get_result(self):
        return self._result_name, self._result_type


class InterfacePanel(QWidget):
    interface_changed = pyqtSignal(str)
    interface_added = pyqtSignal(str)
    interface_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project: Project = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selection_changed)
        self._list.itemDoubleClicked.connect(self._on_rename)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._list)

        btn_layout = QHBoxLayout()
        self._add_btn = QPushButton(tr("interface.add", "Add"))
        self._add_btn.clicked.connect(self._on_add)
        self._remove_btn = QPushButton(tr("interface.remove", "Remove"))
        self._remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._remove_btn)
        layout.addLayout(btn_layout)

    def set_project(self, project: Project):
        self._project = project
        self._refresh()

    def _refresh(self):
        self._list.clear()
        if not self._project:
            return

        for iface_id, iface in self._project.interfaces.items():
            item = QListWidgetItem(iface.settings.name)
            item.setData(Qt.ItemDataRole.UserRole, iface_id)
            if iface_id == self._project.main_interface_id:
                item.setText(f"{iface.settings.name} ({tr('interface.main', 'Main')})")
            self._list.addItem(item)

            if iface_id == self._project._current_interface_id:
                self._list.setCurrentItem(item)

    def _on_selection_changed(self, row: int):
        if not self._project or row < 0:
            return

        item = self._list.item(row)
        if item:
            iface_id = item.data(Qt.ItemDataRole.UserRole)
            if iface_id != self._project._current_interface_id:
                self._project.set_current_interface(iface_id)
                self.interface_changed.emit(iface_id)

    def _on_add(self):
        if not self._project:
            return

        dlg = AddInterfaceDialog(self._project, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, iface_type = dlg.get_result()
            if name:
                iface = self._project.add_interface(name, interface_type=iface_type)
                self._refresh()
                self.interface_added.emit(iface.settings.id)

    def _on_remove(self):
        if not self._project:
            return

        row = self._list.currentRow()
        if row < 0:
            return

        item = self._list.item(row)
        if not item:
            return
            
        iface_id = item.data(Qt.ItemDataRole.UserRole)

        if iface_id == self._project.main_interface_id:
            QMessageBox.warning(
                self,
                tr("error.title", "Error"),
                tr("interface.cannot_remove_main", "Cannot remove main interface")
            )
            return

        ret = QMessageBox.question(
            self,
            tr("interface.confirm_remove", "Remove Interface"),
            tr("interface.confirm_remove_text", "Are you sure you want to remove this interface?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if ret == QMessageBox.StandardButton.Yes:
            self._project.remove_interface(iface_id)
            self._refresh()
            self.interface_removed.emit(iface_id)

    def _on_rename(self, item: QListWidgetItem):
        if not self._project:
            return

        iface_id = item.data(Qt.ItemDataRole.UserRole)
        iface = self._project.interfaces.get(iface_id)
        if not iface:
            return

        name, ok = QInputDialog.getText(
            self,
            tr("interface.rename", "Rename Interface"),
            tr("interface.name_prompt", "Interface name:"),
            text=iface.settings.name
        )

        if ok and name:
            iface.settings.name = name
            self._project.modified = True
            self._refresh()

    def _show_context_menu(self, pos: 'QPoint'):
        item = self._list.itemAt(pos)
        if not item:
            return

        iface_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)

        rename_action = menu.addAction(tr("interface.rename", "Rename"))
        rename_action.triggered.connect(lambda: self._on_rename(item))

        if iface_id != self._project.main_interface_id:
            set_main_action = menu.addAction(tr("interface.set_main", "Set as Main"))
            set_main_action.triggered.connect(lambda: self._set_as_main(iface_id))

        menu.exec(QCursor.pos())

    def _set_as_main(self, iface_id: str):
        if not self._project:
            return

        self._project.main_interface_id = iface_id
        self._project.modified = True
        self._refresh()

    def refresh_ui(self):
        self._refresh()
