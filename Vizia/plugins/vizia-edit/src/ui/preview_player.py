"""
Video önizleme widget'ı (mpv player entegrasyonu)
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from ..utils.signals import player_signals
import os

# mpv kontrolü
try:
    import mpv
    MPV_AVAILABLE = True
except ImportError:
    MPV_AVAILABLE = False
    print("python-mpv kurulu değil. QMediaPlayer fallback kullanılacak.")


class PreviewPlayer(QWidget):
    """Video önizleme oynatıcısı"""
    
    position_changed = pyqtSignal(float)
    duration_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.duration = 0.0
        self.position = 0.0
        self.is_playing = False
        
        # mpv player (varsa)
        self.mpv_player = None
        if MPV_AVAILABLE:
            try:
                self.mpv_player = mpv.MPV(
                    wid=str(int(self.winId())),
                    vo='gpu',
                    keep_open='yes'
                )
            except Exception as e:
                print(f"mpv başlatılamadı: {e}")
                self.mpv_player = None
        
        self.setup_ui()
        
        # Position timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)  # 100ms
    
    def setup_ui(self):
        """UI elemanlarını oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video container
        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: #000000;")
        self.video_container.setMinimumHeight(400)
        layout.addWidget(self.video_container, stretch=1)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setFixedSize(40, 40)
        controls_layout.addWidget(self.play_btn)
        
        # Seek slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.on_seek)
        controls_layout.addWidget(self.seek_slider)
        
        # Time label
        self.time_label = QLabel("00:00:00 / 00:00:00")
        controls_layout.addWidget(self.time_label)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(self.volume_slider)
        
        layout.addLayout(controls_layout)
    
    def load_file(self, filepath: str):
        """Video dosyası yükler"""
        if not os.path.exists(filepath):
            return
        
        self.current_file = filepath
        
        if self.mpv_player:
            try:
                self.mpv_player.loadfile(filepath)
                self.mpv_player.pause = True
                self.duration = self.mpv_player.duration or 0.0
                self.duration_changed.emit(self.duration)
            except Exception as e:
                print(f"Video yükleme hatası: {e}")
        
        self.is_playing = False
        self.play_btn.setText("▶")
    
    def play(self):
        """Oynatmayı başlatır"""
        if self.mpv_player and self.current_file:
            self.mpv_player.pause = False
            self.is_playing = True
            self.play_btn.setText("⏸")
            player_signals.play_started.emit()
    
    def pause(self):
        """Oynatmayı duraklatır"""
        if self.mpv_player:
            self.mpv_player.pause = True
            self.is_playing = False
            self.play_btn.setText("▶")
            player_signals.play_paused.emit()
    
    def stop(self):
        """Oynatmayı durdurur"""
        if self.mpv_player:
            self.mpv_player.command('stop')
            self.is_playing = False
            self.play_btn.setText("▶")
            player_signals.play_stopped.emit()
    
    def toggle_play(self):
        """Oynat/Duraklat toggle"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def seek(self, position: float):
        """Belirtilen pozisyona atlar (saniye)"""
        if self.mpv_player:
            try:
                self.mpv_player.seek(position, reference='absolute')
                self.position = position
                self.position_changed.emit(position)
            except:
                pass
    
    def on_seek(self, value):
        """Seek slider hareket ettiğinde"""
        if self.duration > 0:
            position = (value / 1000.0) * self.duration
            self.seek(position)
    
    def on_volume_change(self, value):
        """Ses seviyesi değiştiğinde"""
        if self.mpv_player:
            self.mpv_player.volume = value
        player_signals.volume_changed.emit(value)
    
    def update_position(self):
        """Oynatma pozisyonunu günceller"""
        if self.mpv_player and self.is_playing:
            try:
                self.position = self.mpv_player.time_pos or 0.0
                self.position_changed.emit(self.position)
                
                # Slider'ı güncelle
                if self.duration > 0:
                    slider_pos = int((self.position / self.duration) * 1000)
                    self.seek_slider.blockSignals(True)
                    self.seek_slider.setValue(slider_pos)
                    self.seek_slider.blockSignals(False)
                
                # Time label'ı güncelle
                self.update_time_label()
            except:
                pass
    
    def update_time_label(self):
        """Zaman etiketini günceller"""
        pos_str = self.format_time(self.position)
        dur_str = self.format_time(self.duration)
        self.time_label.setText(f"{pos_str} / {dur_str}")
    
    def format_time(self, seconds: float) -> str:
        """Saniyeyi HH:MM:SS formatına çevirir"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def closeEvent(self, event):
        """Widget kapatılırken"""
        if self.mpv_player:
            try:
                self.mpv_player.terminate()
            except:
                pass
        super().closeEvent(event)
