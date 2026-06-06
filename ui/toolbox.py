# -*- coding: utf-8 -*-
from core.qt_compat import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMenu, Qt,
    Signal, QMimeData, QDrag, QAction
)
from core.component_registry import ComponentRegistry
from core.i18n import tr
from core.extension_manager import ExtensionManager


_CATEGORY_ICONS = {
    "base": "📦",
    "basic": "🧩",
    "container": "📋",
    "pvz": "🌻",
    "extension": "🔧",
}


class ComponentToolbox(QWidget):
    widget_added = Signal(str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registry = ComponentRegistry.instance()
        self._ext_manager = ExtensionManager.instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self._add_btn = QPushButton("+")
        self._add_btn.setMaximumWidth(30)
        self._add_btn.setToolTip(tr("ext.add_custom", "Add custom component"))
        self._add_btn.clicked.connect(self._show_add_menu)
        header_layout.addWidget(self._add_btn)
        
        layout.addLayout(header_layout)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabel(tr("toolbox.title", "Components"))
        self._tree.setDragEnabled(True)
        self._tree.setDragDropMode(QTreeWidget.DragDropMode.DragOnly)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self._tree.header().setStretchLastSection(True)
        self._tree.setIndentation(16)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)

        self._populate()

        layout.addWidget(self._tree)
        self.setLayout(layout)

    def _show_add_menu(self):
        menu = QMenu(self)
        
        add_new_action = QAction(tr("ext.new_component", "New Component"), self)
        add_new_action.triggered.connect(self._add_new_component)
        menu.addAction(add_new_action)
        
        menu.exec(self._add_btn.mapToGlobal(self._add_btn.rect().bottomLeft()))

    def _add_new_component(self):
        from ui.custom_component_dialog import CustomComponentDialog
        platform = self._ext_manager._current_platform
        dlg = CustomComponentDialog(platform=platform, parent=self)
        if dlg.exec() == CustomComponentDialog.DialogCode.Accepted:
            self._populate()

    def _show_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        
        class_name = item.data(0, Qt.ItemDataRole.UserRole)
        if not class_name:
            return
        
        platform = self._ext_manager._current_platform
        ext_def = self._ext_manager.get_extension(class_name, platform)
        if not ext_def:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction(tr("ext.edit_component", "Edit Component"), self)
        edit_action.triggered.connect(lambda: self._edit_component(class_name, platform))
        menu.addAction(edit_action)
        
        delete_action = QAction(tr("ext.delete_component", "Delete Component"), self)
        delete_action.triggered.connect(lambda: self._delete_component(class_name, platform))
        menu.addAction(delete_action)
        
        menu.exec(self._tree.mapToGlobal(pos))

    def _edit_component(self, class_name: str, platform: str):
        from ui.custom_component_dialog import CustomComponentDialog
        dlg = CustomComponentDialog(class_name, platform=platform, parent=self)
        if dlg.exec() == CustomComponentDialog.DialogCode.Accepted:
            self._populate()

    def _delete_component(self, class_name: str, platform: str):
        from core.qt_compat import QMessageBox
        reply = QMessageBox.question(
            self, tr("ext.delete_title", "Delete Component"),
            tr("ext.delete_confirm", "Are you sure you want to delete '{}'?").format(class_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ext_manager.delete_extension(class_name, platform)
            self._populate()

    def _populate(self):
        self._tree.clear()
        cats = self._registry.categories()

        cat_order = ["base", "basic", "container", "pvz", "extension"]
        for cat_key in cat_order:
            if cat_key not in cats:
                continue
            icon = _CATEGORY_ICONS.get(cat_key, "📁")

            cat_labels = {
                "base": tr("cat.base", "Base Widgets"),
                "basic": tr("cat.basic", "Basic Controls"),
                "container": tr("cat.container", "Containers"),
                "pvz": tr("cat.pvz", "PVZ Components"),
                "extension": tr("cat.extension", "Extension"),
            }
            cat_label = cat_labels.get(cat_key, cat_key)

            cat_item = QTreeWidgetItem(self._tree, [f"{icon} {cat_label}"])
            cat_item.setExpanded(True)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)

            for cdef in cats[cat_key]:
                pvz_tag = " [PVZ]" if cdef.is_pvz else ""
                display_name = tr(f"widget.{cdef.class_name}", cdef.display_name)
                item_text = f"  {display_name}{pvz_tag}"
                child = QTreeWidgetItem(cat_item, [item_text])
                child.setData(0, Qt.ItemDataRole.UserRole, cdef.class_name)
                child.setToolTip(0, tr(f"widget.{cdef.class_name}.desc", cdef.description))

        self._tree.startDrag = self._start_drag

    def _start_drag(self, supportedActions):
        item = self._tree.currentItem()
        if not item:
            return
        class_name = item.data(0, Qt.ItemDataRole.UserRole)
        if not class_name:
            return

        mime_data = QMimeData()
        mime_data.setText(class_name)

        drag = QDrag(self._tree)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

    def refresh_ui(self):
        self._tree.setHeaderLabel(tr("toolbox.title", "Components"))
        self._populate()
