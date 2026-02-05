# OpenClaw Guardian - Project Structure

```
openclaw-guardian/
├── README.md                          # Main documentation
├── install.sh                         # One-click installer
├── LICENSE                            # Apache-2.0 License
├── config/
│   └── guardian.yaml                  # Default configuration template
├── layer1-watchdog/                   # Self-Healing Layer
│   ├── watchdog.py                    # Main watchdog script
│   ├── com.openclaw.guardian.day.plist    # Day schedule (15min)
│   └── com.openclaw.guardian.night.plist  # Night schedule (1hr)
├── layer2-audit/                      # System Audit Layer
│   └── health_fetcher.py              # Health data collector
├── skill/                             # System Watchdog Skill (NEW)
│   ├── SKILL.md                       # Skill documentation
│   └── run.sh                         # LLM report generator
├── layer3-security/                   # Security Layer (Optional)
│   └── README.md                      # Tinman integration guide
└── scripts/                           # Utility scripts (future)
    └── uninstall.sh                   # To be added
```

## File Purposes

### Core Files
- **README.md**: User-facing documentation, installation guide
- **SKILL.md**: Technical documentation for OpenClaw ecosystem
- **install.sh**: Automated setup script with validation

### Layer 1: Watchdog
- **watchdog.py**: External health probes, auto-recovery, rolling backups
- ***.plist**: macOS LaunchAgent schedules for day/night operation

### Layer 2: Audit
- **health_fetcher.py**: Log analysis, LLM health tracking, JSON data export

### Layer 3: Security
- **README.md**: Integration guide for Tinman security scanning

### Configuration
- **guardian.yaml**: User-customizable settings template

## Installation Paths

After running `./install.sh`, files are copied to:

```
~/.openclaw/
├── guardian/                          # Runtime data
│   ├── watchdog.log                   # Watchdog activity log
│   ├── audit.jsonl                    # Self-healing events
│   └── guardian.yaml                  # User configuration
├── scripts/openclaw-guardian/         # Executable scripts
│   ├── watchdog.py
│   └── health_fetcher.py
├── config-backups/                    # Rolling config backups
│   ├── openclaw.json.current
│   ├── openclaw.json.v1
│   ├── openclaw.json.v2
│   └── openclaw.json.v3
└── logs/                              # Standard OpenClaw logs
    ├── gateway.log
    └── gateway.err.log

~/Library/LaunchAgents/                # macOS scheduling
├── com.openclaw.guardian.day.plist
└── com.openclaw.guardian.night.plist
```

## Design Principles

1. **No Hardcoded Paths**: Use `{{HOME}}` and `$HOME` templates
2. **No Sensitive Data**: API keys, tokens, account IDs are never logged
3. **Modular Layers**: Each layer can function independently
4. **Template-Based**: Plist files use `{{HOME}}` for installation-time replacement
5. **Production-Ready**: Includes error handling, validation, and rollback support
