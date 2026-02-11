// web/js/toolbar.js - Toolbar Controls

class Toolbar {
    constructor(app) {
        this.app = app;
        this.transformMode = 'translate'; // translate, rotate, scale
    }
    
    init() {
        this.setupButtons();
        console.log("Toolbar initialized");
    }
    
    setupButtons() {
        // Play/Pause/Stop
        document.getElementById('btn-play')?.addEventListener('click', () => this.onPlay());
        document.getElementById('btn-pause')?.addEventListener('click', () => this.onPause());
        document.getElementById('btn-stop')?.addEventListener('click', () => this.onStop());
        
        // Transform tools
        document.getElementById('btn-move')?.addEventListener('click', () => this.setTransformMode('translate'));
        document.getElementById('btn-rotate')?.addEventListener('click', () => this.setTransformMode('rotate'));
        document.getElementById('btn-scale')?.addEventListener('click', () => this.setTransformMode('scale'));
        
        // Save
        document.getElementById('btn-save')?.addEventListener('click', () => this.onSave());
    }
    
    setTransformMode(mode) {
        this.transformMode = mode;
        
        // Update active button
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        
        if (mode === 'translate') {
            document.getElementById('btn-move')?.classList.add('active');
        } else if (mode === 'rotate') {
            document.getElementById('btn-rotate')?.classList.add('active');
        } else if (mode === 'scale') {
            document.getElementById('btn-scale')?.classList.add('active');
        }
        
        console.log(`Transform mode: ${mode}`);
    }
    
    onPlay() {
        console.log("Çalıştır tıklandı");
    }
    
    onPause() {
        console.log("Duraklat tıklandı");
    }
    
    onStop() {
        console.log("Durdur tıklandı");
    }
    
    onSave() {
        this.app.saveScene();
        alert("Sahne kaydedildi!");
    }
}
