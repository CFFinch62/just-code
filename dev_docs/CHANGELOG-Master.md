# Just Code Editor - Development Changelog

This changelog serves as the main index for all development activities, decisions, and progress for the Just Code Editor project. Detailed phase-specific logs are maintained in separate files.

---

## Project Overview

**Goal**: Build a minimalist, no-nonsense code editor for Linux using Python and PyQt6, with auto-hiding panels, JSON-based configuration, and a hybrid plugin system.

**Key Philosophy**: "Invisible until needed" - maximum focus on code with minimal visual noise.

**Full Specification**: See [just-code-project-prompt.md](just-code-project-prompt.md)

---

## Development Roadmap

### Phase 1: Core Editor ✅ COMPLETE
**Status**: Implementation complete (2025-12-02)

**Summary**: Basic editor with file operations, dark theme, Python syntax highlighting, JSON configuration system.

**Details**: See [CHANGELOG-Phase1.md](CHANGELOG-Phase1.md)

**Key Features**:
- QScintilla editor with dark theme
- File operations (New, Open, Save, Save As)
- Python syntax highlighting
- JSON configuration loading
- Font selection dialog
- Fixed cursor positioning bug
- Removed visual noise (line highlighting)

---

### Phase 2: Panel System ✅ COMPLETE
**Status**: Implementation complete (2025-12-03)

**Summary**: Auto-hiding panels with smooth animations, mouse hover detection, and terminal integration.

**Details**: See [CHANGELOG-Phase2.md](CHANGELOG-Phase2.md)

**Key Features**:
- File browser panel (project-focused view)
- Terminal panel (QProcess command execution)
- Smooth slide animations (250ms, InOutQuad easing)
- Mouse hover detection for file browser auto-show
- Three-state file browser (hidden/pinned/auto-shown)
- Keyboard shortcuts (Ctrl+B, Ctrl+`)
- Working directory sync
- Animation configuration settings

---

### Phase 3: Configuration System ✅ COMPLETE
**Status**: Implementation complete (2025-12-03)

**Summary**: Live config reload, settings menu, UI theme switching, and configuration as code.

**Details**: See [CHANGELOG-Phase3.md](CHANGELOG-Phase3.md)

**Key Features**:
- Settings menu (Ctrl+, opens settings.json)
- Live reload of settings on file save (QFileSystemWatcher)
- UI theme switching (dark/light themes)
- Syntax theme infrastructure (monokai, light themes defined)
- Instant config updates (no restart needed)
- "Configuration as code" philosophy

---

### Phase 4: Multi-file Editing ✅ COMPLETE
**Status**: Implementation complete (2025-12-03)

**Summary**: Tab-based multi-file editing with session persistence.

**Details**: See [CHANGELOG-Phase4.md](CHANGELOG-Phase4.md)

**Key Features**:
- Tab bar for open files (minimal styling, themed)
- Tab management (close, close others, close all)
- Modified file indicators (• suffix on tab title)
- Session persistence (remembers open files between sessions)
- Tab context menu (right-click)
- Files open in new tabs (or switch if already open)

---

### Phase 5: Plugin System (Declarative) ✅ COMPLETE
**Details**: [CHANGELOG-Phase5.md](CHANGELOG-Phase5.md)

**Deliverables**:
- Plugin discovery from `~/.config/justcode/plugins/`
- Trigger system (command, shortcut, on_save, on_open)
- Built-in actions: external_command, snippet, transform, notify, chain
- Plugins menu with Reload and Open Folder
- Error handling with user notifications
- Example plugins: Text Tools, Python Formatter

---

### Phase 6: Plugin System (Scripted) ✅ COMPLETE
**Goals**:
- Lua engine integration (using lupa library) ✅
- Editor API for scripts ✅
- Script sandboxing and security ✅
- Optional Python script support ✅

**Completed**: 2025-12-04

---

### Phase 7: Polish and Distribution 📅 PLANNED
**Goals**:
- Additional language support
- Additional themes
- Keyboard shortcut customization UI (optional)
- Cross-platform testing
- Packaging for distribution (PyInstaller or similar)

**Dependencies**: Phase 1-6 complete

---

## Quick Status Summary

| Phase | Status | Completion Date | Details |
|-------|--------|----------------|---------|
| Phase 1: Core Editor | ✅ COMPLETE | 2025-12-02 | [CHANGELOG-Phase1.md](CHANGELOG-Phase1.md) |
| Phase 2: Panel System | ✅ COMPLETE | 2025-12-03 | [CHANGELOG-Phase2.md](CHANGELOG-Phase2.md) |
| Phase 3: Configuration System | ✅ COMPLETE | 2025-12-03 | [CHANGELOG-Phase3.md](CHANGELOG-Phase3.md) |
| Phase 4: Multi-file Editing | ✅ COMPLETE | 2025-12-03 | [CHANGELOG-Phase4.md](CHANGELOG-Phase4.md) |
| Phase 5: Plugin System (Declarative) | ✅ COMPLETE | 2025-12-04 | [CHANGELOG-Phase5.md](CHANGELOG-Phase5.md) |
| Phase 6: Plugin System (Scripted) | ✅ COMPLETE | 2025-12-04 | [CHANGELOG-Phase6.md](CHANGELOG-Phase6.md) |
| Phase 7: Polish and Distribution | 📅 PLANNED | Not Started | TBD |

---

## Current Status (2025-12-04)

**Active Phase**: Phase 6 - Plugin System (Scripted) ✅ COMPLETE

**Last Completed Work**:
- Lua engine integration using lupa library
- Python script engine with restricted execution
- EditorAPI for scripts (get/set text, selection, cursor, notifications)
- Sandboxed execution (no file I/O, no imports in Python)
- Example plugins: Smart Comments (Lua), Line Tools (Python)
- **Markdown support**: Syntax highlighting and split-pane preview (Ctrl+Shift+M)

**Next Recommended Steps**:
1. Move to Phase 7 (Polish and Distribution)

---

## Key Files and Locations

### Documentation
- `CHANGELOG-Master.md` - This file (main index)
- `CHANGELOG-Phase1.md` - Phase 1 detailed log
- `CHANGELOG-Phase2.md` - Phase 2 detailed log
- `just-code-project-prompt.md` - Full project specification
- `QUICKREF.md` - Quick reference for current status
- `README.md` - Project overview

### Source Code
- `justcode/` - Main application directory
  - `main.py` - Entry point
  - `app/` - Application management
  - `editor/` - Editor components
  - `panels/` - Auto-hiding panels
  - `config/` - Configuration system
  - `resources/` - Default configs and resources

### Scripts
- `setup.sh` - Install dependencies (run once)
- `run.sh` - Run application

---

## Common Commands

```bash
# Navigate to project
cd /home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/JustCode

# Setup (first time)
./setup.sh

# Run application
./run.sh
```

---

## For Future Agents and Developers

### When Starting a New Session

1. **Read this file first** - Get high-level overview
2. **Check Quick Status Summary** - See what's complete and what's in progress
3. **Read relevant phase changelog** - Get detailed info about current phase
4. **Check QUICKREF.md** - Quick reference for current status and commands
5. **Review just-code-project-prompt.md** - Full project specification (if needed)

### When Completing Work

1. **Update the phase-specific changelog** - Add detailed entry to CHANGELOG-PhaseN.md
2. **Update this file** - Update Quick Status Summary and Current Status sections
3. **Update QUICKREF.md** - Update current features and status

### Development Principles (From Spec)

- Build incrementally - get each phase working before moving on
- Resist feature creep - when in doubt, leave it out
- Clean, readable Python with type hints and docstrings
- No premature optimization
- Test manually as you go
- "Invisible until needed" - minimal visual noise

---

## Phase Changelog Files

| File | Description | Status |
|------|-------------|--------|
| [CHANGELOG-Phase1.md](CHANGELOG-Phase1.md) | Core Editor development log | ✅ Complete |
| [CHANGELOG-Phase2.md](CHANGELOG-Phase2.md) | Panel System development log | ✅ Complete |
| [CHANGELOG-Phase3.md](CHANGELOG-Phase3.md) | Configuration System log | ✅ Complete |
| [CHANGELOG-Phase4.md](CHANGELOG-Phase4.md) | Multi-file Editing log | ✅ Complete |
| [CHANGELOG-Phase5.md](CHANGELOG-Phase5.md) | Plugin System (Declarative) log | ✅ Complete |
| [CHANGELOG-Phase6.md](CHANGELOG-Phase6.md) | Plugin System (Scripted) log | ✅ Complete |
| CHANGELOG-Phase7.md | Polish and Distribution log | Not yet created |

---

## Template for Phase Changelog Entries

When adding entries to phase-specific changelogs, use this format:

```markdown
## YYYY-MM-DD - Brief Description

**Agent**: [Agent name]
**Author**: [Developer name]

### Actions Completed
- [List of what was done]

### Code Changes
- [Modified/created files with brief description]

### Design Decisions
- [Any important choices made]

### Issues Encountered and Resolved
- [Problems and solutions]

### Testing Results
- [What was tested and results]

### Technical Notes
- [Any other relevant information]

### Success Metrics
- [How we know it works]
```

---

**Last Updated**: 2025-12-03
**Current Phase**: Phase 4 - Multi-file Editing ✅ COMPLETE
**Status**: Core editor, panels, animations, live config reload, and multi-file editing all working
