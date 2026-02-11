"""
Medya kütüphanesi browser widget'ı
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QFileDialog, QLabel,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QIcon
from ..utils.file_utils import is_supported_media, get_file_size_mb
from ..utils.ffmpeg_utils import get_video_info, get_audio_info
import os


class MediaBrowserItem(QListWidgetItem):
    """Medya browser item'ı"""
    
    def __init__(self, filepath: str):
        super().__init__()
        self.filepath = filepath
        self.name = os.path.basename(filepath)
        self.setText(self.name)
        
        # İkon ayarla (basit)
        # TODO: Thumbnail gösterimi
        
        # Bilgileri al
        self.info = self.get_media_info()
    
    def get_media_info(self):
        """Medya bilgilerini alır"""
        info = {'size': get_file_size_mb(self.filepath)}
        
        video_info = get_video_info(self.filepath)
        if video_info:
            info.update(video_info)
        else:
            audio_info = get_audio_info(self.filepath)
            if audio_info:
                info.update(audio_info)
        
        return info


class MediaBrowser(QWidget):
    """Medya kütüphanesi browser'ı"""
    
    media_selected = pyqtSignal(str)  # Dosya yolu
    media_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_items = []
        self.setup_ui()
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Medya Kütüphanesi")
        title_label.setObjectName("title")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Ekle")
        add_btn.clicked.connect(self.add_media)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Media list
        self.media_list = QListWidget()
        self.media_list.setDragEnabled(True)
        self.media_list.setAcceptDrops(True)
        self.media_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.media_list.itemDoubleClicked.connect(self.on_double_clicked)
        self.media_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.media_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.media_list)
        
        # Info label
        self.info_label = QLabel("Medya yok")
        self.info_label.setObjectName("secondary")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
    
    def add_media(self):
        """Medya ekleme dialog'unu açar"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Medya Dosyası Seç",
            "",
            "Medya Dosyaları (*.mp4 *.mov *.avi *.mkv *.webm *.mp3 *.wav *.png *.jpg);;Tüm Dosyalar (*.*)"
        )
        
        for filepath in files:
            if is_supported_media(filepath):
                self.add_media_file(filepath)
    
    def add_media_file(self, filepath: str):
        """Listeye medya dosyası ekler"""
        if not os.path.exists(filepath):
            return
        
        # Zaten var mı kontrol et
        for item in self.media_items:
            if item.filepath == filepath:
                return
        
        item = MediaBrowserItem(filepath)
        self.media_list.addItem(item)
        self.media_items.append(item)
        
        self.update_info_label()
    
    def on_selection_changed(self):
        """Seçim değiştiğinde"""
        items = self.media_list.selectedItems()
        if items:
            item = items[0]
            if isinstance(item, MediaBrowserItem):
                self.media_selected.emit(item.filepath)
                self.update_info_label_for_item(item)
    
    def on_double_clicked(self, item):
        """Çift tıklanınca"""
        if isinstance(item, MediaBrowserItem):
            self.media_double_clicked.emit(item.filepath)
    
    def update_info_label(self):
        """Bilgi etiketini günceller"""
        count = len(self.media_items)
        if count == 0:
            self.info_label.setText("Medya yok")
        else:
            self.info_label.setText(f"{count} medya dosyası")
    
    def update_info_label_for_item(self, item: MediaBrowserItem):
        """Seçili item için bilgi gösterir"""
        info = item.info
        text = f"{item.name}\n"
        
        if 'duration' in info:
            text += f"Süre: {info['duration']:.1f}s\n"
        if 'width' in info and 'height' in info:
            text += f"Çözünürlük: {info['width']}x{info['height']}\n"
        if 'fps' in info:
            text += f"FPS: {info['fps']:.1f}\n"
        
        text += f"Boyut: {info['size']:.1f} MB"
        
        self.info_label.setText(text)
    
    def show_context_menu(self, position):
        """Sağ tık menüsü"""
        items = self.media_list.selectedItems()
        if not items:
            return
        
        menu = QMenu(self)
        
        remove_action = QAction("Kaldır", self)
        remove_action.triggered.connect(self.remove_selected)
        menu.addAction(remove_action)
        
        menu.exec_(self.media_list.mapToGlobal(position))
    
    def remove_selected(self):
        """Seçili item'ı kaldırır"""
        items = self.media_list.selectedItems()
        for item in items:
            row = self.media_list.row(item)
            self.media_list.takeItem(row)
            if item in self.media_items:
                self.media_items.remove(item)
        
        self.update_info_label()
    
    def get_all_media_files(self):
        """Tüm medya dosyalarını döndürür"""
        return [item.filepath for item in self.media_items]
    
    def dragEnterEvent(self, event):
        """Drag enter eventi"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Drop eventi (dosya sürükleme)"""
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if is_supported_media(filepath):
                self.add_media_file(filepath)
