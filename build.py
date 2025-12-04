#!/usr/bin/env python3
"""
Just Code Editor - Build Script
Cross-platform build system using PyInstaller.

Usage:
    python build.py              # Build for current platform
    python build.py --clean      # Clean build artifacts
    python build.py --onefile    # Build single executable (larger, slower startup)
    python build.py --debug      # Build with console output for debugging
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path

# Application info
APP_NAME = 'JustCode'
APP_VERSION = '1.0.0'

# Directories
ROOT_DIR = Path(__file__).parent.absolute()
DIST_DIR = ROOT_DIR / 'dist'
BUILD_DIR = ROOT_DIR / 'build'
SPEC_FILE = ROOT_DIR / 'justcode.spec'


def get_platform():
    """Get current platform name."""
    if sys.platform == 'win32':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'


def clean():
    """Remove build artifacts."""
    print("Cleaning build artifacts...")
    
    dirs_to_clean = [DIST_DIR, BUILD_DIR]
    for d in dirs_to_clean:
        if d.exists():
            print(f"  Removing {d}")
            shutil.rmtree(d)
    
    # Remove __pycache__ directories
    for pycache in ROOT_DIR.rglob('__pycache__'):
        if 'venv' not in str(pycache):
            print(f"  Removing {pycache}")
            shutil.rmtree(pycache)
    
    print("Clean complete.")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    missing = []

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"  PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        missing.append('pyinstaller')

    # Check PyQt6
    try:
        from PyQt6 import QtCore
        print(f"  PyQt6: {QtCore.PYQT_VERSION_STR}")
    except ImportError:
        missing.append('PyQt6')

    # Check QScintilla
    try:
        from PyQt6 import Qsci
        print("  PyQt6-QScintilla: OK")
    except ImportError:
        missing.append('PyQt6-QScintilla')

    # Check lupa
    try:
        import lupa
        print(f"  lupa: {lupa.LUA_VERSION}")
    except ImportError:
        missing.append('lupa')

    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + ' '.join(missing))
        return False

    print("\nAll dependencies found.")
    return True


def build(onefile=False, debug=False):
    """Build the application."""
    platform = get_platform()
    print(f"\n{'='*50}")
    print(f"Building Just Code for {platform}")
    print(f"{'='*50}\n")

    if not check_dependencies():
        sys.exit(1)

    # Set environment variable for debug mode (read by spec file)
    env = os.environ.copy()
    if debug:
        env['JUSTCODE_DEBUG'] = '1'
        print("Debug mode: console output enabled")

    # Build command - use spec file for full control
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
    ]

    if onefile:
        print("Note: --onefile requires direct PyInstaller call, not spec file")
        cmd.extend([
            '--onefile',
            '--name', APP_NAME,
            '--add-data', f'justcode/resources/default_configs:justcode/resources/default_configs',
            '--add-data', f'justcode/resources/icons:justcode/resources/icons',
            '--hidden-import', 'justcode',
            '--hidden-import', 'justcode.app',
            '--hidden-import', 'justcode.config',
            '--hidden-import', 'justcode.editor',
            '--hidden-import', 'justcode.panels',
            '--hidden-import', 'justcode.plugins',
            '--hidden-import', 'lupa',
            '--hidden-import', 'lupa.lua54',
        ])
        # Add icon based on platform
        if platform == 'windows':
            icon_path = ROOT_DIR / 'justcode' / 'resources' / 'icons' / 'justcode.ico'
            if icon_path.exists():
                cmd.extend(['--icon', str(icon_path)])
        elif platform == 'macos':
            icon_path = ROOT_DIR / 'justcode' / 'resources' / 'icons' / 'justcode.png'
            if icon_path.exists():
                cmd.extend(['--icon', str(icon_path)])
        if not debug:
            cmd.append('--windowed')
        cmd.append('run_justcode.py')
    else:
        cmd.append(str(SPEC_FILE))

    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=ROOT_DIR, env=env)
    
    if result.returncode != 0:
        print("\nBuild failed!")
        sys.exit(1)
    
    # Post-build info
    print(f"\n{'='*50}")
    print("Build complete!")
    print(f"{'='*50}")

    output_dir = DIST_DIR / APP_NAME
    if output_dir.exists():
        print(f"\nOutput: {output_dir}")

        # Calculate size
        total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
        print(f"Size: {total_size / (1024*1024):.1f} MB")

        # Platform-specific instructions
        if platform == 'linux':
            print(f"\nTo run: {output_dir / APP_NAME}")
        elif platform == 'macos':
            app_bundle = DIST_DIR / f'{APP_NAME}.app'
            if app_bundle.exists():
                print(f"\nTo run: open {app_bundle}")
        elif platform == 'windows':
            print(f"\nTo run: {output_dir / f'{APP_NAME}.exe'}")

    return output_dir


def package(onefile=False):
    """Create distributable archive from built application."""
    import tarfile
    import zipfile

    platform = get_platform()

    print(f"\n{'='*50}")
    print(f"Packaging Just Code for {platform}")
    print(f"{'='*50}\n")

    # Determine what to package
    if onefile:
        if platform == 'windows':
            source = DIST_DIR / f'{APP_NAME}.exe'
        else:
            source = DIST_DIR / APP_NAME
        if not source.exists():
            print(f"Error: {source} not found. Run build first.")
            sys.exit(1)
    else:
        if platform == 'macos':
            source = DIST_DIR / f'{APP_NAME}.app'
            if not source.exists():
                source = DIST_DIR / APP_NAME
        else:
            source = DIST_DIR / APP_NAME

        if not source.exists():
            print(f"Error: {source} not found. Run build first.")
            sys.exit(1)

    # Create archive name with version and platform
    archive_base = f'{APP_NAME}-{APP_VERSION}-{platform}'

    if platform == 'linux':
        # Create .tar.gz for Linux
        archive_path = DIST_DIR / f'{archive_base}.tar.gz'
        print(f"Creating {archive_path.name}...")

        with tarfile.open(archive_path, 'w:gz') as tar:
            if onefile:
                tar.add(source, arcname=source.name)
            else:
                tar.add(source, arcname=APP_NAME)

    elif platform == 'windows':
        # Create .zip for Windows
        archive_path = DIST_DIR / f'{archive_base}.zip'
        print(f"Creating {archive_path.name}...")

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if onefile:
                zf.write(source, source.name)
            else:
                for file in source.rglob('*'):
                    if file.is_file():
                        arcname = Path(APP_NAME) / file.relative_to(source)
                        zf.write(file, arcname)

    elif platform == 'macos':
        # Create .zip for macOS (works for both .app bundles and folders)
        archive_path = DIST_DIR / f'{archive_base}.zip'
        print(f"Creating {archive_path.name}...")

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if onefile:
                zf.write(source, source.name)
            else:
                for file in source.rglob('*'):
                    if file.is_file():
                        arcname = Path(source.name) / file.relative_to(source)
                        zf.write(file, arcname)

    # Report results
    archive_size = archive_path.stat().st_size / (1024 * 1024)
    print(f"\nPackage created: {archive_path}")
    print(f"Size: {archive_size:.1f} MB")

    print(f"\n{'='*50}")
    print("Packaging complete!")
    print(f"{'='*50}")

    # Distribution instructions
    print(f"\nTo distribute:")
    print(f"  Upload {archive_path.name} to your release page")
    print(f"\nUser installation:")
    if platform == 'linux':
        print(f"  tar -xzf {archive_path.name}")
        print(f"  ./{APP_NAME}/{APP_NAME}")
    elif platform == 'windows':
        print(f"  Extract {archive_path.name}")
        print(f"  Run {APP_NAME}\\{APP_NAME}.exe")
    elif platform == 'macos':
        print(f"  Extract {archive_path.name}")
        print(f"  Open {source.name}")

    return archive_path


def main():
    parser = argparse.ArgumentParser(description='Build Just Code Editor')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--onefile', action='store_true', help='Build single executable')
    parser.add_argument('--debug', action='store_true', help='Build with console for debugging')
    parser.add_argument('--package', action='store_true', help='Create distributable archive after build')

    args = parser.parse_args()

    if args.clean:
        clean()
        if not args.onefile and not args.debug and not args.package:
            return

    # Build first (unless only packaging existing build)
    build(onefile=args.onefile, debug=args.debug)

    # Package if requested
    if args.package:
        package(onefile=args.onefile)


if __name__ == '__main__':
    main()

