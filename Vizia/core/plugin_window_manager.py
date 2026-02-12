# -*- coding: utf-8 -*-
"""
Plugin Window Manager
Eklenti pencerelerini merkezi olarak yöneten sistem.
"""

from PyQt5.QtCore import Qt, QPoint


class PluginWindowManager:
    """
    Eklenti pencerelerini kaydeder, ön plana getirir ve mod değişikliklerini yönetir.
    """
    
    # Eklenti pencereleri için standart bayraklar
    PLUGIN_WINDOW_FLAGS = (
        Qt.FramelessWindowHint | 
        Qt.WindowStaysOnTopHint | 
        Qt.Tool | 
        Qt.WindowDoesNotAcceptFocus
    )
    
    def __init__(self):
        # Kayıtlı pencereler: {window: [sub_window1, sub_window2, ...]}
        self._windows = {}
        # Mod hafızası: {plugin_id: {mode: state}}
        self._mode_states = {}
    
    def register(self, window, sub_windows=None):
        """
        Bir eklenti penceresini ve opsiyonel alt pencerelerini kayıt eder.
        
        Args:
            window: Ana eklenti penceresi
            sub_windows: Alt pencereler listesi (opsiyonel)
        """
        if window is not None:
            self._windows[window] = sub_windows if sub_windows else []
    
    def unregister(self, window):
        """
        Pencereyi kayıttan çıkarır.
        
        Args:
            window: Kayıttan çıkarılacak pencere
        """
        if window in self._windows:
            del self._windows[window]
    
    def bring_all_to_front(self):
        """
        Tüm kayıtlı ve görünür pencereleri raise_() ile öne getirir.
        """
        self._cleanup()
        
        for window, sub_windows in list(self._windows.items()):
            try:
                if window.isVisible():
                    window.raise_()
                
                # Alt pencereleri de öne getir
                for sub_win in sub_windows:
                    try:
                        if sub_win.isVisible():
                            sub_win.raise_()
                    except (RuntimeError, AttributeError):
                        pass  # Alt pencere silinmiş veya QWidget değil
            except (RuntimeError, AttributeError):
                pass  # Ana pencere silinmiş veya QWidget değil
    
    def is_mouse_on_any(self, global_pos):
        """
        Farenin herhangi bir eklenti penceresinin üzerinde olup olmadığını kontrol eder.
        Üzerindeyse raise_() + activateWindow() çağırır ve True döner.
        
        Args:
            global_pos: Global koordinatlarda fare pozisyonu (QPoint)
            
        Returns:
            bool: Fare bir eklenti penceresinin üzerindeyse True
        """
        self._cleanup()
        
        for window, sub_windows in list(self._windows.items()):
            try:
                if window.isVisible() and window.geometry().contains(global_pos):
                    window.raise_()
                    window.activateWindow()
                    return True
                
                # Alt pencereleri de kontrol et
                for sub_win in sub_windows:
                    try:
                        if sub_win.isVisible() and sub_win.geometry().contains(global_pos):
                            sub_win.raise_()
                            sub_win.activateWindow()
                            return True
                    except (RuntimeError, AttributeError):
                        pass  # Alt pencere silinmiş veya QWidget değil
            except (RuntimeError, AttributeError):
                pass  # Ana pencere silinmiş veya QWidget değil
        
        return False
    
    def save_mode_state(self, plugin_id, mode, state):
        """
        Eklentinin mevcut moddaki durumunu kaydeder.
        
        Args:
            plugin_id: Eklentinin benzersiz kimliği
            mode: Mod adı (örn: 'whiteboard' veya 'desktop')
            state: Kaydedilecek durum verisi
        """
        if plugin_id not in self._mode_states:
            self._mode_states[plugin_id] = {}
        self._mode_states[plugin_id][mode] = state
    
    def load_mode_state(self, plugin_id, mode):
        """
        Kaydedilmiş durumu yükler.
        
        Args:
            plugin_id: Eklentinin benzersiz kimliği
            mode: Mod adı
            
        Returns:
            Kaydedilmiş durum verisi veya None
        """
        if plugin_id in self._mode_states:
            return self._mode_states[plugin_id].get(mode)
        return None
    
    def on_mode_changed(self, new_mode_is_whiteboard):
        """
        Mod değiştiğinde tüm kayıtlı pencerelerde on_mode_changed() metodu varsa çağırır.
        
        Args:
            new_mode_is_whiteboard: True ise whiteboard modu, False ise desktop modu
        """
        self._cleanup()
        
        for window in list(self._windows.keys()):
            try:
                if hasattr(window, 'on_mode_changed'):
                    window.on_mode_changed(new_mode_is_whiteboard)
            except (RuntimeError, AttributeError):
                pass  # Pencere silinmiş veya geçersiz
    
    def apply_standard_flags(self, widget, accepts_focus=False):
        """
        Eklenti pencerelerine standart bayrakları uygular.
        
        Args:
            widget: Bayrak uygulanacak widget
            accepts_focus: True ise WindowDoesNotAcceptFocus bayrağı eklenmez
        """
        if accepts_focus:
            flags = (Qt.FramelessWindowHint | 
                    Qt.WindowStaysOnTopHint | 
                    Qt.Tool)
        else:
            flags = self.PLUGIN_WINDOW_FLAGS
        
        widget.setWindowFlags(flags)
    
    def _cleanup(self):
        """
        Silinmiş (RuntimeError veren) veya geçersiz (AttributeError veren) pencereleri listeden çıkarır.
        """
        to_remove = []
        for window in list(self._windows.keys()):
            try:
                # Pencereyi test et - QWidget olmayan nesneleri de tespit et
                _ = window.isVisible()
            except (RuntimeError, AttributeError):
                # Pencere silinmiş veya QWidget değil
                to_remove.append(window)
        
        for window in to_remove:
            del self._windows[window]
