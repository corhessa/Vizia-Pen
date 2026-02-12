# Vizia Engine - Professional 3D Editor

A comprehensive 3D editor built with PyQt5 and Galacean Engine, featuring a modern dark-themed interface with Unity/Godot-inspired workflow.

## What It Does

Vizia Engine is a professional 3D editor that can run as a Vizia-Pen plugin. It provides:

- **Modern Editor Interface** with dark theme
- **Real-time 3D Rendering** powered by Galacean Engine
- **Scene Management** - Save/load scenes in JSON format
- **Undo/Redo System** - Full history support for all operations
- **TypeScript Scripting** - Interactive scene manipulation

## How It Works

### As a Vizia-Pen Plugin

The engine integrates with Vizia-Pen through the plugin system. Simply click the Engine icon in the toolbar to launch the 3D editor.

### Standalone Mode

You can also run the editor independently:
```bash
python main.py
```

## Features

### 🎨 Editor Interface
- **Toolbar** - Play/Pause/Stop controls and transform tools (Move, Rotate, Scale)
- **Hierarchy Panel** - Scene object tree with parent-child relationships
- **3D Viewport** - Galacean Engine powered real-time 3D rendering
- **Inspector Panel** - Object properties, transform, materials, and components
- **Asset Browser** - File management and asset organization
- **Console Panel** - Log, warning, and error messages with filtering
- **TypeScript Terminal** - Interactive code execution with Monaco Editor

### ⌨️ Keyboard Shortcuts
- `Ctrl+S` - Save scene
- `Ctrl+Z` - Undo
- `Ctrl+Y` or `Ctrl+Shift+Z` - Redo
- `W` - Move tool
- `E` - Rotate tool
- `R` - Scale tool
- `Delete` - Delete selected object
- `F` - Focus on selected object
- `Ctrl+D` - Duplicate object

## Dependencies

### Required
- Python 3.7 or higher
- PyQt5 >= 5.15.11
- PyQtWebEngine >= 5.15.7
- Internet connection (for Galacean Engine CDN)

### Installation

```bash
pip install -r requirements.txt
```

### Common Installation Issues

**Issue**: PyQtWebEngine not installing properly  
**Solution**: Make sure PyQt5 and PyQtWebEngine versions match:
```bash
pip uninstall PyQt5 PyQtWebEngine
pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7
```

**Issue**: "No module named 'PyQt5.QtWebEngineWidgets'"  
**Solution**: Install PyQtWebEngine separately:
```bash
pip install PyQtWebEngine==5.15.7
```

## Project Structure

```
vizia-engine/
├── main.py                    # Standalone launcher
├── plugin.py                  # Plugin mode interface
├── requirements.txt           # Python dependencies
├── engine/
│   ├── viewport.py           # Main PyQt5 window
│   ├── resources.py          # Resource path management
│   └── bridge.py             # Python-JavaScript bridge
├── web/
│   ├── vizia_editor.html     # Main editor HTML
│   └── js/                   # JavaScript modules
└── icons/
    └── game.png              # Application icon
```

## Galacean Engine

Vizia Engine uses [Galacean Engine](https://galacean.antgroup.com/) for 3D rendering:
- High-performance WebGL2 renderer
- Modern PBR materials
- Advanced lighting system
- Component-based architecture
- Loaded via CDN (no build step required)

**Note**: Internet connection is required for Galacean Engine CDN.

## Troubleshooting

### Editor won't start
1. Check Python version: `python --version` (3.7+)
2. Verify dependencies: `pip list | grep PyQt`
3. Check console for error messages

### Black screen in viewport
1. Ensure internet connection for Galacean CDN
2. Check browser console for WebGL errors
3. Update graphics drivers

---

**Vizia Engine** - Building the future of 3D content creation 🚀
