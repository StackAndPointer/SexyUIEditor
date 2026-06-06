# -*- coding: utf-8 -*-
import sys
import ctypes
from ctypes import c_int, byref, sizeof
from core.qt_compat import QWidget, QTimer


def set_transparent_titlebar(widget: QWidget):
    if sys.platform != "win32":
        return
    
    def _apply():
        try:
            hwnd = int(widget.winId())
            
            DWMWA_CAPTION_COLOR = 35
            
            empty = ctypes.create_unicode_buffer("")
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR, byref(empty), sizeof(empty)
            )
            
            DWMWA_SYSTEMBACKDROP_TYPE = 38
            DWMWA_MICA_EFFECT = 1029
            
            value = c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_SYSTEMBACKDROP_TYPE, byref(value), sizeof(value)
            )
            
            SWP_FRAMECHANGED = 0x0020
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOZORDER = 0x0004
            ctypes.windll.user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
            )
        except Exception:
            pass
    
    QTimer.singleShot(100, _apply)
