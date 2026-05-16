# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from core.project import Project
from core.i18n import tr


class ObjectTree(QWidget):
    widget_selected = pyqtSignal(str)
    widget_deleted = pyqtSignal(str)

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabel(tr("objtree.title", "Objects"))
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.currentItemChanged.connect(self._on_item_changed)

        layout.addWidget(self._tree)
        self.setLayout(layout)

    def set_project(self, project: Project):
        self.project = project
        self.refresh()

    def refresh(self):
        self._tree.clear()
        for wid_id in self.project.root_widget_ids:
            self._add_widget_item(wid_id, self._tree)

        self._tree.expandAll()

    def select_widget(self, widget_id: str):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            found = self._find_item(item, widget_id)
            if found:
                self._tree.setCurrentItem(found)
                return

    def _add_widget_item(self, widget_id: str, parent):
        w = self.project.get_widget(widget_id)
        if not w:
            return

        label = f"{w.class_name} ({w.instance_name or w.id})"
        item = QTreeWidgetItem(parent, [label])
        item.setData(0, Qt.ItemDataRole.UserRole, widget_id)

        for child_id in w.children:
            self._add_widget_item(child_id, item)

    def _find_item(self, item: QTreeWidgetItem, widget_id: str) -> QTreeWidgetItem:
        if item.data(0, Qt.ItemDataRole.UserRole) == widget_id:
            return item
        for i in range(item.childCount()):
            found = self._find_item(item.child(i), widget_id)
            if found:
                return found
        return None

    def _on_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        if current:
            wid = current.data(0, Qt.ItemDataRole.UserRole)
            if wid:
                self.widget_selected.emit(wid)

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return

        wid = item.data(0, Qt.ItemDataRole.UserRole)
        if not wid:
            return

        menu = QMenu(self)
        delete_action = menu.addAction(tr("action.delete", "Delete"))
        action = menu.exec(self._tree.mapToGlobal(pos))

        if action == delete_action:
            self.widget_deleted.emit(wid)

    def refresh_ui(self):
        self._tree.setHeaderLabel(tr("objtree.title", "Objects"))
        self.refresh()
