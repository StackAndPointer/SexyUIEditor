# -*- coding: utf-8 -*-
"""
Extension Components Manager
Handles custom user-defined components with JSON definitions.
Separates C++ and C# extensions into different directories.
"""
import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

from core.component_registry import ComponentDef, PropertyDef, PropType, ComponentRegistry


_EXTENSION_DIR_NAME = "SexyUIExtensions"
_CPP_SUBDIR = "cpp"
_CSHARP_SUBDIR = "csharp"


@dataclass
class ExtensionComponentDef:
    class_name: str
    display_name: str
    description: str = ""
    parent_class: str = ""
    is_container: bool = False
    properties: List[Dict] = field(default_factory=list)
    source_code: str = ""
    header_code: str = ""
    platform: str = "cpp"
    
    def to_dict(self) -> dict:
        return {
            "class_name": self.class_name,
            "display_name": self.display_name,
            "description": self.description,
            "parent_class": self.parent_class,
            "is_container": self.is_container,
            "properties": self.properties,
            "source_code": self.source_code,
            "header_code": self.header_code,
            "platform": self.platform,
        }
    
    @classmethod
    def from_dict(cls, data: dict, platform: str = "cpp") -> "ExtensionComponentDef":
        return cls(
            class_name=data.get("class_name", ""),
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            parent_class=data.get("parent_class", ""),
            is_container=data.get("is_container", False),
            properties=data.get("properties", []),
            source_code=data.get("source_code", ""),
            header_code=data.get("header_code", ""),
            platform=platform,
        )
    
    def to_component_def(self) -> ComponentDef:
        props = []
        for p in self.properties:
            try:
                prop_type = PropType(p.get("prop_type", "string"))
            except ValueError:
                prop_type = PropType.STRING
            prop = PropertyDef(
                name=p.get("name", ""),
                prop_type=prop_type,
                default=p.get("default"),
                display_name=p.get("display_name", ""),
                enum_values=p.get("enum_values", []),
                category=p.get("category", "common"),
                tooltip=p.get("tooltip", ""),
            )
            props.append(prop)
        
        return ComponentDef(
            class_name=self.class_name,
            parent_class=self.parent_class,
            display_name=self.display_name,
            category="extension",
            properties=props,
            is_container=self.is_container,
            icon_name="extension",
            description=self.description,
        )


class ExtensionManager:
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._cpp_extensions: Dict[str, ExtensionComponentDef] = {}
        self._csharp_extensions: Dict[str, ExtensionComponentDef] = {}
        self._base_dir: Optional[str] = None
        self._current_platform: str = "cpp"
    
    def set_base_dir(self, base_dir: str):
        self._base_dir = base_dir
        self._ensure_directories()
        self._load_all()
    
    def set_platform(self, platform: str):
        if platform in ("cpp", "csharp"):
            self._current_platform = platform
            self._register_to_component_registry()
    
    def get_extension_dir(self) -> str:
        if not self._base_dir:
            return ""
        return os.path.join(self._base_dir, _EXTENSION_DIR_NAME)
    
    def get_cpp_dir(self) -> str:
        return os.path.join(self.get_extension_dir(), _CPP_SUBDIR)
    
    def get_csharp_dir(self) -> str:
        return os.path.join(self.get_extension_dir(), _CSHARP_SUBDIR)
    
    def _ensure_directories(self):
        ext_dir = self.get_extension_dir()
        if ext_dir:
            os.makedirs(os.path.join(ext_dir, _CPP_SUBDIR), exist_ok=True)
            os.makedirs(os.path.join(ext_dir, _CSHARP_SUBDIR), exist_ok=True)
    
    def _load_all(self):
        self._cpp_extensions.clear()
        self._csharp_extensions.clear()
        
        self._load_from_dir(self.get_cpp_dir(), "cpp", self._cpp_extensions)
        self._load_from_dir(self.get_csharp_dir(), "csharp", self._csharp_extensions)
        
        self._register_to_component_registry()
    
    def _load_from_dir(self, directory: str, platform: str, target_dict: Dict):
        if not directory or not os.path.isdir(directory):
            return
        
        for fname in os.listdir(directory):
            if fname.endswith(".json"):
                fpath = os.path.join(directory, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ext_def = ExtensionComponentDef.from_dict(data, platform)
                    if ext_def.class_name:
                        source_path = os.path.join(directory, f"{ext_def.class_name}.cpp" if platform == "cpp" else f"{ext_def.class_name}.cs")
                        if os.path.exists(source_path):
                            with open(source_path, "r", encoding="utf-8") as sf:
                                ext_def.source_code = sf.read()
                        
                        if platform == "cpp":
                            header_path = os.path.join(directory, f"{ext_def.class_name}.h")
                            if os.path.exists(header_path):
                                with open(header_path, "r", encoding="utf-8") as hf:
                                    ext_def.header_code = hf.read()
                        
                        target_dict[ext_def.class_name] = ext_def
                except Exception as e:
                    print(f"Failed to load extension {fname}: {e}")
    
    def _register_to_component_registry(self):
        registry = ComponentRegistry.instance()
        
        for class_name in list(self._cpp_extensions.keys()):
            if class_name in registry._defs:
                del registry._defs[class_name]
        for class_name in list(self._csharp_extensions.keys()):
            if class_name in registry._defs:
                del registry._defs[class_name]
        
        if self._current_platform == "cpp":
            for ext_def in self._cpp_extensions.values():
                comp_def = ext_def.to_component_def()
                registry._defs[ext_def.class_name] = comp_def
        else:
            for ext_def in self._csharp_extensions.values():
                comp_def = ext_def.to_component_def()
                registry._defs[ext_def.class_name] = comp_def
    
    def save_extension(self, ext_def: ExtensionComponentDef) -> bool:
        if not self._base_dir:
            return False
        
        self._ensure_directories()
        
        platform = ext_def.platform
        target_dir = self.get_cpp_dir() if platform == "cpp" else self.get_csharp_dir()
        target_dict = self._cpp_extensions if platform == "cpp" else self._csharp_extensions
        
        json_path = os.path.join(target_dir, f"{ext_def.class_name}.json")
        
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(ext_def.to_dict(), f, indent=2, ensure_ascii=False)
            
            if ext_def.source_code:
                if platform == "cpp":
                    source_path = os.path.join(target_dir, f"{ext_def.class_name}.cpp")
                else:
                    source_path = os.path.join(target_dir, f"{ext_def.class_name}.cs")
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(ext_def.source_code)
            
            if platform == "cpp" and ext_def.header_code:
                header_path = os.path.join(target_dir, f"{ext_def.class_name}.h")
                with open(header_path, "w", encoding="utf-8") as f:
                    f.write(ext_def.header_code)
            
            target_dict[ext_def.class_name] = ext_def
            
            if platform == self._current_platform:
                registry = ComponentRegistry.instance()
                registry._defs[ext_def.class_name] = ext_def.to_component_def()
            
            return True
        except Exception as e:
            print(f"Failed to save extension: {e}")
            return False
    
    def delete_extension(self, class_name: str, platform: str = None) -> bool:
        if platform is None:
            platform = self._current_platform
        
        target_dict = self._cpp_extensions if platform == "cpp" else self._csharp_extensions
        target_dir = self.get_cpp_dir() if platform == "cpp" else self.get_csharp_dir()
        
        if class_name not in target_dict:
            return False
        
        del target_dict[class_name]
        
        json_path = os.path.join(target_dir, f"{class_name}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
        
        if platform == "cpp":
            for ext in [".h", ".cpp"]:
                p = os.path.join(target_dir, f"{class_name}{ext}")
                if os.path.exists(p):
                    os.remove(p)
        else:
            cs_path = os.path.join(target_dir, f"{class_name}.cs")
            if os.path.exists(cs_path):
                os.remove(cs_path)
        
        registry = ComponentRegistry.instance()
        if class_name in registry._defs:
            del registry._defs[class_name]
        
        return True
    
    def get_extension(self, class_name: str, platform: str = None) -> Optional[ExtensionComponentDef]:
        if platform is None:
            platform = self._current_platform
        target_dict = self._cpp_extensions if platform == "cpp" else self._csharp_extensions
        return target_dict.get(class_name)
    
    def get_all_extensions(self, platform: str = None) -> Dict[str, ExtensionComponentDef]:
        if platform is None:
            platform = self._current_platform
        return dict(self._cpp_extensions if platform == "cpp" else self._csharp_extensions)
    
    def get_cpp_header_path(self, class_name: str) -> str:
        return os.path.join(self.get_cpp_dir(), f"{class_name}.h")
    
    def get_cpp_source_path(self, class_name: str) -> str:
        return os.path.join(self.get_cpp_dir(), f"{class_name}.cpp")
    
    def get_csharp_source_path(self, class_name: str) -> str:
        return os.path.join(self.get_csharp_dir(), f"{class_name}.cs")
    
    def get_used_extensions(self, interface_data: dict) -> List[str]:
        used = set()
        widgets = interface_data.get("widgets", [])
        for w in widgets:
            class_name = w.get("class_name", "")
            ext = self.get_extension(class_name)
            if ext:
                used.add(class_name)
        return list(used)


def create_default_properties() -> List[Dict]:
    return [
        {"name": "mX", "prop_type": "int", "default": 0, "display_name": "X坐标", "category": "geometry"},
        {"name": "mY", "prop_type": "int", "default": 0, "display_name": "Y坐标", "category": "geometry"},
        {"name": "mWidth", "prop_type": "int", "default": 100, "display_name": "宽度", "category": "geometry"},
        {"name": "mHeight", "prop_type": "int", "default": 100, "display_name": "高度", "category": "geometry"},
    ]
