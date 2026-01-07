# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- E2E testing framework (Sprint 5)
- 7-day validation period (Sprint 6)
- Mainnet deployment preparation
- Auto-generated API documentation (MkDocs)

### Added
- Centralized logging configuration with file rotation
- Logging support in strategies modules for better observability
- Pytest logging configuration (suppressed during normal runs)

### Changed
- Unified logging setup across all modules (removed duplicate basicConfig calls)

## [0.4.0] - 2026-01-06

### Added
- Position synchronization on bot startup (prevents state drift)
- Duplicate position prevention (same symbol check)
- Circuit breaker fix (only count successful orders, not duplicate signals)
- State persistence improvements (JSON serialization fix)
- BTC tick size rounding fix for Hyperliquid testnet
- Public web dashboard for monitoring (Flask on port 8080)
- Bot auto-start script for Docker (`bot-autostart.sh`)
- Comprehensive documentation updates (CURRENTRUN.md, ISSUES.md, decision logs)

### Fixed
- NameError in duplicate position check (#37)
- Circuit breaker false triggers from duplicate signals
- State file corruption on recursive serialization
- Price rounding errors causing order rejections on Hyperliquid testnet
- Log file creation issue (logs now written to /tmp/bot_v2.log with rotation)

### Changed
- Standardized python3 usage across all scripts and deployment files
- Updated Docker health checks for better reliability
- Improved error handling in state manager

### Security
- Dashboard XSS vulnerability fixed (HTML escaping in log rendering)

## [0.3.0] - 2026-01-02

### Added
- Live testnet trading integration with Hyperliquid exchange
- Simulation mode for unfunded testnet wallets (zero-balance support)
- Real-time monitoring guide (CURRENTRUN.md)
- Decision log documentation (ADR-style technical decisions)
- State persistence with filelock for concurrent access safety
- Circuit breaker safeguards (max drawdown, max trades limits)

### Changed
- Reorganized documentation structure (docs/, archive separation)
- Sprint-based development workflow formalized

## [0.2.0] - 2025-12-28

### Added
- Live Market Dashboard (Jupyter-based real-time monitoring)
- Interactive fractal visualizations with plotly
- Real-time data streaming from Hyperliquid exchange
- Dashboard performance optimizations (debouncing, incremental updates)

### Fixed
- Notebook synchronization issues with plotly graphs
- Memory leaks in dashboard refresh logic

## [0.1.0] - 2025-12-15

### Added
- Initial release with core Smart Money Concepts (SMC) implementation
- Three trading strategies:
  - Liquidity Sweep Strategy
  - Fair Value Gap (FVG) Fill Strategy
  - Break of Structure (BOS) + Order Block Strategy
- Core modules:
  - Market Structure (BOS, CHoCH detection)
  - Liquidity Zones
  - Order Blocks
  - Fair Value Gaps
  - Imbalances
- Risk management:
  - Position sizing calculator
  - Confidence factors system
- Backtesting framework (vectorbt integration)
- Comprehensive test suite (350+ tests, 94% coverage)
- Data fetching:
  - Hyperliquid integration
  - CCXT multi-exchange support
  - Rate limiting and retry logic
- Development tools:
  - Pre-commit hooks (Black, Ruff, mypy)
  - GitHub Actions CI/CD
  - Docker development environment

---

## Version History

| Version | Date | Status | Highlights |
|---------|------|--------|------------|
| 0.4.0 | 2026-01-06 | Current | Testnet validation, critical bug fixes |
| 0.3.0 | 2026-01-02 | Stable | Live trading integration |
| 0.2.0 | 2025-12-28 | Stable | Live dashboard |
| 0.1.0 | 2025-12-15 | Stable | Initial release |

---

## Migration Guides

### Upgrading to 0.4.0

**Breaking Changes:**
- None

**New Features:**
- Bot now creates log files at `/tmp/bot_v2.log` with automatic rotation (10MB, 5 backups)
- Position synchronization runs automatically on startup
- Duplicate positions are prevented (only one position per symbol)

**Action Required:**
- No manual migration needed
- Old log files can be safely removed
- State files are backward compatible

### Upgrading to 0.3.0

**Breaking Changes:**
- State file format changed (added position tracking)

**Action Required:**
- Delete old `.trading_state.json` files to use new format
- Update `.env` with Hyperliquid testnet credentials

---

## Deprecation Notices

None at this time.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and how to propose changes.

For release management and versioning strategy, see [SPRINT_FRAMEWORK.md](docs/SPRINT_FRAMEWORK.md).
