// web/js/hierarchy.js - Hierarchy Panel

class Hierarchy {
    constructor(app) {
        this.app = app;
        this.objects = new Map();
        this.container = null;
    }
    
    init() {
        this.container = document.getElementById('hierarchy-list');
        this.setupContextMenu();
        this.setupEventListeners();
        console.log("Hierarchy initialized");
    }
    
    setupEventListeners() {
        window.addEventListener('objectAdded', (e) => {
            this.addObjectToList(e.detail);
        });
        
        window.addEventListener('objectDeleted', (e) => {
            this.removeObjectFromList(e.detail.id);
        });
    }
    
    setupContextMenu() {
        const hierarchyPanel = document.getElementById('hierarchy-panel');
        hierarchyPanel.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.showContextMenu(e.clientX, e.clientY);
        });
    }
    
    showContextMenu(x, y) {
        // Remove existing menu
        const existingMenu = document.getElementById('hierarchy-context-menu');
        if (existingMenu) existingMenu.remove();
        
        const menu = document.createElement('div');
        menu.id = 'hierarchy-context-menu';
        menu.className = 'context-menu';
        menu.style.position = 'fixed';
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        
        const menuItems = [
            { label: '➕ Küp Ekle', action: () => this.app.scene.addCube('Küp') },
            { label: '➕ Küre Ekle', action: () => this.app.scene.addSphere('Küre') },
            { label: '💡 Işık Ekle', action: () => console.log('Işık ekleme yapımda') },
            { label: '📷 Kamera Ekle', action: () => console.log('Kamera ekleme yapımda') }
        ];
        
        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.className = 'context-menu-item';
            menuItem.textContent = item.label;
            menuItem.addEventListener('click', () => {
                item.action();
                menu.remove();
            });
            menu.appendChild(menuItem);
        });
        
        document.body.appendChild(menu);
        
        // Close on click outside
        const closeMenu = (e) => {
            if (!menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        };
        setTimeout(() => document.addEventListener('click', closeMenu), 0);
    }
    
    addObjectToList(objData) {
        const item = document.createElement('div');
        item.className = 'hierarchy-item';
        item.dataset.id = objData.id;
        item.textContent = objData.name;
        
        item.addEventListener('click', () => {
            this.selectObject(objData.id);
        });
        
        this.container.appendChild(item);
        this.objects.set(objData.id, objData);
    }
    
    removeObjectFromList(id) {
        const item = this.container.querySelector(`[data-id="${id}"]`);
        if (item) {
            item.remove();
            this.objects.delete(id);
        }
    }
    
    selectObject(id) {
        // Remove previous selection
        document.querySelectorAll('.hierarchy-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add selection to clicked item
        const item = this.container.querySelector(`[data-id="${id}"]`);
        if (item) {
            item.classList.add('selected');
            const objData = this.objects.get(id);
            this.app.selectObject(objData);
        }
    }
}
