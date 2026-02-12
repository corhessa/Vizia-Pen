// web/js/app.js - Main Application Entry Point

class ViziaApp {
    constructor() {
        this.scene = null;
        this.ui = null;
        this.history = null;
        this.storage = null;
        this.selectedObject = null;
        
        console.log("🎨 Vizia Studio Pro - Initializing...");
    }
    
    async init() {
        try {
            // Initialize UI first
            this.ui = new UI();
            this.ui.init();
            
            // Initialize scene manager
            this.scene = new SceneManager();
            await this.scene.init();
            
            // Initialize history (undo/redo)
            this.history = new HistoryManager();
            
            // Initialize storage
            this.storage = new StorageManager();
            
            // Initialize shortcuts
            const shortcuts = new ShortcutManager(this);
            shortcuts.init();
            
            // Initialize toolbar
            const toolbar = new Toolbar(this);
            toolbar.init();
            
            // Initialize hierarchy
            const hierarchy = new Hierarchy(this);
            hierarchy.init();
            
            // Initialize inspector
            const inspector = new Inspector(this);
            inspector.init();
            
            // Initialize console
            const consolePanel = new ConsolePanel();
            consolePanel.init();
            
            // Initialize TypeScript terminal
            const terminal = new Terminal(this);
            await terminal.init();
            
            // Load default scene or last scene
            this.loadDefaultScene();
            
            console.log("✅ Vizia Studio Pro - Hazır!");
            consolePanel.log("Vizia Studio Pro başarıyla başlatıldı!", "info");
            
        } catch (error) {
            console.error("❌ Başlatma Hatası:", error);
            alert("Vizia Engine başlatılamadı: " + error.message);
        }
    }
    
    loadDefaultScene() {
        // Try to load last scene from localStorage
        const lastScene = this.storage.loadScene("last_scene");
        if (lastScene) {
            this.scene.loadScene(lastScene);
        } else {
            // Create default scene
            this.scene.createDefaultScene();
        }
    }
    
    selectObject(object) {
        this.selectedObject = object;
        // Update inspector
        if (window.app && window.app.ui) {
            window.dispatchEvent(new CustomEvent('objectSelected', { detail: object }));
        }
    }
    
    saveScene() {
        const sceneData = this.scene.serializeScene();
        this.storage.saveScene("last_scene", sceneData);
        console.log("Sahne kaydedildi!");
        return sceneData;
    }
}

// Global app instance
window.app = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    window.app = new ViziaApp();
    await window.app.init();
});
