# Phase 5: Plugin System (Declarative) - Development Log

**Back to**: [CHANGELOG-Master.md](CHANGELOG-Master.md)

**Phase Status**: ✅ COMPLETE (2025-12-04)

**Goals**:
- [x] Plugin discovery and loading
- [x] Trigger system (commands, shortcuts, on_save, on_open)
- [x] Built-in action types implementation
- [x] Plugin error handling and reporting

**Module Status**:
- `plugins/models.py` - ✅ Complete (Plugin, Trigger, Action dataclasses)
- `plugins/loader.py` - ✅ Complete (PluginManager class)
- `plugins/actions.py` - ✅ Complete (ActionExecutor class)
- `plugins/__init__.py` - ✅ Complete (exports)

---

## Phase 5 Implementation Plan

### Plugin Structure
Each plugin is a directory containing a `plugin.json` file:
```
~/.config/justcode/plugins/
  my-plugin/
    plugin.json      # Required: metadata and declarative actions
    scripts/         # Optional: for Phase 6 (Lua/Python scripts)
```

### Built-in Action Types
1. **external_command** - Run shell command, pipe content in/out
2. **snippet** - Insert templated text with variables
3. **transform** - Built-in text transformations (uppercase, lowercase, sort lines)
4. **notify** - Show notification message
5. **chain** - Execute multiple actions in sequence

### Trigger Types
1. **command** - Manual command (appears in Plugins menu)
2. **shortcut** - Keyboard shortcut binding
3. **on_save** - Triggered when file is saved
4. **on_open** - Triggered when file is opened

### Plugin JSON Schema
```json
{
  "name": "Plugin Name",
  "version": "1.0.0",
  "description": "What it does",
  "author": "Author Name",
  
  "triggers": [
    {
      "id": "action_id",
      "type": "command|shortcut|on_save|on_open",
      "command_name": "Menu Name",
      "shortcut": "Ctrl+Shift+X",
      "context": {"languages": ["python", "javascript"]}
    }
  ],
  
  "actions": {
    "action_id": {
      "type": "external_command|snippet|transform|notify|chain",
      ...action-specific properties...
    }
  }
}
```

---

## 2025-12-04 - Phase 5 Started

**Agent**: Claude (Opus 4.5)
**Author**: Chuck (via agent)

### Planning

Phase 5 implements the declarative plugin system. Key components:

1. **Plugin data structures** - Dataclasses for Plugin, Trigger, Action
2. **Plugin loader** - Discovery and loading from plugins directory
3. **Trigger system** - Event handling for commands, shortcuts, on_save, on_open
4. **Action executors** - Implementation of built-in action types
5. **Menu integration** - Plugins menu with discovered commands
6. **Error handling** - Graceful error reporting

### Architecture

```
PluginManager
├── load_plugins()
│   └── scan ~/.config/justcode/plugins/
├── get_commands() → list of plugin commands for menu
├── execute_action(action_id, context)
├── on_file_save(file_path) → trigger on_save actions
└── on_file_open(file_path) → trigger on_open actions

ActionExecutor
├── execute_external_command(action, context)
├── execute_snippet(action, context)
├── execute_transform(action, context)
├── execute_notify(action, context)
└── execute_chain(action, context)
```

### Files Created/Modified

**New Files**:
- `justcode/plugins/models.py` - Plugin, Trigger, Action dataclasses
- `justcode/plugins/loader.py` - PluginManager class (~190 lines)
- `justcode/plugins/actions.py` - ActionExecutor class (~320 lines)
- `justcode/plugins/__init__.py` - Module exports

**Modified Files**:
- `justcode/app/main_window.py` - Added Plugins menu, plugin system integration
- `justcode/editor/tab_widget.py` - Added file_saved signal for on_save triggers

---

## Implementation Complete

### What Was Built

1. **Plugin Data Model** (`plugins/models.py`)
   - `TriggerType` enum: COMMAND, SHORTCUT, ON_SAVE, ON_OPEN
   - `ActionType` enum: EXTERNAL_COMMAND, SNIPPET, TRANSFORM, NOTIFY, CHAIN, SCRIPT
   - `TriggerContext` dataclass: language/file pattern matching
   - `Trigger` dataclass: defines when actions run
   - `Action` dataclass: defines what to execute
   - `Plugin` dataclass: complete plugin definition

2. **Plugin Manager** (`plugins/loader.py`)
   - Discovers plugins in `~/.config/justcode/plugins/`
   - Loads and validates `plugin.json` files
   - Manages trigger execution
   - Handles on_save and on_open events

3. **Action Executor** (`plugins/actions.py`)
   - `external_command`: Run shell commands with input/output piping
   - `snippet`: Insert templated text with variables ($selection, $file_name, $date, etc.)
   - `transform`: uppercase, lowercase, titlecase, sort_lines, reverse_lines, unique_lines, trim_whitespace, remove_blank_lines
   - `notify`: Show message dialog
   - `chain`: Execute multiple actions in sequence

4. **Menu Integration** (`app/main_window.py`)
   - Plugins menu with Reload and Open Folder
   - Dynamic menu population from discovered plugins
   - Shortcut support from plugin definitions
   - Editor callbacks for text manipulation

5. **Example Plugins** (installed to `~/.config/justcode/plugins/`)
   - **Text Tools**: Uppercase, lowercase, titlecase, sort lines, reverse lines, unique lines, trim whitespace
   - **Python Formatter**: Format with Black (requires black installed), check syntax

---

**Last Updated**: 2025-12-04

