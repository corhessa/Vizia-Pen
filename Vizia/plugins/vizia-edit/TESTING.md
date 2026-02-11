# Vizia Edit - Installation & Testing Guide

## Quick Start

### 1. Otomatik Kurulum (Önerilen)

**Linux/macOS:**
```bash
./install.sh
```

**Windows:**
```
install.bat
```

**Manuel Kurulum:**

```bash
# Bağımlılıkları kontrol et
python3 check_dependencies.py

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
# Ubuntu/Debian:
sudo apt install ffmpeg mpv libmpv-dev

# macOS (Homebrew):
brew install ffmpeg mpv

# Windows: Download from official sites and add to PATH
```

**❗ Kurulum Sorunları?** Detaylı çözümler için [INSTALL.md](INSTALL.md) dosyasına bakın.

### 2. Run Standalone

```bash
python run.py
```

### 3. Use as Vizia-Pen Plugin

1. Copy the entire `vizia-edit` folder to `Vizia/plugins/`
2. Launch Vizia-Pen
3. Click "Vizia Edit" in the Extensions drawer

## Testing Without Full Installation

### Test Core Engine (No GUI)

The core video editing engine can be tested without PyQt5 or FFmpeg:

```bash
python3 << 'EOF'
from src.core.timeline import Timeline, Track, Clip
from src.core.project import Project

# Create project
project = Project("My Video")

# Add clip
clip = Clip(
    filepath="video.mp4",
    start_time=0.0,
    duration=10.0,
    media_duration=10.0
)
project.timeline.tracks[0].add_clip(clip)

# Save project
project.save("/tmp/test.vzproj")

# Load project
loaded = Project.load("/tmp/test.vzproj")
print(f"Loaded: {loaded.name}")
EOF
```

### Check FFmpeg

```bash
ffmpeg -version
```

If not installed, video processing features will not work but the UI will still load.

### Check mpv

```bash
mpv --version
```

If not installed, the app will fall back to QMediaPlayer for preview.

## Features Checklist

### ✅ Implemented
- [x] Project management (save/load JSON)
- [x] Timeline data model (tracks, clips)
- [x] FFmpeg integration (video/audio processing)
- [x] Effects system (filters, color correction)
- [x] Export engine (with hardware encoding support)
- [x] Thumbnail generator
- [x] Vizia Dark + Purple theme
- [x] Custom title bar (frameless window)
- [x] Media browser with drag & drop
- [x] Timeline widget with QGraphicsScene
- [x] Preview player (mpv integration)
- [x] Properties panel
- [x] Effects panel
- [x] Text editor
- [x] Audio mixer
- [x] Export dialog
- [x] Keyboard shortcuts
- [x] Auto-save functionality

### 🚧 Can Be Enhanced
- [ ] More advanced timeline interactions (drag clips, resize, split)
- [ ] Waveform visualization (NumPy-based)
- [ ] More transition effects
- [ ] Real-time preview with effects
- [ ] Undo/Redo system
- [ ] Keyframe animation
- [ ] Multi-language support
- [ ] Custom keyboard shortcuts

## Architecture

### Performance Design

**Python is only used for UI and orchestration. All heavy processing uses native tools:**

- **Video Processing**: FFmpeg subprocess (not Python)
- **Audio Processing**: FFmpeg subprocess (not Python)  
- **Preview/Playback**: mpv player (GPU accelerated)
- **Thumbnails**: FFmpeg batch extraction
- **Export**: FFmpeg with hardware encoding (NVENC/QSV)
- **Timeline**: QGraphicsScene (hardware accelerated)
- **Waveform**: NumPy computations

### Module Organization

```
src/
├── core/          # Core editing engine (no UI)
│   ├── timeline.py      # Data model
│   ├── project.py       # Save/load
│   ├── video_engine.py  # FFmpeg wrapper
│   ├── audio_engine.py  # Audio processing
│   ├── effects.py       # Effect definitions
│   ├── export.py        # Export pipeline
│   └── thumbnails.py    # Thumbnail generator
├── ui/            # PyQt5 UI components
├── utils/         # Utilities
└── widgets/       # Custom widgets
```

## Troubleshooting

### "FFmpeg not found"
Install FFmpeg and ensure it's in your PATH:
```bash
ffmpeg -version
```

### "python-mpv not available"
Install mpv development libraries:
```bash
# Ubuntu
sudo apt install mpv libmpv-dev
pip install python-mpv
```

### Import errors
Make sure PyQt5 is installed:
```bash
pip install PyQt5
```

### Export fails
- Check disk space
- Verify output directory permissions
- Check FFmpeg logs in console

## Development

### Code Style
- Comments and UI text: Turkish
- Variable/function names: English
- Type hints: Used throughout
- Docstrings: Turkish

### Adding New Effects

1. Define effect in `src/core/effects.py`
2. Add FFmpeg filter implementation
3. Update UI in `src/ui/effects_panel.py`

### Adding New Export Formats

1. Update `EXPORT_FORMATS` in `src/utils/constants.py`
2. Add format-specific logic in `src/core/export.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## License

Developed for the Vizia ecosystem.

---

**Vizia Edit** - Making professional video editing accessible! 🎬
