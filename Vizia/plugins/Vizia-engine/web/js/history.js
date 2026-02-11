// web/js/history.js - Undo/Redo System

class HistoryManager {
    constructor() {
        this.undoStack = [];
        this.redoStack = [];
        this.maxStackSize = 50;
    }
    
    addAction(action) {
        this.undoStack.push(action);
        if (this.undoStack.length > this.maxStackSize) {
            this.undoStack.shift();
        }
        this.redoStack = []; // Clear redo stack when new action is added
    }
    
    undo() {
        if (this.undoStack.length === 0) {
            console.log("Nothing to undo");
            return;
        }
        
        const action = this.undoStack.pop();
        if (action && action.undo) {
            action.undo();
            this.redoStack.push(action);
            console.log("Undo:", action.type);
        }
    }
    
    redo() {
        if (this.redoStack.length === 0) {
            console.log("Nothing to redo");
            return;
        }
        
        const action = this.redoStack.pop();
        if (action && action.redo) {
            action.redo();
            this.undoStack.push(action);
            console.log("Redo:", action.type);
        }
    }
    
    clear() {
        this.undoStack = [];
        this.redoStack = [];
    }
    
    // Helper to create action objects
    createAction(type, undoFn, redoFn) {
        return {
            type,
            undo: undoFn,
            redo: redoFn
        };
    }
}
