// web/js/scene.js - Scene Management with Galacean Engine

class SceneManager {
    constructor() {
        this.engine = null;
        this.scene = null;
        this.rootEntity = null;
        this.camera = null;
        this.cameraEntity = null;
        this.objects = new Map(); // id -> entity mapping
        this.canvas = null;
    }
    
    async init() {
        try {
            this.canvas = document.getElementById('viewport-canvas');
            
            // Check if Galacean is available
            if (typeof Galacean === 'undefined') {
                throw new Error("Galacean Engine yüklenemedi. İnternet bağlantınızı kontrol edin.");
            }
            
            // Create engine
            this.engine = await Galacean.WebGLEngine.create({ canvas: this.canvas });
            this.engine.canvas.resizeByClientSize();
            
            // Create scene
            this.scene = this.engine.sceneManager.activeScene;
            this.rootEntity = this.scene.createRootEntity("Root");
            
            // Setup camera
            this.setupCamera();
            
            // Setup lighting
            this.setupLighting();
            
            // Setup grid
            this.setupGrid();
            
            // Start render loop
            this.engine.run();
            
            // Handle window resize
            window.addEventListener('resize', () => {
                this.engine.canvas.resizeByClientSize();
            });
            
            console.log("✅ Galacean Engine başlatıldı");
            
        } catch (error) {
            console.error("❌ Galacean Engine Hatası:", error);
            // Fallback to simple canvas rendering
            this.initFallback();
        }
    }
    
    initFallback() {
        console.warn("Basit render modu kullanılıyor (Galacean yüklenemedi)");
        const ctx = this.canvas.getContext('2d');
        if (ctx) {
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.font = '16px Arial';
            ctx.fillText('⚠️ WebGL kullanılamıyor veya Galacean yüklenemedi', 50, 50);
            ctx.fillText('Hata için konsolu kontrol edin', 50, 80);
        }
    }
    
    setupCamera() {
        this.cameraEntity = this.rootEntity.createChild("Kamera");
        this.cameraEntity.transform.setPosition(5, 5, 5);
        this.cameraEntity.transform.lookAt(new Galacean.Vector3(0, 0, 0));
        
        this.camera = this.cameraEntity.addComponent(Galacean.Camera);
        
        // Add camera controller for orbit, pan, zoom
        const controller = this.cameraEntity.addComponent(Galacean.OrbitControl);
        controller.target.set(0, 0, 0);
        controller.minDistance = 1;
        controller.maxDistance = 100;
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = this.rootEntity.createChild("OrtamIşığı");
        const ambient = ambientLight.addComponent(Galacean.AmbientLight);
        ambient.color.set(0.4, 0.4, 0.4, 1);
        
        // Directional light
        const lightEntity = this.rootEntity.createChild("YönlüIşık");
        lightEntity.transform.setPosition(3, 10, 5);
        lightEntity.transform.lookAt(new Galacean.Vector3(0, 0, 0));
        
        const directionalLight = lightEntity.addComponent(Galacean.DirectionalLight);
        directionalLight.intensity = 1.0;
        directionalLight.color.set(1, 1, 1, 1);
        
        this.objects.set("OrtamIşığı", ambientLight);
        this.objects.set("YönlüIşık", lightEntity);
    }
    
    setupGrid() {
        // Create a simple grid helper (if Galacean has one)
        // Otherwise, we can create a plane with grid texture
        const gridEntity = this.rootEntity.createChild("Izgara");
        gridEntity.transform.setPosition(0, 0, 0);
        
        // Add grid visualization (simplified)
        const renderer = gridEntity.addComponent(Galacean.MeshRenderer);
        const material = new Galacean.UnlitMaterial(this.engine);
        material.baseColor.set(0.2, 0.2, 0.2, 1);
        renderer.setMaterial(material);
        
        const mesh = Galacean.PrimitiveMesh.createPlane(this.engine, 20, 20);
        renderer.mesh = mesh;
        
        this.objects.set("Izgara", gridEntity);
    }
    
    createDefaultScene() {
        // Add a default cube
        this.addCube("Küp", [0, 1, 0]);
        
        console.log("Varsayılan sahne oluşturuldu");
    }
    
    addCube(name, position = [0, 0, 0]) {
        const cubeEntity = this.rootEntity.createChild(name);
        cubeEntity.transform.setPosition(position[0], position[1], position[2]);
        
        const renderer = cubeEntity.addComponent(Galacean.MeshRenderer);
        const material = new Galacean.PBRMaterial(this.engine);
        material.baseColor.set(0.6, 0.6, 0.8, 1);
        material.metallic = 0.3;
        material.roughness = 0.5;
        renderer.setMaterial(material);
        
        const mesh = Galacean.PrimitiveMesh.createCuboid(this.engine, 1, 1, 1);
        renderer.mesh = mesh;
        
        const id = this.generateId();
        this.objects.set(id, cubeEntity);
        
        // Notify hierarchy
        window.dispatchEvent(new CustomEvent('objectAdded', {
            detail: { id, name, type: 'cube', entity: cubeEntity }
        }));
        
        return id;
    }
    
    addSphere(name, position = [0, 0, 0]) {
        const sphereEntity = this.rootEntity.createChild(name);
        sphereEntity.transform.setPosition(position[0], position[1], position[2]);
        
        const renderer = sphereEntity.addComponent(Galacean.MeshRenderer);
        const material = new Galacean.PBRMaterial(this.engine);
        material.baseColor.set(0.8, 0.6, 0.6, 1);
        material.metallic = 0.3;
        material.roughness = 0.5;
        renderer.setMaterial(material);
        
        const mesh = Galacean.PrimitiveMesh.createSphere(this.engine, 0.5);
        renderer.mesh = mesh;
        
        const id = this.generateId();
        this.objects.set(id, sphereEntity);
        
        window.dispatchEvent(new CustomEvent('objectAdded', {
            detail: { id, name, type: 'sphere', entity: sphereEntity }
        }));
        
        return id;
    }
    
    deleteObject(id) {
        const entity = this.objects.get(id);
        if (entity) {
            entity.destroy();
            this.objects.delete(id);
            window.dispatchEvent(new CustomEvent('objectDeleted', { detail: { id } }));
        }
    }
    
    generateId() {
        return 'obj_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    serializeScene() {
        const sceneData = {
            version: "1.0",
            objects: []
        };
        
        this.objects.forEach((entity, id) => {
            const pos = entity.transform.position;
            const rot = entity.transform.rotation;
            const scale = entity.transform.scale;
            
            sceneData.objects.push({
                id,
                name: entity.name,
                type: 'mesh',
                transform: {
                    position: [pos.x, pos.y, pos.z],
                    rotation: [rot.x, rot.y, rot.z, rot.w],
                    scale: [scale.x, scale.y, scale.z]
                }
            });
        });
        
        return sceneData;
    }
    
    loadScene(sceneData) {
        // Clear current scene
        this.objects.forEach((entity, id) => {
            if (!['Camera', 'AmbientLight', 'DirectionalLight', 'Grid'].includes(id)) {
                entity.destroy();
            }
        });
        
        // Load objects from scene data
        if (sceneData && sceneData.objects) {
            sceneData.objects.forEach(obj => {
                // Reconstruct objects based on type
                // This is simplified - real implementation would be more complex
            });
        }
    }
}
