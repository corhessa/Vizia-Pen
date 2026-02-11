# Vizia Engine - Professional 3D Editor

A comprehensive 3D editor built with PyQt5 and Galacean Engine, featuring a modern dark-themed interface with Unity/Godot-inspired workflow.

## Features

### 🎨 Modern Editor Interface
- **Dark Theme** - Professional and eye-friendly interface
- **Toolbar** - Play/Pause/Stop controls and transform tools (Move, Rotate, Scale)
- **Hierarchy Panel** - Scene object tree with parent-child relationships
- **3D Viewport** - Galacean Engine powered real-time 3D rendering
- **Inspector Panel** - Object properties, transform, materials, and components
- **Asset Browser** - File management and asset organization
- **Console Panel** - Log, warning, and error messages with filtering
- **TypeScript Terminal** - Interactive code execution with Monaco Editor

### ⚡ Key Capabilities
- **Dual Mode Operation**:
  - Standalone mode: Run independently with `python main.py`
  - Plugin mode: Integrate with other applications via `plugin.py`
- **Real-time 3D Rendering** with Galacean Engine
- **Scene Management** - Save/load scenes in JSON format
- **Undo/Redo System** - Full history support for all operations
- **Keyboard Shortcuts** - Efficient workflow with standard shortcuts
- **TypeScript Scripting** - Interactive scene manipulation via terminal

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

## Installation

### Prerequisites
- Python 3.7 or higher
- Internet connection (for Galacean Engine CDN)

### Step 1: Clone the Repository
```bash
git clone https://github.com/corhessa/Vizia-engine.git
cd Vizia-engine
```

### Step 2: Install Dependencies

#### Linux
```bash
# Install PyQt5 dependencies
sudo apt-get update
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine

# Or use pip
pip install -r requirements.txt
```

#### macOS
```bash
# Install using Homebrew (recommended)
brew install pyqt@5

# Or use pip
pip install -r requirements.txt
```

#### Windows
```bash
# Use pip
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

## Usage

### Standalone Mode (Recommended)
Run the editor as a standalone application:
```bash
python main.py
```

### Plugin Mode
Use Vizia Engine as a plugin in another application:
```python
from engine import ViziaEngineItem
from PyQt5.QtWidgets import QApplication

app = QApplication([])
overlay = None  # Your overlay/parent widget
window = ViziaEngineItem(overlay)
window.show()
app.exec_()
```

Or use the plugin wrapper:
```python
from plugin import ViziaPlugin

plugin = ViziaPlugin()
plugin.run(overlay)
```

## Project Structure

```
Vizia-engine/
├── main.py                    # Standalone launcher
├── plugin.py                  # Plugin mode interface
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── engine/
│   ├── __init__.py           # Package initialization
│   ├── viewport.py           # Main PyQt5 window
│   ├── resources.py          # Resource path management
│   └── bridge.py             # Python-JavaScript bridge
├── web/
│   ├── vizia_editor.html     # Main editor HTML
│   └── js/
│       ├── app.js            # Application entry point
│       ├── scene.js          # Scene management (Galacean)
│       ├── ui.js             # UI panel management
│       ├── inspector.js      # Inspector panel
│       ├── hierarchy.js      # Hierarchy panel
│       ├── toolbar.js        # Toolbar controls
│       ├── console.js        # Console panel
│       ├── terminal.js       # TypeScript terminal
│       ├── shortcuts.js      # Keyboard shortcuts
│       ├── history.js        # Undo/Redo system
│       └── storage.js        # Scene persistence
└── icons/
    └── game.png              # Application icon
```

## Editor Panels

### Toolbar
- **Play/Pause/Stop** - Scene playback controls
- **Transform Tools** - Move (W), Rotate (E), Scale (R)
- **Gizmo Toggle** - Show/hide transform handles
- **Save Button** - Quick save scene

### Hierarchy Panel
- Tree view of all scene objects
- Parent-child relationships
- Right-click context menu for adding objects
- Search functionality
- Drag and drop support

### 3D Viewport
- Real-time Galacean Engine rendering
- Grid display
- Transform gizmos
- Camera controls:
  - **Orbit**: Alt + Left Click
  - **Pan**: Middle Mouse / Alt + Right Click
  - **Zoom**: Mouse Wheel
- Object selection by clicking

### Inspector Panel
- **Transform**: Position, Rotation, Scale controls
- **Material**: Color, metalness, roughness
- **Light**: Intensity, color, range
- **Components**: Add/remove object components

### Asset Browser
- File management interface
- Scene file listing
- Preview thumbnails (future)
- Import/export support

### Console Panel
- Log messages with timestamps
- Warning and error filtering
- Clear button
- Auto-scroll to bottom

### TypeScript Terminal
- Monaco Editor integration
- TypeScript syntax highlighting
- Code execution with output display
- Galacean API access for scene manipulation
- Multi-line code support
- History navigation

## Scene System

Scenes are saved in JSON format with the following structure:
```json
{
  "version": "1.0",
  "objects": [
    {
      "id": "unique-id",
      "name": "Cube",
      "type": "mesh",
      "transform": {
        "position": [0, 0, 0],
        "rotation": [0, 0, 0],
        "scale": [1, 1, 1]
      },
      "material": {
        "color": "#ffffff",
        "metalness": 0.5,
        "roughness": 0.5
      },
      "children": []
    }
  ]
}
```

## Galacean Engine

Vizia Engine uses [Galacean Engine](https://galacean.antgroup.com/) for 3D rendering:
- High-performance WebGL2 renderer
- Modern PBR materials
- Advanced lighting system
- Component-based architecture
- Loaded via CDN (no build step required)

**Note**: Internet connection is required for Galacean Engine CDN. If unavailable, the editor will fall back to Three.js.

## Development

### Adding New Features
1. JavaScript modules are in `web/js/`
2. Python backend is in `engine/`
3. Communication via PyQt5 WebChannel (bridge.py)

### Testing
Run the editor in standalone mode for testing:
```bash
python main.py
```

### Debugging
- JavaScript console: Available in TypeScript Terminal panel
- Python console: Check terminal output when running main.py

## Requirements

### Python Dependencies
- PyQt5 >= 5.15.11
- PyQtWebEngine >= 5.15.7

### Browser Requirements
- WebGL2 support
- Modern JavaScript (ES6+)
- LocalStorage enabled

## Troubleshooting

### Editor won't start
1. Check Python version: `python --version` (3.7+)
2. Verify dependencies: `pip list | grep PyQt`
3. Check console for error messages

### Black screen in viewport
1. Ensure internet connection for Galacean CDN
2. Check browser console for WebGL errors
3. Update graphics drivers

### Import errors
1. Ensure you're in the correct directory
2. Run from project root: `python main.py`
3. Check Python path includes engine module

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Specify your license here]

## Credits

- **Galacean Engine** - 3D rendering engine by Ant Group
- **PyQt5** - Python Qt bindings
- **Monaco Editor** - Code editor by Microsoft

## Support

For issues and questions:
- GitHub Issues: https://github.com/corhessa/Vizia-engine/issues
- Documentation: [Add docs link]

---

**Vizia Engine** - Building the future of 3D content creation 🚀

