# 📚 Documentation Index

Welcome to PiSync Documentation! Here's how to navigate all available docs.

---

## 🎯 Quick Start by Task

| **I want to...**                  | **Read this**                                                                       | **Time**  |
| --------------------------------- | ----------------------------------------------------------------------------------- | --------- |
| Just install and use PiSync       | [README.md](../README.md) → Quick Start                                             | 5 min     |
| Understand how PiSync works       | [ARCHITECTURE.md](ARCHITECTURE.md)                                                  | 10 min    |
| Set up my development environment | [DEVELOPMENT.md](DEVELOPMENT.md) → Getting Started                                  | 15 min    |
| Understand the code structure     | [DEVELOPMENT.md](DEVELOPMENT.md) → Project Structure                                | 10 min    |
| Learn common development tasks    | [DEVELOPMENT.md](DEVELOPMENT.md) → Common Tasks                                     | 15 min    |
| See known bugs and limitations    | [BUGS.md](BUGS.md)                                                                  | 10 min    |
| Check future feature ideas        | [ROADMAP.md](ROADMAP.md)                                                            | 15 min    |
| Troubleshoot an issue             | [BUGS.md](BUGS.md) then [DEVELOPMENT.md](DEVELOPMENT.md)                            | varies    |
| Build and distribute the app      | [docs-internal/DISTRIBUTION.md](../docs-internal/DISTRIBUTION.md)                   | 30 min    |
| Manage and update dependencies    | [docs-internal/DEPENDENCY_MANAGEMENT.md](../docs-internal/DEPENDENCY_MANAGEMENT.md) | 15 min    |
| Make my code production-ready     | [docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md)   | 30 min    |
| Get production setup templates    | [docs-internal/QUICKSTART_PRODUCTION.md](../docs-internal/QUICKSTART_PRODUCTION.md) | 2-4 hours |

---

## 📖 All Documentation Files

### For Users

- **[../README.md](../README.md)** - What is PiSync? Features, installation, usage
- **[ROADMAP.md](ROADMAP.md)** - Future features, improvements, planned releases

### For Developers

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, layers, data flow, threading model
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Setup, workflows, debugging, code standards
- **[BUGS.md](BUGS.md)** - Known issues, limitations, workarounds, ranked by severity

### For Developers

- **[INDEX.md](INDEX.md)** - This file

### For Packaging & Distribution (Internal)

- **[docs-internal/DISTRIBUTION.md](../docs-internal/DISTRIBUTION.md)** - Building wheels, source distributions, standalone executables, publishing to PyPI
- **[docs-internal/DEPENDENCY_MANAGEMENT.md](../docs-internal/DEPENDENCY_MANAGEMENT.md)** - Managing dependencies with pip-tools, updating packages, lock file workflow
- **[docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md)** - Complete guide to production-grade practices (Packaging, Testing, Code Quality, CI/CD, etc.)
- **[docs-internal/QUICKSTART_PRODUCTION.md](../docs-internal/QUICKSTART_PRODUCTION.md)** - Copy-paste templates to get started on each production phase

---

## 🚀 Getting Started by Role

### End Users

**Just want to use PiSync?**

1. Read [README.md](../README.md) - What PiSync does
2. Follow Quick Start section to install
3. Check [BUGS.md](BUGS.md) if issues arise

### First-Time Contributors

**Want to contribute to development?**

1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Setup and structure
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the design
3. Pick a task from [BUGS.md](BUGS.md) or [ROADMAP.md](ROADMAP.md)
4. Follow development workflow in DEVELOPMENT.md

### Experienced Developers

**Want to modernize the codebase?**

1. Read [docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md) - See what's needed
2. Follow [docs-internal/QUICKSTART_PRODUCTION.md](../docs-internal/QUICKSTART_PRODUCTION.md) - Implement in phases
3. Reference [docs-internal/DISTRIBUTION.md](../docs-internal/DISTRIBUTION.md) for publishing

---

## 📊 Documentation Overview

```
ARCHITECTURE.md ─────────────────────────────────┐
(System design, layers, patterns)                │
                                                  ├─→ DEVELOPMENT.md
                                                  │   (How to work with code)
README.md ────────────────────────────────────────┘
(Overview, features, usage)

BUGS.md ──────────────────────────┐
(Known issues, workarounds)       │
                                  ├─→ PRODUCTION_STANDARDS.md
ROADMAP.md ───────────────────────┤   (Production checklist)
(Future features & improvements)  │
                                  └─→ QUICKSTART_PRODUCTION.md
                                      (Implementation templates)
```

---

## 🎓 Learning Paths

### Path 1: User Learning (20 minutes)

```
README.md (What is PiSync?)
  ↓
README.md (Quick Start)
  ↓
README.md (SSH Setup)
  ↓
Done! Use PiSync
```

### Path 2: Developer Onboarding (1 hour)

```
README.md (Overview)
  ↓
DEVELOPMENT.md (Getting Started)
  ↓
ARCHITECTURE.md (Design Overview)
  ↓
DEVELOPMENT.md (Project Structure)
  ↓
DEVELOPMENT.md (Common Tasks)
  ↓
Ready to code!
```

### Path 3: Bug Fixing (30 minutes)

```
BUGS.md (Find your bug)
  ↓
DEVELOPMENT.md (Debugging tips)
  ↓
ARCHITECTURE.md (Understand relevant layer)
  ↓
DEVELOPMENT.md (Code standards)
  ↓
Fix and test!
```

---

## 📋 Key Features by Document

| Document                     | Key Sections                                      | Best For                        |
| ---------------------------- | ------------------------------------------------- | ------------------------------- |
| **README.md**                | Features, Quick Start, SSH Setup, Troubleshooting | Users & quick reference         |
| **ARCHITECTURE.md**          | Layers, Components, Data Flow, Diagrams, Patterns | Understanding design            |
| **DEVELOPMENT.md**           | Setup, Structure, Workflows, Debugging, Standards | Daily development               |
| **DISTRIBUTION.md**          | Wheel builds, PyPI publishing, CI/CD automation   | Package distribution            |
| **DEPENDENCY_MANAGEMENT.md** | pip-tools workflow, updates, security patches     | Managing dependencies           |
| **PRODUCTION_STANDARDS.md**  | 8 major categories, checklist, roadmap            | Production planning             |
| **QUICKSTART_PRODUCTION.md** | 5 phases, copy-paste templates, Makefile          | Implementation                  |
| **BUGS.md**                  | 14+ issues, workarounds, severity ranking         | Issue tracking, troubleshooting |
| **ROADMAP.md**               | v1.1-v2.0 features, priorities, timelines         | Planning & feature requests     |

---

## 🔍 Common Questions

### Q: Where's the API documentation?

**A:** Check [ARCHITECTURE.md](ARCHITECTURE.md) for protocol/interface docs. Source code has docstrings.

### Q: How do I report a bug?

**A:** Check [BUGS.md](BUGS.md) first. If you found a new issue, open a GitHub issue with reproduction steps.

### Q: Where's the contribution guide?

**A:** Coming soon! For now, see [DEVELOPMENT.md](DEVELOPMENT.md) for code standards and workflow.

### Q: What's the roadmap?

**A:** See [ROADMAP.md](ROADMAP.md) for planned features, versions, and priorities.

### Q: How do I run tests?

**A:** See [DEVELOPMENT.md](DEVELOPMENT.md) → Testing section. After implementing [docs-internal/QUICKSTART_PRODUCTION.md](../docs-internal/QUICKSTART_PRODUCTION.md), use `make test`.

### Q: Can I use on Windows/Linux?

**A:** Currently macOS only. See [ROADMAP.md](ROADMAP.md) for cross-platform support roadmap.

---

## 📞 Document Map by Layer

### Presentation Layer (UI)

- Components overview in [ARCHITECTURE.md](ARCHITECTURE.md)
- File structure in [DEVELOPMENT.md](DEVELOPMENT.md)
- Updating UI in [DEVELOPMENT.md](DEVELOPMENT.md#Common-Tasks)

### Application Layer (Controllers)

- Architecture details in [ARCHITECTURE.md](ARCHITECTURE.md)
- Adding controllers in [DEVELOPMENT.md](DEVELOPMENT.md)
- Threading model in [ARCHITECTURE.md](ARCHITECTURE.md)

### Domain Layer (Models)

- Model definitions in [ARCHITECTURE.md](ARCHITECTURE.md)
- Error hierarchy in [ARCHITECTURE.md](ARCHITECTURE.md)
- Custom errors in codebase docstrings

### Infrastructure Layer (Services)

- Service layer overview in [ARCHITECTURE.md](ARCHITECTURE.md)
- SFTP operations in [ARCHITECTURE.md](ARCHITECTURE.md)
- Connection management in [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 🔄 Documentation Status

| Document                                             | Last Updated | Status          | Priority |
| ---------------------------------------------------- | ------------ | --------------- | -------- |
| [README.md](README.md)                               | Mar 11, 2026 | ✅ Complete     | Core     |
| [ARCHITECTURE.md](ARCHITECTURE.md)                   | Mar 11, 2026 | ✅ Complete     | Core     |
| [DEVELOPMENT.md](DEVELOPMENT.md)                     | Mar 11, 2026 | ✅ Complete     | Core     |
| [BUGS.md](BUGS.md)                                   | Mar 12, 2026 | ✅ Complete     | Core     |
| [ideas.md](ideas.md)                                 | Original     | ⚠️ Needs Review | Medium   |
| [PRODUCTION_STANDARDS.md](PRODUCTION_STANDARDS.md)   | Mar 12, 2026 | ✅ Complete     | High     |
| [QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md) | Mar 12, 2026 | ✅ Complete     | High     |

---

## 💡 Pro Tips

1. **Use search** - Most browsers support Ctrl+F. Search for keywords across docs.
2. **Open in VS Code** - VS Code has better markdown preview and outline navigation.
3. **Use TOC viewer** - Browser extensions can generate table of contents for easy jumping.
4. **Cross-reference links** - Docs link to each other for context.
5. **Bookmark these** - Save [QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md) and [DEVELOPMENT.md](DEVELOPMENT.md) for regular reference.

---

## 📚 External Resources

### Official Documentation

- [PySide6 Docs](https://doc.qt.io/qtforpython/) - Qt framework documentation
- [Paramiko Docs](https://www.paramiko.org/) - SSH library documentation
- [Python Docs](https://docs.python.org/3/) - Python standard library

### Learning Resources

- [Python Desktop Applications](https://realpython.com/python-gui-tkinter/)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)
- [Clean Code Principles](https://clean-code-python.readthedocs.io/)

### Community

- [Python Discord](https://discord.com/invite/python)
- [Reddit r/learnprogramming](https://reddit.com/r/learnprogramming)
- [Stack Overflow Python Tag](https://stackoverflow.com/questions/tagged/python)

---

## ✨ What's New (March 2026)

- ⭐ **Added:** [PRODUCTION_STANDARDS.md](PRODUCTION_STANDARDS.md) - Complete production readiness guide
- ⭐ **Added:** [QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md) - Copy-paste implementation templates
- 🔄 **Updated:** [bugs.md](bugs.md) - Now with 14 ranked potential issues
- 📋 **Created:** This index for easier navigation

---

**Last Updated:** March 12, 2026

**Need help?** Check the appropriate document above or open an issue on GitHub.

Happy exploring! 🚀
