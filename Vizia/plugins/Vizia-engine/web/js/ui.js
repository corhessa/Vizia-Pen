// web/js/ui.js - UI Panel Management

class UI {
    constructor() {
        this.panels = {};
        this.isDraggingPanel = false;
    }
    
    init() {
        this.setupPanels();
        this.setupResizers();
        console.log("UI Manager initialized");
    }
    
    setupPanels() {
        // Main panels are already in HTML
        this.panels = {
            toolbar: document.getElementById('toolbar'),
            hierarchy: document.getElementById('hierarchy-panel'),
            viewport: document.getElementById('viewport-panel'),
            inspector: document.getElementById('inspector-panel'),
            bottomPanel: document.getElementById('bottom-panel'),
            console: document.getElementById('console-tab'),
            terminal: document.getElementById('terminal-tab'),
            assets: document.getElementById('assets-tab')
        };
        
        // Setup bottom panel tabs
        this.setupBottomTabs();
    }
    
    setupBottomTabs() {
        const tabs = document.querySelectorAll('.bottom-tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active from all
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.bottom-tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                
                // Add active to clicked
                tab.classList.add('active');
                const targetId = tab.dataset.tab;
                document.getElementById(targetId).classList.add('active');
            });
        });
    }
    
    setupResizers() {
        // Setup panel resizers for flexible layout
        const leftResizer = document.getElementById('left-resizer');
        const rightResizer = document.getElementById('right-resizer');
        const bottomResizer = document.getElementById('bottom-resizer');
        
        if (leftResizer) {
            this.setupResizer(leftResizer, 'hierarchy-panel', 'horizontal', 'left');
        }
        
        if (rightResizer) {
            this.setupResizer(rightResizer, 'inspector-panel', 'horizontal', 'right');
        }
        
        if (bottomResizer) {
            this.setupResizer(bottomResizer, 'bottom-panel', 'vertical', 'bottom');
        }
    }
    
    setupResizer(resizer, panelId, direction, side) {
        let isResizing = false;
        let startPos = 0;
        let startSize = 0;
        const panel = document.getElementById(panelId);
        
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            startPos = direction === 'horizontal' ? e.clientX : e.clientY;
            startSize = direction === 'horizontal' ? panel.offsetWidth : panel.offsetHeight;
            document.body.style.cursor = direction === 'horizontal' ? 'ew-resize' : 'ns-resize';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            let delta = (direction === 'horizontal' ? e.clientX : e.clientY) - startPos;
            if (side === 'right' || side === 'bottom') {
                delta = -delta;
            }
            
            let newSize = startSize + delta;
            newSize = Math.max(150, Math.min(newSize, 600)); // Min 150px, max 600px
            
            if (direction === 'horizontal') {
                panel.style.width = newSize + 'px';
            } else {
                panel.style.height = newSize + 'px';
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = 'default';
            }
        });
    }
    
    showPanel(panelId) {
        if (this.panels[panelId]) {
            this.panels[panelId].style.display = 'flex';
        }
    }
    
    hidePanel(panelId) {
        if (this.panels[panelId]) {
            this.panels[panelId].style.display = 'none';
        }
    }
    
    togglePanel(panelId) {
        if (this.panels[panelId]) {
            const isVisible = this.panels[panelId].style.display !== 'none';
            this.panels[panelId].style.display = isVisible ? 'none' : 'flex';
        }
    }
}
