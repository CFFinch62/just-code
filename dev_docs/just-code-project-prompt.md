# Just Code Editor - Project Development Prompt

## Who I Am

I am a 63-year-old developer with 40+ years of programming experience spanning BASIC, Python, Ruby, Lisp dialects (particularly Racket), and extensive work with PyQt. I work in marine electronics professionally, wearing multiple technical hats, and operate as a freelance developer. I have a strong preference for literal, structured thinking and data-driven approaches. I favor languages with natural structure over brace-and-semicolon syntax. I am also passionate about teaching programming to young students, emphasizing critical thinking over rote coding.

## Project Overview

**Project Name:** Just Code

**Philosophy:** The name carries three intentional meanings:
1. "Just code already" - an imperative to get to work
2. "It's just code" - nothing else, no clutter, no noise
3. "Just" as in righteous - proper, well-crafted code

**Core Problem:** Modern code editors and IDEs are visually noisy. They present more icons, menu items, panels, and features than most users need or will ever use. This project is a rebellion against that bloat.

**Target Platform:** Linux as primary development environment, with cross-platform distribution as a future goal. This is native desktop software, not Electron.

**Technology Stack:**
- Python (my strongest language)
- PyQt6 with QScintilla for the editor component
- JSON for all configuration and plugin definitions

## Design Principles

1. **Invisible until needed** - UI elements should auto-hide and appear only on demand
2. **Configuration as code** - Settings are JSON files edited in the editor itself (eat your own dog food)
3. **Minimal by default, powerful when needed** - Simple surface, depth available for those who seek it
4. **No visual noise** - Every pixel on screen must earn its place

## Core UI Architecture

### Default State
The editor launches to a clean, focused view: just the code editing pane. No sidebars visible. No terminal. No status bar clutter. Just code.

### File/Project Browser (Left Panel)
- **Default state:** Hidden
- **Reveal trigger:** Mouse hover at left edge OR keyboard shortcut
- **Behavior:** Slides in smoothly, slides out when focus returns to editor
- **Content:** Simple tree view of files and folders, minimal icons

### Terminal Panel (Bottom)
- **Default state:** Hidden
- **Reveal trigger:** Keyboard shortcut OR menu action
- **Behavior:** Slides up from bottom, can be dismissed easily
- **Content:** Standard terminal emulator functionality

### Menu Bar
Minimal, essential items only:
- File (New, Open, Open Folder, Save, Save As, Recent, Exit)
- Edit (Undo, Redo, Cut, Copy, Paste, Find, Replace)
- View (Toggle File Browser, Toggle Terminal, Zoom)
- Settings (opens JSON config files directly in editor)
- Help (About, Keyboard Shortcuts)

### Toolbar
Either nonexistent or extremely minimal (3-5 icons maximum). Consider making it optional/hideable.

### Status Bar
Minimal or hidden. If present, show only: cursor position, file encoding (if non-UTF8), file modified indicator. No git branch, no language selector, no extension spam.

## Configuration System

All settings live in JSON files within a config directory (e.g., `~/.justcode/` or `~/.config/justcode/`).

### Configuration Files

**settings.json** - Core editor behavior
```json
{
  "editor": {
    "font_family": "JetBrains Mono",
    "font_size": 14,
    "tab_width": 4,
    "use_spaces": true,
    "word_wrap": false,
    "line_numbers": true,
    "highlight_current_line": true,
    "auto_indent": true
  },
  "ui": {
    "theme": "default-dark",
    "file_browser_auto_hide": true,
    "terminal_auto_hide": true,
    "show_toolbar": false,
    "show_status_bar": true
  },
  "behavior": {
    "auto_save_delay_seconds": 30,
    "remember_open_files": true,
    "trim_trailing_whitespace": true
  }
}
```

**ui-themes.json** - Visual theming
```json
{
  "themes": {
    "default-dark": {
      "background": "#1e1e1e",
      "foreground": "#d4d4d4",
      "selection": "#264f78",
      "cursor": "#ffffff",
      "line_highlight": "#2a2a2a",
      "panel_background": "#252526",
      "panel_border": "#3c3c3c"
    }
  }
}
```

**syntax-themes.json** - Syntax highlighting colors (separate from UI theme)
```json
{
  "themes": {
    "default": {
      "keyword": "#569cd6",
      "string": "#ce9178",
      "number": "#b5cea8",
      "comment": "#6a9955",
      "function": "#dcdcaa",
      "class": "#4ec9b0",
      "operator": "#d4d4d4"
    }
  }
}
```

**languages.json** - Language-specific settings
```json
{
  "python": {
    "extensions": [".py", ".pyw"],
    "tab_width": 4,
    "use_spaces": true,
    "comment_string": "#",
    "syntax_theme": "default"
  },
  "javascript": {
    "extensions": [".js", ".mjs"],
    "tab_width": 2,
    "use_spaces": true,
    "comment_string": "//",
    "syntax_theme": "default"
  }
}
```

**keybindings.json** - Keyboard shortcuts
```json
{
  "file.new": "Ctrl+N",
  "file.open": "Ctrl+O",
  "file.save": "Ctrl+S",
  "file.save_as": "Ctrl+Shift+S",
  "edit.find": "Ctrl+F",
  "edit.replace": "Ctrl+H",
  "view.toggle_file_browser": "Ctrl+B",
  "view.toggle_terminal": "Ctrl+`",
  "view.command_palette": "Ctrl+Shift+P"
}
```

### Editing Settings
When user accesses Settings menu, the appropriate JSON file opens in a new editor tab. The editor itself is the settings UI. Changes take effect on save.

## Plugin System (Hybrid Approach)

Plugins follow a hybrid model: declarative JSON for simple use cases, with optional scripting for advanced needs.

### Plugin Structure
Each plugin is a directory containing:
```
my-plugin/
  plugin.json      # Required: metadata and declarative actions
  scripts/         # Optional: Lua or Python scripts for advanced logic
    action.lua
```

### Declarative Plugin Example (JSON Only)
```json
{
  "name": "Python Black Formatter",
  "version": "1.0.0",
  "description": "Format Python files using Black",
  "author": "Just Code Community",
  
  "triggers": [
    {
      "id": "format_on_save",
      "type": "on_save",
      "context": {"languages": ["python"]}
    },
    {
      "id": "format_manual",
      "type": "command",
      "command_name": "Format with Black",
      "shortcut": "Ctrl+Shift+B",
      "context": {"languages": ["python"]}
    }
  ],
  
  "actions": {
    "format_on_save": {
      "type": "external_command",
      "command": "black --quiet -",
      "input": "file_contents",
      "output": "replace_file_contents"
    },
    "format_manual": {
      "type": "external_command", 
      "command": "black --quiet -",
      "input": "file_contents",
      "output": "replace_file_contents"
    }
  }
}
```

### Scripted Plugin Example (JSON + Lua)
```json
{
  "name": "Smart Import Organizer",
  "version": "1.0.0",
  "description": "Intelligently sorts and groups Python imports",
  "author": "Just Code Community",
  
  "triggers": [
    {
      "id": "organize",
      "type": "command",
      "command_name": "Organize Imports",
      "shortcut": "Ctrl+Shift+I",
      "context": {"languages": ["python"]}
    }
  ],
  
  "actions": {
    "organize": {
      "type": "script",
      "engine": "lua",
      "file": "scripts/organize.lua",
      "entry_point": "organize_imports"
    }
  }
}
```

### Built-in Action Types (Declarative)
The editor should support these action types natively:

- **external_command** - Run shell command, pipe content in/out
- **snippet** - Insert templated text with variables
- **transform** - Built-in text transformations (uppercase, lowercase, sort lines, etc.)
- **notify** - Show a notification message
- **open_file** - Open a specific file
- **chain** - Execute multiple actions in sequence

### Script Engine
- Primary: Lua (lightweight, embeddable, sandboxed)
- Secondary/Optional: Python (for power users who want full ecosystem access)
- Scripts receive an editor API object with methods like:
  - `get_text()`, `set_text(string)`
  - `get_selection()`, `set_selection(start, end)`
  - `get_cursor_position()`, `set_cursor_position(line, col)`
  - `get_current_language()`
  - `show_notification(message)`

## Development Phases

### Phase 1: Core Editor
- Main window with QScintilla editor pane
- Basic file operations (new, open, save, save as)
- Simple menu bar
- JSON configuration loading for editor settings
- Single UI theme (dark)
- Syntax highlighting for Python (proof of concept)

### Phase 2: Panel System
- Auto-hiding file browser panel
- Auto-hiding terminal panel
- Smooth slide animations
- Keyboard shortcuts for panel toggle

### Phase 3: Configuration System
- All JSON config files implemented
- Settings menu opens config files in editor
- Live reload of settings on file save
- UI theme switching
- Syntax theme switching

### Phase 4: Multi-file Editing
- Tab bar for open files (minimal styling)
- Tab management (close, close others, close all)
- Remember open files between sessions
- Modified file indicators

### Phase 5: Plugin System (Declarative)
- Plugin discovery and loading
- Trigger system (commands, shortcuts, on_save, etc.)
- Built-in action types implementation
- Plugin error handling and reporting

### Phase 6: Plugin System (Scripted)
- Lua engine integration
- Editor API for scripts
- Script sandboxing and security
- Optional Python script support

### Phase 7: Polish and Distribution
- Additional language support
- Additional themes
- Keyboard shortcut customization UI (optional)
- Cross-platform testing
- Packaging for distribution (PyInstaller or similar)

## Technical Requirements

### Dependencies
- Python 3.10+
- PyQt6
- QScintilla (PyQt6-QScintilla)
- lupa (Lua integration for Python) - for Phase 6

### Code Style
- Clean, readable Python
- Type hints where helpful
- Docstrings for public methods
- Logical module organization
- No premature optimization

### Project Structure
```
justcode/
  main.py                 # Entry point
  app/
    __init__.py
    application.py        # QApplication subclass, app lifecycle
    main_window.py        # Main window, coordinates panels
  editor/
    __init__.py
    editor_widget.py      # QScintilla wrapper
    syntax/
      __init__.py
      python.py           # Python lexer config
  panels/
    __init__.py
    file_browser.py       # Auto-hide file tree
    terminal.py           # Auto-hide terminal
  config/
    __init__.py
    loader.py             # JSON config loading
    settings.py           # Settings dataclasses
    themes.py             # Theme management
  plugins/
    __init__.py
    loader.py             # Plugin discovery and loading
    actions.py            # Built-in action implementations
    scripting/
      __init__.py
      lua_engine.py       # Lua script execution
  resources/
    default_configs/      # Default JSON config files
    icons/                # Minimal icon set
```

## Success Criteria

Just Code is successful when:

1. Opening the app feels calm - no visual assault
2. I can start typing code within 1 second of launch
3. I never see a UI element I didn't ask for
4. Editing settings feels natural (it's just editing JSON)
5. Adding a simple plugin requires no programming knowledge
6. The app stays out of my way while still being capable
7. A student seeing it for the first time isn't overwhelmed
8. I actually want to use it for my own work

## What I Don't Want

- Electron or web-based anything
- Extension marketplace integration
- Telemetry or analytics
- Auto-update nagging
- "Getting Started" welcome tabs
- Tip of the day
- Activity bars with colored badges
- Git integration in the UI (use the terminal)
- Minimap
- Breadcrumbs
- Multiple cursors (keep it simple)
- AI integration (ironic, I know)
- Language server protocol complexity

## Reference Points

Editors to study for what TO do:
- Gedit (simplicity)
- Lite XL (lightweight, Lua-based)
- Micro (terminal editor, simple config)

Editors to study for what NOT to do:
- VS Code (feature creep, Electron)
- Atom (slow, Electron, dead)
- Any JetBrains IDE (powerful but overwhelming)

## Final Notes

This editor is being built for me first. It scratches my itch. If others find it useful, wonderful. But the primary user is a 63-year-old developer who has seen enough IDEs for a lifetime and just wants to write code in peace.

Build it incrementally. Get each phase working before moving on. Resist the urge to add features. When in doubt, leave it out.

The best code editor is the one that disappears.
