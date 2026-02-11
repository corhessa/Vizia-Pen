

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt, pyqtSignal

# Try to import WebEngine, fallback to simple text browser if not available
HAS_WEBENGINE = False
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
    HAS_WEBENGINE = True
except ImportError:
    print("⚠️  [WARNING] PyQtWebEngine not found. Using fallback mode.")
    print("   Install it with: pip install PyQtWebEngine==5.15.7")

# Relative import from same package
try:
    from .resources import ViziaEngineAssets
except ImportError:
    # Fallback for direct execution
    from resources import ViziaEngineAssets

class ViziaEngineItem(QWidget):
    request_close = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Pencere ayarları - Normal pencere modu
        self.setWindowTitle("Vizia Studio Pro - 3D Editör")
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        # Tam ekran durumu
        self.is_fullscreen = False
        
        # Ana Düzen
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- 2. WEB TARAYICI VE AYARLAR ---
        if HAS_WEBENGINE:
            self.browser = QWebEngineView()
            self.browser.setStyleSheet("background-color: #1c1c1e;")
            
            # !!! İŞTE SİHİRLİ KODLAR BURADA !!!
            settings = self.browser.settings()
            # 1. Yerel dosyaların diğer yerel dosyaları okumasına izin ver
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            # 2. Yerel dosyaların internete erişmesine izin ver (Gerekirse)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            # 3. JavaScript'i aç
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            # 4. Yerel depolamayı aç
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            # 5. WebGL Hızlandırması
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            
            # HTML Dosyasını Yükle
            url = ViziaEngineAssets.get_engine_url()
            print(f"DEBUG: Vizia Engine Yükleniyor... URL: {url.toString()}")
            self.browser.setUrl(url)
        else:
            # Fallback: Simple text browser with installation instructions
            self.browser = QTextBrowser()
            self.browser.setStyleSheet("background-color: #1c1c1e; color: #ffffff; padding: 20px;")
            self.browser.setHtml("""
                <html>
                <head>
                    <style>
                        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; }
                        h1 { color: #ff3b30; }
                        h2 { color: #0a84ff; margin-top: 30px; }
                        code { background-color: #2c2c2e; padding: 4px 8px; border-radius: 4px; }
                        pre { background-color: #2c2c2e; padding: 15px; border-radius: 8px; overflow-x: auto; }
                        .step { margin: 20px 0; padding: 15px; background-color: #2c2c2e; border-radius: 8px; }
                    </style>
                </head>
                <body>
                    <h1>⚠️ PyQtWebEngine Not Installed</h1>
                    <p>Vizia Engine requires PyQtWebEngine to run the 3D editor interface.</p>
                    
                    <h2>Quick Fix</h2>
                    <div class="step">
                        <p><strong>Step 1:</strong> Open a terminal/command prompt</p>
                        <p><strong>Step 2:</strong> Run the following command:</p>
                        <pre>pip install PyQtWebEngine==5.15.7</pre>
                        <p><strong>Step 3:</strong> Restart Vizia Engine</p>
                    </div>
                    
                    <h2>Alternative: Install All Dependencies</h2>
                    <div class="step">
                        <pre>pip install -r requirements.txt</pre>
                    </div>
                    
                    <h2>Platform-Specific Issues</h2>
                    <div class="step">
                        <p><strong>Linux:</strong></p>
                        <pre>sudo apt-get install python3-pyqt5.qtwebengine
pip install PyQtWebEngine==5.15.7</pre>
                        
                        <p><strong>macOS:</strong></p>
                        <pre>brew install pyqt@5
pip install PyQtWebEngine==5.15.7</pre>
                        
                        <p><strong>Windows:</strong></p>
                        <pre>pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7</pre>
                    </div>
                    
                    <h2>Still Having Issues?</h2>
                    <p>Try uninstalling and reinstalling:</p>
                    <div class="step">
                        <pre>pip uninstall PyQt5 PyQtWebEngine -y
pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7</pre>
                    </div>
                </body>
                </html>
            """)
        
        self.layout.addWidget(self.browser)

        # Pencere boyutu ayarları
        self.resize(1200, 800)  # Daha büyük varsayılan boyut
        
    def keyPressEvent(self, event):
        """F11 ile tam ekran geçişi"""
        if event.key() == Qt.Key_F11:
            self.toggleFullScreen()
        else:
            super().keyPressEvent(event)
    
    def toggleFullScreen(self):
        """Tam ekran modunu aç/kapat"""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True