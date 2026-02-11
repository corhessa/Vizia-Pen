// web/js/shortcuts.js - Keyboard Shortcuts

class ShortcutManager {
    constructor(app) {
        this.app = app;
        this.shortcuts = new Map();
    }
    
    init() {
        this.registerShortcuts();
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        console.log("Shortcuts initialized");
    }
    
    registerShortcuts() {
        // Save
        this.register('ctrl+s', () => {
            this.app.saveScene();
            console.log("Scene saved (Ctrl+S)");
        });
        
        // Undo
        this.register('ctrl+z', () => {
            if (this.app.history) {
                this.app.history.undo();
            }
        });
        
        // Redo
        this.register('ctrl+y', () => {
            if (this.app.history) {
                this.app.history.redo();
            }
        });
        
        this.register('ctrl+shift+z', () => {
            if (this.app.history) {
                this.app.history.redo();
            }
        });
        
        // Transform tools
        this.register('w', () => {
            document.getElementById('btn-move')?.click();
        });
        
        this.register('e', () => {
            document.getElementById('btn-rotate')?.click();
        });
        
        this.register('r', () => {
            document.getElementById('btn-scale')?.click();
        });
        
        // Delete
        this.register('delete', () => {
            if (this.app.selectedObject) {
                this.app.scene.deleteObject(this.app.selectedObject.id);
            }
        });
        
        // Focus (F)
        this.register('f', () => {
            console.log("Focus on selected object");
        });
        
        // Duplicate
        this.register('ctrl+d', () => {
            console.log("Duplicate object");
        });
    }
    
    register(shortcut, callback) {
        this.shortcuts.set(shortcut.toLowerCase(), callback);
    }
    
    handleKeyDown(e) {
        // Don't trigger shortcuts when typing in inputs
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        let shortcut = '';
        
        if (e.ctrlKey || e.metaKey) shortcut += 'ctrl+';
        if (e.shiftKey) shortcut += 'shift+';
        if (e.altKey) shortcut += 'alt+';
        
        shortcut += e.key.toLowerCase();
        
        const callback = this.shortcuts.get(shortcut);
        if (callback) {
            e.preventDefault();
            callback();
        }
    }
}
