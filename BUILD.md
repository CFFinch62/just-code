# Just Code - Build Guide

Build instructions for creating standalone executables using PyInstaller.

## Prerequisites

### All Platforms
- Python 3.10+ 
- pip (Python package manager)
- Virtual environment (recommended)

### Platform-Specific

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-dev python3-venv

# Fedora
sudo dnf install python3-devel
```

**macOS:**
```bash
# Xcode command line tools
xcode-select --install
```

**Windows:**
- Python from python.org (not Microsoft Store version)
- Visual C++ Build Tools (for some dependencies)

## Setup

1. Clone the repository and create virtual environment:
```bash
git clone <repo-url>
cd JustCode
python -m venv venv
```

2. Activate virtual environment:
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Building

### Quick Build (Current Platform)

```bash
python build.py
```

Output: `dist/JustCode/`

### Build Options

| Option | Description |
|--------|-------------|
| `--clean` | Remove build artifacts before building |
| `--debug` | Build with console output for debugging |
| `--onefile` | Create single executable (larger, slower startup) |

Examples:
```bash
python build.py --clean           # Clean and build
python build.py --debug           # Build with console output
python build.py --clean --debug   # Clean build with debug
```

### Platform Scripts

**Linux:**
```bash
./scripts/build-linux.sh
```

**macOS:**
```bash
./scripts/build-macos.sh
```

**Windows:**
```cmd
scripts\build-windows.bat
```

## Output

### Linux
```
dist/JustCode/
├── JustCode              # Main executable
├── _internal/            # Dependencies
└── ...
```

Run with: `./dist/JustCode/JustCode`

### macOS
```
dist/JustCode.app/        # Application bundle
```

Run with: `open dist/JustCode.app`

Create DMG for distribution:
```bash
hdiutil create -volname JustCode -srcfolder dist/JustCode.app -ov dist/JustCode.dmg
```

### Windows
```
dist/JustCode/
├── JustCode.exe          # Main executable
├── _internal/            # Dependencies
└── ...
```

Run with: `dist\JustCode\JustCode.exe`

## File Structure

```
JustCode/
├── build.py              # Main build script
├── justcode.spec         # PyInstaller spec file
├── run_justcode.py       # Entry point for PyInstaller
├── scripts/
│   ├── build-linux.sh    # Linux build script
│   ├── build-macos.sh    # macOS build script
│   └── build-windows.bat # Windows build script
```

## Troubleshooting

### Missing Dependencies
```
ModuleNotFoundError: No module named 'xxx'
```
Add the module to `hiddenimports` in `justcode.spec`.

### Application Won't Start
Build with `--debug` to see console output:
```bash
python build.py --debug
./dist/JustCode/JustCode
```

### Large Output Size
The default build is ~240MB due to Qt libraries. Use `--onefile` for a single executable (slower startup but easier distribution).

### Icon Not Showing
Place icons in `justcode/resources/icons/`:
- `justcode.ico` (Windows)
- `justcode.icns` (macOS)

## Cross-Compilation

PyInstaller does not support cross-compilation. Build on each target platform:

- **Linux binary** → Build on Linux
- **Windows EXE** → Build on Windows  
- **macOS App** → Build on macOS

For CI/CD, use GitHub Actions with matrix builds across platforms.

