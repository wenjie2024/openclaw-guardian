# OpenClaw Guardian

Production-ready self-healing and monitoring for OpenClaw deployments.

## What It Does

OpenClaw Guardian provides a three-layer defense system that keeps your OpenClaw instance healthy, secure, and automatically recovering from failures without manual intervention.

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Layer 3: Security (Optional)           │
│  Daily scans for prompt injection,      │
│  tool misuse, context bleed             │
│  (requires tinman skill)                │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Layer 2: System Audit                  │
│  Every N hours: Gateway health,         │
│  LLM routing diagnostics, cron jobs     │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Layer 1: Self-Healing Watchdog         │
│  Health probes, auto-recovery,          │
│  rolling config backups                 │
└─────────────────────────────────────────┘
```

## Installation

### Automated Installation (Recommended)

Run this command in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/openclaw-guardian/main/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-guardian.git
cd openclaw-guardian
./install.sh
```

The installer will:
- Create necessary directories
- Install watchdog scripts
- Configure macOS LaunchAgents (for automatic scheduling)
- Set up rolling config backups
- Verify the installation

### Manual Configuration

After installation, edit your configuration:

```bash
# Copy the example configuration
cp ~/.openclaw/guardian.yaml.example ~/.openclaw/guardian.yaml

# Edit to your needs
nano ~/.openclaw/guardian.yaml
```

### Scheduling Configuration

**Layer 1 (Watchdog)** is automatically scheduled via macOS LaunchAgents:
- **Day** (08:00-23:00): Every 15 minutes
- **Night** (00:00-07:00): Every 60 minutes

**Layer 2 (System Audit)** requires you to configure a cron job:

```bash
# Edit your crontab
crontab -e

# Add a line like this (adjust frequency to your needs):
# Every 2 hours during daytime (08:00-22:00)
0 8-22/2 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"

# Or every 4 hours (less frequent, lower token usage):
0 */4 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"

# Or once per day:
0 9 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"
```

> ⚠️ **Token Usage Notice**: More frequent health checks and reports will consume more LLM tokens. Adjust the schedule based on your stability needs and token budget. Layer 1 (Watchdog) runs independently and will continue to protect your system even if Layer 2 reports are infrequent.

## Features

### Layer 1: Self-Healing Watchdog

- **Health Probes**: External sessions spawn to detect Gateway failures
- **Auto-Recovery**: Automatic config restoration from rolling backups (current/v1/v2/v3)
- **Error Classification**: Detects CONFIG_ERROR, TIMEOUT, CONNECTION, AUTH_ERROR
- **Smart Scheduling**: Optimized day/night frequencies to balance responsiveness and cost
- **Notifications**: Alerts via Discord or macOS notification center

### Layer 2: System Audit

- **Dual Log Analysis**: Reads both `gateway.log` and `gateway.err.log`
- **LLM Health Tracking**: Monitors provider cooldown, auth failures, rate limits, timeouts
- **Failover Detection**: Tracks model switching paths
- **Cron Job Monitoring**: Reports task success/failure with execution times
- **Self-Healing Events**: Reports Watchdog recovery actions

### Layer 3: Security (Optional)

Integrates with [Tinman](https://github.com/oliveskin/openclaw-skill-tinman) for:
- Daily security scans
- Prompt injection detection
- Tool misuse monitoring
- Context bleed detection

To enable:
```bash
openclaw skill install tinman
# Then set tinman_enabled: true in ~/.openclaw/guardian.yaml
```

## Configuration

Default configuration (`~/.openclaw/guardian.yaml`):

```yaml
watchdog:
  day_interval_minutes: 15      # 08:00-23:00
  night_interval_minutes: 60    # 00:00-07:00
  max_consecutive_restarts: 3
  log_rotation_mb: 10
  backup_count: 4

audit:
  report_interval_hours: 2      # Configure via your own cron job
  log_read_size_kb: 512
  history_window_hours: 2

security:
  tinman_enabled: false
  daily_scan_time: "09:15"

notification:
  discord_channel: "#alerts"
  fallback: "macos_notification"
```

## Monitoring

### Check Watchdog Status

```bash
# View recent logs
tail -f ~/.openclaw/guardian/watchdog.log

# Check if LaunchAgents are loaded
launchctl list | grep com.openclaw.guardian

# Manual health check
python3 ~/.openclaw/scripts/openclaw-guardian/health_fetcher.py
```

### View Audit Events

```bash
# Recent self-healing events
cat ~/.openclaw/guardian/audit.jsonl | tail -10
```

## Troubleshooting

### Watchdog not running

```bash
# Reload LaunchAgents
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
```

### Config recovery failed

```bash
# List available backups
ls -la ~/.openclaw/config-backups/

# Manual restore
cp ~/.openclaw/config-backups/openclaw.json.current ~/.openclaw/openclaw.json
openclaw gateway restart
```

### High token usage

Reduce probe frequency in `~/.openclaw/guardian.yaml`:
```yaml
watchdog:
  day_interval_minutes: 30  # Instead of 15
```

Or increase your cron job interval for Layer 2 reports.

## Architecture

### Data Flow

```
Watchdog Probe (Layer 1)
      ↓
  Detect Failure
      ↓
Classify Error → Auto-Recover → Write Audit Event
      ↓
System Audit (Layer 2) - On your schedule
      ↓
Read Logs + Audit Events → Generate Report → Send Alert
```

### File Locations

| Component | Path |
|-----------|------|
| Watchdog Script | `~/.openclaw/scripts/openclaw-guardian/watchdog.py` |
| Health Fetcher | `~/.openclaw/scripts/openclaw-guardian/health_fetcher.py` |
| Day Schedule | `~/Library/LaunchAgents/com.openclaw.guardian.day.plist` |
| Night Schedule | `~/Library/LaunchAgents/com.openclaw.guardian.night.plist` |
| Logs | `~/.openclaw/guardian/watchdog.log` |
| Audit Events | `~/.openclaw/guardian/audit.jsonl` |
| Config Backups | `~/.openclaw/config-backups/` |

## Security

**Sensitive Information Protection**:

| Type | Handling |
|------|----------|
| API Keys | Never logged or displayed |
| Provider accounts | Stripped (e.g., `moonshot:default` → `moonshot`) |
| File paths | Use `$HOME` templates |
| Tokens | Redacted in all outputs |

## Requirements

- macOS 12+ (for LaunchAgent scheduling)
- OpenClaw 2026.2.2+
- Python 3.10+
- Tinman (optional, for Layer 3 security)

## Contributing

PRs welcome! Please ensure:
1. No sensitive information in commits
2. Use template variables for paths (`$HOME`, not `/Users/xxx`)
3. Test on clean OpenClaw installation

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Acknowledgments

- Built for the OpenClaw community
- Security practices inspired by [Tinman](https://github.com/oliveskin/openclaw-skill-tinman)
- Production monitoring patterns from real-world deployments

## Support

- GitHub Issues: Bug reports and feature requests
- OpenClaw Discord: Community support
- ClawHub: Find related skills

---

**License**: Apache-2.0

**Remember**: Guardian watches over your OpenClaw so you don't have to.
