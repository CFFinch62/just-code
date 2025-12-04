# Just Code - User Guide

A minimalist code editor for Linux built with PyQt6 and QScintilla.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Working with Files](#working-with-files)
- [The Editor](#the-editor)
- [File Browser Panel](#file-browser-panel)
- [Terminal Panel](#terminal-panel)
- [Markdown Support](#markdown-support)
- [Customization](#customization)
- [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Getting Started

### Installation

```bash
# Clone or download the project
cd JustCode

# Run the setup script (creates virtual environment, installs dependencies)
./setup.sh

# Start the editor
./run.sh
```

### First Launch

On first launch, Just Code creates configuration files in `~/.config/justcode/`:
- `settings.json` - Editor and UI settings
- `ui-themes.json` - Color themes
- `syntax-themes.json` - Syntax highlighting colors
- `languages.json` - Language-specific settings
- `keybindings.json` - Keyboard shortcuts

---

## Interface Overview

Just Code follows a minimalist philosophy: **invisible until needed**.

```
┌─────────────────────────────────────────────────────────────────┐
│  File  Edit  View  Settings  Plugins  Help                      │  ← Menu Bar
├────────────────┬────────────────────────────────────────────────┤
│                │  Tab 1  │  Tab 2  │  Tab 3  │                  │  ← Tab Bar
│   File         ├─────────────────────────────────────────────────┤
│   Browser      │                                                 │
│   Panel        │              Editor Area                        │
│                │                                                 │
│   (Ctrl+B)     │                                                 │
│                │                                                 │
├────────────────┴─────────────────────────────────────────────────┤
│  Terminal Panel (Ctrl+`)                                         │
├──────────────────────────────────────────────────────────────────┤
│  Status Bar                                                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Working with Files

### Creating Files
- **Ctrl+N** - Create a new untitled file
- New files appear in tabs as "Untitled", "Untitled 2", etc.

### Opening Files
- **Ctrl+O** - Open file dialog
- **Ctrl+Shift+O** - Open a folder in the file browser
- Double-click files in the file browser panel

### Saving Files
- **Ctrl+S** - Save current file
- **Ctrl+Shift+S** - Save As (choose new location/name)
- Modified files show a **•** indicator in the tab

### Closing Files
- **Ctrl+W** - Close current tab
- Right-click tab → "Close Others" or "Close All"
- Unsaved changes prompt for confirmation

### Session Persistence
Just Code remembers your open files between sessions. This can be disabled in settings.

---

## The Editor

### Syntax Highlighting
Automatic syntax highlighting for 22+ languages based on file extension:
- Python (.py)
- JavaScript (.js, .mjs)
- TypeScript (.ts, .tsx)
- HTML, CSS, JSON, YAML, XML
- C, C++, C#, Java, Go, Rust
- Ruby, PHP, Perl, Lua
- Shell scripts, SQL, Makefiles
- Markdown (.md)

### Editor Features
- **Line numbers** - Toggle in settings
- **Auto-indent** - Maintains indentation level
- **Tab/Spaces** - Configurable per language
- **Word wrap** - Toggle in settings
- **Zoom** - Ctrl++ / Ctrl+- to adjust font size

### Font Selection
View → Font... opens a font picker dialog.

---

## File Browser Panel

Toggle with **Ctrl+B**. Shows project files in a tree view.

### Navigation
- **Double-click folder** - Enter directory
- **Double-click file** - Open in editor
- **↑ button** - Go to parent directory

### Bookmarks
Save frequently used directories:
1. Navigate to a directory
2. Edit settings.json (`Ctrl+,`)
3. Add paths to `file_browser.bookmarks` array

### Default Directory
Set a startup directory in settings:
```json
"file_browser": {
    "default_directory": "/path/to/your/projects"
}
```

---

## Terminal Panel

Toggle with **Ctrl+`** (backtick). A real bash terminal.

### Features
- Full bash shell access
- Command history (Up/Down arrows)
- Auto-syncs working directory with file browser
- **Ctrl+C** - Interrupt running command
- **Ctrl+L** - Clear screen

### Directory Sync
When you navigate in the file browser or open a file, the terminal automatically changes to that directory.

---

## Customization

Just Code uses **configuration as code**. All settings are JSON files edited directly in the editor.

### Accessing Settings
- **Ctrl+,** - Open settings.json
- **Settings menu** - Access all config files:
  - Open Settings
  - Open UI Themes
  - Open Syntax Themes
  - Open Languages
  - Open Keybindings

### Live Reload
Changes take effect immediately when you save. No restart required.

### UI Themes
16 built-in themes including:
- **Dark**: default-dark, monokai, dracula, nord, tokyo-night, one-dark, github-dark, catppuccin-mocha, ayu-dark, palenight
- **Light**: default-light, solarized-light, gruvbox-light
- **Special**: system (follows OS theme)

Change theme: Settings → UI Theme → [select theme]

### Syntax Themes
11 syntax color schemes: default, monokai, dracula, nord, solarized-dark, solarized-light, gruvbox-dark, gruvbox-light, one-dark, github-dark, light

---

## Keyboard Shortcuts

All shortcuts can be customized in `keybindings.json` (Settings → Open Keybindings).

### File Operations
| Shortcut | Action |
|----------|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+Shift+O | Open folder |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save As |
| Ctrl+W | Close tab |
| Ctrl+Q | Exit |

### Editing
| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Shift+Z | Redo |
| Ctrl+X | Cut |
| Ctrl+C | Copy |
| Ctrl+V | Paste |

### View
| Shortcut | Action |
|----------|--------|
| Ctrl+B | Toggle file browser |
| Ctrl+` | Toggle terminal |
| Ctrl+Shift+M | Toggle markdown preview |
| Ctrl++ | Zoom in |
| Ctrl+- | Zoom out |

### Settings
| Shortcut | Action |
|----------|--------|
| Ctrl+, | Open settings |

### Terminal Shortcuts
| Shortcut | Action |
|----------|--------|
| Up/Down | Command history |
| Ctrl+C | Interrupt command |
| Ctrl+L | Clear screen |

---

## Tips and Tricks

1. **Quick theme switch**: Use Settings → UI Theme menu for instant preview
2. **Project workflow**: Use Ctrl+Shift+O to open a project folder, then navigate with the file browser
3. **Markdown editing**: Open a .md file and press Ctrl+Shift+M for live preview
4. **Terminal integration**: Terminal auto-follows your file browser navigation
5. **Session restore**: Your open tabs are remembered between sessions
6. **Customize shortcuts**: Edit keybindings.json - changes apply on save

---

## Troubleshooting

### Editor doesn't start
```bash
# Check Python version (3.10+ required)
python3 --version

# Reinstall dependencies
./setup.sh
```

### Config files corrupted
Delete `~/.config/justcode/` to reset to defaults:
```bash
rm -rf ~/.config/justcode
```

### Theme not applying
- Make sure the theme name matches exactly (case-sensitive)
- Check for JSON syntax errors in ui-themes.json

---

For more information:
- **Configuration Reference**: See `CONFIG-REFERENCE.md`
- **Plugin Development**: See `PLUGIN-GUIDE.md`
