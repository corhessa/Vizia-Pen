// web/js/terminal.js - TypeScript Terminal with Monaco Editor

class Terminal {
    constructor(app) {
        this.app = app;
        this.editor = null;
        this.output = null;
    }
    
    async init() {
        this.output = document.getElementById('terminal-output');
        const editorContainer = document.getElementById('terminal-editor');
        
        // Check if Monaco is available
        if (typeof monaco === 'undefined') {
            console.warn("Monaco Editor not loaded, using textarea fallback");
            this.initFallback(editorContainer);
            return;
        }
        
        try {
            // Initialize Monaco Editor
            this.editor = monaco.editor.create(editorContainer, {
                value: '// TypeScript Terminal\n// Access scene via: app.scene\n\n',
                language: 'typescript',
                theme: 'vs-dark',
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true
            });
            
            console.log("Monaco Editor initialized");
        } catch (error) {
            console.error("Monaco init error:", error);
            this.initFallback(editorContainer);
        }
        
        this.setupButtons();
    }
    
    initFallback(container) {
        const textarea = document.createElement('textarea');
        textarea.className = 'terminal-fallback';
        textarea.placeholder = '// TypeScript Terminal\n// Write your code here...';
        textarea.style.width = '100%';
        textarea.style.height = '100%';
        textarea.style.background = '#1e1e1e';
        textarea.style.color = '#d4d4d4';
        textarea.style.border = 'none';
        textarea.style.padding = '10px';
        textarea.style.fontFamily = 'Consolas, Monaco, monospace';
        textarea.style.fontSize = '14px';
        textarea.style.resize = 'none';
        
        container.appendChild(textarea);
        this.editor = { getValue: () => textarea.value };
    }
    
    setupButtons() {
        document.getElementById('btn-terminal-run')?.addEventListener('click', () => this.runCode());
        document.getElementById('btn-terminal-clear')?.addEventListener('click', () => this.clearOutput());
    }
    
    runCode() {
        const code = this.editor.getValue();
        this.output.innerHTML = '';
        
        try {
            // Create a safe execution context
            const func = new Function('app', 'scene', 'Galacean', code);
            const result = func(this.app, this.app.scene, typeof Galacean !== 'undefined' ? Galacean : null);
            
            if (result !== undefined) {
                this.appendOutput(String(result), 'result');
            } else {
                this.appendOutput('Code executed successfully', 'success');
            }
        } catch (error) {
            this.appendOutput('Error: ' + error.message, 'error');
            console.error(error);
        }
    }
    
    appendOutput(message, type = 'log') {
        const line = document.createElement('div');
        line.className = `terminal-output-line terminal-output-${type}`;
        line.textContent = message;
        this.output.appendChild(line);
        this.output.scrollTop = this.output.scrollHeight;
    }
    
    clearOutput() {
        this.output.innerHTML = '';
    }
}
