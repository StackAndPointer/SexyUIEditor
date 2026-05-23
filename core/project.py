# -*- coding: utf-8 -*-
import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EventAction:
    action_type: str = "none"
    predefined_id: str = ""
    params: Dict[str, str] = field(default_factory=dict)


@dataclass
class WidgetInstance:
    id: str = ""
    class_name: str = ""
    instance_name: str = ""
    properties: Dict[str, object] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    parent_id: str = ""
    z_order: int = 0
    event_actions: Dict[str, List[EventAction]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class ProjectCode:
    header_includes: str = ""
    cpp_includes: str = ""
    forward_declarations: str = ""
    declarations: str = ""
    init_code: str = ""
    destroy_code: str = ""
    draw_code: str = ""
    update_code: str = ""
    functions: str = ""
    post_class: str = ""
    event_handlers: Dict[str, str] = field(default_factory=dict)


@dataclass
class InterfaceSettings:
    id: str = ""
    name: str = ""
    class_name: str = "MyWidget"
    parent_class: str = "Widget"
    interface_type: str = "main"
    width: int = 800
    height: int = 600
    background_image: str = ""
    background_stretch: bool = False
    background_color: str = "0,0,0"
    listeners: List[str] = field(default_factory=list)
    source_header: str = ""
    source_cpp: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class Interface:
    settings: InterfaceSettings = field(default_factory=InterfaceSettings)
    widgets: Dict[str, WidgetInstance] = field(default_factory=dict)
    root_widget_ids: List[str] = field(default_factory=list)
    user_code: ProjectCode = field(default_factory=ProjectCode)

    def __post_init__(self):
        if not self.settings.id:
            self.settings.id = str(uuid.uuid4())[:8]


@dataclass
class InterfaceTransition:
    source_id: str = ""
    target_id: str = ""
    trigger_widget_id: str = ""
    trigger_event: str = ""
    transition_type: str = "show"


@dataclass
class ProjectSettings:
    namespace: str = ""
    header_include: str = ""
    target_platform: str = "cpp"
    cpp_structure: str = "qe"
    
    def get_default_width(self) -> int:
        return 800
    
    def get_default_height(self) -> int:
        return 480 if self.target_platform == "csharp" else 600


class Project:
    CPP_EXTENSION = ".sexyui"
    CSHARP_EXTENSION = ".cssexyui"
    
    def __init__(self):
        self.settings = ProjectSettings()
        self.interfaces: Dict[str, Interface] = {}
        self.main_interface_id: str = ""
        self.transitions: List[InterfaceTransition] = []
        self.resources: Dict[str, str] = {}
        self.filepath: Optional[str] = None
        self.modified = False
        self._current_interface_id: str = ""
        self._init_main_interface()

    def _init_main_interface(self):
        iface = Interface(settings=InterfaceSettings(
            name="Main", 
            class_name="MainWidget", 
            interface_type="main",
            width=self.settings.get_default_width(),
            height=self.settings.get_default_height()
        ))
        self.interfaces[iface.settings.id] = iface
        self.main_interface_id = iface.settings.id
        self._current_interface_id = iface.settings.id

    @property
    def current_interface(self) -> Optional[Interface]:
        return self.interfaces.get(self._current_interface_id)

    @property
    def widgets(self) -> Dict[str, WidgetInstance]:
        iface = self.current_interface
        return iface.widgets if iface else {}

    @property
    def root_widget_ids(self) -> List[str]:
        iface = self.current_interface
        return iface.root_widget_ids if iface else []

    @property
    def user_code(self) -> ProjectCode:
        iface = self.current_interface
        return iface.user_code if iface else ProjectCode()

    def set_current_interface(self, interface_id: str):
        if interface_id in self.interfaces:
            self._current_interface_id = interface_id

    def add_interface(self, name: str, class_name: str = "", interface_type: str = "dialog") -> Interface:
        if not class_name:
            class_name = name.replace(" ", "") + "Widget"
        iface = Interface(settings=InterfaceSettings(
            name=name, 
            class_name=class_name, 
            interface_type=interface_type,
            width=self.settings.get_default_width(),
            height=self.settings.get_default_height()
        ))
        self.interfaces[iface.settings.id] = iface
        self.modified = True
        return iface

    def remove_interface(self, interface_id: str):
        if interface_id == self.main_interface_id:
            return
        if interface_id in self.interfaces:
            del self.interfaces[interface_id]
            if self._current_interface_id == interface_id:
                self._current_interface_id = self.main_interface_id
            self.transitions = [t for t in self.transitions if t.source_id != interface_id and t.target_id != interface_id]
            self.modified = True

    def get_interface_names(self) -> List[str]:
        return [iface.settings.name for iface in self.interfaces.values()]

    def get_interface_by_name(self, name: str) -> Optional[Interface]:
        for iface in self.interfaces.values():
            if iface.settings.name == name:
                return iface
        return None

    def add_widget(self, widget: WidgetInstance, parent_id: str = "") -> str:
        iface = self.current_interface
        if not iface:
            return ""
        iface.widgets[widget.id] = widget
        widget.parent_id = parent_id
        if parent_id and parent_id in iface.widgets:
            iface.widgets[parent_id].children.append(widget.id)
        else:
            iface.root_widget_ids.append(widget.id)
        self.modified = True
        return widget.id

    def remove_widget(self, widget_id: str):
        iface = self.current_interface
        if not iface or widget_id not in iface.widgets:
            return
        w = iface.widgets[widget_id]
        for child_id in list(w.children):
            self.remove_widget(child_id)
        if w.parent_id and w.parent_id in iface.widgets:
            parent = iface.widgets[w.parent_id]
            if widget_id in parent.children:
                parent.children.remove(widget_id)
        if widget_id in iface.root_widget_ids:
            iface.root_widget_ids.remove(widget_id)
        del iface.widgets[widget_id]
        self.modified = True

    def get_widget(self, widget_id: str) -> Optional[WidgetInstance]:
        iface = self.current_interface
        if not iface:
            return None
        return iface.widgets.get(widget_id)

    def move_widget(self, widget_id: str, new_parent_id: str = ""):
        iface = self.current_interface
        if not iface:
            return
        w = iface.widgets.get(widget_id)
        if not w:
            return
        if w.parent_id and w.parent_id in iface.widgets:
            old_parent = iface.widgets[w.parent_id]
            if widget_id in old_parent.children:
                old_parent.children.remove(widget_id)
        if widget_id in iface.root_widget_ids:
            iface.root_widget_ids.remove(widget_id)
        w.parent_id = new_parent_id
        if new_parent_id and new_parent_id in iface.widgets:
            iface.widgets[new_parent_id].children.append(widget_id)
        else:
            iface.root_widget_ids.append(widget_id)
        self.modified = True

    def add_transition(self, source_id: str, target_id: str, trigger_widget_id: str, trigger_event: str, transition_type: str = "show"):
        transition = InterfaceTransition(
            source_id=source_id,
            target_id=target_id,
            trigger_widget_id=trigger_widget_id,
            trigger_event=trigger_event,
            transition_type=transition_type
        )
        self.transitions.append(transition)
        self.modified = True

    def to_dict(self) -> dict:
        return {
            "settings": {
                "namespace": self.settings.namespace,
                "header_include": self.settings.header_include,
                "target_platform": self.settings.target_platform,
                "cpp_structure": self.settings.cpp_structure,
            },
            "interfaces": {
                iid: {
                    "settings": {
                        "id": iface.settings.id,
                        "name": iface.settings.name,
                        "class_name": iface.settings.class_name,
                        "parent_class": iface.settings.parent_class,
                        "interface_type": iface.settings.interface_type,
                        "width": iface.settings.width,
                        "height": iface.settings.height,
                        "background_image": iface.settings.background_image,
                        "background_stretch": iface.settings.background_stretch,
                        "background_color": iface.settings.background_color,
                        "listeners": iface.settings.listeners,
                        "source_header": iface.settings.source_header,
                        "source_cpp": iface.settings.source_cpp,
                    },
                    "widgets": {
                        wid: {
                            "id": w.id,
                            "class_name": w.class_name,
                            "instance_name": w.instance_name,
                            "properties": w.properties,
                            "children": w.children,
                            "parent_id": w.parent_id,
                            "z_order": w.z_order,
                            "event_actions": {
                                evt: [{"action_type": a.action_type, "predefined_id": a.predefined_id, "params": a.params}
                                      for a in actions]
                                for evt, actions in w.event_actions.items()
                            },
                        }
                        for wid, w in iface.widgets.items()
                    },
                    "root_widget_ids": iface.root_widget_ids,
                    "user_code": {
                        "header_includes": iface.user_code.header_includes,
                        "cpp_includes": iface.user_code.cpp_includes,
                        "forward_declarations": iface.user_code.forward_declarations,
                        "declarations": iface.user_code.declarations,
                        "init_code": iface.user_code.init_code,
                        "destroy_code": iface.user_code.destroy_code,
                        "draw_code": iface.user_code.draw_code,
                        "update_code": iface.user_code.update_code,
                        "functions": iface.user_code.functions,
                        "post_class": iface.user_code.post_class,
                        "event_handlers": iface.user_code.event_handlers,
                    },
                }
                for iid, iface in self.interfaces.items()
            },
            "main_interface_id": self.main_interface_id,
            "current_interface_id": self._current_interface_id,
            "transitions": [
                {
                    "source_id": t.source_id,
                    "target_id": t.target_id,
                    "trigger_widget_id": t.trigger_widget_id,
                    "trigger_event": t.trigger_event,
                    "transition_type": t.transition_type,
                }
                for t in self.transitions
            ],
            "resources": self.resources,
        }

    def from_dict(self, data: dict):
        s = data.get("settings", {})
        self.settings = ProjectSettings(
            namespace=s.get("namespace", ""),
            header_include=s.get("header_include", ""),
            target_platform=s.get("target_platform", "cpp"),
            cpp_structure=s.get("cpp_structure", "qe"),
        )
        self.interfaces.clear()

        if "interfaces" in data:
            for iid, idata in data.get("interfaces", {}).items():
                isettings = idata.get("settings", {})
                settings = InterfaceSettings(
                    id=isettings.get("id", iid),
                    name=isettings.get("name", "Interface"),
                    class_name=isettings.get("class_name", "MyWidget"),
                    parent_class=isettings.get("parent_class", "Widget"),
                    interface_type=isettings.get("interface_type", "main"),
                    width=isettings.get("width", 800),
                    height=isettings.get("height", 600),
                    background_image=isettings.get("background_image", ""),
                    background_stretch=isettings.get("background_stretch", False),
                    background_color=isettings.get("background_color", "0,0,0"),
                    listeners=isettings.get("listeners", []),
                    source_header=isettings.get("source_header", ""),
                    source_cpp=isettings.get("source_cpp", ""),
                )
                iface = Interface(settings=settings)
                for wid, wd in idata.get("widgets", {}).items():
                    event_actions_data = wd.get("event_actions", {})
                    event_actions = {}
                    for evt, actions in event_actions_data.items():
                        event_actions[evt] = [EventAction(
                            action_type=a.get("action_type", "none"),
                            predefined_id=a.get("predefined_id", ""),
                            params=a.get("params", {})
                        ) for a in actions]
                    iface.widgets[wid] = WidgetInstance(
                        id=wd["id"],
                        class_name=wd["class_name"],
                        instance_name=wd.get("instance_name", ""),
                        properties=wd.get("properties", {}),
                        children=wd.get("children", []),
                        parent_id=wd.get("parent_id", ""),
                        z_order=wd.get("z_order", 0),
                        event_actions=event_actions,
                    )
                iface.root_widget_ids = idata.get("root_widget_ids", [])
                uc = idata.get("user_code", {})
                iface.user_code = ProjectCode(
                    header_includes=uc.get("header_includes", ""),
                    cpp_includes=uc.get("cpp_includes", ""),
                    forward_declarations=uc.get("forward_declarations", ""),
                    declarations=uc.get("declarations", ""),
                    init_code=uc.get("init_code", ""),
                    destroy_code=uc.get("destroy_code", ""),
                    draw_code=uc.get("draw_code", ""),
                    update_code=uc.get("update_code", ""),
                    functions=uc.get("functions", ""),
                    post_class=uc.get("post_class", ""),
                    event_handlers=uc.get("event_handlers", {}),
                )
                self.interfaces[iid] = iface
            self.main_interface_id = data.get("main_interface_id", "")
            self._current_interface_id = data.get("current_interface_id", self.main_interface_id)
        else:
            iface = Interface(settings=InterfaceSettings(
                name="Main",
                class_name=s.get("class_name", "MyWidget"),
                parent_class=s.get("parent_class", "Widget"),
                width=s.get("width", 800),
                height=s.get("height", 600),
                background_image=s.get("background_image", ""),
                background_color=s.get("background_color", "0,0,0"),
                listeners=s.get("listeners", []),
            ))
            for wid, wd in data.get("widgets", {}).items():
                event_actions_data = wd.get("event_actions", {})
                event_actions = {}
                for evt, actions in event_actions_data.items():
                    event_actions[evt] = [EventAction(
                        action_type=a.get("action_type", "none"),
                        predefined_id=a.get("predefined_id", ""),
                        params=a.get("params", {})
                    ) for a in actions]
                iface.widgets[wid] = WidgetInstance(
                    id=wd["id"],
                    class_name=wd["class_name"],
                    instance_name=wd.get("instance_name", ""),
                    properties=wd.get("properties", {}),
                    children=wd.get("children", []),
                    parent_id=wd.get("parent_id", ""),
                    z_order=wd.get("z_order", 0),
                    event_actions=event_actions,
                )
            iface.root_widget_ids = data.get("root_widget_ids", [])
            uc = data.get("user_code", {})
            iface.user_code = ProjectCode(
                header_includes=uc.get("header_includes", ""),
                cpp_includes=uc.get("cpp_includes", ""),
                declarations=uc.get("declarations", ""),
                init_code=uc.get("init_code", ""),
                destroy_code=uc.get("destroy_code", ""),
                draw_code=uc.get("draw_code", ""),
                update_code=uc.get("update_code", ""),
                functions=uc.get("functions", ""),
                event_handlers=uc.get("event_handlers", {}),
            )
            self.interfaces[iface.settings.id] = iface
            self.main_interface_id = iface.settings.id
            self._current_interface_id = iface.settings.id

        if not self.interfaces:
            self._init_main_interface()
        self.transitions = [
            InterfaceTransition(
                source_id=t.get("source_id", ""),
                target_id=t.get("target_id", ""),
                trigger_widget_id=t.get("trigger_widget_id", ""),
                trigger_event=t.get("trigger_event", ""),
                transition_type=t.get("transition_type", "show"),
            )
            for t in data.get("transitions", [])
        ]
        self.resources = data.get("resources", {})
        self.modified = False

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        self.filepath = filepath
        self.modified = False

    def load(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            self.from_dict(json.load(f))
        self.filepath = filepath
        
    def get_extension_for_platform(self, platform: str = None) -> str:
        plat = platform or self.settings.target_platform
        if plat == "csharp":
            return self.CSHARP_EXTENSION
        return self.CPP_EXTENSION
    
    def is_csharp_project(self) -> bool:
        return self.settings.target_platform == "csharp"
    
    def set_target_platform(self, platform: str):
        if platform in ("cpp", "csharp"):
            old_platform = self.settings.target_platform
            self.settings.target_platform = platform
            if old_platform != platform:
                new_width = self.settings.get_default_width()
                new_height = self.settings.get_default_height()
                for iface in self.interfaces.values():
                    old_height = iface.settings.height
                    if old_platform == "cpp" and old_height == 600:
                        iface.settings.height = new_height
                    elif old_platform == "csharp" and old_height == 480:
                        iface.settings.height = new_height
            self.modified = True
