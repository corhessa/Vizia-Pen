// web/js/storage.js - Scene Save/Load (JSON)

class StorageManager {
    constructor() {
        this.storageKey = 'vizia_scenes';
    }
    
    saveScene(name, sceneData) {
        try {
            const scenes = this.getAllScenes();
            scenes[name] = {
                data: sceneData,
                timestamp: Date.now()
            };
            localStorage.setItem(this.storageKey, JSON.stringify(scenes));
            console.log(`Scene "${name}" saved successfully`);
            return true;
        } catch (error) {
            console.error("Save error:", error);
            return false;
        }
    }
    
    loadScene(name) {
        try {
            const scenes = this.getAllScenes();
            const scene = scenes[name];
            if (scene) {
                console.log(`Scene "${name}" loaded`);
                return scene.data;
            }
            return null;
        } catch (error) {
            console.error("Load error:", error);
            return null;
        }
    }
    
    getAllScenes() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : {};
        } catch (error) {
            console.error("Error reading scenes:", error);
            return {};
        }
    }
    
    deleteScene(name) {
        try {
            const scenes = this.getAllScenes();
            delete scenes[name];
            localStorage.setItem(this.storageKey, JSON.stringify(scenes));
            console.log(`Scene "${name}" deleted`);
            return true;
        } catch (error) {
            console.error("Delete error:", error);
            return false;
        }
    }
    
    exportScene(sceneData, filename = 'scene.json') {
        const json = JSON.stringify(sceneData, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        
        URL.revokeObjectURL(url);
        console.log(`Scene exported as ${filename}`);
    }
    
    importScene(file, callback) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const sceneData = JSON.parse(e.target.result);
                callback(sceneData);
                console.log("Scene imported successfully");
            } catch (error) {
                console.error("Import error:", error);
            }
        };
        reader.readAsText(file);
    }
}
