# Contributing to OpenClaw Guardian

Thank you for considering contributing to OpenClaw Guardian!

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-guardian.git
cd openclaw-guardian
```

## Security Requirements

**CRITICAL**: Guardian handles sensitive systems. Follow these rules:

### Prohibited in Code
- ❌ Hardcoded file paths (use `$HOME` templates)
- ❌ API keys or tokens (even in comments)
- ❌ Real username references
- ❌ Absolute paths like `/Users/username/...`

### Required Patterns
```python
# ✅ Use environment-aware paths
CONFIG_DIR = os.path.expanduser("~/.openclaw")
LOG_FILE = os.path.join(CONFIG_DIR, "guardian", "watchdog.log")

# ✅ Template variables in plist files
<string>{{HOME}}/.openclaw/scripts/watchdog.py</string>

# ✅ No sensitive info in logs
log(f"Provider {provider_name} cooldown")  # OK
log(f"API key: {api_key}")  # NEVER
```

## Testing

### Test Watchdog Script
```bash
python3 -m py_compile layer1-watchdog/watchdog.py
python3 layer1-watchdog/watchdog.py --dry-run
```

### Test Health Fetcher
```bash
python3 layer2-audit/health_fetcher.py
```

### Validate Plist Files
```bash
plutil layer1-watchdog/com.openclaw.guardian.day.plist
plutil layer1-watchdog/com.openclaw.guardian.night.plist
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** your changes on a clean OpenClaw installation
4. **Ensure** no sensitive information is included (run `grep -r "winniewu\|sk-" .` to check)
5. **Commit** with clear messages
6. **Push** to your fork
7. **Open** a Pull Request

## Code Style

### Python
- Follow PEP 8
- Use type hints where helpful
- Document functions with docstrings

### Shell Scripts
- Use `set -e` for error handling
- Quote all variables: `"$HOME"` not `$HOME`
- Use `[[ ]]` for conditionals

## Adding New Checks

When adding new health checks:

1. Update `health_fetcher.py`:
   - Add pattern to `LLM_PATTERNS`
   - Update analysis function
   - Add to output JSON

2. Update documentation:
   - Add to README.md
   - Update SKILL.md
   - Add example to report format

3. Test thoroughly:
   - Verify no false positives
   - Check token cost impact
   - Test on real log samples

## Reporting Issues

Include:
- OpenClaw version (`openclaw --version`)
- macOS version (`sw_vers`)
- Guardian version (from SKILL.md)
- Relevant log excerpts (redact sensitive info)
- Steps to reproduce

## Questions?

- GitHub Discussions: General questions
- GitHub Issues: Bug reports
- OpenClaw Discord: Community chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
