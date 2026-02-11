"""
Vizia Engine - Python-JavaScript Bridge
Bridge for communication between PyQt5 and JavaScript
"""

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

class ViziaEngineBridge(QObject):
    """
    Bridge class for Python-JavaScript communication
    Allows JavaScript to call Python methods and vice versa
    """
    
    # Signals that can be emitted from Python to JavaScript
    sceneUpdated = pyqtSignal(str)
    objectSelected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        print("🌉 Bridge initialized")
    
    @pyqtSlot(str)
    def logFromJS(self, message):
        """Receive log messages from JavaScript"""
        print(f"[JS] {message}")
    
    @pyqtSlot(str, result=str)
    def getResourcePath(self, resourceName):
        """Get full path to a resource"""
        # This can be extended to return actual paths
        return f"Resource: {resourceName}"
    
    @pyqtSlot()
    def saveScene(self):
        """Trigger scene save from Python side"""
        print("Scene save requested from Python")
        self.sceneUpdated.emit("Scene saved")
    
    @pyqtSlot(str)
    def selectObject(self, objectId):
        """Handle object selection from JavaScript"""
        print(f"Object selected: {objectId}")
        self.objectSelected.emit(objectId)
