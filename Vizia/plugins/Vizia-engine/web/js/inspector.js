// web/js/inspector.js - Inspector Panel

class Inspector {
    constructor(app) {
        this.app = app;
        this.container = null;
        this.currentObject = null;
    }
    
    init() {
        this.container = document.getElementById('inspector-content');
        window.addEventListener('objectSelected', (e) => {
            this.showObjectProperties(e.detail);
        });
        console.log("Inspector initialized");
    }
    
    showObjectProperties(objData) {
        this.currentObject = objData;
        this.container.innerHTML = '';
        
        if (!objData || !objData.entity) {
            this.container.innerHTML = '<div class="inspector-empty">Özellikleri görmek için bir nesne seçin</div>';
            return;
        }
        
        // Object name
        const nameSection = this.createSection('Nesne');
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.value = objData.name;
        nameInput.className = 'inspector-input';
        nameSection.appendChild(nameInput);
        this.container.appendChild(nameSection);
        
        // Transform
        const transform = objData.entity.transform;
        const transformSection = this.createSection('Dönüşüm');
        
        // Position
        transformSection.appendChild(this.createVectorControl('Konum', transform.position, (x, y, z) => {
            transform.setPosition(x, y, z);
        }));
        
        // Rotation
        transformSection.appendChild(this.createVectorControl('Döndürme', 
            { x: 0, y: 0, z: 0 }, // Simplified
            (x, y, z) => {
                // Apply rotation
            }
        ));
        
        // Scale
        transformSection.appendChild(this.createVectorControl('Ölçek', transform.scale, (x, y, z) => {
            transform.setScale(x, y, z);
        }));
        
        this.container.appendChild(transformSection);
        
        // Material section (simplified)
        const materialSection = this.createSection('Materyal');
        materialSection.innerHTML += '<div style="color: #888; font-size: 12px;">PBR Materyal</div>';
        this.container.appendChild(materialSection);
    }
    
    createSection(title) {
        const section = document.createElement('div');
        section.className = 'inspector-section';
        
        const header = document.createElement('div');
        header.className = 'inspector-section-header';
        header.textContent = title;
        section.appendChild(header);
        
        return section;
    }
    
    createVectorControl(label, vector, onChange) {
        const container = document.createElement('div');
        container.className = 'inspector-vector';
        
        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        labelEl.className = 'inspector-label';
        container.appendChild(labelEl);
        
        const inputContainer = document.createElement('div');
        inputContainer.className = 'inspector-vector-inputs';
        
        ['x', 'y', 'z'].forEach(axis => {
            const input = document.createElement('input');
            input.type = 'number';
            input.step = '0.1';
            input.value = vector[axis].toFixed(2);
            input.className = 'inspector-input inspector-number';
            input.dataset.axis = axis;
            
            input.addEventListener('change', () => {
                const x = parseFloat(inputContainer.querySelector('[data-axis="x"]').value);
                const y = parseFloat(inputContainer.querySelector('[data-axis="y"]').value);
                const z = parseFloat(inputContainer.querySelector('[data-axis="z"]').value);
                onChange(x, y, z);
            });
            
            const wrapper = document.createElement('div');
            wrapper.className = 'inspector-input-wrapper';
            const axisLabel = document.createElement('span');
            axisLabel.textContent = axis.toUpperCase();
            axisLabel.className = 'axis-label';
            wrapper.appendChild(axisLabel);
            wrapper.appendChild(input);
            
            inputContainer.appendChild(wrapper);
        });
        
        container.appendChild(inputContainer);
        return container;
    }
}
