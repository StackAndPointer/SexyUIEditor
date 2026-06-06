# -*- coding: utf-8 -*-
from core.qt_compat import (
    QWidget, QVBoxLayout, QFormLayout, QScrollArea,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QComboBox, QPushButton, QLabel, QGroupBox, QColorDialog,
    Qt, Signal, QColor
)
from core.project import Project, WidgetInstance
from core.component_registry import ComponentRegistry, PropType
from core.resource_manager import ResourceManager
from core.i18n import tr
from ui.image_picker import ImagePickerDialog
from ui.event_config import EventConfigDialog


class PropertyPanel(QWidget):
    property_changed = Signal(str, str, object)

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._current_id = ""
        self._registry = ComponentRegistry.instance()
        self._res_mgr = ResourceManager.instance()
        self._widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 12px; background: #f0f0f0; }
            QScrollBar::handle:vertical { background: #c0c0c0; min-height: 20px; border-radius: 4px; margin: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        self._content = QWidget()
        self._form_layout = QVBoxLayout(self._content)
        self._form_layout.setContentsMargins(8, 8, 8, 8)
        self._form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._content)
        self._main_layout.addWidget(self._scroll)

        self._placeholder = QLabel(tr("prop.no_selection", "No widget selected"))
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._form_layout.addWidget(self._placeholder)
        self.setLayout(self._main_layout)

    def set_project(self, project: Project):
        self.project = project
        self.clear()

    def show_widget(self, widget_id: str):
        self._current_id = widget_id
        self._clear_form()

        if not widget_id:
            self._placeholder = QLabel(tr("prop.no_selection", "No widget selected"))
            self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._form_layout.addWidget(self._placeholder)
            return

        w = self.project.get_widget(widget_id)
        if not w:
            return

        cdef = self._registry.get(w.class_name)
        if not cdef:
            return

        header = QLabel(f"<b>{w.class_name}</b> - {w.instance_name or w.id}")
        self._form_layout.addWidget(header)

        name_edit = QLineEdit(w.instance_name)
        name_edit.setPlaceholderText(tr("prop.instance_name", "Instance name"))
        name_edit.textChanged.connect(lambda v: self._set_instance_name(v))
        self._form_layout.addWidget(QLabel(tr("prop.instance_name", "Instance Name")))
        self._form_layout.addWidget(name_edit)

        categories = {}
        for p in cdef.properties:
            categories.setdefault(p.category, []).append(p)

        cat_labels = {
            "geometry": tr("cat.geometry", "Geometry"),
            "identity": tr("cat.identity", "Identity"),
            "content": tr("cat.content", "Content"),
            "appearance": tr("cat.appearance", "Appearance"),
            "behavior": tr("cat.behavior", "Behavior"),
            "images": tr("cat.images", "Images"),
            "animation": tr("cat.animation", "Animation"),
            "value": tr("cat.value", "Value"),
        }

        for cat_name, props in categories.items():
            group = QGroupBox(cat_labels.get(cat_name, cat_name))
            form = QFormLayout()
            form.setContentsMargins(4, 4, 4, 4)

            for p in props:
                val = w.properties.get(p.name, p.default)
                editor = self._create_editor(p, val)
                if editor:
                    display_name = tr(f"prop.{p.name}", p.display_name or p.name)
                    label = QLabel(display_name)
                    if p.tooltip:
                        label.setToolTip(f"<b>{p.name}</b><br>{p.tooltip}")
                        editor.setToolTip(f"<b>{p.name}</b><br>{p.tooltip}")
                    form.addRow(label, editor)
                    self._widgets[p.name] = editor

            group.setLayout(form)
            self._form_layout.addWidget(group)

        event_group = QGroupBox(tr("cat.events", "Events"))
        event_layout = QVBoxLayout()
        event_layout.setContentsMargins(4, 4, 4, 4)

        event_names = self._get_available_events(w.class_name)
        for event_name in event_names:
            actions = w.event_actions.get(event_name, [])
            action_count = len(actions)
            btn_text = f"{event_name} ({action_count})" if action_count > 0 else event_name
            event_btn = QPushButton(btn_text)
            event_btn.clicked.connect(lambda checked, en=event_name: self._on_configure_event(en))
            event_layout.addWidget(event_btn)

        if not event_names:
            no_events = QLabel(tr("event.no_events", "No events available"))
            no_events.setStyleSheet("color: #888;")
            event_layout.addWidget(no_events)

        event_group.setLayout(event_layout)
        self._form_layout.addWidget(event_group)

        self._form_layout.addStretch()

    def _get_available_events(self, class_name: str) -> list:
        from core.code_generator import CodeGenerator
        gen = CodeGenerator.instance()
        events = []
        if class_name in gen.BUTTON_WIDGETS or class_name == "GameButton":
            events.append("ButtonDepress")
        if class_name in gen.EDIT_WIDGETS:
            events.append("EditWidgetText")
        if class_name in gen.CHECKBOX_WIDGETS:
            events.append("CheckboxChecked")
        if class_name in gen.SLIDER_WIDGETS:
            events.append("SliderVal")
        if class_name in gen.LIST_WIDGETS:
            events.append("ListClicked")
        return events

    def _on_configure_event(self, event_name: str):
        if not self._current_id:
            return
        w = self.project.get_widget(self._current_id)
        if not w:
            return
        dlg = EventConfigDialog(w, event_name, self.project, self)
        dlg.exec()
        self.show_widget(self._current_id)

    def clear(self):
        self._current_id = ""
        self._clear_form()

    def refresh_resources(self):
        if self._current_id:
            self.show_widget(self._current_id)

    def _clear_form(self):
        self._widgets.clear()
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _create_editor(self, prop_def, value) -> QWidget:
        pt = prop_def.prop_type

        if pt == PropType.INT:
            editor = QSpinBox()
            editor.setRange(-99999, 99999)
            editor.setValue(int(value) if value is not None else 0)
            editor.setMaximumWidth(120)
            editor.valueChanged.connect(lambda v: self._on_prop_changed(prop_def.name, v))
            return editor

        elif pt == PropType.FLOAT:
            editor = QDoubleSpinBox()
            editor.setRange(-99999.0, 99999.0)
            editor.setDecimals(3)
            editor.setValue(float(value) if value is not None else 0.0)
            editor.setMaximumWidth(120)
            editor.valueChanged.connect(lambda v: self._on_prop_changed(prop_def.name, v))
            return editor

        elif pt == PropType.STRING:
            editor = QLineEdit(str(value) if value else "")
            editor.setMaximumWidth(150)
            editor.textChanged.connect(lambda v: self._on_prop_changed(prop_def.name, v))
            return editor

        elif pt == PropType.BOOL:
            editor = QCheckBox()
            editor.setChecked(bool(value))
            editor.stateChanged.connect(lambda v: self._on_prop_changed(prop_def.name, v == Qt.CheckState.Checked.value))
            return editor

        elif pt == PropType.COLOR:
            editor = QPushButton(str(value) or "0,0,0")
            editor.setMaximumWidth(100)
            editor.clicked.connect(lambda: self._pick_color(prop_def.name, editor))
            return editor

        elif pt == PropType.IMAGE:
            current = str(value) if value else ""
            editor = QPushButton(current or tr("prop.select_image", "Select..."))
            editor.setMaximumWidth(150)
            editor.clicked.connect(lambda: self._pick_resource(prop_def.name, editor, "image"))
            return editor

        elif pt == PropType.FONT:
            current = str(value) if value else ""
            editor = QPushButton(current or tr("prop.select_font", "Select..."))
            editor.setMaximumWidth(150)
            editor.clicked.connect(lambda: self._pick_resource(prop_def.name, editor, "font"))
            return editor

        elif pt == PropType.ENUM:
            editor = QComboBox()
            for ev in prop_def.enum_values:
                display = ev.split("=")[-1] if "=" in ev else ev
                editor.addItem(display, ev)
            current = str(value) if value else ""
            for i in range(editor.count()):
                if editor.itemData(i) == current or editor.itemText(i) == current:
                    editor.setCurrentIndex(i)
                    break
            editor.setMaximumWidth(120)
            editor.currentIndexChanged.connect(
                lambda idx: self._on_prop_changed(prop_def.name, editor.itemData(idx) or editor.itemText(idx)))
            return editor

        elif pt == PropType.RECT:
            editor = QLineEdit(str(value) if value else "0,0,0,0")
            editor.setPlaceholderText("x,y,w,h")
            editor.setMaximumWidth(120)
            editor.textChanged.connect(lambda v: self._on_prop_changed(prop_def.name, v))
            return editor

        editor = QLineEdit(str(value) if value else "")
        editor.setMaximumWidth(150)
        return editor

    def _on_prop_changed(self, prop_name: str, value):
        if not self._current_id:
            return
        w = self.project.get_widget(self._current_id)
        if w:
            w.properties[prop_name] = value
            self.project.modified = True
            self.property_changed.emit(self._current_id, prop_name, value)
            
            if prop_name == "mUniformImage" and w.class_name == "NewLawnButton":
                if value:
                    w.properties["mButtonImage"] = value
                    w.properties["mOverImage"] = value
                    w.properties["mDownImage"] = value
                    self._refresh_property("mButtonImage", value)
                    self._refresh_property("mOverImage", value)
                    self._refresh_property("mDownImage", value)

    def _refresh_property(self, prop_name: str, value):
        if prop_name in self._widgets:
            editor = self._widgets[prop_name]
            if isinstance(editor, QPushButton):
                editor.setText(str(value) if value else "")

    def _set_instance_name(self, name: str):
        if not self._current_id:
            return
        w = self.project.get_widget(self._current_id)
        if w:
            w.instance_name = name
            self.project.modified = True

    def _pick_color(self, prop_name: str, button: QPushButton):
        current_text = button.text()
        parts = current_text.split(",")
        initial = QColor(0, 0, 0)
        if len(parts) >= 3:
            try:
                initial = QColor(int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                pass

        color = QColorDialog.getColor(initial, self, tr("dialog.pick_color", "Pick Color"))
        if color.isValid():
            text = f"{color.red()},{color.green()},{color.blue()}"
            button.setText(text)
            self._on_prop_changed(prop_name, text)

    def _pick_resource(self, prop_name: str, button: QPushButton, resource_type: str):
        current = button.text()
        if current.startswith(tr("prop.select_image", "Select...")) or current.startswith(tr("prop.select_font", "Select...")):
            current = ""

        platform = self.project.settings.target_platform
        dialog = ImagePickerDialog(current, resource_type, self, platform=platform)
        if dialog.exec():
            selected = dialog.get_selected_value()
            button.setText(selected or (tr("prop.select_image", "Select...") if resource_type == "image" else tr("prop.select_font", "Select...")))
            self._on_prop_changed(prop_name, selected)

    def refresh_ui(self):
        if self._current_id:
            self.show_widget(self._current_id)
