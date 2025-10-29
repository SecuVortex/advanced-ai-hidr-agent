# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| < 3.0   | :x:                |

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, email: **secuvortex@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You should receive a response within 48 hours.

## Security Best Practices

When using HIDR:

1. **Run as Administrator** - Required for process termination
2. **Keep API keys secure** - Use `.env` file (never commit)
3. **Review quarantined files** - Before deletion
4. **Update regularly** - Check for security patches
5. **Test in sandbox** - Before production use

## Known Limitations

- Requires admin privileges for full functionality
- YARA signatures need regular updates
- API rate limits apply (VirusTotal: 4 req/min free tier)

## Disclosure Policy

- Security issues will be patched within 7 days
- Public disclosure after patch release
- Credit given to reporters (if desired)

---

**Contact**: secuvortex@gmail.com
