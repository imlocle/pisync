# 📖 PiSync Documentation

Welcome to the PiSync documentation directory. Here you'll find everything you need to understand, use, develop, and deploy PiSync.

---

## 🚀 Quick Navigation

**New to PiSync?**
→ Start with [../README.md](../README.md) for overview and features

**Want to use PiSync?**
→ Follow the [Quick Start](../README.md#-quick-start) section in the main README

**Want to develop PiSync?**
→ Read [DEVELOPMENT.md](DEVELOPMENT.md) to set up your environment

**Need to understand the architecture?**
→ Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design

**Encountering issues?**
→ See [BUGS.md](BUGS.md) for known problems and workarounds

**Curious about future features?**
→ Browse [ROADMAP.md](ROADMAP.md) for the development timeline

---

## 📚 All Documentation Files

| Document                                                                                | Purpose                                                      | Audience         |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------- |
| **[ARCHITECTURE.md](ARCHITECTURE.md)**                                                  | System design, layers, data flows, threading model           | Developers       |
| **[BUGS.md](BUGS.md)**                                                                  | Known issues, limitations, workarounds, performance baseline | Everyone         |
| **[DEVELOPMENT.md](DEVELOPMENT.md)**                                                    | Setup, workflows, debugging, code standards                  | Developers       |
| **[INDEX.md](INDEX.md)**                                                                | Comprehensive navigation hub with learning paths             | Everyone         |
| **[ROADMAP.md](ROADMAP.md)**                                                            | Planned features, version timeline, community requests       | Everyone         |
| **[docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md)**   | Production-grade practices, checklist _(Internal)_           | Developers       |
| **[docs-internal/QUICKSTART_PRODUCTION.md](../docs-internal/QUICKSTART_PRODUCTION.md)** | Copy-paste templates _(Internal)_                            | Developers       |
| **[docs-internal/DISTRIBUTION.md](../docs-internal/DISTRIBUTION.md)**                   | Building and packaging _(Internal)_                          | Release managers |
| **[docs-internal/DEPENDENCY_MANAGEMENT.md](../docs-internal/DEPENDENCY_MANAGEMENT.md)** | Managing dependencies _(Internal)_                           | Developers       |

---

## 🎯 By Role

### 👤 End Users

1. Read [../README.md](../README.md) - What is PiSync?
2. Follow "Quick Start" section to install
3. Check [BUGS.md](BUGS.md) if you encounter issues

### 👨‍💻 Developers

1. Read [DEVELOPMENT.md](DEVELOPMENT.md) - Set up your environment
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the design
3. Pick a task from [BUGS.md](BUGS.md) or [ROADMAP.md](ROADMAP.md)

### 🔧 DevOps / Release Managers

1. Read [docs-internal/DISTRIBUTION.md](../docs-internal/DISTRIBUTION.md) - How to build and release
2. Read [docs-internal/DEPENDENCY_MANAGEMENT.md](../docs-internal/DEPENDENCY_MANAGEMENT.md) - Manage dependencies
3. Follow [docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md) - Production checklist

---

## 📖 Learning Paths

### Path 1: User (20 minutes)

```
Main README (What & Why)
  ↓
Main README (Quick Start)
  ↓
Done! You're ready to use PiSync
```

### Path 2: Developer (1 hour)

```
Main README (Overview)
  ↓
DEVELOPMENT.md (Getting Started)
  ↓
ARCHITECTURE.md (System Design)
  ↓
DEVELOPMENT.md (Common Tasks)
  ↓
Ready to code!
```

### Path 3: Bug Fixing (30 minutes)

```
BUGS.md (Find your issue)
  ↓
DEVELOPMENT.md (Debugging)
  ↓
ARCHITECTURE.md (Understand architecture layer)
  ↓
DEVELOPMENT.md (Code standards)
  ↓
Fix, test, commit!
```

---

## ❓ Common Questions

**Q: Where do I report bugs?**
→ See [BUGS.md](BUGS.md) first. If it's new, open a [GitHub issue](https://github.com/imlocle/pisync/issues)

**Q: What's the development workflow?**
→ Read [DEVELOPMENT.md](DEVELOPMENT.md#development-workflow)

**Q: What features are planned?**
→ Check [ROADMAP.md](ROADMAP.md) for v1.1-v2.0 features

**Q: How do I make my code production-ready?**
→ See [docs-internal/PRODUCTION_STANDARDS.md](../docs-internal/PRODUCTION_STANDARDS.md) for the complete checklist

**Q: Can I contribute?**
→ Yes! See [DEVELOPMENT.md](DEVELOPMENT.md) for setup and workflow

**Q: Why isn't PiSync available on Windows/Linux?**
→ Check [ROADMAP.md](ROADMAP.md#roadmap--ideas) - multi-platform support planned for v2.0+

**Q: What PiSync version do I have?**
→ Run `python main.py --version` or check `src/__version__.py`

---

## 🔗 Quick Links

- **GitHub Repository:** https://github.com/imlocle/pisync
- **Main README:** [../README.md](../README.md)
- **Issue Tracker:** https://github.com/imlocle/pisync/issues
- **Discussions:** https://github.com/imlocle/pisync/discussions

---

## 📝 Documentation Structure

```
docs/
├── README.md                        ← You are here (Public)
├── ARCHITECTURE.md                  (System design & layers - Public)
├── BUGS.md                          (Known issues & workarounds - Public)
├── DEVELOPMENT.md                   (Developer setup & workflow - Public)
├── INDEX.md                         (Comprehensive navigation hub - Public)
├── ROADMAP.md                       (Future features & timeline - Public)
│
└── ../docs-internal/                ← Internal documentation
    ├── PRODUCTION_STANDARDS.md      (Production checklist)
    ├── QUICKSTART_PRODUCTION.md     (Implementation templates)
    ├── DISTRIBUTION.md              (Build & packaging)
    └── DEPENDENCY_MANAGEMENT.md     (Dependency workflow)
```

---

## 🎉 Ready to Get Started?

- **Users:** Head to [../README.md](../README.md#-quick-start)
- **Developers:** Jump to [DEVELOPMENT.md](DEVELOPMENT.md#getting-started)
- **Lost?** Check [INDEX.md](INDEX.md) for a comprehensive navigation hub

---

**Last Updated:** March 12, 2026  
**Status:** Production v1.0.0  
**Maintained by:** PiSync Contributors
