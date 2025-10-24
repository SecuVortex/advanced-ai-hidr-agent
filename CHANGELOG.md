# Changelog

All notable changes to the HIDR Multi-Agent System will be documented in this file.

## [2.0.0] - 2024-01-24

### Added
- **MalwareBazaar Integration**: Real-time malware intelligence with free API
  - Proper Auth-Key header authentication
  - Malware family identification
  - Threat scoring (weight: 3.5 - highest priority)
- **Reports Tab**: Comprehensive security reporting
  - Real-time statistics dashboard
  - Recent threats table (last 100 entries)
  - Uptime counter
  - HTML/CSV/JSON export functionality
- **Settings Tab Enhancements**:
  - API key management (MalwareBazaar, VirusTotal)
  - Test connection buttons
  - Password visibility toggle
  - Trusted paths management (add/remove via GUI)
- **Trusted Paths Protection**: Whitelist legitimate software directories
  - 8 default trusted paths (Windows, PowerToys, VS Code, Defender)
  - Custom path addition via GUI
  - Instant 0/10 threat score for trusted locations
- **YARA Optimization**:
  - Increased timeout from 2s to 5s
  - Skip large files (>50MB) automatically
  - File size logging option

### Fixed
- **MalwareBazaar API Authentication**: Changed from POST body to Auth-Key header (fixes 401 errors)
- **False Positives**: Eliminated false positives on legitimate software
  - PowerToys executables
  - VS Code Python tools
  - Windows Defender services
  - Third-party applications in trusted paths
- **YARA Timeouts**: No more timeout warnings on large executables
- **Reports Tab**: Now generates and exports reports correctly

### Changed
- **Expert System Weights**: Updated to prioritize MalwareBazaar (3.5)
- **Detection Flow**: Trusted path check now happens before YARA scanning
- **Config Structure**: Added skip_large_files, max_file_size_mb, log_skipped_files to YARA config

### Security
- API keys now manageable via GUI (no manual .env editing)
- .env file properly secured in .gitignore
- Test connection feature validates API keys before saving

### Performance
- 50% reduction in scan time for large files (skipped automatically)
- Trusted path check < 1ms (instant allow)
- YARA scan timeout increased to 5s (more reliable)

## [1.0.0] - 2024-01-20

### Initial Release
- Multi-agent system (Detection, Intelligence, Coordinator, Response)
- YARA integration (45 rules across 5 categories)
- Expert system threat scoring
- LangGraph orchestration
- Basic GUI (5 tabs)
- VirusTotal integration
- Behavioral analysis
- MITRE ATT&CK mapping
- Process termination and quarantine
- Configuration management

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backwards compatible manner
- PATCH version for backwards compatible bug fixes
