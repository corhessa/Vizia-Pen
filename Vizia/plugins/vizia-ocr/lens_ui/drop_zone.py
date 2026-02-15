from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

# İki noktayı kaldırdık
from workflow.orchestrator import WorkflowOrchestrator

# ... kodun geri kalanı aynı

class ViziaDropZone(QFrame):
    def __init__(self, parent_panel):
        super().__init__(parent_panel)
        self.parent_panel = parent_panel
        self.orchestrator = WorkflowOrchestrator()
        
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QFrame { background-color: #2c2c2e; border: 2px dashed #48484a; border-radius: 10px; }
            QLabel { border: none; color: #a1a1a6; }
        """)
        
        layout = QVBoxLayout(self)
        self.lbl_info = QLabel("PDF veya TXT dosyasını\nburaya sürükleyin")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_info)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("QFrame { background-color: #3a3a3c; border: 2px dashed #0a84ff; border-radius: 10px; }")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("QFrame { background-color: #2c2c2e; border: 2px dashed #48484a; border-radius: 10px; }")

    def dropEvent(self, event):
        self.setStyleSheet("QFrame { background-color: #2c2c2e; border: 2px dashed #48484a; border-radius: 10px; }")
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.pdf', '.txt')):
                self.lbl_info.setText(f"İşleniyor:\n{file_path.split('/')[-1]}")
                self.orchestrator.process_file(file_path)
                break