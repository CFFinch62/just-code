# Phase 6: Plugin System (Scripted) - Development Log

**Back to**: [CHANGELOG-Master.md](CHANGELOG-Master.md)

**Phase Status**: ✅ COMPLETE (2025-12-04)

**Goals**:
- [x] Lua engine integration (using lupa library)
- [x] Editor API for scripts
- [x] Script sandboxing and security
- [x] Optional Python script support

**Module Status**:
- `plugins/scripting/__init__.py` - ✅ Complete
- `plugins/scripting/lua_engine.py` - ✅ Complete (~180 lines)
- `plugins/scripting/python_engine.py` - ✅ Complete (~155 lines)
- `plugins/scripting/editor_api.py` - ✅ Complete (~115 lines)

---

## Phase 6 Implementation Plan

### Script Action Type
Plugins can use `"type": "script"` in their actions:
```json
{
  "actions": {
    "my_action": {
      "type": "script",
      "engine": "lua",
      "file": "scripts/my_script.lua",
      "entry_point": "main_function"
    }
  }
}
```

### Editor API
Scripts receive an `editor` object with these methods:
- `editor.get_text()` - Get full editor text
- `editor.set_text(string)` - Replace full editor text
- `editor.get_selection()` - Get selected text
- `editor.replace_selection(string)` - Replace selection
- `editor.get_cursor_position()` - Returns {line, column}
- `editor.set_cursor_position(line, column)` - Move cursor
- `editor.get_current_language()` - Get file language
- `editor.get_file_path()` - Get current file path
- `editor.show_notification(message)` - Show notification

### Security (Sandboxing)
Lua scripts run in a restricted environment:
- No file system access (io, os modules disabled)
- No network access
- No system command execution
- Only editor API and safe Lua builtins available

Python scripts (optional) have similar restrictions.

### Plugin Directory Structure
```
~/.config/justcode/plugins/
  my-lua-plugin/
    plugin.json
    scripts/
      my_script.lua
```

---

## Development Log

### Entry 1: Phase 6 Started (2025-12-04)
- Created CHANGELOG-Phase6.md
- Planning Lua engine implementation using lupa library
- Will implement Editor API for script access to editor

### Entry 2: Core Implementation (2025-12-04)
- Added lupa to requirements.txt and installed
- Created EditorAPI class with all editor interaction methods
- Created LuaEngine with sandboxing (disabled io, os, file operations)
- Created PythonEngine with restricted builtins
- Integrated script action type into ActionExecutor
- Updated PluginManager to pass plugin base path for script resolution
- Added set_cursor_position and get_language callbacks to main_window

### Entry 3: Example Plugins (2025-12-04)
- Created "Smart Comments" plugin (Lua) with:
  - Toggle Comment (Ctrl+/) - adds/removes language-appropriate comments
  - Wrap Selection in Stars - decorative box around text
  - Add File Header - adds timestamped header comment
- Created "Line Tools" plugin (Python) with:
  - Duplicate Lines (Ctrl+Shift+D)
  - Join Lines - merge selection into one line
  - Number Lines - add line numbers to selection

---

## Architecture

### Class Diagram
```
LuaEngine
├── __init__(editor_api)
├── execute_file(file_path, entry_point)
├── execute_string(code, entry_point)
└── _create_sandbox()

PythonEngine
├── __init__(editor_api)
├── execute_file(file_path, entry_point)
└── _create_restricted_globals()

EditorAPI
├── __init__(callbacks)
├── get_text() -> str
├── set_text(text: str)
├── get_selection() -> str
├── replace_selection(text: str)
├── get_cursor_position() -> dict
├── set_cursor_position(line: int, col: int)
├── get_current_language() -> str
├── get_file_path() -> str
└── show_notification(message: str)
```

### Integration with ActionExecutor
The ActionExecutor's `execute_script()` method will:
1. Determine script engine (lua or python)
2. Create EditorAPI instance with callbacks
3. Create engine instance with EditorAPI
4. Execute script file with entry point
5. Handle errors gracefully

---

## Additional Feature: Markdown Support

Added markdown editing support with split-pane preview:

### New Files
- `editor/syntax/markdown.py` - Markdown lexer with theming (~140 lines)
- `editor/markdown_preview.py` - HTML preview widget (~230 lines)
- `editor/markdown_editor.py` - Split-pane editor widget (~250 lines)

### Features
- **Syntax highlighting**: Headers, bold, italic, code, links, lists
- **Split-pane preview**: Toggle with Ctrl+Shift+M
- **Live updates**: Preview updates as you type (debounced)
- **Dark theme**: Preview styled to match editor theme
- **Markdown rendering**: Headers, emphasis, links, images, code blocks, lists, blockquotes, horizontal rules

### Usage
1. Open a `.md` or `.markdown` file
2. Press `Ctrl+Shift+M` to toggle preview
3. Edit on left, see rendered preview on right
4. Press `Ctrl+Shift+M` again to hide preview

---

**Last Updated**: 2025-12-04

