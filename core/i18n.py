# -*- coding: utf-8 -*-
import json
import os
import locale
from PyQt6.QtCore import pyqtSignal, QObject

_I18N_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "i18n")

SUPPORTED_LOCALES = {
    "zh_CN": "简体中文",
    "en": "English",
}


class I18nManager(QObject):
    _instance = None
    _translations = {}
    _current_locale = "zh_CN"
    locale_changed = pyqtSignal(str)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()

    def detect_system_locale(self) -> str:
        try:
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale:
                if sys_locale.startswith("zh"):
                    return "zh_CN"
                elif sys_locale.startswith("en"):
                    return "en"
        except Exception:
            pass
        return "en"

    def get_saved_locale(self) -> str:
        from PyQt6.QtCore import QSettings
        settings = QSettings("SexyUIEditor", "SexyUIEditor")
        return settings.value("language", "", type=str)

    def save_locale(self, locale_name: str):
        from PyQt6.QtCore import QSettings
        settings = QSettings("SexyUIEditor", "SexyUIEditor")
        settings.setValue("language", locale_name)

    def init_locale(self):
        saved = self.get_saved_locale()
        if saved and saved in SUPPORTED_LOCALES:
            self.load_locale(saved)
        else:
            sys_locale = self.detect_system_locale()
            self.load_locale(sys_locale)
            self.save_locale(sys_locale)

    def load_locale(self, locale_name):
        if locale_name not in SUPPORTED_LOCALES:
            locale_name = "en"
        self._current_locale = locale_name
        path = os.path.join(_I18N_DIR, f"{locale_name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self._translations = json.load(f)
        else:
            self._translations = {}
        self.locale_changed.emit(locale_name)

    def tr(self, key, default=None):
        val = self._translations.get(key)
        if val is not None:
            return val
        if default is not None:
            return default
        return key

    @property
    def current_locale(self):
        return self._current_locale

    def get_available_locales(self):
        return list(SUPPORTED_LOCALES.keys())

    def get_locale_name(self, locale_code: str) -> str:
        return SUPPORTED_LOCALES.get(locale_code, locale_code)


def tr(key, default=None):
    return I18nManager.instance().tr(key, default)
