# -*- coding: utf-8 -*-
import os
import json
import uuid
from core.qt_compat import (
    QMainWindow, QDockWidget, QToolBar, QFileDialog,
    QStatusBar, QMessageBox, QSplitter, QTabWidget, QLabel, QLineEdit, QMenu, QComboBox,
    Qt, QSize, QSettings, QAction, QIcon, QKeySequence, QDragEnterEvent, QDropEvent, QActionGroup
)
from core.i18n import tr, I18nManager
from core.project import Project
from core.undo_manager import UndoManager
from core.resource_manager import ResourceManager
from core.code_generator import CodeGenerator
from core.code_sync import CodeSyncManager
from core.net_resources import get_net_resource_manager
from core.extension_manager import ExtensionManager
from ui.canvas import DesignCanvas
from ui.toolbox import ComponentToolbox
from ui.property_panel import PropertyPanel
from ui.object_tree import ObjectTree
from ui.resource_dialog import ResourceDialog
from ui.preview_window import PreviewWindow
from ui.code_view import CodeViewDialog
from ui.interface_panel import InterfacePanel
from ui.dark_titlebar import set_transparent_titlebar


class MainWindow(QMainWindow):
    MAX_HISTORY = 10

    def __init__(self):
        super().__init__()
        self._settings = QSettings("SexyUIEditor", "SexyUIEditor")
        self._apply_dark_theme()
        self._set_dark_titlebar()
        self.setAcceptDrops(True)
        self._set_window_icon()
        self.project = Project()
        self.undo_mgr = UndoManager.instance()
        self.res_mgr = ResourceManager.instance()
        self.code_gen = CodeGenerator.instance()
        self._widget_counter = {}
        
        net_content_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Content")
        if os.path.exists(net_content_path):
            self.net_res_mgr = get_net_resource_manager(net_content_path)
            self.net_res_mgr.load()
        else:
            self.net_res_mgr = get_net_resource_manager()
        
        self._ext_manager = ExtensionManager.instance()
        self._ext_manager.set_base_dir(os.path.dirname(os.path.dirname(__file__)))

        self._setup_ui()
        self._setup_toolbar()
        self._setup_menus()
        self._setup_statusbar()
        self._connect_signals()
        self._update_title()

    def _setup_ui(self):
        self.setWindowTitle(tr("app.title", "SexyUI Editor"))
        self.resize(1400, 900)

        self.interface_panel = InterfacePanel(self)
        iface_dock = QDockWidget(tr("dock.interfaces", "Interfaces"), self)
        iface_dock.setWidget(self.interface_panel)
        iface_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        iface_dock.setMinimumWidth(160)
        iface_dock.setMaximumWidth(250)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, iface_dock)

        self.object_tree = ObjectTree(self.project, self)
        tree_dock = QDockWidget(tr("dock.object_tree", "Object Tree"), self)
        tree_dock.setWidget(self.object_tree)
        tree_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        tree_dock.setMinimumWidth(160)
        tree_dock.setMaximumWidth(250)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tree_dock)

        self.toolbox = ComponentToolbox(self)
        toolbox_dock = QDockWidget(tr("dock.toolbox", "Toolbox"), self)
        toolbox_dock.setWidget(self.toolbox)
        toolbox_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        toolbox_dock.setMinimumWidth(160)
        toolbox_dock.setMaximumWidth(250)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, toolbox_dock)

        self.canvas = DesignCanvas(self.project, self)
        self.setCentralWidget(self.canvas)

        self.property_panel = PropertyPanel(self.project, self)
        self.property_panel.setMinimumWidth(280)
        prop_dock = QDockWidget(tr("dock.properties", "Properties"), self)
        prop_dock.setWidget(self.property_panel)
        prop_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        prop_dock.setMinimumWidth(300)
        prop_dock.setMaximumWidth(450)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, prop_dock)

    def _setup_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(tr("menu.file", "&File"))
        self._add_action(file_menu, tr("action.new", "New"), self._on_new, QKeySequence.StandardKey.New)
        self._add_action(file_menu, tr("action.open", "Open..."), self._on_open, QKeySequence.StandardKey.Open)
        self._add_action(file_menu, tr("action.save", "Save"), self._on_save, QKeySequence.StandardKey.Save)
        self._add_action(file_menu, tr("action.save_as", "Save As..."), self._on_save_as, QKeySequence("Ctrl+Shift+S"))
        file_menu.addSeparator()
        self._add_action(file_menu, tr("action.exit", "Exit"), self._on_exit, QKeySequence("Alt+F4"))

        edit_menu = menubar.addMenu(tr("menu.edit", "&Edit"))
        self.undo_action = self._add_action(
            edit_menu, tr("action.undo", "Undo"), self._on_undo, QKeySequence.StandardKey.Undo)
        self.redo_action = self._add_action(
            edit_menu, tr("action.redo", "Redo"), self._on_redo, QKeySequence.StandardKey.Redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("action.delete", "Delete"), self._on_delete, QKeySequence.StandardKey.Delete)
        edit_menu.addSeparator()
        self._add_action(edit_menu, tr("action.settings", "Project Settings..."), self._on_project_settings)

        view_menu = menubar.addMenu(tr("menu.view", "&View"))
        self._add_action(view_menu, tr("action.preview", "Preview"), self._on_preview, QKeySequence("F5"))
        self._add_action(view_menu, tr("action.code", "View Code"), self._on_view_code, QKeySequence("F6"))
        view_menu.addSeparator()
        self._add_action(view_menu, tr("action.export_all", "Export All Interfaces..."), self._on_export_all_interfaces)
        self._add_action(view_menu, tr("action.import_interfaces", "Import Interfaces..."), self._on_import_interfaces)

        resource_menu = menubar.addMenu(tr("menu.resource", "&Resource"))
        self._add_action(resource_menu, tr("action.manage_res", "Manage Resources..."), self._on_manage_resources)

        settings_menu = menubar.addMenu(tr("menu.settings", "&Settings"))
        lang_menu = settings_menu.addMenu(tr("action.language", "Language"))
        self._lang_action_group = QActionGroup(self)
        self._lang_action_group.setExclusive(True)
        i18n = I18nManager.instance()
        for locale_code in i18n.get_available_locales():
            action = lang_menu.addAction(i18n.get_locale_name(locale_code))
            action.setCheckable(True)
            action.setChecked(locale_code == i18n.current_locale)
            action.triggered.connect(lambda checked, lc=locale_code: self._on_language_changed(lc))
            self._lang_action_group.addAction(action)
        settings_menu.addSeparator()
        self._add_action(settings_menu, tr("action.associate_files", "Associate File Types..."), self._on_associate_files)

        sync_menu = menubar.addMenu(tr("menu.sync", "&Sync"))
        self._add_action(sync_menu, tr("action.sync_from_source", "Sync from Source"), self._on_sync_from_source, QKeySequence("F7"))
        self._add_action(sync_menu, tr("action.generate_source", "Generate Source..."), self._on_generate_source, QKeySequence("F8"))
        self._add_action(sync_menu, tr("action.link_source", "Link Source Files..."), self._on_link_source)
        sync_menu.addSeparator()
        self._auto_sync_action = QAction(tr("action.auto_sync", "Auto Sync"), self)
        self._auto_sync_action.setCheckable(True)
        self._auto_sync_action.setChecked(True)
        sync_menu.addAction(self._auto_sync_action)

        help_menu = menubar.addMenu(tr("menu.help", "&Help"))
        self._add_action(help_menu, tr("action.about", "About..."), self._on_about)

        self._update_undo_redo_actions()

    def _setup_toolbar(self):
        toolbar = QToolBar(tr("toolbar.main", "Main Toolbar"))
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addAction(self._make_action(tr("action.new", "New"), self._on_new))
        toolbar.addAction(self._make_action(tr("action.open", "Open"), self._on_open))
        toolbar.addAction(self._make_action(tr("action.save", "Save"), self._on_save))
        toolbar.addSeparator()
        self.toolbar_undo = toolbar.addAction(tr("action.undo", "Undo"), self._on_undo)
        self.toolbar_redo = toolbar.addAction(tr("action.redo", "Redo"), self._on_redo)
        toolbar.addSeparator()
        toolbar.addAction(self._make_action(tr("action.preview", "Preview"), self._on_preview))
        toolbar.addAction(self._make_action(tr("action.code", "Code"), self._on_view_code))
        toolbar.addSeparator()

        toolbar.addWidget(QLabel(tr("settings.class_name", "Class Name:") + " "))
        self._class_name_edit = QLineEdit(self._get_current_class_name())
        self._class_name_edit.setMaximumWidth(150)
        self._class_name_edit.textChanged.connect(self._on_class_name_changed)
        toolbar.addWidget(self._class_name_edit)
        toolbar.addSeparator()

        toolbar.addWidget(QLabel(tr("settings.output_lang", "Output:") + " "))
        self._output_lang_combo = QComboBox()
        self._output_lang_combo.addItem("C++", "cpp")
        self._output_lang_combo.addItem("C#", "csharp")
        self._output_lang_combo.setCurrentIndex(0)
        self._output_lang_combo.currentIndexChanged.connect(self._on_output_lang_changed)
        toolbar.addWidget(self._output_lang_combo)
        
        self._cpp_structure_combo = QComboBox()
        self._cpp_structure_combo.addItem("QE", "qe")
        self._cpp_structure_combo.addItem("Portable", "portable")
        self._cpp_structure_combo.setCurrentIndex(0)
        self._cpp_structure_combo.currentIndexChanged.connect(self._on_cpp_structure_changed)
        toolbar.addWidget(self._cpp_structure_combo)
        
        toolbar.addSeparator()

        toolbar.addAction(self._make_action(tr("action.settings", "Settings"), self._on_project_settings))

    def _get_current_class_name(self) -> str:
        iface = self.project.current_interface
        return iface.settings.class_name if iface else "Widget"

    def _setup_statusbar(self):
        self.statusBar().showMessage(tr("status.ready", "Ready"))

    def _connect_signals(self):
        self.toolbox.widget_added.connect(self._on_widget_added)
        self.canvas.widget_selected.connect(self._on_widget_selected)
        self.canvas.widget_moved.connect(self._on_widget_moved)
        self.canvas.widget_resized.connect(self._on_widget_resized)
        self.canvas.widget_context_menu.connect(self._on_widget_context_menu)
        self.object_tree.widget_selected.connect(self._on_widget_selected)
        self.object_tree.widget_deleted.connect(self._on_widget_deleted_from_tree)
        self.undo_mgr.set_on_changed(self._update_undo_redo_actions)
        I18nManager.instance().locale_changed.connect(self._on_locale_changed)
        self.interface_panel.interface_changed.connect(self._on_interface_changed)
        self.interface_panel.set_project(self.project)

    def _add_action(self, menu, text, slot, shortcut=None):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _make_action(self, text, slot):
        action = QAction(text, self)
        action.triggered.connect(slot)
        return action

    def _update_title(self):
        name = self._get_current_class_name()
        modified = "*" if self.project.modified else ""
        filepath = self.project.filepath or tr("untitled", "Untitled")
        self.setWindowTitle(f"SexyUI Editor - {name}{modified} [{filepath}]")

    def _update_undo_redo_actions(self):
        can_undo = self.undo_mgr.can_undo()
        can_redo = self.undo_mgr.can_redo()
        self.undo_action.setEnabled(can_undo)
        self.redo_action.setEnabled(can_redo)
        self.toolbar_undo.setEnabled(can_undo)
        self.toolbar_redo.setEnabled(can_redo)
        if can_undo:
            self.undo_action.setText(tr("action.undo", "Undo") + f" ({self.undo_mgr.undo_description()})")
        if can_redo:
            self.redo_action.setText(tr("action.redo", "Redo") + f" ({self.undo_mgr.redo_description()})")

    def _on_new(self):
        if not self._check_save_before_action():
            return
        self.project = Project()
        self.undo_mgr.clear()
        self._widget_counter.clear()
        self.canvas.set_project(self.project)
        self.object_tree.set_project(self.project)
        self.property_panel.set_project(self.project)
        self._update_title()
        self.statusBar().showMessage(tr("status.new_project", "New project created"))

    def _on_open(self):
        if not self._check_save_before_action():
            return
        history = self._settings.value("open_history", [], type=list)
        start_dir = history[0] if history else ""
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.open", "Open Project"), start_dir,
            "SexyUI Project (*.sexyui *.cssexyui);;C++ Project (*.sexyui);;C# Project (*.cssexyui);;All Files (*)"
        )
        if filepath:
            self._open_file(filepath)
            self._save_history("save_history", filepath)

    def _on_save(self):
        if self.project.filepath:
            self.project.save(self.project.filepath)
            self._auto_link_source_files()
            self._update_title()
            self.statusBar().showMessage(tr("status.saved", "Project saved"))
        else:
            self._on_save_as()

    def _on_save_as(self):
        history = self._settings.value("save_history", [], type=list)
        start_dir = history[0] if history else ""
        
        if self.project.is_csharp_project():
            filter_str = "SexyUI C# Project (*.cssexyui);;SexyUI C++ Project (*.sexyui);;All Files (*)"
            expected_ext = ".cssexyui"
        else:
            filter_str = "SexyUI C++ Project (*.sexyui);;SexyUI C# Project (*.cssexyui);;All Files (*)"
            expected_ext = ".sexyui"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr("dialog.save_as", "Save Project As"), start_dir, filter_str
        )
        if filepath:
            filepath = self._ensure_correct_extension(filepath, expected_ext)
            self.project.save(filepath)
            self._save_history("save_history", filepath)
            self._auto_link_source_files()
            self._update_title()
            self.statusBar().showMessage(tr("status.saved_as", f"Saved as: {filepath}"))

    def _auto_link_source_files(self):
        if not self.project.filepath:
            return
        
        project_dir = os.path.dirname(self.project.filepath)
        platform = self.project.settings.target_platform
        
        for iface_id, iface in self.project.interfaces.items():
            class_name = iface.settings.class_name
            
            if platform == "csharp":
                cs_file = os.path.join(project_dir, f"{class_name}.cs")
                if os.path.exists(cs_file):
                    iface.settings.source_header = cs_file
                    iface.settings.source_cpp = ""
            else:
                header_file = os.path.join(project_dir, f"{class_name}.h")
                cpp_file = os.path.join(project_dir, f"{class_name}.cpp")
                
                if os.path.exists(header_file):
                    iface.settings.source_header = header_file
                if os.path.exists(cpp_file):
                    iface.settings.source_cpp = cpp_file

    def _ensure_correct_extension(self, filepath: str, expected_ext: str) -> str:
        filepath_lower = filepath.lower()
        if filepath_lower.endswith('.cssexyui'):
            if expected_ext == '.sexyui':
                return filepath[:-9] + '.sexyui'
            return filepath
        if filepath_lower.endswith('.sexyui'):
            if expected_ext == '.cssexyui':
                return filepath[:-7] + '.cssexyui'
            return filepath
        if filepath_lower.endswith('.sexyui.cs'):
            base = filepath[:-3]
            if expected_ext == '.cssexyui':
                return base[:-7] + '.cssexyui'
            return base
        if filepath_lower.endswith('.cs'):
            return filepath[:-3] + expected_ext
        if filepath_lower.endswith('.sexyui.sexyui'):
            base = filepath[:-7]
            return base + expected_ext
        if filepath_lower.endswith('.cs.cssexyui'):
            base = filepath[:-10]
            return base + expected_ext
        return filepath + expected_ext

    def _on_exit(self):
        self.close()

    def closeEvent(self, event):
        if not self._check_save_before_action():
            event.ignore()
            return
        event.accept()

    def _check_save_before_action(self) -> bool:
        if not self.project.modified:
            return True
        ret = QMessageBox.question(
            self, tr("confirm.save", "Save Changes?"),
            tr("confirm.unsaved_save", "Current project has unsaved changes. Save before continuing?"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        if ret == QMessageBox.StandardButton.Save:
            self._on_save()
            return True
        elif ret == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _save_history(self, key: str, path: str):
        history = self._settings.value(key, [], type=list)
        if path in history:
            history.remove(path)
        history.insert(0, path)
        history = history[:self.MAX_HISTORY]
        self._settings.setValue(key, history)

    def _on_undo(self):
        self.undo_mgr.undo()
        self.canvas.refresh()
        self.object_tree.refresh()
        self._update_title()

    def _on_redo(self):
        self.undo_mgr.redo()
        self.canvas.refresh()
        self.object_tree.refresh()
        self._update_title()

    def _on_delete(self):
        widget_id = self.canvas.selected_widget_id()
        if widget_id:
            self._on_widget_deleted_from_tree(widget_id)

    def _on_widget_context_menu(self, widget_id: str, global_pos):
        menu = QMenu(self)
        delete_action = menu.addAction(tr("action.delete", "Delete"))
        action = menu.exec(global_pos)
        if action == delete_action:
            self._on_widget_deleted_from_tree(widget_id)

    def _on_project_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self.project, self)
        if dlg.exec() == SettingsDialog.DialogCode.Accepted:
            self.project.modified = True
            self._class_name_edit.setText(self._get_current_class_name())
            self._update_title()
            self.canvas._image_cache.clear()
            self.canvas.refresh()

    def _on_class_name_changed(self, text):
        iface = self.project.current_interface
        if iface:
            iface.settings.class_name = text
            self.project.modified = True
            self._update_title()

    def _on_output_lang_changed(self, index):
        new_lang = self._output_lang_combo.currentData()
        old_lang = self.project.settings.target_platform
        
        if new_lang != old_lang:
            has_images = False
            for iface in self.project.interfaces.values():
                for widget in iface.widgets.values():
                    for prop_name, prop_val in widget.properties.items():
                        if isinstance(prop_val, str) and prop_val.startswith("IMAGE_"):
                            has_images = True
                            break
                    if has_images:
                        break
            
            if has_images:
                from core.qt_compat import QMessageBox
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle(tr("warning.title", "Warning"))
                if new_lang == "csharp":
                    msg.setText(tr("warning.switch_to_csharp", 
                        "Switching to C# mode: Image resources may not be compatible.\n\n"
                        "C++ and C# versions use different resource systems.\n"
                        "Some images may not display correctly after switching.\n\n"
                        "Continue anyway?"))
                else:
                    msg.setText(tr("warning.switch_to_cpp", 
                        "Switching to C++ mode: Image resources may not be compatible.\n\n"
                        "C++ and C# versions use different resource systems.\n"
                        "Some images may not display correctly after switching.\n\n"
                        "Continue anyway?"))
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                msg.setDefaultButton(QMessageBox.StandardButton.No)
                if msg.exec() != QMessageBox.StandardButton.Yes:
                    self._output_lang_combo.blockSignals(True)
                    self._output_lang_combo.setCurrentIndex(0 if old_lang == "cpp" else 1)
                    self._output_lang_combo.blockSignals(False)
                    return
        
        self.code_gen.set_output_language(new_lang)
        self.project.set_target_platform(new_lang)
        self._ext_manager.set_platform(new_lang)
        self.toolbox.refresh_ui()
        self.canvas.refresh()
        self._update_title()
        self.statusBar().showMessage(tr("status.output_lang_changed", f"Output language: {new_lang.upper()}"))
        
        self._cpp_structure_combo.setVisible(new_lang == "cpp")

    def _on_cpp_structure_changed(self, index):
        new_structure = self._cpp_structure_combo.currentData()
        self.project.settings.cpp_structure = new_structure
        self.statusBar().showMessage(tr("status.cpp_structure_changed", f"C++ Structure: {new_structure.upper()}"))

    def _on_preview(self):
        dlg = PreviewWindow(self.project, self)
        dlg.exec()

    def _on_view_code(self):
        lang = self._output_lang_combo.currentData()
        project_path = getattr(self.project, 'filepath', '') or ""
        if lang == "csharp":
            cs_code = self.code_gen.generate_csharp(self.project)
            dlg = CodeViewDialog("", cs_code, self._get_current_class_name(), self, language="csharp",
                               project=self.project, code_gen=self.code_gen, project_path=project_path)
            dlg.exec()
        else:
            header = self.code_gen.generate_header(self.project)
            cpp = self.code_gen.generate_cpp(self.project)
            dlg = CodeViewDialog(header, cpp, self._get_current_class_name(), self, language="cpp",
                               project=self.project, code_gen=self.code_gen, project_path=project_path)
            dlg.exec()

    def _on_export_all_interfaces(self):
        if not self.project.interfaces:
            QMessageBox.information(self, tr("info.title", "Info"), tr("info.no_interfaces", "No interfaces to export."))
            return

        export_dir = QFileDialog.getExistingDirectory(
            self,
            tr("dialog.export_dir", "Select Export Directory"),
            ""
        )

        if not export_dir:
            return

        import os
        language = self.project.settings.target_platform
        all_code = self.code_gen.generate_all_interfaces(self.project, language)
        exported_count = 0

        if language == "csharp":
            for class_name, (cs_code, _) in all_code.items():
                cs_path = os.path.join(export_dir, f"{class_name}.cs")
                with open(cs_path, 'w', encoding='utf-8') as f:
                    f.write(cs_code)
                exported_count += 1
        else:
            for class_name, (header, cpp) in all_code.items():
                header_path = os.path.join(export_dir, f"{class_name}.h")
                cpp_path = os.path.join(export_dir, f"{class_name}.cpp")

                with open(header_path, 'w', encoding='utf-8') as f:
                    f.write(header)
                with open(cpp_path, 'w', encoding='utf-8') as f:
                    f.write(cpp)

                exported_count += 1

        self.statusBar().showMessage(tr("status.exported_all", "Exported {} interfaces").format(exported_count))
        QMessageBox.information(
            self,
            tr("code.export_success", "Export Successful"),
            tr("status.exported_all", "Exported {} interfaces to:\n{}").format(exported_count, export_dir)
        )

    def _on_import_interfaces(self):
        if self.project.is_csharp_project():
            file_filter = tr("filter.csharp_project", "SexyUI C# Project (*.cssexyui);;All Files (*)")
        else:
            file_filter = tr("filter.cpp_project", "SexyUI C++ Project (*.sexyui);;All Files (*)")
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            tr("dialog.import_interfaces", "Import Interfaces from Project"),
            "",
            file_filter
        )

        if not files:
            return

        imported_count = 0
        skipped_count = 0

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                interfaces_data = data.get("interfaces", {})
                for iface_id, iface_data in interfaces_data.items():
                    isettings = iface_data.get("settings", {})
                    class_name = isettings.get("class_name", "ImportedWidget")
                    
                    if any(iface.settings.class_name == class_name for iface in self.project.interfaces.values()):
                        skipped_count += 1
                        continue
                    
                    new_id = str(uuid.uuid4())[:8]
                    while new_id in self.project.interfaces:
                        new_id = str(uuid.uuid4())[:8]
                    
                    isettings["id"] = new_id
                    iface_data["settings"] = isettings
                    
                    temp_project = Project()
                    temp_project.from_dict({"settings": {}, "interfaces": {new_id: iface_data}})
                    
                    self.project.interfaces[new_id] = temp_project.interfaces[new_id]
                    imported_count += 1
                    
            except Exception as e:
                QMessageBox.warning(self, tr("error.title", "Error"), f"Failed to import {filepath}:\n{str(e)}")

        if imported_count > 0:
            self._update_interface_list()
            self._mark_modified()
            self.canvas.refresh()
            
        message = tr("status.imported", "Imported {} interfaces").format(imported_count)
        if skipped_count > 0:
            message += tr("status.skipped", ", {} skipped (duplicate class names)").format(skipped_count)
        
        self.statusBar().showMessage(message)
        QMessageBox.information(
            self,
            tr("info.title", "Info"),
            message
        )

    def _on_manage_resources(self):
        dlg = ResourceDialog(self.res_mgr, self)
        if dlg.exec() == ResourceDialog.DialogCode.Accepted:
            self.property_panel.refresh_resources()

    def _on_about(self):
        QMessageBox.about(
            self,
            tr("about.title", "About SexyUI Editor"),
            tr("about.text", "SexyUI Editor v1.0\n\nA visual UI editor for the Sexy Framework.\nSupports drag-and-drop layout design, code generation, and resource management.")
        )

    def _on_sync_from_source(self):
        sync_mgr = CodeSyncManager(self.project)
        success, message = sync_mgr.sync_from_source()

        if success:
            self.statusBar().showMessage(tr("status.sync_success", message))
            self._update_title()
            self.canvas.refresh()
        else:
            QMessageBox.warning(self, tr("error.sync", "Sync Failed"), message)

    def _on_generate_source(self):
        default_name = self._get_current_class_name()
        header_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("dialog.save_header", "Save Header File"),
            f"{default_name}.h",
            "C++ Header (*.h)"
        )

        if header_path:
            cpp_path = header_path.replace('.h', '.cpp')

            sync_mgr = CodeSyncManager(self.project)
            success, message = sync_mgr.sync_to_source(header_path, cpp_path)

            if success:
                self.statusBar().showMessage(tr("status.generate_success", message))
            else:
                QMessageBox.warning(self, tr("error.generate", "Generate Failed"), message)

    def _on_link_source(self):
        header_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("dialog.select_header", "Select Header File"),
            "",
            "C++ Header (*.h);;All Files (*)"
        )

        if header_path:
            cpp_path = header_path.replace('.h', '.cpp')
            import os
            if not os.path.exists(cpp_path):
                cpp_path, _ = QFileDialog.getOpenFileName(
                    self,
                    tr("dialog.select_cpp", "Select CPP File"),
                    "",
                    "C++ Source (*.cpp);;All Files (*)"
                )

            self.project.settings.source_header = header_path
            self.project.settings.source_cpp = cpp_path

            self._on_sync_from_source()

    def _on_associate_files(self):
        import sys
        import ctypes
        
        # Check if running as compiled executable (Nuitka or PyInstaller)
        is_compiled = (
            getattr(sys, 'frozen', False) or 
            hasattr(sys, '__compiled__') or
            'main.dist' in os.path.abspath(__file__)
        )
        
        if is_compiled:
            # For compiled exe, use the executable path directly
            exe_path = sys.executable
        else:
            # For development, use main.py
            main_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
            exe_path = f'pythonw "{main_py}"'
        
        ret = QMessageBox.question(
            self,
            tr("dialog.associate_files_title", "Associate File Types"),
            tr("dialog.associate_files_detail", "This will associate .sexyui and .cssexyui files with SexyUI Editor.\n\nContinue?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if ret != QMessageBox.StandardButton.Yes:
            return
        
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                self._register_file_association(exe_path)
                QMessageBox.information(
                    self,
                    tr("dialog.associate_success", "Success"),
                    tr("dialog.associate_files_success", "File types associated successfully!")
                )
            else:
                QMessageBox.warning(
                    self,
                    tr("dialog.admin_required", "Admin Required"),
                    tr("dialog.admin_required_detail", "Please run the editor as administrator to associate file types.")
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr("error.title", "Error"),
                tr("dialog.associate_failed", f"Failed to associate file types: {str(e)}")
            )
    
    def _register_file_association(self, exe_path):
        import winreg
        
        file_types = [
            (".sexyui", "SexyUI.Project", "SexyUI C++ Project"),
            (".cssexyui", "SexyUI.CSharpProject", "SexyUI C# Project")
        ]
        
        for ext, prog_id, description in file_types:
            try:
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ext)
                winreg.SetValue(key, None, winreg.REG_SZ, prog_id)
                winreg.CloseKey(key)
                
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, prog_id)
                winreg.SetValue(key, None, winreg.REG_SZ, description)
                winreg.CloseKey(key)
                
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\shell\\open\\command")
                winreg.SetValue(key, None, winreg.REG_SZ, f'"{exe_path}" "%1"')
                winreg.CloseKey(key)
                
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{prog_id}\\DefaultIcon")
                winreg.SetValue(key, None, winreg.REG_SZ, f'"{exe_path}",0')
                winreg.CloseKey(key)
            except Exception as e:
                raise Exception(f"Failed to register {ext}: {str(e)}")

    def showEvent(self, event):
        super().showEvent(event)

        if self._auto_sync_action.isChecked():
            sync_mgr = CodeSyncManager(self.project)
            if sync_mgr.check_file_changes():
                ret = QMessageBox.question(
                    self,
                    tr("sync.file_changed", "File Changed"),
                    tr("sync.file_changed_detail", "Source files have been modified externally. Sync now?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if ret == QMessageBox.StandardButton.Yes:
                    self._on_sync_from_source()

    def _on_language_changed(self, locale_code: str):
        i18n = I18nManager.instance()
        i18n.load_locale(locale_code)
        i18n.save_locale(locale_code)

    def _on_interface_changed(self, interface_id: str):
        self.canvas.refresh()
        self.object_tree.refresh()
        self.property_panel.clear()
        self._update_title()

    def _on_locale_changed(self, locale_code: str):
        for action in self._lang_action_group.actions():
            action.setChecked(False)
        for action in self._lang_action_group.actions():
            if action.text() == I18nManager.instance().get_locale_name(locale_code):
                action.setChecked(True)
                break
        self._refresh_ui()

    def _refresh_ui(self):
        self.setWindowTitle(tr("app.title", "SexyUI Editor"))
        self._update_title()
        self._refresh_menus()
        self._refresh_toolbar()
        self.toolbox.refresh_ui()
        self.property_panel.refresh_ui()
        self.object_tree.refresh_ui()
        self.canvas.refresh()
        self.statusBar().showMessage(tr("status.ready", "Ready"))

    def _refresh_menus(self):
        menubar = self.menuBar()
        for action in menubar.actions():
            menu = action.menu()
            if menu:
                self._refresh_menu(menu)

    def _refresh_menu(self, menu: QMenu):
        menu.setTitle(tr(f"menu.{menu.title().replace('&', '').lower()}", menu.title()))
        for action in menu.actions():
            if action.menu():
                self._refresh_menu(action.menu())
            elif not action.isSeparator():
                action.setText(tr(f"action.{action.text().lower().replace(' ', '_').replace('.', '')}", action.text()))

    def _refresh_toolbar(self):
        self.toolbar_undo.setText(tr("action.undo", "Undo"))
        self.toolbar_redo.setText(tr("action.redo", "Redo"))

    def _generate_unique_name(self, class_name: str) -> str:
        base = class_name.replace("Widget", "").replace("Button", "Btn")
        base = base[0].lower() + base[1:] if base else "widget"
        count = self._widget_counter.get(base, 0) + 1
        while True:
            name = f"{base}{count}"
            exists = any(
                w.instance_name == name for w in self.project.widgets.values()
            )
            if not exists:
                self._widget_counter[base] = count
                return name
            count += 1

    def _generate_unique_id(self) -> int:
        used_ids = set()
        for w in self.project.widgets.values():
            wid = w.properties.get("mId", 0)
            if isinstance(wid, int):
                used_ids.add(wid)
        new_id = 500
        while new_id in used_ids:
            new_id += 1
        return new_id

    def _on_widget_added(self, class_name: str, x: int, y: int):
        from core.component_registry import ComponentRegistry, PropType
        from core.undo_manager import snapshot_undo, snapshot_redo

        reg = ComponentRegistry.instance()
        cdef = reg.get(class_name)
        if not cdef:
            return

        before = snapshot_undo(self.project, f"Add {class_name}")

        from core.project import WidgetInstance
        props = {}
        for p in cdef.properties:
            props[p.name] = p.default
        props["mX"] = x
        props["mY"] = y
        props["mId"] = self._generate_unique_id()

        default_sizes = {
            "Widget": (200, 150),
            "ButtonWidget": (120, 35),
            "DialogButton": (120, 35),
            "HyperlinkWidget": (100, 25),
            "EditWidget": (150, 25),
            "TextWidget": (200, 100),
            "ListWidget": (150, 120),
            "ScrollbarWidget": (20, 120),
            "Checkbox": (20, 20),
            "Slider": (150, 20),
            "Dialog": (300, 200),
            "LawnDialog": (300, 200),
            "LawnStoneButton": (120, 35),
            "NewLawnButton": (120, 35),
            "LawnEditWidget": (150, 25),
            "ScrollbuttonWidget": (20, 20),
            "GameButton": (120, 35),
        }
        dw, dh = default_sizes.get(class_name, (100, 30))
        props["mWidth"] = dw
        props["mHeight"] = dh

        self._assign_default_images(class_name, props)

        inst_name = self._generate_unique_name(class_name)

        wid = WidgetInstance(
            class_name=class_name,
            instance_name=inst_name,
            properties=props,
        )
        self.project.add_widget(wid)

        after = snapshot_redo(self.project, f"Add {class_name}")
        self.undo_mgr.push_action(f"Add {class_name}", after, before)

        self.canvas.refresh()
        self.object_tree.refresh()
        self._update_title()

    def _on_widget_selected(self, widget_id: str):
        self.canvas.select_widget(widget_id)
        self.object_tree.select_widget(widget_id)
        self.property_panel.show_widget(widget_id)

    def _on_widget_moved(self, widget_id: str, x: int, y: int):
        w = self.project.get_widget(widget_id)
        if w:
            old_x, old_y = w.properties.get("mX", 0), w.properties.get("mY", 0)
            w.properties["mX"] = x
            w.properties["mY"] = y
            self.project.modified = True
            self.property_panel.show_widget(widget_id)
            self._update_title()

    def _on_widget_resized(self, widget_id: str, w: int, h: int):
        wid = self.project.get_widget(widget_id)
        if wid:
            wid.properties["mWidth"] = w
            wid.properties["mHeight"] = h
            self.project.modified = True
            self.property_panel.show_widget(widget_id)
            self._update_title()

    def _on_widget_deleted_from_tree(self, widget_id: str):
        from core.undo_manager import snapshot_undo, snapshot_redo
        before = snapshot_undo(self.project, "Delete widget")
        self.project.remove_widget(widget_id)
        after = snapshot_redo(self.project, "Delete widget")
        self.undo_mgr.push_action("Delete widget", after, before)
        self.canvas.refresh()
        self.object_tree.refresh()
        self.property_panel.clear()
        self._update_title()

    def _assign_default_images(self, class_name: str, props: dict):
        platform = self.project.settings.target_platform
        
        if platform == "csharp":
            if class_name in ("ButtonWidget", "DialogButton", "LawnStoneButton", "NewLawnButton", "GameButton"):
                props["mButtonImage"] = "IMAGE_BUTTON_MIDDLE"
                props["mOverImage"] = "IMAGE_BUTTON_MIDDLE"
                props["mDownImage"] = "IMAGE_BUTTON_DOWN_MIDDLE"
            elif class_name in ("EditWidget", "LawnEditWidget"):
                props["mFont"] = "FONT_DWARVENTODCRAFT12"
            elif class_name in ("Dialog", "LawnDialog"):
                props["mComponentImage"] = "IMAGE_DIALOG_HEADER"
            elif class_name == "Checkbox":
                props["mUncheckedImage"] = "IMAGE_OPTIONS_CHECKBOX0"
                props["mCheckedImage"] = "IMAGE_OPTIONS_CHECKBOX1"
            elif class_name == "Slider":
                props["mTrackImage"] = "IMAGE_OPTIONS_SLIDERSLOT"
                props["mThumbImage"] = "IMAGE_OPTIONS_SLIDERKNOB2"
        else:
            if class_name in ("ButtonWidget", "DialogButton", "LawnStoneButton", "NewLawnButton", "GameButton"):
                props["mButtonImage"] = "IMAGE_BUTTON_MIDDLE"
                props["mOverImage"] = "IMAGE_BUTTON_MIDDLE"
                props["mDownImage"] = "IMAGE_BUTTON_MIDDLE"
            elif class_name in ("EditWidget", "LawnEditWidget"):
                props["mFont"] = "FONT_DWARVENTODCRAFT12"
            elif class_name in ("Dialog", "LawnDialog"):
                props["mComponentImage"] = "IMAGE_DIALOG_HEADER"
            elif class_name == "Checkbox":
                props["mUncheckedImage"] = "IMAGE_OPTIONS_CHECKBOX0"
                props["mCheckedImage"] = "IMAGE_OPTIONS_CHECKBOX1"
            elif class_name == "Slider":
                props["mTrackImage"] = "IMAGE_OPTIONS_SLIDERSLOT"
                props["mThumbImage"] = "IMAGE_OPTIONS_SLIDERKNOB2"

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
            }
            QDockWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(undock.png);
            }
            QDockWidget::title {
                background-color: #3c3c3c;
                padding: 6px;
                border: 1px solid #3c3c3c;
            }
            QToolBar {
                background-color: #3c3c3c;
                border: none;
                spacing: 4px;
                padding: 4px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                color: #d4d4d4;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolBar QToolButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QToolBar QToolButton:pressed {
                background-color: #3a3a3a;
            }
            QToolBar QLabel {
                color: #d4d4d4;
                background: transparent;
            }
            QToolBar QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border-bottom: 1px solid #2b2b2b;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #5a5a5a;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
            QMenu::separator {
                height: 1px;
                background-color: #5a5a5a;
                margin: 5px 10px;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border-top: 1px solid #2b2b2b;
            }
            QTreeWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                alternate-background-color: #333333;
            }
            QTreeWidget::item {
                padding: 4px;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #4a4a4a;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #d4d4d4;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #2b2b2b;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #d4d4d4;
                padding: 8px 16px;
                border: 1px solid #3c3c3c;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom: 2px solid #0078d4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #4a4a4a;
            }
            QGroupBox {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #0078d4;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #d4d4d4;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: #d4d4d4;
                selection-background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
            QCheckBox {
                color: #d4d4d4;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 1px solid #0078d4;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #6a6a6a;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                border-radius: 4px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6a6a6a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                background-color: #2b2b2b;
                height: 12px;
                border: none;
            }
            QScrollBar::handle:horizontal {
                background-color: #5a5a5a;
                border-radius: 4px;
                min-width: 30px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #6a6a6a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            QToolTip {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #5a5a5a;
                padding: 4px 8px;
            }
            QMessageBox {
                background-color: #2b2b2b;
            }
            QMessageBox QLabel {
                color: #d4d4d4;
            }
            QDialog {
                background-color: #2b2b2b;
                color: #d4d4d4;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #d4d4d4;
                gridline-color: #3c3c3c;
                border: 1px solid #3c3c3c;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #4a4a4a;
            }
        """)

    def _set_dark_titlebar(self):
        set_transparent_titlebar(self)

    def _set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                if filepath.endswith(".sexyui") or filepath.endswith(".cssexyui"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.endswith(".sexyui") or filepath.endswith(".cssexyui"):
                self._open_file(filepath)
                break

    def _open_file(self, filepath: str):
        try:
            self.project.load(filepath)
            self.undo_mgr.clear()
            self._widget_counter.clear()
            self._save_history("open_history", filepath)
            
            if filepath.endswith(".cssexyui"):
                self.project.set_target_platform("csharp")
                self._ext_manager.set_platform("csharp")
                self._output_lang_combo.setCurrentIndex(1)
                self._cpp_structure_combo.setVisible(False)
            else:
                self.project.set_target_platform("cpp")
                self._ext_manager.set_platform("cpp")
                self._output_lang_combo.setCurrentIndex(0)
                self._cpp_structure_combo.setVisible(True)
                
                structure = getattr(self.project.settings, 'cpp_structure', 'qe')
                structure_index = 0 if structure == "qe" else 1
                self._cpp_structure_combo.setCurrentIndex(structure_index)
            
            self.toolbox.refresh_ui()
            self.canvas.set_project(self.project)
            self.object_tree.set_project(self.project)
            self.property_panel.set_project(self.project)
            self.interface_panel.set_project(self.project)
            self._update_title()
            self.statusBar().showMessage(tr("status.opened", f"Opened: {filepath}"))
        except Exception as e:
            QMessageBox.critical(self, tr("error.title", "Error"), str(e))

    def load_project(self, filepath: str):
        """Public method to load a project file (used for file association)"""
        if not self._check_save_before_action():
            return
        self._open_file(filepath)
