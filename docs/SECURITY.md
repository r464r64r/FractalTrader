# Security Policy

## ⚠️ Important Notice

**FractalTrader is currently in TESTNET ONLY operation.**

**DO NOT** use this software with real funds until Sprint 6 validation is complete and mainnet deployment is officially announced in the releases section.

---

## Reporting Vulnerabilities

**DO NOT** open public GitHub issues for security vulnerabilities.

Security vulnerabilities should be reported privately to maintain the safety of all users.

### How to Report

1. **Email**: Send details to the project maintainers (contact information will be added when public)
2. **GitHub Security Advisories**: Use the "Report a vulnerability" button in the Security tab (preferred)
3. **Expected Response**: You should receive an acknowledgment within 48 hours

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if available)
- Your contact information for follow-up

### Our Commitment

If your report is confirmed as a vulnerability, we will:
1. Acknowledge the vulnerability within 48 hours
2. Provide an estimated timeline for a fix
3. Develop and test a patch
4. Release the fix as a security update
5. Publicly disclose the vulnerability after the fix is deployed (with credit to you, if desired)

---

## Supported Versions

| Version | Status | Support |
|---------|--------|---------|
| 0.4.x   | Testnet | ✅ Full support |
| 0.3.x   | Testnet | ⚠️ Security fixes only |
| < 0.3   | Deprecated | ❌ No support |

**Note**: Mainnet versions are not yet available. Do not use any version with real funds.

---

## Security Considerations

### API Keys and Private Keys

**CRITICAL - Never Expose Credentials:**
- ❌ **NEVER** commit private keys, API secrets, or wallet mnemonics to version control
- ❌ **NEVER** share your `.env` file or credentials
- ❌ **NEVER** post logs containing private keys or API secrets in public issues

**Best Practices:**
- ✅ Use environment variables or `.env` files (automatically gitignored)
- ✅ Rotate API keys regularly (monthly recommended)
- ✅ Use API keys with minimum required permissions
- ✅ Store private keys in secure vaults (e.g., hardware wallets for mainnet)
- ✅ Use separate wallets for testnet and mainnet

### Testnet vs Mainnet

**Testnet (Current):**
- ✅ Safe for testing and development
- ✅ No real funds at risk
- ✅ Can be reset without financial loss
- ⚠️ Testnet keys have no value but should still be kept private

**Mainnet (Future):**
- ⚠️ NOT YET SUPPORTED - Do not attempt to use with mainnet
- ⚠️ Requires additional validation (Sprint 6: 7-day continuous operation)
- ⚠️ Use separate wallets from testnet
- ⚠️ Never reuse testnet private keys on mainnet
- ⚠️ Start with small position sizes
- ⚠️ Monitor continuously for the first week

### Trading Security

**Built-in Safeguards:**
- ✅ Circuit breakers enabled by default:
  - Maximum drawdown: 20% (bot stops trading)
  - Maximum trades: 50 per session (prevents runaway loops)
- ✅ State persistence prevents unintended position accumulation
- ✅ Position synchronization on startup (checks exchange vs local state)
- ✅ Duplicate position prevention (one position per symbol max)
- ✅ Order size validation prevents fat-finger errors
- ✅ Price tick size rounding prevents order rejections

**Risks to Be Aware Of:**
- ⚠️ Market conditions can change rapidly (gaps, flash crashes)
- ⚠️ Exchange outages can prevent closing positions
- ⚠️ Slippage on large orders or low liquidity pairs
- ⚠️ Funding rates on perpetual contracts (positive or negative)
- ⚠️ Smart contract risks (Hyperliquid is a smart contract DEX)

### Container Security

**Docker Security:**
- ✅ Containers run as non-root user
- ✅ No privileged mode required
- ✅ Minimal attack surface (only necessary ports exposed)
- ⚠️ Port 8080 (dashboard) should be firewalled in production
- ⚠️ Dashboard has no authentication (local use only)

**Network Security:**
- ✅ Use firewalls to restrict access to dashboard port
- ✅ Use VPN or SSH tunneling for remote access
- ❌ Do not expose dashboard to public internet

### Dependency Security

**Automated Scanning:**
- ✅ Dependabot enabled (GitHub automatic security updates)
- ✅ CodeQL analysis in CI/CD pipeline
- ✅ Bandit static analysis for security issues
- ✅ Safety checks for known vulnerabilities

**Manual Review:**
- ✅ All dependencies pinned in `requirements.txt`
- ✅ Regular security audits (monthly)
- ✅ Minimal dependency footprint (only necessary packages)

### Data Security

**State Files:**
- ⚠️ State files (`.testnet_state.json`) contain position and trade data
- ⚠️ Not encrypted (coming in Sprint 6)
- ✅ Automatically gitignored
- ✅ Protected by file locks (concurrent access safety)

**Logs:**
- ✅ Log files automatically gitignored
- ⚠️ May contain sensitive information (API responses, prices)
- ✅ Rotated automatically (10MB max, 5 backups)
- ⚠️ Review before sharing logs for debugging

**Secrets Management:**
- ✅ `.env` files gitignored by default
- ✅ Credentials never logged
- ⚠️ Be careful with `docker logs` output (may contain startup messages)

---

## Known Limitations

### Current (v0.4.x)

1. **Testnet-only deployment** - Mainnet not supported yet
2. **No state file encryption** - State stored in plaintext JSON
3. **Dashboard has no authentication** - Only for local use
4. **No multi-factor authentication** - Relying on API key security only
5. **No position size limits by account value** - Fixed position sizes

### Planned Improvements (Sprint 6+)

1. **Encrypted state files** - AES-256 encryption for sensitive data
2. **Dashboard authentication** - Password protection for web interface
3. **Position size limits** - Maximum position as % of account balance
4. **Emergency kill switch** - Webhook or SMS to stop bot remotely
5. **Audit logging** - Immutable log of all trading actions

---

## Security Best Practices

### For Developers

1. **Code Review**: All PRs require review before merge
2. **No Secrets in Code**: Use environment variables
3. **Input Validation**: Sanitize all external inputs
4. **Error Handling**: Fail securely, don't expose internals
5. **Dependency Updates**: Review and test security patches weekly

### For Users

1. **Start Small**: Test on testnet first, use small sizes on mainnet
2. **Monitor Actively**: Check bot status every few hours initially
3. **Set Alerts**: Use dashboard or custom monitoring
4. **Backup State**: Keep backups of `.testnet_state.json`
5. **Review Logs**: Check logs daily for errors or anomalies
6. **Secure Your Environment**:
   - Use strong passwords for server access
   - Enable 2FA on GitHub, exchange accounts
   - Use SSH keys (not passwords) for server access
   - Keep OS and Docker updated

---

## Incident Response

### If You Suspect a Security Issue

1. **Stop the bot immediately**: `python3 -m live.cli stop`
2. **Check positions on exchange**: Verify via exchange web interface
3. **Review logs**: Look for unexpected behavior
4. **Report the issue**: Follow vulnerability reporting process above
5. **Do not share details publicly** until fix is available

### If Your Credentials Are Compromised

1. **Revoke API keys immediately** on exchange
2. **Transfer funds** to a new wallet (if mainnet)
3. **Generate new credentials**
4. **Review trade history** for unauthorized activity
5. **Update `.env` file** with new credentials
6. **Report incident** if you suspect the bot software was involved

---

## Security Checklist

### Before Running on Testnet

- [ ] `.env` file contains testnet credentials only
- [ ] `.env` file is gitignored and not committed
- [ ] Docker containers are running with non-root user
- [ ] Dashboard port (8080) is not exposed to public internet
- [ ] Logs are being written to `/tmp/bot_v2.log`
- [ ] State file is automatically saved and gitignored

### Before Running on Mainnet (When Supported)

- [ ] Completed 7-day testnet validation (Sprint 6)
- [ ] Using separate mainnet wallet (not testnet wallet)
- [ ] API keys have withdraw restrictions (if available)
- [ ] Circuit breakers configured conservatively
- [ ] Position sizes tested and appropriate for account
- [ ] Monitoring dashboard accessible and functional
- [ ] Alert system configured (email, SMS, or webhook)
- [ ] Emergency stop procedure documented and tested
- [ ] State file backup strategy in place

---

## Security Updates

Subscribe to releases on GitHub to be notified of security updates:
- Watch this repository → Custom → Releases

Security-critical updates will be marked with `[SECURITY]` in the release title.

---

## Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk.

The developers are not responsible for:
- Financial losses from trading
- Security breaches due to improper configuration
- Exchange failures or smart contract exploits
- Data loss or corruption

Always conduct your own security audit before using with real funds.

---

## Contact

For security-related questions or concerns, please use the vulnerability reporting process described above.

For general questions, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

**Last Updated**: 2026-01-07
**Next Review**: Sprint 6 (Mainnet preparation)
