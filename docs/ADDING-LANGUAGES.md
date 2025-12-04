# Adding New Languages to Just Code Editor

This guide explains how to add syntax highlighting for new programming languages.

## How Syntax Highlighting Works

Just Code uses QScintilla's lexer system for syntax highlighting. The flow is:

1. **File opened** → `_setup_syntax_for_file()` in `tab_widget.py`
2. **Extension matched** → `_get_builtin_lexer()` returns appropriate lexer class
3. **Theme applied** → `_apply_lexer_style_colors()` maps theme colors to lexer styles
4. **Lexer attached** → Editor displays highlighted code

Theme colors come from `~/.config/justcode/syntax-themes.json`:
```json
{
  "keyword": "#569cd6",
  "string": "#ce9178",
  "number": "#b5cea8",
  "comment": "#6a9955",
  "function": "#dcdcaa",
  "class": "#4ec9b0",
  "operator": "#d4d4d4"
}
```

---

## Option 1: Add a QScintilla Built-in Lexer

QScintilla includes lexers for many languages. If one exists but isn't mapped, this is the easiest option.

### Available QScintilla Lexers

```
QsciLexerAVS        QsciLexerBash       QsciLexerBatch      QsciLexerCMake
QsciLexerCoffeeScript QsciLexerCPP      QsciLexerCSharp     QsciLexerCSS
QsciLexerD          QsciLexerDiff       QsciLexerFortran    QsciLexerFortran77
QsciLexerHTML       QsciLexerIDL        QsciLexerJava       QsciLexerJavaScript
QsciLexerJSON       QsciLexerLua        QsciLexerMakefile   QsciLexerMarkdown
QsciLexerMatlab     QsciLexerOctave     QsciLexerPascal     QsciLexerPerl
QsciLexerPO         QsciLexerPostScript QsciLexerPOV        QsciLexerProperties
QsciLexerPython     QsciLexerRuby       QsciLexerSpice      QsciLexerSQL
QsciLexerTCL        QsciLexerTeX        QsciLexerVerilog    QsciLexerVHDL
QsciLexerXML        QsciLexerYAML
```

### Step 1: Add to Extension Map

Edit `justcode/editor/tab_widget.py`, find `_get_builtin_lexer()`:

```python
def _get_builtin_lexer(self, ext: str, filename: str, editor):
    from PyQt6.Qsci import (
        # ... existing imports ...
        QsciLexerPascal,  # Add new import
    )

    lexer_map = {
        # ... existing mappings ...
        
        # Pascal (NEW)
        '.pas': QsciLexerPascal,
        '.pp': QsciLexerPascal,
        '.inc': QsciLexerPascal,
    }
```

### Step 2: Add Theme Color Mapping

In the same file, find `_apply_lexer_style_colors()` and add a block:

```python
def _apply_lexer_style_colors(self, lexer, colors: dict):
    from PyQt6.Qsci import (
        # ... existing imports ...
        QsciLexerPascal,
    )
    
    # ... existing code ...
    
    # Pascal (NEW)
    elif isinstance(lexer, QsciLexerPascal):
        set_color(QsciLexerPascal.Comment, 'comment')
        set_color(QsciLexerPascal.CommentLine, 'comment')
        set_color(QsciLexerPascal.Keyword, 'keyword')
        set_color(QsciLexerPascal.String, 'string')
        set_color(QsciLexerPascal.Number, 'number')
        set_color(QsciLexerPascal.Operator, 'operator')
```

### Finding Style Constants

To find available style constants for a lexer:

```python
from PyQt6.Qsci import QsciLexerPascal
# List all style constants
[attr for attr in dir(QsciLexerPascal) if not attr.startswith('_') and attr[0].isupper()]
```

---

## Option 2: Create a Custom Lexer

For languages QScintilla doesn't support, create a custom lexer.

### Step 1: Create Lexer File

Create `justcode/editor/syntax/mylang.py`:

```python
from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont

class MyLangLexer(QsciLexerCustom):
    """Custom lexer for MyLang."""
    
    # Define style numbers
    Default = 0
    Comment = 1
    Keyword = 2
    String = 3
    Number = 4
    Operator = 5
    
    # Keywords for this language
    KEYWORDS = {'if', 'else', 'while', 'for', 'return', 'func', 'var'}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_styles()
    
    def _init_styles(self):
        """Initialize default colors (will be overridden by theme)."""
        self.setDefaultColor(QColor("#d4d4d4"))
        self.setDefaultPaper(QColor("#1e1e1e"))
    
    def language(self):
        return "MyLang"
    
    def description(self, style):
        styles = {
            0: "Default",
            1: "Comment", 
            2: "Keyword",
            3: "String",
            4: "Number",
            5: "Operator",
        }
        return styles.get(style, "")
    
    def styleText(self, start, end):
        """Parse and style the text between start and end."""
        self.startStyling(start)
        
        text = self.parent().text()[start:end]
        
        # Simple tokenizer - customize for your language
        i = 0
        while i < len(text):
            ch = text[i]
            
            # Comments (# to end of line)
            if ch == '#':
                j = text.find('\n', i)
                if j == -1:
                    j = len(text)
                self.setStyling(j - i, self.Comment)
                i = j
                continue
            
            # Strings
            if ch in '"\'':
                quote = ch
                j = i + 1
                while j < len(text) and text[j] != quote:
                    if text[j] == '\\':
                        j += 1
                    j += 1
                j += 1  # Include closing quote
                self.setStyling(j - i, self.String)
                i = j
                continue
            
            # Numbers
            if ch.isdigit():
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == '.'):
                    j += 1
                self.setStyling(j - i, self.Number)
                i = j
                continue
            
            # Words (keywords/identifiers)
            if ch.isalpha() or ch == '_':
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                word = text[i:j]
                if word in self.KEYWORDS:
                    self.setStyling(j - i, self.Keyword)
                else:
                    self.setStyling(j - i, self.Default)
                i = j
                continue
            
            # Operators
            if ch in '+-*/=<>!&|':
                self.setStyling(1, self.Operator)
                i += 1
                continue
            
            # Default
            self.setStyling(1, self.Default)
            i += 1
```

### Step 2: Register the Lexer

In `_get_builtin_lexer()`:

```python
def _get_builtin_lexer(self, ext: str, filename: str, editor):
    # ... existing code ...
    
    # Check for custom lexers first
    if ext == '.mylang':
        from .syntax.mylang import MyLangLexer
        return MyLangLexer(editor)
    
    # ... rest of built-in lexer code ...
```

### Step 3: Add Theme Mapping

In `_apply_lexer_style_colors()`:

```python
from justcode.editor.syntax.mylang import MyLangLexer

# ... in the method ...

elif isinstance(lexer, MyLangLexer):
    set_color(MyLangLexer.Comment, 'comment')
    set_color(MyLangLexer.Keyword, 'keyword')
    set_color(MyLangLexer.String, 'string')
    set_color(MyLangLexer.Number, 'number')
    set_color(MyLangLexer.Operator, 'operator')
```

---

## Adding Language to Run System

To enable "Run File" (F5) for the new language, edit `main_window.py`:

```python
def _get_run_command(self, file_path: Path) -> str:
    run_commands = {
        # ... existing commands ...
        '.mylang': f'mylang-interpreter "{filename}"',
    }
```

---

## Adding to languages.json

For editor settings (tab width, etc.), add to `resources/default_configs/languages.json`:

```json
{
    "mylang": {
        "extensions": [".mylang"],
        "tab_width": 4,
        "use_spaces": true,
        "comment_string": "#",
        "syntax_theme": "default"
    }
}
```

---

## Summary

| Task | File(s) to Edit |
|------|-----------------|
| Map extension to built-in lexer | `tab_widget.py` → `_get_builtin_lexer()` |
| Map theme colors to lexer styles | `tab_widget.py` → `_apply_lexer_style_colors()` |
| Create custom lexer | New file in `editor/syntax/` |
| Add run command | `main_window.py` → `_get_run_command()` |
| Add editor settings | `resources/default_configs/languages.json` |

