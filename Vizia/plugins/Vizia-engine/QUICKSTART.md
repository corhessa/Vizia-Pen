# Vizia Engine - Quick Start Guide

Get up and running with Vizia Engine in 5 minutes! 🚀

## Prerequisites

- Python 3.7 or higher
- Internet connection (for 3D engine and editor CDN)
- 500 MB free disk space

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/corhessa/Vizia-engine.git
cd Vizia-engine
```

### Step 2: Install Dependencies

#### Option A: Using pip (Recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Manual installation
```bash
pip install PyQt5==5.15.11
pip install PyQtWebEngine==5.15.7
```

#### Platform-Specific Notes

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
pip install -r requirements.txt
```

**macOS:**
```bash
brew install pyqt@5
pip install -r requirements.txt
```

**Windows:**
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python3 -c "from engine import ViziaEngineItem; print('✅ Installation successful!')"
```

If you see "✅ Installation successful!", you're ready to go!

## Running the Editor

### Quick Start (Standalone Mode)

```bash
python main.py
```

This will open the Vizia Studio Pro editor in a standalone window.

### Using Examples

```bash
python examples.py
```

This will show you interactive examples of:
1. Standalone mode
2. Plugin mode
3. Programmatic scene creation

## First Steps in the Editor

### 1. Understanding the Interface

When you open Vizia Engine, you'll see:

```
┌─────────────────────────────────────────────────────────────┐
│  [▶ Play] [⏸ Pause] [⏹ Stop]  [Move] [Rotate] [Scale] [💾] │ ← Toolbar
├──────────┬─────────────────────────────────────┬────────────┤
│ Hierarchy│           3D Viewport              │ Inspector  │
│          │                                     │            │
│ □ Cube   │        [3D Scene Renders Here]     │ Transform  │
│ □ Light  │                                     │ Position   │
│ □ Camera │                                     │ X: 0.0     │
│          │                                     │ Y: 1.0     │
│ [+]      │                                     │ Z: 0.0     │
│          │                                     │            │
├──────────┴─────────────────────────────────────┴────────────┤
│ [Console] [Terminal] [Assets]                               │
│ > Vizia Studio Pro initialized successfully!                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2. Adding Your First Object

**Method 1: Using Context Menu**
1. Right-click in the Hierarchy panel (left)
2. Select "Add Cube" or "Add Sphere"
3. The object appears in both the Hierarchy and 3D Viewport

**Method 2: Using the Terminal**
1. Click the "Terminal" tab at the bottom
2. Type: `app.scene.addCube('MyCube', [0, 1, 0])`
3. Click "▶ Run"

### 3. Selecting and Editing Objects

1. Click an object in the Hierarchy panel
2. The Inspector panel (right) shows its properties
3. Edit Position, Rotation, or Scale values
4. Changes apply immediately in the 3D viewport

### 4. Camera Controls

- **Orbit**: Hold Alt + Left Mouse Button and drag
- **Pan**: Hold Middle Mouse Button and drag
- **Zoom**: Mouse Wheel scroll

### 5. Using Transform Tools

Press these keys to switch tools:
- **W** - Move tool
- **E** - Rotate tool
- **R** - Scale tool

### 6. Saving Your Scene

**Method 1: Keyboard Shortcut**
```
Press Ctrl+S
```

**Method 2: Toolbar Button**
```
Click the 💾 Save button
```

**Method 3: Terminal**
```javascript
app.saveScene()
```

Your scene is saved to browser's LocalStorage.

## Tutorial: Creating a Simple Scene

Let's create a simple scene with multiple objects!

### Step 1: Open the Terminal

Click the "Terminal" tab at the bottom of the editor.

### Step 2: Add Objects

Copy and paste this code into the terminal:

```javascript
// Clear any existing scene
// (You can manually delete objects from Hierarchy instead)

// Add a ground plane (make it flat)
const ground = app.scene.addCube('Ground', [0, 0, 0]);

// Add a few cubes in a row
for (let i = 0; i < 5; i++) {
    app.scene.addCube(`Cube_${i}`, [i * 2 - 4, 1, 0]);
}

// Add spheres on top
for (let i = 0; i < 3; i++) {
    app.scene.addSphere(`Sphere_${i}`, [i * 3 - 3, 3, 0]);
}

console.log("Scene created! Check the Hierarchy panel.");
```

### Step 3: Run the Code

Click the "▶ Run" button.

### Step 4: Explore Your Scene

1. Check the Hierarchy panel - all objects should be listed
2. Click on each object to see its properties
3. Use camera controls to view from different angles
4. Select objects and modify their positions

### Step 5: Save Your Work

Press `Ctrl+S` to save the scene.

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save scene |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` or `Ctrl+Shift+Z` | Redo |
| `W` | Move tool |
| `E` | Rotate tool |
| `R` | Scale tool |
| `Delete` | Delete selected object |
| `F` | Focus on selected object |
| `Ctrl+D` | Duplicate object |

## Using the TypeScript Terminal

The terminal gives you programmatic access to the entire scene:

### Basic Commands

```javascript
// Access the app
console.log(app);

// Access the scene manager
console.log(app.scene);

// Add objects
app.scene.addCube('Test', [0, 0, 0]);
app.scene.addSphere('Ball', [2, 1, 0]);

// Get all objects
console.log(Array.from(app.scene.objects.keys()));

// Delete an object (you need the object ID)
// Get ID from hierarchy first
app.scene.deleteObject('obj_1234567890_abc123');

// Save scene
app.saveScene();
```

### Advanced Examples

```javascript
// Create a pyramid of cubes
let y = 0;
for (let layer = 5; layer > 0; layer--) {
    for (let x = 0; x < layer; x++) {
        app.scene.addCube(`Pyramid_${y}_${x}`, 
            [x - layer/2, y, 0]);
    }
    y += 1;
}

// Create a circle of spheres
const radius = 5;
const count = 12;
for (let i = 0; i < count; i++) {
    const angle = (i / count) * Math.PI * 2;
    const x = Math.cos(angle) * radius;
    const z = Math.sin(angle) * radius;
    app.scene.addSphere(`Circle_${i}`, [x, 1, z]);
}
```

## Troubleshooting

### Editor shows black screen
- Check internet connection (Galacean Engine loads from CDN)
- Open browser console (F12) and check for errors
- Ensure WebGL is supported in your system

### PyQtWebEngine import error
```bash
pip uninstall PyQt5 PyQtWebEngine -y
pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7
```

### Terminal not working
- If Monaco Editor doesn't load, a fallback textarea is used
- Check internet connection
- The terminal will still execute code, just without syntax highlighting

### Objects not appearing
- Check the Console tab for errors
- Verify Galacean Engine loaded (check browser console)
- Try refreshing: Close and reopen the editor

## Next Steps

Now that you're up and running:

1. 📖 Read the full [README.md](README.md) for detailed documentation
2. 🏗️ Explore the [ARCHITECTURE.md](ARCHITECTURE.md) to understand the internals
3. 🧪 Check [TESTING.md](TESTING.md) for testing guidelines
4. 💡 Run [examples.py](examples.py) for more usage patterns
5. 🎨 Experiment with the TypeScript terminal for creative scenes

## Getting Help

- 📚 Documentation: Check README.md and ARCHITECTURE.md
- 🐛 Issues: https://github.com/corhessa/Vizia-engine/issues
- 💬 Discussions: GitHub Discussions page

## What's Next?

Some ideas for your first project:
- Create an architectural visualization
- Design a game level layout
- Build a 3D data visualization
- Prototype a VR scene
- Experiment with procedural generation

Have fun creating with Vizia Engine! 🎨🚀

---

*Made with ❤️ by the Vizia Team*
