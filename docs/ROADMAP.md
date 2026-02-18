# PiSync MVP Roadmap

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.0  
> **Status:** ✅ Active roadmap

> **Version**: 1.0  
> **Target MVP Release**: March 2026  
> **Current Status**: 80% Complete  
> **Last Updated**: February 11, 2026

---

## 🎯 MVP Vision

**Goal**: Release a stable, polished macOS application that automatically transfers media files from Mac to Raspberry Pi with a modern, professional user experience.

**Target Users**: Mac users with Raspberry Pi media servers who want automated, reliable file transfers.

**Core Value Proposition**: "Set it and forget it" - automatic monitoring and transfer with beautiful UI and clear feedback.

---

## 📊 Current Status (80% Complete)

### ✅ Completed (80%)

**Core Functionality** (100%)

- ✅ Automatic file monitoring with watchdog
- ✅ File stability tracking (prevents partial transfers)
- ✅ SFTP-based encrypted transfers
- ✅ Path mapping (mirrors local structure)
- ✅ Drag & drop support
- ✅ Manual and automatic transfer modes
- ✅ Optional auto-delete after transfer

**User Interface** (100%)

- ✅ Modern dark theme (500+ line stylesheet)
- ✅ Dual-pane file explorers
- ✅ Real-time activity log with timestamps
- ✅ Progress indicators
- ✅ Tabbed settings window
- ✅ Status bar with indicators
- ✅ Splash screen

**Architecture** (100%)

- ✅ Clean layered design
- ✅ Protocol-based abstractions
- ✅ Thread-safe operations
- ✅ Error handling with custom exceptions
- ✅ Settings management with Pydantic

**Bug Fixes** (100%)

- ✅ Drag & drop moves (not copies)
- ✅ Upload All shows real-time progress
- ✅ File stability shows progress bar
- ✅ SFTP thread safety resolved

### 🚧 In Progress (20%)

**Documentation** (60%)

- ✅ Architecture documentation
- ✅ Implementation details
- ✅ Bug fix summaries
- ⚠️ Needs cleanup (remove legacy docs)
- ❌ User guide not written
- ❌ VPN setup guide not written

**Testing** (0%)

- ❌ No test suite
- ❌ No automated tests
- ❌ No CI/CD pipeline

**Packaging** (0%)

- ❌ Not packaged as .app
- ❌ No installer
- ❌ No code signing
- ❌ No auto-updater

---

## 🗓️ MVP Roadmap

### Phase 1: Documentation Cleanup (1 week)

**Target**: February 18, 2026  
**Priority**: HIGH

**Tasks**:

1. ✅ Create CURRENT-STATE.md (comprehensive status)
2. ✅ Create ROADMAP.md (this document)
3. ✅ Update ideas.md with remote access section
4. ⏳ Remove legacy documentation files
5. ⏳ Update README.md files
6. ⏳ Create USER-GUIDE.md
7. ⏳ Create VPN-SETUP-GUIDE.md

**Deliverables**:

- Clean, current documentation (< 15 files)
- User-friendly setup guide
- VPN configuration guide
- Updated README with quick start

**Success Criteria**:

- All docs reviewed and current
- No contradictory information
- Clear path from install to first transfer
- VPN setup takes < 15 minutes

---

### Phase 2: Testing Foundation (2 weeks)

**Target**: March 4, 2026  
**Priority**: HIGH

**Tasks**:

1. Set up pytest infrastructure
2. Write unit tests for domain layer
3. Write integration tests for services
4. Mock FileSystem for testing
5. Add test fixtures
6. Set up CI with GitHub Actions
7. Achieve 60%+ code coverage

**Deliverables**:

- `tests/` directory with organized tests
- pytest configuration
- CI pipeline running tests
- Coverage report

**Success Criteria**:

- 60%+ code coverage
- All critical paths tested
- Tests run in < 2 minutes
- CI passes on every commit

**Test Structure**:

```
tests/
├── unit/
│   ├── test_domain_models.py
│   ├── test_path_mapper.py
│   ├── test_settings.py
│   └── test_transfer_engine.py
├── integration/
│   ├── test_file_monitor.py
│   ├── test_sftp_operations.py
│   └── test_transfer_flow.py
├── fixtures/
│   ├── sample_files.py
│   └── mock_sftp.py
└── conftest.py
```

---

### Phase 3: Packaging & Distribution (1 week)

**Target**: March 11, 2026  
**Priority**: HIGH

**Tasks**:

1. Create PyInstaller spec file
2. Bundle assets (icons, stylesheets)
3. Create macOS .app bundle
4. Test on clean macOS system
5. Create DMG installer
6. Add code signing (optional for MVP)
7. Write installation instructions

**Deliverables**:

- `PiSync.app` bundle
- `PiSync.dmg` installer
- Installation guide
- Uninstallation guide

**Success Criteria**:

- App launches on clean system
- All features work in bundled app
- DMG installs cleanly
- < 100 MB app size

**Build Script**:

```bash
# build.sh
pyinstaller --name PiSync \
    --windowed \
    --icon assets/icons/pisync_logo.icns \
    --add-data "assets:assets" \
    --osx-bundle-identifier com.pisync.app \
    main.py

# Create DMG
create-dmg \
    --volname "PiSync Installer" \
    --window-size 600 400 \
    --icon-size 100 \
    --app-drop-link 400 200 \
    PiSync.dmg \
    dist/PiSync.app
```

---

### Phase 4: Beta Testing (2 weeks)

**Target**: March 25, 2026  
**Priority**: MEDIUM

**Tasks**:

1. Recruit 5-10 beta testers
2. Create beta testing guide
3. Set up feedback collection
4. Monitor for crashes/bugs
5. Fix critical issues
6. Gather UX feedback
7. Iterate on pain points

**Deliverables**:

- Beta testing guide
- Feedback form
- Bug tracking system
- Updated app with fixes

**Success Criteria**:

- No critical bugs
- 80%+ positive feedback
- < 5% crash rate
- Clear path to v1.0

**Beta Testing Checklist**:

- [ ] Fresh install on clean system
- [ ] SSH key setup
- [ ] First transfer
- [ ] Automatic monitoring
- [ ] Upload All feature
- [ ] Settings changes
- [ ] Error handling
- [ ] Performance with large files
- [ ] Network interruption recovery

---

### Phase 5: MVP Release (1 week)

**Target**: April 1, 2026  
**Priority**: HIGH

**Tasks**:

1. Final bug fixes from beta
2. Polish documentation
3. Create release notes
4. Prepare marketing materials
5. Set up website/landing page
6. Create demo video
7. Publish v1.0.0

**Deliverables**:

- PiSync v1.0.0
- Release notes
- User guide
- Demo video
- Landing page

**Success Criteria**:

- Stable, polished release
- Complete documentation
- Clear value proposition
- Ready for public use

---

## 🎯 MVP Feature Set

### Must Have (MVP Blockers)

**Core Functionality**:

- ✅ Automatic file monitoring
- ✅ SFTP transfers
- ✅ File stability checking
- ✅ Path mapping
- ✅ Error handling

**User Interface**:

- ✅ Modern, professional UI
- ✅ Activity log
- ✅ Progress indicators
- ✅ Settings management

**Quality**:

- ⏳ Test suite (60%+ coverage)
- ⏳ Documentation (user guide)
- ⏳ Packaging (.app bundle)
- ⏳ Beta testing

### Nice to Have (Post-MVP)

**Features**:

- ❌ Parallel transfers
- ❌ Transfer resume
- ❌ Compression
- ❌ Remote access (VPN guide only)
- ❌ Multi-Pi support

**Quality**:

- ❌ 90%+ test coverage
- ❌ Performance benchmarks
- ❌ Automated UI tests
- ❌ Code signing

### Won't Have (Future Versions)

**Features**:

- ❌ Mobile app
- ❌ Web interface
- ❌ Cloud integration
- ❌ Plugin system
- ❌ TMDB integration

---

## 📋 Detailed Task Breakdown

### Documentation Cleanup (Week 1)

**Day 1-2: Remove Legacy Docs**

- [ ] Review all 21 doc files
- [ ] Identify legacy/outdated content
- [ ] Delete or archive old docs
- [ ] Update cross-references
- [ ] Target: < 15 doc files

**Day 3-4: Create User Guide**

- [ ] Write USER-GUIDE.md
  - [ ] Installation
  - [ ] First-time setup
  - [ ] SSH key configuration
  - [ ] First transfer
  - [ ] Automatic monitoring
  - [ ] Settings reference
  - [ ] Troubleshooting
  - [ ] FAQ

**Day 5: Create VPN Guide**

- [ ] Write VPN-SETUP-GUIDE.md
  - [ ] Why VPN for remote access
  - [ ] Tailscale setup (recommended)
  - [ ] WireGuard setup
  - [ ] OpenVPN setup
  - [ ] Testing connection
  - [ ] Troubleshooting

**Day 6-7: Update Core Docs**

- [ ] Update README.md (root)
- [ ] Update docs/README.md
- [ ] Update docs/START-HERE.md
- [ ] Update architecture-overview.md
- [ ] Review all cross-references

### Testing Foundation (Weeks 2-3)

**Week 2: Unit Tests**

- [ ] Day 1: Setup pytest, fixtures
- [ ] Day 2: Test domain models
- [ ] Day 3: Test path mapper
- [ ] Day 4: Test settings
- [ ] Day 5: Test transfer engine

**Week 3: Integration Tests**

- [ ] Day 1: Mock SFTP client
- [ ] Day 2: Test file monitor
- [ ] Day 3: Test transfer flow
- [ ] Day 4: Test error handling
- [ ] Day 5: CI setup, coverage report

### Packaging (Week 4)

**Day 1-2: PyInstaller Setup**

- [ ] Create spec file
- [ ] Bundle assets
- [ ] Test on dev machine
- [ ] Fix import issues

**Day 3-4: macOS Bundle**

- [ ] Create .app bundle
- [ ] Test on clean VM
- [ ] Fix path issues
- [ ] Optimize size

**Day 5: DMG Creation**

- [ ] Create DMG installer
- [ ] Add background image
- [ ] Test installation
- [ ] Write install guide

### Beta Testing (Weeks 5-6)

**Week 5: Preparation**

- [ ] Recruit testers
- [ ] Create testing guide
- [ ] Set up feedback form
- [ ] Distribute beta builds

**Week 6: Iteration**

- [ ] Collect feedback
- [ ] Fix critical bugs
- [ ] Improve UX pain points
- [ ] Prepare for release

### Release (Week 7)

**Day 1-2: Final Polish**

- [ ] Fix remaining bugs
- [ ] Update documentation
- [ ] Create release notes

**Day 3-4: Marketing**

- [ ] Create demo video
- [ ] Set up landing page
- [ ] Prepare social media posts

**Day 5: Launch**

- [ ] Publish v1.0.0
- [ ] Announce release
- [ ] Monitor feedback

---

## 🚀 Post-MVP Roadmap (v1.1 - v2.0)

### v1.1 (April 2026) - Performance & Reliability

**Focus**: Make it faster and more reliable

**Features**:

- Parallel transfers (3-5 concurrent)
- Transfer resume capability
- Better error recovery
- Performance optimizations
- Improved logging

**Effort**: 2-3 weeks

### v1.2 (May 2026) - Remote Access

**Focus**: Work from anywhere

**Features**:

- VPN integration (Tailscale)
- Connection method detection
- Dynamic DNS support
- Connection troubleshooting
- Security improvements

**Effort**: 2-3 weeks

### v1.3 (June 2026) - Advanced Features

**Focus**: Power user features

**Features**:

- Compression during transfer
- Bandwidth throttling
- Transfer scheduling
- File deduplication
- Advanced filtering

**Effort**: 3-4 weeks

### v2.0 (Q3 2026) - Major Update

**Focus**: Ecosystem expansion

**Features**:

- Multi-Pi support
- Mobile companion app (iOS/Android)
- Web interface
- TMDB integration
- Plugin system
- Cloud backup integration

**Effort**: 8-12 weeks

---

## 📊 Success Metrics

### MVP Success Criteria

**Technical**:

- ✅ 0 critical bugs
- ⏳ 60%+ test coverage
- ⏳ < 100 MB app size
- ✅ < 2.5s startup time
- ✅ < 100 MB memory usage

**User Experience**:

- ⏳ < 15 min setup time
- ✅ < 5 clicks to first transfer
- ✅ Clear error messages
- ✅ Responsive UI (no freezing)

**Quality**:

- ⏳ Complete documentation
- ⏳ Beta tested by 5+ users
- ⏳ 80%+ positive feedback
- ⏳ < 5% crash rate

### Post-MVP Metrics

**Adoption**:

- 100+ downloads in first month
- 50+ active users
- 10+ GitHub stars

**Engagement**:

- 70%+ retention after 1 week
- 50%+ retention after 1 month
- 5+ feature requests
- 10+ bug reports

**Quality**:

- < 1% crash rate
- 90%+ positive reviews
- < 24h response time for critical bugs

---

## 🎯 MVP Definition of Done

### Code

- [x] All features implemented
- [x] No critical bugs
- [ ] 60%+ test coverage
- [x] Code reviewed
- [x] Documentation complete

### Documentation

- [x] Architecture documented
- [ ] User guide written
- [ ] VPN setup guide written
- [ ] API documented (if applicable)
- [ ] Troubleshooting guide complete

### Quality

- [ ] Beta tested
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Accessibility considered
- [ ] Error handling comprehensive

### Distribution

- [ ] Packaged as .app
- [ ] DMG installer created
- [ ] Installation tested
- [ ] Uninstallation tested
- [ ] Works on clean system

### Marketing

- [ ] Landing page created
- [ ] Demo video recorded
- [ ] Screenshots taken
- [ ] Release notes written
- [ ] Social media prepared

---

## 🚧 Risks & Mitigation

### Technical Risks

**Risk**: SFTP performance issues with large files  
**Mitigation**: Implement chunked transfers, add compression option  
**Likelihood**: Medium | **Impact**: Medium

**Risk**: Network interruptions cause failed transfers  
**Mitigation**: Add resume capability, better error handling  
**Likelihood**: High | **Impact**: Medium

**Risk**: macOS security restrictions (Gatekeeper, notarization)  
**Mitigation**: Code signing, notarization process  
**Likelihood**: High | **Impact**: High

**Risk**: SSH key setup too complex for users  
**Mitigation**: Detailed guide, video tutorial, troubleshooting  
**Likelihood**: Medium | **Impact**: High

### Schedule Risks

**Risk**: Testing takes longer than expected  
**Mitigation**: Start testing early, recruit testers in advance  
**Likelihood**: Medium | **Impact**: Medium

**Risk**: Packaging issues delay release  
**Mitigation**: Test packaging early, have backup plan  
**Likelihood**: Medium | **Impact**: High

**Risk**: Critical bugs found in beta  
**Mitigation**: Buffer time in schedule, prioritize fixes  
**Likelihood**: High | **Impact**: Medium

### User Adoption Risks

**Risk**: Setup too complex, users give up  
**Mitigation**: Excellent documentation, video guides, support  
**Likelihood**: Medium | **Impact**: High

**Risk**: VPN requirement too technical  
**Mitigation**: Clear guide, recommend Tailscale (easiest)  
**Likelihood**: Medium | **Impact**: Medium

**Risk**: Limited to macOS reduces audience  
**Mitigation**: Plan Windows/Linux support for v2.0  
**Likelihood**: Low | **Impact**: Medium

---

## 📞 Support & Resources

### Development Resources

- **Repository**: (GitHub URL)
- **Documentation**: `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

### User Resources

- **User Guide**: `docs/USER-GUIDE.md` (to be created)
- **VPN Setup**: `docs/VPN-SETUP-GUIDE.md` (to be created)
- **FAQ**: In user guide
- **Support**: GitHub Issues

### Team

- **Developer**: (Your name)
- **Beta Testers**: TBD
- **Contributors**: Open to community

---

## 🎉 Conclusion

PiSync is 80% complete and on track for MVP release in April 2026. The core functionality is solid, the UI is polished, and recent bug fixes have improved reliability.

**Next Steps**:

1. Clean up documentation (1 week)
2. Build test suite (2 weeks)
3. Package for distribution (1 week)
4. Beta test (2 weeks)
5. Release v1.0.0 (April 1, 2026)

**Key Focus Areas**:

- Documentation quality
- Test coverage
- User experience
- Reliable packaging

With focused effort on these areas, PiSync will be ready for a successful MVP release.

---

**Document Version**: 1.0  
**Last Updated**: February 11, 2026  
**Next Review**: Weekly during MVP development  
**Status**: ✅ Active roadmap
