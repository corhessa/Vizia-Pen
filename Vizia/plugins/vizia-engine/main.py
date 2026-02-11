#!/usr/bin/env python3
"""
Vizia Engine - Standalone Mode
Run the 3D editor as a standalone application
"""

import sys
from PyQt5.QtWidgets import QApplication

try:
    from engine.viewport import ViziaEngineItem
except ImportError as e:
    print(f"❌ [ENGINE] Import Error: {e}")
    print("   Make sure to install dependencies: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Main entry point for standalone mode"""
    app = QApplication(sys.argv)
    app.setApplicationName("Vizia Studio Pro - 3D Editör")
    app.setOrganizationName("Vizia")
    
    # Create main window (no parent for standalone mode)
    window = ViziaEngineItem(None)
    window.show()
    
    # Center window on screen
    screen = app.primaryScreen().geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)
    
    print("✅ Vizia Studio Pro başlatıldı (Bağımsız Mod)")
    print("   • Pencereyi tam ekran yapmak için F11'e basın")
    print("   • Pencereyi kapatmak için X düğmesine tıklayın")
    print("   • Sahneyi kaydetmek için Ctrl+S tuşlarına basın")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
