# -*- coding: utf-8 -*-
import sys
import os
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from core.i18n import I18nManager
from core.resource_manager import ResourceManager


def _load_default_resources():
    res_mgr = ResourceManager.instance()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pak_dir = os.path.join(base_dir, "pak")

    if not os.path.isdir(pak_dir):
        return

    img_dir = os.path.join(pak_dir, "images")
    if os.path.isdir(img_dir):
        for fname in sorted(os.listdir(img_dir)):
            if fname.lower().endswith((".png", ".jpg", ".bmp", ".gif", ".tga")):
                name = os.path.splitext(fname)[0]
                fpath = os.path.join("images", fname)
                res_mgr.add_image(name, fpath)

    font_dir = os.path.join(pak_dir, "data")
    if os.path.isdir(font_dir):
        for fname in sorted(os.listdir(font_dir)):
            if fname.lower().endswith(".txt") and not fname.startswith("_"):
                name = os.path.splitext(fname)[0]
                fpath = os.path.join("data", fname)
                res_mgr.add_font(name, fpath)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SexyUIEditor")
    app.setOrganizationName("StackAndPointer")
    app.setApplicationVersion("1.1")

    i18n = I18nManager.instance()
    i18n.init_locale()

    _load_default_resources()

    window = MainWindow()
    window.show()
    
    # Handle command line arguments (file association)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path and os.path.exists(file_path):
            window.load_project(file_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
