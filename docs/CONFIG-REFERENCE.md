# Just Code - Configuration Reference

All configuration files are stored in `~/.config/justcode/` and use JSON format.

## Table of Contents

- [settings.json](#settingsjson)
- [ui-themes.json](#ui-themesjson)
- [syntax-themes.json](#syntax-themesjson)
- [languages.json](#languagesjson)
- [keybindings.json](#keybindingsjson)

---

## settings.json

Main application settings. Access via **Ctrl+,** or Settings → Open Settings.

### Full Schema

```json
{
  "editor": {
    "font_family": "Monospace",
    "font_size": 12,
    "tab_width": 4,
    "use_spaces": true,
    "word_wrap": false,
    "line_numbers": true,
    "highlight_current_line": false,
    "auto_indent": true
  },
  "ui": {
    "theme": "tokyo-night",
    "show_status_bar": true,
    "panel_animation_duration_ms": 250,
    "enable_panel_animations": true,
    "hover_edge_threshold_px": 5
  },
  "behavior": {
    "remember_open_files": true
  },
  "file_browser": {
    "font_size": 11,
    "default_directory": "/path/to/projects",
    "bookmarks": ["/path/one", "/path/two"]
  }
}
```

### editor Section

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `font_family` | string | "Monospace" | Editor font family |
| `font_size` | integer | 12 | Font size in points |
| `tab_width` | integer | 4 | Number of spaces per tab |
| `use_spaces` | boolean | true | Use spaces instead of tabs |
| `word_wrap` | boolean | false | Wrap long lines |
| `line_numbers` | boolean | true | Show line numbers |
| `highlight_current_line` | boolean | false | Highlight current line |
| `auto_indent` | boolean | true | Auto-indent new lines |

### ui Section

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `theme` | string | "tokyo-night" | UI theme name |
| `show_status_bar` | boolean | true | Show status bar |
| `panel_animation_duration_ms` | integer | 250 | Panel slide animation duration |
| `enable_panel_animations` | boolean | true | Enable panel animations |
| `hover_edge_threshold_px` | integer | 5 | Edge hover detection threshold |

### behavior Section

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `remember_open_files` | boolean | true | Restore open files on startup |

### file_browser Section

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `font_size` | integer | 11 | File browser font size |
| `default_directory` | string | "" | Directory to open on startup |
| `bookmarks` | array | [] | List of bookmarked directories |

---

## ui-themes.json

Defines color themes for the UI. Access via Settings → Open UI Themes.

### Theme Structure

```json
{
  "themes": {
    "my-theme": {
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


### Built-in Themes

**Dark Themes:**
- `default-dark` - VS Code-inspired dark theme
- `monokai` - Classic Monokai colors
- `dracula` - Popular Dracula theme
- `nord` - Arctic, bluish colors
- `solarized-dark` - Solarized dark variant
- `gruvbox-dark` - Retro groove colors
- `one-dark` - Atom One Dark
- `github-dark` - GitHub's dark mode
- `tokyo-night` - Tokyo Night (default)
- `catppuccin-mocha` - Catppuccin Mocha
- `ayu-dark` - Ayu dark theme
- `palenight` - Material Palenight

**Light Themes:**
- `default-light` - Clean light theme
- `solarized-light` - Solarized light variant
- `gruvbox-light` - Gruvbox light variant

---

## syntax-themes.json

Defines syntax highlighting colors. Access via Settings → Open Syntax Themes.

### Theme Structure

```json
{
  "themes": {
    "my-syntax-theme": {
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

### Color Properties

| Property | Description | Example |
|----------|-------------|---------|
| `keyword` | Language keywords | `if`, `for`, `class`, `def` |
| `string` | String literals | `"hello"`, `'world'` |
| `number` | Numeric literals | `42`, `3.14` |
| `comment` | Comments | `# comment`, `// comment` |
| `function` | Function names | `print`, `len` |
| `class` | Class names | `MyClass` |
| `operator` | Operators | `+`, `-`, `=`, `==` |

### Built-in Syntax Themes

`default`, `monokai`, `dracula`, `nord`, `solarized-dark`, `solarized-light`, `gruvbox-dark`, `gruvbox-light`, `one-dark`, `github-dark`, `light`

---

## languages.json

Defines language-specific settings. Access via Settings → Open Languages.

### Language Structure

```json
{
  "python": {
    "extensions": [".py", ".pyw"],
    "tab_width": 4,
    "use_spaces": true,
    "comment_string": "#",
    "syntax_theme": "default"
  }
}
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `extensions` | array | File extensions for this language |
| `tab_width` | integer | Tab width (overrides editor setting) |
| `use_spaces` | boolean | Use spaces (overrides editor setting) |
| `comment_string` | string | Comment prefix for the language |
| `syntax_theme` | string | Syntax theme name to use |

### Supported Languages

| Language | Extensions |
|----------|------------|
| Python | .py, .pyw |
| JavaScript | .js, .mjs, .cjs |
| TypeScript | .ts, .tsx |
| JSON | .json, .jsonc |
| HTML | .html, .htm, .xhtml |
| CSS | .css, .scss, .sass, .less |
| Java | .java |
| C | .c, .h |
| C++ | .cpp, .cc, .cxx, .hpp, .hh, .hxx |
| C# | .cs |
| Go | .go |
| Rust | .rs |
| Ruby | .rb, .rake, .gemspec |
| PHP | .php, .phtml |
| Shell | .sh, .bash, .zsh |
| SQL | .sql |
| YAML | .yml, .yaml |
| Markdown | .md, .markdown |
| XML | .xml, .xsl, .xslt, .svg |
| Lua | .lua |
| Perl | .pl, .pm |
| Makefile | Makefile, .mk |

---

## keybindings.json

Defines keyboard shortcuts. Access via Settings → Open Keybindings.

### Structure

```json
{
  "_comment": "Keyboard shortcuts - changes apply on save",

  "file.new": "Ctrl+N",
  "file.open": "Ctrl+O",
  "file.save": "Ctrl+S",
  "view.toggle_terminal": "Ctrl+`"
}
```

### Available Commands

| Command ID | Default | Description |
|------------|---------|-------------|
| `file.new` | Ctrl+N | Create new file |
| `file.open` | Ctrl+O | Open file |
| `file.open_folder` | Ctrl+Shift+O | Open folder |
| `file.save` | Ctrl+S | Save file |
| `file.save_as` | Ctrl+Shift+S | Save As |
| `file.close` | Ctrl+W | Close tab |
| `file.exit` | Ctrl+Q | Exit application |
| `edit.undo` | Ctrl+Z | Undo |
| `edit.redo` | Ctrl+Shift+Z | Redo |
| `edit.cut` | Ctrl+X | Cut |
| `edit.copy` | Ctrl+C | Copy |
| `edit.paste` | Ctrl+V | Paste |
| `view.toggle_file_browser` | Ctrl+B | Toggle file browser |
| `view.toggle_terminal` | Ctrl+\` | Toggle terminal |
| `view.toggle_markdown_preview` | Ctrl+Shift+M | Toggle markdown preview |
| `view.zoom_in` | Ctrl++ | Zoom in |
| `view.zoom_out` | Ctrl+- | Zoom out |
| `settings.open` | Ctrl+, | Open settings |

### Shortcut Format

Use Qt shortcut format:
- Modifiers: `Ctrl`, `Shift`, `Alt`, `Meta`
- Combine with `+`: `Ctrl+Shift+S`
- Special keys: `F1`-`F12`, `Tab`, `Return`, `Escape`, `Delete`, `Home`, `End`, `PageUp`, `PageDown`

### Disabling a Shortcut

Set to empty string to disable:
```json
"file.new": ""
```

---

## Configuration Tips

### Creating Custom Themes

1. Open `ui-themes.json` (Settings → Open UI Themes)
2. Copy an existing theme block
3. Rename it and modify colors
4. Save - new theme appears in Settings → UI Theme menu

### Per-Language Settings

Override editor settings for specific languages:
```json
"javascript": {
  "extensions": [".js"],
  "tab_width": 2,
  "use_spaces": true
}
```

### Backup Configuration

All configs are in `~/.config/justcode/`. Back up this directory to preserve settings.

### Reset to Defaults

Delete the config directory to reset:
```bash
rm -rf ~/.config/justcode
```
Default configs will be recreated on next launch.
