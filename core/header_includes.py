# -*- coding: utf-8 -*-
"""
Header include manager for different C++ project structures.
Supports QE and Portable project structures.
"""

from typing import Dict, List
from core.i18n import tr


class HeaderIncludeManager:
    """
    Manages header file includes for different C++ project structures.
    
    QE Structure: Uses relative paths like "../../SexyAppFramework/Widget.h"
    Portable Structure: Uses simplified paths like "widget/Widget.h"
    """
    
    STRUCTURE_QE = "qe"
    STRUCTURE_PORTABLE = "portable"
    
    _INCLUDE_MAP_QE: Dict[str, str] = {
        "Widget": "../../SexyAppFramework/Widget.h",
        "ButtonListener": "../../SexyAppFramework/ButtonListener.h",
        "CheckboxListener": "../../SexyAppFramework/CheckboxListener.h",
        "SliderListener": "../../SexyAppFramework/SliderListener.h",
        "EditListener": "../../SexyAppFramework/EditListener.h",
        "Dialog": "../../SexyAppFramework/Dialog.h",
        "ButtonWidget": "../../SexyAppFramework/ButtonWidget.h",
        "EditWidget": "../../SexyAppFramework/EditWidget.h",
        "Checkbox": "../../SexyAppFramework/Checkbox.h",
        "Slider": "../../SexyAppFramework/Slider.h",
        "DialogButton": "../../SexyAppFramework/DialogButton.h",
        "ListWidget": "../../SexyAppFramework/ListWidget.h",
        "ScrollWidget": "../../SexyAppFramework/ScrollWidget.h",
        "HyperlinkWidget": "../../SexyAppFramework/HyperlinkWidget.h",
        "ScrollbuttonWidget": "../../SexyAppFramework/ScrollbuttonWidget.h",
        "TextWidget": "../../SexyAppFramework/TextWidget.h",
        "Image": "../../SexyAppFramework/Image.h",
        "Font": "../../SexyAppFramework/Font.h",
        "Graphics": "../../SexyAppFramework/Graphics.h",
        "Color": "../../SexyAppFramework/Color.h",
        "Rect": "../../SexyAppFramework/Rect.h",
        "SexyVector": "../../SexyAppFramework/SexyVector.h",
        "WidgetManager": "../../SexyAppFramework/WidgetManager.h",
        "WidgetContainer": "../../SexyAppFramework/WidgetContainer.h",
        "MemoryImage": "../../SexyAppFramework/MemoryImage.h",
        "DDImage": "../../SexyAppFramework/DDImage.h",
        "ResourceManager": "../../SexyAppFramework/ResourceManager.h",
        "SoundManager": "../../SexyAppFramework/SoundManager.h",
        "Music": "../../SexyAppFramework/Music.h",
        "SoundInstance": "../../SexyAppFramework/SoundInstance.h",
        "PerfTimer": "../../SexyAppFramework/PerfTimer.h",
        "Debug": "../../SexyAppFramework/Debug.h",
        "ModMusic": "../../SexyAppFramework/ModMusic.h",
        "BufferedVirtualIO": "../../SexyAppFramework/BufferedVirtualIO.h",
        "XMLParser": "../../SexyAppFramework/XMLParser.h",
        "XMLElement": "../../SexyAppFramework/XMLElement.h",
        "SysFont": "../../SexyAppFramework/SysFont.h",
        "FontData": "../../SexyAppFramework/FontData.h",
        "GameButton": "GameButton.h",
        "NewLawnButton": "NewLawnButton.h",
        "LawnDialog": "LawnDialog.h",
        "LawnStoneButton": "LawnStoneButton.h",
        "LawnEditWidget": "LawnEditWidget.h",
        "ConstEnums": "../../ConstEnums.h",
        "GameConstants": "../../GameConstants.h",
    }
    
    _INCLUDE_MAP_PORTABLE: Dict[str, str] = {
        "Widget": "widget/Widget.h",
        "ButtonListener": "widget/ButtonListener.h",
        "CheckboxListener": "widget/CheckboxListener.h",
        "SliderListener": "widget/SliderListener.h",
        "EditListener": "widget/EditListener.h",
        "Dialog": "widget/Dialog.h",
        "ButtonWidget": "widget/ButtonWidget.h",
        "EditWidget": "widget/EditWidget.h",
        "Checkbox": "widget/Checkbox.h",
        "Slider": "widget/Slider.h",
        "DialogButton": "widget/DialogButton.h",
        "ListWidget": "widget/ListWidget.h",
        "ScrollWidget": "widget/ScrollWidget.h",
        "HyperlinkWidget": "widget/HyperlinkWidget.h",
        "ScrollbuttonWidget": "widget/ScrollbuttonWidget.h",
        "TextWidget": "widget/TextWidget.h",
        "Image": "image/Image.h",
        "Font": "font/Font.h",
        "Graphics": "graphics/Graphics.h",
        "Color": "misc/Color.h",
        "Rect": "misc/Rect.h",
        "SexyVector": "misc/SexyVector.h",
        "WidgetManager": "widget/WidgetManager.h",
        "WidgetContainer": "widget/WidgetContainer.h",
        "MemoryImage": "image/MemoryImage.h",
        "DDImage": "image/DDImage.h",
        "ResourceManager": "resource/ResourceManager.h",
        "SoundManager": "sound/SoundManager.h",
        "Music": "sound/Music.h",
        "SoundInstance": "sound/SoundInstance.h",
        "PerfTimer": "misc/PerfTimer.h",
        "Debug": "misc/Debug.h",
        "ModMusic": "sound/ModMusic.h",
        "BufferedVirtualIO": "misc/BufferedVirtualIO.h",
        "XMLParser": "xml/XMLParser.h",
        "XMLElement": "xml/XMLElement.h",
        "SysFont": "font/SysFont.h",
        "FontData": "font/FontData.h",
        "GameButton": "GameButton.h",
        "NewLawnButton": "NewLawnButton.h",
        "LawnDialog": "LawnDialog.h",
        "LawnStoneButton": "LawnStoneButton.h",
        "LawnEditWidget": "LawnEditWidget.h",
        "ConstEnums": "../../ConstEnums.h",
        "GameConstants": "../../GameConstants.h",
    }
    
    @classmethod
    def get_include(cls, class_name: str, structure: str = "portable") -> str:
        """
        Get the include path for a class.
        
        Args:
            class_name: The class name (e.g., "Widget", "ButtonWidget")
            structure: The project structure ("qe" or "portable")
            
        Returns:
            The include path for the class
        """
        if structure == cls.STRUCTURE_QE:
            return cls._INCLUDE_MAP_QE.get(class_name, f"{class_name}.h")
        else:
            return cls._INCLUDE_MAP_PORTABLE.get(class_name, f"{class_name}.h")
    
    @classmethod
    def get_includes_for_classes(cls, class_names: List[str], structure: str = "portable") -> List[str]:
        """
        Get include paths for multiple classes.
        
        Args:
            class_names: List of class names
            structure: The project structure ("qe" or "portable")
            
        Returns:
            List of include paths, sorted and deduplicated
        """
        includes = set()
        for class_name in class_names:
            include = cls.get_include(class_name, structure)
            if include:
                includes.add(include)
        return sorted(list(includes))
    
    @classmethod
    def generate_include_statements(cls, class_names: List[str], structure: str = "portable") -> str:
        """
        Generate include statements for multiple classes.
        
        Args:
            class_names: List of class names
            structure: The project structure ("qe" or "portable")
            
        Returns:
            String containing all include statements
        """
        includes = cls.get_includes_for_classes(class_names, structure)
        return "\n".join(f'#include "{inc}"' for inc in includes)
    
    @classmethod
    def get_structure_display_name(cls, structure: str) -> str:
        """
        Get the display name for a project structure.
        
        Args:
            structure: The project structure ("qe" or "portable")
            
        Returns:
            The display name
        """
        if structure == cls.STRUCTURE_QE:
            return tr("structure.qe", "QE")
        else:
            return tr("structure.portable", "Portable")
    
    @classmethod
    def get_structure_description(cls, structure: str) -> str:
        """
        Get the description for a project structure.
        
        Args:
            structure: The project structure ("qe" or "portable")
            
        Returns:
            The description
        """
        if structure == cls.STRUCTURE_QE:
            return tr("structure.qe.desc", "QE project structure with relative paths (../../SexyAppFramework/)")
        else:
            return tr("structure.portable.desc", "Portable project structure with simplified paths (widget/)")

    @classmethod
    def get_available_structures(cls) -> List[str]:
        """
        Get list of available project structures.
        
        Returns:
            List of structure identifiers
        """
        return [cls.STRUCTURE_QE, cls.STRUCTURE_PORTABLE]
