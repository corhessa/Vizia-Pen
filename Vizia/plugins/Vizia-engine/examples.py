#!/usr/bin/env python3
"""
Vizia Engine - Example Usage
Demonstrates both standalone and plugin modes
"""

import sys
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def example_standalone():
    """
    Example 1: Run Vizia Engine in standalone mode
    This creates its own QApplication and runs independently
    """
    print("=" * 60)
    print("Example 1: Standalone Mode")
    print("=" * 60)
    
    from PyQt5.QtWidgets import QApplication
    from engine import ViziaEngineItem
    
    app = QApplication(sys.argv)
    
    # Create the editor window
    editor = ViziaEngineItem(None)
    editor.show()
    
    # Center on screen
    screen = app.primaryScreen().geometry()
    x = (screen.width() - editor.width()) // 2
    y = (screen.height() - editor.height()) // 2
    editor.move(x, y)
    
    print("✅ Vizia Engine started in standalone mode")
    print("   Close the window to exit")
    
    sys.exit(app.exec_())


def example_plugin():
    """
    Example 2: Use Vizia Engine as a plugin
    This integrates with an existing application
    """
    print("=" * 60)
    print("Example 2: Plugin Mode")
    print("=" * 60)
    
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
    from plugin import ViziaPlugin
    
    app = QApplication(sys.argv)
    
    # Create a main application window
    main_window = QMainWindow()
    main_window.setWindowTitle("Host Application")
    main_window.setGeometry(100, 100, 400, 300)
    
    # Create central widget
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # Add a button to launch Vizia Engine
    btn = QPushButton("Launch Vizia Engine")
    layout.addWidget(btn)
    
    main_window.setCentralWidget(central)
    
    # Create plugin instance
    plugin = ViziaPlugin()
    
    # Connect button to plugin
    btn.clicked.connect(lambda: plugin.run(main_window))
    
    main_window.show()
    
    print("✅ Host application started")
    print("   Click the button to launch Vizia Engine")
    
    sys.exit(app.exec_())


def example_programmatic():
    """
    Example 3: Programmatic scene creation
    Shows how to interact with the editor via JavaScript
    """
    print("=" * 60)
    print("Example 3: Programmatic Scene Creation")
    print("=" * 60)
    print()
    print("Once the editor is open, use the TypeScript Terminal:")
    print()
    print("// Add multiple cubes in a line")
    print("for (let i = 0; i < 5; i++) {")
    print("  app.scene.addCube(`Cube_${i}`, [i * 2, 1, 0]);")
    print("}")
    print()
    print("// Add a sphere")
    print("app.scene.addSphere('MySphere', [0, 2, 5]);")
    print()
    print("// Save the scene")
    print("app.saveScene();")
    print()
    print("// Get all objects")
    print("console.log(Array.from(app.scene.objects.keys()));")
    print()
    
    # Now run the editor
    example_standalone()


def show_menu():
    """Show example menu"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "VIZIA ENGINE EXAMPLES" + " " * 22 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("Choose an example to run:")
    print()
    print("  1. Standalone Mode")
    print("     Run Vizia Engine as a standalone application")
    print()
    print("  2. Plugin Mode")
    print("     Integrate Vizia Engine into an existing app")
    print()
    print("  3. Programmatic Scene Creation")
    print("     Learn how to create scenes via code")
    print()
    print("  Q. Quit")
    print()
    
    choice = input("Enter your choice (1-3 or Q): ").strip().upper()
    return choice


def main():
    """Main entry point"""
    
    # Check if PyQt5 is available
    try:
        import PyQt5
    except ImportError:
        print("❌ Error: PyQt5 not installed")
        print()
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        print()
        sys.exit(1)
    
    # Show menu
    choice = show_menu()
    
    if choice == "1":
        example_standalone()
    elif choice == "2":
        example_plugin()
    elif choice == "3":
        example_programmatic()
    elif choice == "Q":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice. Please run again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
