import os
import datetime
from PyQt5.QtWidgets import QApplication

class ScreenshotManager:
    @staticmethod
    def save_screenshot(crop_rect=None, save_folder=None):
        try:
            screen = QApplication.primaryScreen()
            if not screen: return False
            pixmap = screen.grabWindow(0)
            if crop_rect: pixmap = pixmap.copy(crop_rect)

            if not save_folder:
                save_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Vizia Screenshots")
            
            if not os.path.exists(save_folder): os.makedirs(save_folder)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"Vizia_{timestamp}.png"
            full_path = os.path.join(save_folder, filename)
            
            pixmap.save(full_path, "png")
            return True
        except Exception as e:
            print(f"Screenshot Error: {e}")
            return False