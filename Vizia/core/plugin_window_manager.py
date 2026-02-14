# -*- coding: utf-8 -*-
"""
Plugin Window Manager
Eklenti pencerelerini merkezi olarak yöneten ve temizleyen sistem.
"""

from PyQt5.QtCore import Qt

class PluginWindowManager:
    
    PLUGIN_WINDOW_FLAGS = (
        Qt.FramelessWindowHint | 
        Qt.WindowStaysOnTopHint | 
        Qt.Tool | 
        Qt.WindowDoesNotAcceptFocus
    )
    
    # [EVLAT EDİNME] Artık ana ekranı (overlay) tanıyor
    def __init__(self, overlay=None):
        self.overlay = overlay
        self._windows = {}
        self._mode_states = {}
    
    def register(self, window, sub_windows=None):
        if window is not None:
            # [ANA ÇÖZÜM] Sisteme giren eklenti penceresi (örn. Recorder) ana ekrana evlatlık verilir.
            if self.overlay:
                flags = window.windowFlags()
                window.setParent(self.overlay)
                # Qt.Tool bayrağı onun ebeveyni içinde gömülü değil, üstünde yüzen bir araç olmasını sağlar.
                window.setWindowFlags(flags | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
                
            self._windows[window] = sub_windows if sub_windows else []
            
            # Alt pencereler (örn: Recorder ayar paneli) için de aynısı yapılır
            if sub_windows and self.overlay:
                for sub_win in sub_windows:
                    if sub_win is not None:
                        s_flags = sub_win.windowFlags()
                        sub_win.setParent(self.overlay)
                        sub_win.setWindowFlags(s_flags | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
    
    def unregister(self, window):
        if window in self._windows:
            del self._windows[window]
    
    def bring_all_to_front(self):
        self._cleanup()
        for window, sub_windows in list(self._windows.items()):
            try:
                if window.isVisible(): window.raise_()
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
                    return True
                for sub_win in sub_windows:
                    try:
                        if sub_win.isVisible() and sub_win.geometry().contains(global_pos):
                            return True
                    except (RuntimeError, AttributeError): pass
            except (RuntimeError, AttributeError): pass
        return False
        
    def notify_canvas_click(self):
        self._cleanup()
        for window in list(self._windows.keys()):
            try:
                if hasattr(window, 'on_canvas_click'): window.on_canvas_click()
            except (RuntimeError, AttributeError): pass
    
    def save_mode_state(self, plugin_id, mode, state):
        if plugin_id not in self._mode_states: self._mode_states[plugin_id] = {}
        self._mode_states[plugin_id][mode] = state
    
    def load_mode_state(self, plugin_id, mode):
        if plugin_id in self._mode_states: return self._mode_states[plugin_id].get(mode)
        return None
    
    def on_mode_changed(self, new_mode_is_whiteboard):
        self._cleanup()
        for window in list(self._windows.keys()):
            try:
                if hasattr(window, 'on_mode_changed'): window.on_mode_changed(new_mode_is_whiteboard)
            except (RuntimeError, AttributeError): pass
    
    def apply_standard_flags(self, widget, accepts_focus=False):
        if accepts_focus:
            flags = (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        else:
            flags = self.PLUGIN_WINDOW_FLAGS
        widget.setWindowFlags(flags)
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
    
    def _cleanup(self):
        to_remove = []
        for window in list(self._windows.keys()):
            try:
                if window is None or not hasattr(window, "isVisible"):
                    to_remove.append(window)
                    continue
                _ = window.isVisible()
            except (RuntimeError, AttributeError):
                to_remove.append(window)
        
        for window in to_remove:
            if window in self._windows: del self._windows[window]