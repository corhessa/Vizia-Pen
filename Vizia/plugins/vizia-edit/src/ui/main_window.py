"""
Ana editor penceresi (CapCut benzeri layout)
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QMenu, QAction, QToolBar,
                             QFileDialog, QMessageBox, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QIcon

from .title_bar import TitleBar
from .timeline_widget import TimelineWidget
from .preview_player import PreviewPlayer
from .media_browser import MediaBrowser
from .properties_panel import PropertiesPanel
from .effects_panel import EffectsPanel
from .text_editor import TextEditor
from .audio_mixer import AudioMixer
from .export_dialog import ExportDialog
from .styles import get_main_stylesheet

from ..core.project import Project
from ..core.timeline import Clip
from ..core.video_engine import VideoEngine
from ..utils.constants import SHORTCUTS, AUTOSAVE_INTERVAL
from ..utils.signals import project_signals, timeline_signals
from ..utils.file_utils import is_video_file, is_audio_file, is_image_file
from ..utils.ffmpeg_utils import check_ffmpeg


class MainWindow(QMainWindow):
    """Ana video editör penceresi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = Project()
        self.video_engine = VideoEngine()
        
        # FFmpeg kontrolü
        if not check_ffmpeg():
            QMessageBox.warning(
                self,
                "FFmpeg Bulunamadı",
                "FFmpeg bulunamadı. Video işleme özellikleri çalışmayacak.\n"
                "Lütfen FFmpeg'i sisteminize kurun."
            )
        
        self.setup_window()
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_autosave()
        self.connect_signals()
        
        self.setStyleSheet(get_main_stylesheet())
    
    def setup_window(self):
        """Pencere ayarları"""
        self.setWindowTitle("Vizia Edit - Video Düzenleyici")
        self.resize(1600, 900)
        
        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Ana içerik splitter'ı
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Medya browser ve efektler
        left_panel = QWidget()
        left_panel.setObjectName("panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(4, 4, 4, 4)
        
        self.media_browser = MediaBrowser()
        left_layout.addWidget(self.media_browser, stretch=2)
        
        self.effects_panel = EffectsPanel()
        left_layout.addWidget(self.effects_panel, stretch=1)
        
        content_splitter.addWidget(left_panel)
        
        # Orta panel - Preview ve timeline
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview player
        self.preview_player = PreviewPlayer()
        center_layout.addWidget(self.preview_player, stretch=2)
        
        # Timeline
        self.timeline_widget = TimelineWidget()
        self.timeline_widget.set_timeline(self.project.timeline)
        center_layout.addWidget(self.timeline_widget, stretch=1)
        
        content_splitter.addWidget(center_widget)
        
        # Sağ panel - Properties, text, audio
        right_panel = QWidget()
        right_panel.setObjectName("panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 4, 4, 4)
        
        self.properties_panel = PropertiesPanel()
        right_layout.addWidget(self.properties_panel, stretch=1)
        
        self.text_editor = TextEditor()
        right_layout.addWidget(self.text_editor, stretch=1)
        
        self.audio_mixer = AudioMixer()
        right_layout.addWidget(self.audio_mixer, stretch=1)
        
        content_splitter.addWidget(right_panel)
        
        # Splitter oranları
        content_splitter.setStretchFactor(0, 1)  # Sol
        content_splitter.setStretchFactor(1, 3)  # Orta
        content_splitter.setStretchFactor(2, 1)  # Sağ
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
    
    def setup_menu(self):
        """Menü çubuğunu oluşturur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu("Dosya")
        
        new_action = QAction("Yeni Proje", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Aç", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Kaydet", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Farklı Kaydet", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("Medya Ekle", self)
        import_action.setShortcut(SHORTCUTS['import'])
        import_action.triggered.connect(self.import_media)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export", self)
        export_action.setShortcut(SHORTCUTS['export'])
        export_action.triggered.connect(self.export_project)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Düzenle menüsü
        edit_menu = menubar.addMenu("Düzenle")
        
        undo_action = QAction("Geri Al", self)
        undo_action.setShortcut(SHORTCUTS['undo'])
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Yinele", self)
        redo_action.setShortcut(SHORTCUTS['redo'])
        edit_menu.addAction(redo_action)
        
        # Görünüm menüsü
        view_menu = menubar.addMenu("Görünüm")
        
        zoom_in_action = QAction("Yakınlaştır", self)
        zoom_in_action.setShortcut(SHORTCUTS['zoom_in'])
        zoom_in_action.triggered.connect(self.timeline_widget.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Uzaklaştır", self)
        zoom_out_action.setShortcut(SHORTCUTS['zoom_out'])
        zoom_out_action.triggered.connect(self.timeline_widget.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu("Yardım")
        
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Toolbar'ı oluşturur"""
        toolbar = QToolBar("Ana Araçlar")
        self.addToolBar(toolbar)
        
        # Placeholder butonlar
        toolbar.addAction("▶ Oynat")
        toolbar.addAction("⏸ Duraklat")
        toolbar.addAction("⏹ Dur")
        toolbar.addSeparator()
        toolbar.addAction("✂ Kes")
        toolbar.addAction("📋 Kopyala")
        toolbar.addAction("📄 Yapıştır")
    
    def setup_shortcuts(self):
        """Klavye kısayollarını ayarlar"""
        # Play/Pause - Space
        # TODO: Implement keyboard shortcuts
        pass
    
    def setup_autosave(self):
        """Otomatik kaydetmeyi ayarlar"""
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(AUTOSAVE_INTERVAL * 1000)  # ms
    
    def connect_signals(self):
        """Sinyalleri bağlar"""
        # Medya browser
        self.media_browser.media_double_clicked.connect(self.on_media_double_clicked)
        
        # Timeline
        self.timeline_widget.playhead_moved.connect(self.on_playhead_moved)
        
        # Text editor
        self.text_editor.text_added.connect(self.on_text_added)
        
        # Project signals
        project_signals.project_modified.connect(self.on_project_modified)
    
    def new_project(self):
        """Yeni proje oluşturur"""
        # TODO: Mevcut projeyi kaydetme kontrolü
        self.project = Project()
        self.timeline_widget.set_timeline(self.project.timeline)
        self.title_bar.set_title("Vizia Edit - Yeni Proje")
        self.status_bar.showMessage("Yeni proje oluşturuldu")
    
    def open_project(self):
        """Proje açar"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Proje Aç",
            "",
            "Vizia Proje (*.vzproj)"
        )
        
        if filepath:
            project = Project.load(filepath)
            if project:
                self.project = project
                self.timeline_widget.set_timeline(self.project.timeline)
                self.title_bar.set_title(f"Vizia Edit - {self.project.name}")
                self.status_bar.showMessage(f"Proje açıldı: {filepath}")
    
    def save_project(self):
        """Projeyi kaydeder"""
        if self.project.filepath:
            self.project.save()
            self.status_bar.showMessage("Proje kaydedildi")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Projeyi farklı kaydet"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Projeyi Kaydet",
            "",
            "Vizia Proje (*.vzproj)"
        )
        
        if filepath:
            self.project.save(filepath)
            self.title_bar.set_title(f"Vizia Edit - {self.project.name}")
            self.status_bar.showMessage(f"Proje kaydedildi: {filepath}")
    
    def autosave(self):
        """Otomatik kaydetme"""
        if self.project.filepath and self.project.modified:
            self.project.save()
            self.status_bar.showMessage("Otomatik kaydedildi", 2000)
    
    def import_media(self):
        """Medya ekleme"""
        self.media_browser.add_media()
    
    def export_project(self):
        """Projeyi export eder"""
        dialog = ExportDialog(self.project.timeline, self)
        dialog.exec_()
    
    def on_media_double_clicked(self, filepath: str):
        """Medya çift tıklanınca timeline'a ekler"""
        # Yeni klip oluştur
        clip = Clip(filepath=filepath)
        
        # Video bilgilerini al
        if is_video_file(filepath):
            info = self.video_engine.get_video_info(filepath)
            if info:
                clip.media_duration = info.get('duration', 0)
                clip.duration = clip.media_duration
                clip.media_type = 'video'
        elif is_audio_file(filepath):
            clip.media_type = 'audio'
        elif is_image_file(filepath):
            clip.media_type = 'image'
            clip.duration = 5.0  # 5 saniye varsayılan
        
        # İlk uygun track'e ekle
        if clip.media_type == 'video':
            track_index = 0
        elif clip.media_type == 'audio':
            track_index = 1
        else:
            track_index = 0
        
        self.timeline_widget.add_clip_to_track(track_index, clip)
        self.project.mark_modified()
    
    def on_playhead_moved(self, position: float):
        """Playhead hareket ettiğinde preview'ı günceller"""
        self.preview_player.seek(position)
    
    def on_text_added(self, text_data: dict):
        """Metin eklendiğinde"""
        # Yeni text clip oluştur
        clip = Clip()
        clip.media_type = 'text'
        clip.text_content = text_data['content']
        clip.text_font = text_data['font']
        clip.text_size = text_data['size']
        clip.text_color = text_data['color']
        clip.text_position = text_data['position']
        clip.duration = 5.0  # 5 saniye varsayılan
        clip.name = "Metin: " + text_data['content'][:20]
        
        # Text track'e ekle (varsa)
        # TODO: Text track oluştur veya bul
        self.project.mark_modified()
    
    def on_project_modified(self):
        """Proje değiştiğinde başlığı güncelle"""
        title = f"Vizia Edit - {self.project.name}"
        if self.project.modified:
            title += " *"
        self.title_bar.set_title(title)
    
    def show_about(self):
        """Hakkında dialog'u"""
        QMessageBox.about(
            self,
            "Vizia Edit Hakkında",
            "<h2>Vizia Edit</h2>"
            "<p>Profesyonel Video Düzenleyici</p>"
            "<p>Vizia ekosistemi için geliştirilmiştir.</p>"
            "<p>Version 1.0.0</p>"
        )
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        if self.project.modified:
            reply = QMessageBox.question(
                self,
                "Kaydedilmemiş Değişiklikler",
                "Projeyi kaydetmek ister misiniz?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_project()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
