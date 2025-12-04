# Just Code - Plugin Guide

Just Code supports a hybrid plugin system: **declarative JSON** for simple use cases, with optional **Lua/Python scripting** for advanced logic.

## Table of Contents

- [Plugin Basics](#plugin-basics)
- [Creating a Plugin](#creating-a-plugin)
- [Triggers](#triggers)
- [Actions](#actions)
- [Scripted Plugins](#scripted-plugins)
- [Editor API](#editor-api)
- [Examples](#examples)

---

## Plugin Basics

### Plugin Location

Plugins are stored in `~/.config/justcode/plugins/`. Each plugin is a directory:

```
~/.config/justcode/plugins/
├── my-plugin/
│   ├── plugin.json        # Required: plugin definition
│   └── scripts/           # Optional: Lua/Python scripts
│       └── my_script.lua
├── another-plugin/
│   └── plugin.json
```

### Plugin Discovery

Plugins are automatically loaded when Just Code starts. They appear in the **Plugins** menu.

---

## Creating a Plugin

### Minimal plugin.json

```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": "Your Name",

  "triggers": [],
  "actions": {}
}
```

### Full Structure

```json
{
  "name": "Plugin Name",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Author Name",

  "triggers": [
    {
      "id": "my_trigger",
      "type": "command",
      "action_id": "my_action",
      "command_name": "Do Something",
      "shortcut": "Ctrl+Shift+D",
      "context": {
        "languages": ["python", "javascript"],
        "file_patterns": ["*.py", "*.js"]
      }
    }
  ],

  "actions": {
    "my_action": {
      "type": "transform",
      "operation": "uppercase"
    }
  }
}
```

---

## Triggers

Triggers define **when** an action runs.

### Trigger Types

| Type | Description |
|------|-------------|
| `command` | Appears in Plugins menu, can have shortcut |
| `shortcut` | Only keyboard shortcut, no menu entry |
| `on_save` | Runs automatically when file is saved |
| `on_open` | Runs automatically when file is opened |

### Trigger Properties

```json
{
  "id": "unique_id",           // Required: unique identifier
  "type": "command",           // Required: trigger type
  "action_id": "my_action",    // Required: which action to run
  "command_name": "Menu Name", // For command type: menu label
  "shortcut": "Ctrl+Shift+X",  // Optional: keyboard shortcut
  "context": {                 // Optional: when to enable
    "languages": ["python"],   // Limit to languages
    "file_patterns": ["*.py"]  // Limit to file patterns
  }
}
```

### Context Filtering

Triggers only activate when context matches:

```json
"context": {
  "languages": ["python", "javascript"],
  "file_patterns": ["test_*.py", "*.spec.js"]
}
```


### transform

Built-in text transformations:

```json
"uppercase_selection": {
  "type": "transform",
  "operation": "uppercase"
}
```

**Available operations:**
- `uppercase` - Convert to UPPERCASE
- `lowercase` - Convert to lowercase
- `title_case` - Convert To Title Case
- `reverse` - esreveR text
- `sort_lines` - Sort lines alphabetically
- `reverse_lines` - Reverse line order
- `unique_lines` - Remove duplicate lines
- `trim_lines` - Trim whitespace from lines

### snippet

Insert text at cursor position:

```json
"insert_header": {
  "type": "snippet",
  "text": "#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n"
}
```

**Template variables:**
- `${file_name}` - Current file name
- `${file_path}` - Full file path
- `${date}` - Current date
- `${time}` - Current time

### notify

Show a notification message:

```json
"show_message": {
  "type": "notify",
  "title": "Plugin Name",
  "message": "Operation completed!"
}
```

### chain

Execute multiple actions in sequence:

```json
"format_and_save": {
  "type": "chain",
  "actions": ["format_code", "save_file"]
}
```

---

## Scripted Plugins

For complex logic, use Lua or Python scripts.

### Lua Scripts

```json
"actions": {
  "my_lua_action": {
    "type": "script",
    "engine": "lua",
    "file": "scripts/my_script.lua",
    "entry_point": "main"
  }
}
```

**scripts/my_script.lua:**
```lua
function main()
    local text = editor.get_text()
    local upper = string.upper(text)
    editor.set_text(upper)
    editor.show_notification("Done!", "Converted to uppercase")
end
```

### Python Scripts

```json
"actions": {
  "my_python_action": {
    "type": "script",
    "engine": "python",
    "file": "scripts/my_script.py",
    "entry_point": "main"
  }
}
```

**scripts/my_script.py:**
```python
def main():
    text = editor.get_text()
    upper = text.upper()
    editor.set_text(upper)
    editor.show_notification("Done!", "Converted to uppercase")
```

### Inline Scripts

For simple scripts, use inline code:

```json
"uppercase_inline": {
  "type": "script",
  "engine": "lua",
  "code": "editor.set_text(string.upper(editor.get_text()))"
}
```

### Security (Sandboxing)

Scripts run in a **restricted environment**:
- ❌ No file system access
- ❌ No network access
- ❌ No system command execution
- ✅ Only editor API and safe builtins

---

## Editor API

Scripts have access to the `editor` object with these methods:

### Text Operations

| Method | Description |
|--------|-------------|
| `editor.get_text()` | Get entire file content |
| `editor.set_text(text)` | Replace entire file content |
| `editor.get_selection()` | Get selected text |
| `editor.replace_selection(text)` | Replace selection |
| `editor.insert_text(text)` | Insert at cursor |

### Cursor Operations

| Method | Description |
|--------|-------------|
| `editor.get_cursor_position()` | Returns `{line, column}` (1-based) |
| `editor.set_cursor_position(line, col)` | Move cursor |

### File Information

| Method | Description |
|--------|-------------|
| `editor.get_file_path()` | Get current file path |
| `editor.get_language()` | Get current language |

### Notifications

| Method | Description |
|--------|-------------|
| `editor.show_notification(msg, title)` | Show notification |

---

## Examples

### Example 1: Python Black Formatter

```json
{
  "name": "Python Black Formatter",
  "version": "1.0.0",
  "description": "Format Python files with Black",
  "author": "Just Code",

  "triggers": [
    {
      "id": "format_on_save",
      "type": "on_save",
      "action_id": "format",
      "context": {"languages": ["python"]}
    },
    {
      "id": "format_manual",
      "type": "command",
      "action_id": "format",
      "command_name": "Format with Black",
      "shortcut": "Ctrl+Shift+B",
      "context": {"languages": ["python"]}
    }
  ],

  "actions": {
    "format": {
      "type": "external_command",
      "command": "black --quiet -",
      "input": "file_contents",
      "output": "replace_file_contents"
    }
  }
}
```

### Example 2: Sort Lines Plugin

```json
{
  "name": "Sort Lines",
  "version": "1.0.0",
  "description": "Sort selected lines alphabetically",
  "author": "Just Code",

  "triggers": [
    {
      "id": "sort",
      "type": "command",
      "action_id": "sort_selection",
      "command_name": "Sort Lines",
      "shortcut": "Ctrl+Shift+L"
    }
  ],

  "actions": {
    "sort_selection": {
      "type": "transform",
      "operation": "sort_lines"
    }
  }
}
```

### Example 3: Lua Script Plugin

```json
{
  "name": "Word Counter",
  "version": "1.0.0",
  "description": "Count words in document",
  "author": "Just Code",

  "triggers": [
    {
      "id": "count",
      "type": "command",
      "action_id": "count_words",
      "command_name": "Count Words"
    }
  ],

  "actions": {
    "count_words": {
      "type": "script",
      "engine": "lua",
      "code": "local text = editor.get_text(); local _, count = string.gsub(text, '%S+', ''); editor.show_notification('Word count: ' .. count, 'Word Counter')"
    }
  }
}
```

---

## Troubleshooting

### Plugin not loading
- Check `plugin.json` syntax with a JSON validator
- Ensure plugin directory is in `~/.config/justcode/plugins/`
- Check console for error messages

### Script not running
- Verify `engine` is `"lua"` or `"python"`
- Check `file` path is relative to plugin directory
- Verify `entry_point` function exists in script

### Action not working
- Check `action_id` in trigger matches key in `actions`
- Verify `context` matches current file type
- Try removing `context` to test without filtering

