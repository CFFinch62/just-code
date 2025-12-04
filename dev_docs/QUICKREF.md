# Just Code - Quick Reference

## Project Status
- **Phase**: 6 (Plugin System - Scripted) - ✅ COMPLETE
- **Next Task**: Phase 7 (Polish and Distribution)

## Key Files
- `CHANGELOG-Master.md` - **READ THIS FIRST** - Main index and roadmap
- `CHANGELOG-Phase1.md` - Phase 1 detailed development log
- `CHANGELOG-Phase2.md` - Phase 2 detailed development log
- `CHANGELOG-Phase3.md` - Phase 3 detailed development log
- `CHANGELOG-Phase4.md` - Phase 4 detailed development log
- `CHANGELOG-Phase5.md` - Phase 5 detailed development log
- `just-code-project-prompt.md` - Full project specification
- `README.md` - Project overview
- `justcode/main.py` - Application entry point

## Directory Structure
```
JustCode/
├── justcode/              # Main application
│   ├── main.py           # Entry point ✅
│   ├── app/              # Application management ✅
│   ├── editor/           # Editor & syntax highlighting ✅
│   ├── panels/           # File browser & terminal ✅
│   ├── config/           # Configuration system ✅
│   ├── plugins/          # Plugin system ✅
│   └── resources/        # Default configs & icons ✅
├── CHANGELOG.md          # Development log
├── README.md             # Project info
├── requirements.txt      # Dependencies
├── setup.sh              # Automated setup script
└── run.sh                # Run application
```

## Development Phases
1. ✅ **Core Editor** - COMPLETE
2. ✅ **Panel System** - COMPLETE
3. ✅ **Configuration System** - COMPLETE
4. ✅ **Multi-file Editing** - COMPLETE
5. ✅ **Plugin System (Declarative)** - COMPLETE
6. ✅ **Plugin System (Scripted)** - COMPLETE
7. 📅 **Polish and Distribution** - Planned

## Phase 1 Checklist
- [x] Project structure
- [x] Default configs
- [x] Basic PyQt6 app
- [x] Main window + QScintilla
- [x] File operations (New, Open, Save, Save As)
- [x] Menu bar
- [x] Config loading
- [x] Dark theme
- [x] Python syntax highlighting
- [x] Fixed cursor positioning bug
- [x] Font selection dialog

## Phase 2 Checklist
- [x] File browser panel
- [x] Project-focused view (only selected folder)
- [x] Navigate folders (double-click)
- [x] Navigate up (↑ button)
- [x] Toggle with Ctrl+B
- [x] Open Folder (Ctrl+Shift+O)
- [x] Terminal panel with command execution
- [x] Panel slide animations (250ms, InOutQuad easing)
- [x] Simple toggle behavior (keyboard shortcuts and menu only)

## Phase 3 Checklist
- [x] Settings menu
- [x] Open Settings command (Ctrl+,)
- [x] Live reload with QFileSystemWatcher
- [x] UI theme switching (15 themes, dynamic menu from ui-themes.json)
- [x] Syntax theme system (connected to lexers, 11 themes)
- [x] Extended language support (20 languages defined)
- [x] Instant config updates (no restart)
- [x] File browser font size adjustment
- [x] File browser bookmark system with default directory
- [x] Real bash terminal with command history
- [x] Terminal auto-syncs working directory with file browser/editor
- [x] File close command (Ctrl+W)

## Phase 4 Checklist
- [x] Tab bar for open files (minimal styling)
- [x] Multiple editor instances (one per tab)
- [x] Tab management (close, close others, close all)
- [x] Modified file indicators (• suffix)
- [x] Session persistence (remember open files)
- [x] Tab context menu
- [x] UI theme applied to tabs

## Quick Commands
```bash
# Navigate to project
cd /home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/JustCode

# Setup (first time)
./setup.sh

# Run application
./run.sh
```

## Keyboard Shortcuts
- **Ctrl+N** - New file
- **Ctrl+O** - Open file
- **Ctrl+Shift+O** - Open folder
- **Ctrl+S** - Save
- **Ctrl+Shift+S** - Save As
- **Ctrl+W** - Close file
- **Ctrl+,** - Open Settings
- **Ctrl+B** - Toggle file browser
- **Ctrl+`** - Toggle terminal
- **Ctrl+Shift+M** - Toggle markdown preview (for .md files)
- **Ctrl+Z** - Undo
- **Ctrl+Shift+Z** - Redo
- **Ctrl+X/C/V** - Cut/Copy/Paste
- **Ctrl++/-** - Zoom in/out
- **Ctrl+Q** - Exit

### Terminal Shortcuts
- **Up/Down** - Command history
- **Ctrl+L** - Clear screen (shows working directory)
- **Ctrl+C** - Send interrupt

## Current Features
✅ Dark themed editor
✅ Python syntax highlighting
✅ File operations (New, Open, Save, Save As, Close)
✅ **Multi-file editing with tabs**
✅ **Tab management (close, close others, close all)**
✅ **Modified file indicators on tabs**
✅ **Session persistence (remembers open files)**
✅ Project-focused file browser with bookmarks
✅ File browser font size adjustment
✅ Default start directory for file browser
✅ Real bash terminal with command history
✅ Terminal auto-syncs working directory with file browser/editor
✅ Smooth panel animations (slide in/out)
✅ Simple panel toggles (keyboard shortcuts and menu)
✅ Font selection
✅ Live config reload (no restart needed)
✅ UI theme switching (15 themes)
✅ Syntax theme system (11 themes)
✅ 20 language definitions
✅ Settings menu (Ctrl+, opens settings.json)
✅ Configuration as code (edit JSON directly)
✅ Clean minimal UI
✅ No visual noise
✅ Minimal CPU overhead
✅ **Plugin system (declarative)**
✅ **Text transformation plugins (uppercase, lowercase, sort, etc.)**
✅ **External command plugins (Black formatter, etc.)**
✅ **On-save triggers for automatic actions**
✅ **Lua scripting for plugins**
✅ **Python scripting for plugins**
✅ **Sandboxed script execution**
✅ **Markdown syntax highlighting**
✅ **Markdown split-pane preview (Ctrl+Shift+M)**

## Known Issues
- None currently

## Philosophy Reminders
- Invisible until needed
- No visual noise
- Configuration as code (JSON in editor)
- Build incrementally
- When in doubt, leave it out

## For Future Agents
1. Read `CHANGELOG-Master.md` first
2. Check current phase status
3. Follow phases in order
4. Update CHANGELOG after work
5. Keep it minimal!

## Recent Changes

### 2025-12-04 - Markdown Support
- Markdown syntax highlighting (MarkdownLexer)
- Split-pane markdown preview (MarkdownEditorWidget)
- Toggle preview with Ctrl+Shift+M
- Live preview updates while typing (debounced)
- Preview renders: headers, bold, italic, links, images, code blocks, lists, blockquotes
- Dark theme styling for preview pane

### 2025-12-03 - Phase 4 Complete
- Multi-file editing with tabs (TabEditorWidget)
- Tab management: close, close others, close all
- Modified file indicators (• suffix on tab title)
- Session persistence (saves/restores open files)
- Tab context menu (right-click)
- UI theme applied to tab bar
- Session file: `~/.config/justcode/session.json`

### 2025-12-03 - Phase 3 Extended
- Dynamic UI theme menu (populates from ui-themes.json)
- Added 12 new UI themes (15 total)
- Syntax theme system connected to lexers (11 themes)
- Extended language support (20 languages)
- File browser font size adjustment
- File browser bookmark system
- Default start directory for file browser
- Real bash terminal with persistent shell
- Command history (Up/Down arrows)
- Terminal auto-syncs working directory with file browser/editor
- Clear button shows current working directory
- File close command (Ctrl+W)

### 2025-12-03 - Phase 3 Initial
- Settings menu with Ctrl+, shortcut
- Live config reload with QFileSystemWatcher
- UI theme switching (dark/light themes)
- Syntax theme infrastructure
- Configuration as code - edit JSON directly in editor
- Instant config updates without restart

### 2025-12-03 - Phase 2 Complete
- Implemented terminal panel with QProcess command execution
- Added smooth panel slide animations (QPropertyAnimation, 250ms, InOutQuad)
- Simple toggle behavior for both panels (keyboard shortcuts and menu only)
- Removed auto-hide/mouse hover detection for simplicity and performance
- Animation configuration settings

### 2025-12-02 - Phase 1 & Phase 2 Start
- Fixed cursor positioning bug (setFixedPitch)
- Removed visual noise (line highlighting)
- Implemented project-focused file browser
- Added font selection dialog
- Added Open Folder functionality
