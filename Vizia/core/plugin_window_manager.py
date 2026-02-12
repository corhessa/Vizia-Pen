# -*- coding: utf-8 -*-
"""
Plugin Window Manager
Eklenti pencerelerini merkezi olarak yöneten ve temizleyen sistem.
"""

from PyQt5.QtCore import Qt, QPoint

class PluginWindowManager:
    
    PLUGIN_WINDOW_FLAGS = (
        Qt.FramelessWindowHint | 
        Qt.WindowStaysOnTopHint | 
        Qt.Tool | 
        Qt.WindowDoesNotAcceptFocus
    )
    
    def __init__(self):
        self._windows = {}
        self._mode_states = {}
    
    def register(self, window, sub_windows=None):
        if window is not None:
            self._windows[window] = sub_windows if sub_windows else []
    
    def unregister(self, window):
        if window in self._windows:
            del self._windows[window]
    
    def bring_all_to_front(self):
        self._cleanup()
        
        for window, sub_windows in list(self._windows.items()):
            try:
                if window.isVisible():
                    window.raise_()
                for sub_win in sub_windows:
                    try:
                        if sub_win.isVisible(): sub_win.raise_()
                    except (RuntimeError, AttributeError): pass
            except (RuntimeError, AttributeError): pass
    
    def is_mouse_on_any(self, global_pos):
        self._cleanup()
        
        for window, sub_windows in list(self._windows.items()):
            try:
                if window.isVisible() and window.geometry().contains(global_pos):
                    window.raise_()
                    window.activateWindow()
                    return True
                
                for sub_win in sub_windows:
                    try:
                        if sub_win.isVisible() and sub_win.geometry().contains(global_pos):
                            sub_win.raise_()
                            sub_win.activateWindow()
                            return True
                    except (RuntimeError, AttributeError): pass
            except (RuntimeError, AttributeError): pass
        
        return False
        
    def notify_canvas_click(self):
        """
        Overlay'e (boşluğa) tıklandığında tüm kayıtlı pencerelere bildirir.
        Özellikle Geometri eklentisinin şekil seçimlerini kaldırması için kullanılır.
        """
        self._cleanup()
        for window in list(self._windows.keys()):
            try:
                # Eklenti penceresinde on_canvas_click metodu varsa çağır
                if hasattr(window, 'on_canvas_click'):
                    window.on_canvas_click()
            except (RuntimeError, AttributeError): pass
    
    def save_mode_state(self, plugin_id, mode, state):
        if plugin_id not in self._mode_states:
            self._mode_states[plugin_id] = {}
        self._mode_states[plugin_id][mode] = state
    
    def load_mode_state(self, plugin_id, mode):
        if plugin_id in self._mode_states:
            return self._mode_states[plugin_id].get(mode)
        return None
    
    def on_mode_changed(self, new_mode_is_whiteboard):
        self._cleanup()
        for window in list(self._windows.keys()):
            try:
                if hasattr(window, 'on_mode_changed'):
                    window.on_mode_changed(new_mode_is_whiteboard)
            except (RuntimeError, AttributeError): pass
    
    def apply_standard_flags(self, widget, accepts_focus=False):
        if accepts_focus:
            flags = (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        else:
            flags = self.PLUGIN_WINDOW_FLAGS
        widget.setWindowFlags(flags)
    
    def _cleanup(self):
        """
        Silinmiş veya geçersiz pencereleri listeden güvenli bir şekilde temizler.
        """
        to_remove = []
        for window in list(self._windows.keys()):
            try:
                if window is None:
                    to_remove.append(window)
                    continue
                if not hasattr(window, "isVisible"):
                    to_remove.append(window)
                    continue
                _ = window.isVisible()
            except (RuntimeError, AttributeError):
                to_remove.append(window)
        
        for window in to_remove:
            if window in self._windows:
                del self._windows[window]