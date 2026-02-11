// web/js/console.js - Console Panel

class ConsolePanel {
    constructor() {
        this.container = null;
        this.messages = [];
        this.filters = {
            log: true,
            warn: true,
            error: true
        };
    }
    
    init() {
        this.container = document.getElementById('console-output');
        this.setupButtons();
        this.interceptConsole();
        
        // Hoş geldin mesajı
        this.log("🎨 Vizia Studio Pro'ya hoş geldiniz!", "info");
        this.log("📋 Hiyerarşi panelinde sağ tıklayarak nesne ekleyebilirsiniz", "info");
        this.log("⌨️  F11 tuşu ile tam ekran moduna geçebilirsiniz", "info");
        this.log("💾 Ctrl+S ile sahneyi kaydedebilirsiniz", "info");
    }
    
    setupButtons() {
        document.getElementById('btn-console-clear')?.addEventListener('click', () => this.clear());
        document.getElementById('btn-console-log')?.addEventListener('click', () => this.toggleFilter('log'));
        document.getElementById('btn-console-warn')?.addEventListener('click', () => this.toggleFilter('warn'));
        document.getElementById('btn-console-error')?.addEventListener('click', () => this.toggleFilter('error'));
    }
    
    interceptConsole() {
        const originalLog = console.log;
        const originalWarn = console.warn;
        const originalError = console.error;
        
        console.log = (...args) => {
            originalLog.apply(console, args);
            this.log(args.join(' '), 'log');
        };
        
        console.warn = (...args) => {
            originalWarn.apply(console, args);
            this.log(args.join(' '), 'warn');
        };
        
        console.error = (...args) => {
            originalError.apply(console, args);
            this.log(args.join(' '), 'error');
        };
    }
    
    log(message, type = 'log') {
        const timestamp = new Date().toLocaleTimeString();
        const msg = { message, type, timestamp };
        this.messages.push(msg);
        
        if (this.filters[type]) {
            this.appendMessage(msg);
        }
    }
    
    appendMessage(msg) {
        const line = document.createElement('div');
        line.className = `console-line console-${msg.type}`;
        
        const time = document.createElement('span');
        time.className = 'console-time';
        time.textContent = `[${msg.timestamp}]`;
        
        const text = document.createElement('span');
        text.textContent = msg.message;
        
        line.appendChild(time);
        line.appendChild(text);
        
        this.container.appendChild(line);
        this.container.scrollTop = this.container.scrollHeight;
    }
    
    clear() {
        this.messages = [];
        this.container.innerHTML = '';
    }
    
    toggleFilter(type) {
        this.filters[type] = !this.filters[type];
        
        const btn = document.getElementById(`btn-console-${type}`);
        if (btn) {
            btn.classList.toggle('active', this.filters[type]);
        }
        
        this.refresh();
    }
    
    refresh() {
        this.container.innerHTML = '';
        this.messages.forEach(msg => {
            if (this.filters[msg.type]) {
                this.appendMessage(msg);
            }
        });
    }
}
