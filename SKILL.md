---
name: openclaw-guardian
description: A three-layer self-healing and monitoring stack for OpenClaw - ensures stability through automated health checks, intelligent recovery, and comprehensive auditing.
version: 1.0.0
author: Community
license: MIT
requires:
  openclaw: ">=2026.2.2"
  python: ">=3.10"
  os: "macOS"
---

# OpenClaw Guardian

A production-ready monitoring and self-healing system for OpenClaw deployments.

## 🏗️ Architecture

### Three-Layer Defense

```
Layer 3: Security Audit (Tinman Integration)
├── Daily scans for prompt injection
├── Tool misuse detection  
└── Context bleed monitoring

Layer 2: System Audit (Health Reports)
├── Every 2 hours (daytime)
├── Gateway health analysis
├── LLM routing diagnostics
├── Cron job monitoring
└── Self-healing event tracking

Layer 1: Self-Healing Watchdog
├── Health probes every 15min (day) / 1hr (night)
├── Automatic config recovery
├── Gateway restart on failure
└── Rolling backup management
```

## 🚀 Quick Start

```bash
# Install
cd openclaw-guardian
./install.sh

# Verify
launchctl list | grep com.openclaw.guardian
tail -f ~/.openclaw/guardian/watchdog.log
```

## 📋 Components

### Layer 1: Watchdog

**File**: `layer1-watchdog/watchdog.py`

Monitors Gateway health and performs automatic recovery:

- **Health Check**: `openclaw sessions spawn --task "Say OK"`
- **Error Classification**: Detects CONFIG_ERROR, TIMEOUT, CONNECTION, AUTH_ERROR
- **Auto-Recovery**: Restores config from rolling backups
- **Notification**: Alerts via Discord/macos notification center

**Schedule**:
- Day (08:00-23:00): Every 15 minutes
- Night (00:00-07:00): Every 60 minutes

### Layer 2: Health Fetcher

**File**: `layer2-audit/health_fetcher.py`

Collects system health data for reporting:

**Data Sources**:
- `gateway.log` - Gateway operations
- `gateway.err.log` - Errors and diagnostics
- `guardian/audit.jsonl` - Self-healing events
- `openclaw cron list` - Task status

**LLM Health Metrics**:
- Provider cooldown events
- Auth failures
- Rate limits
- Timeouts
- Failover chains

**Security**: All API keys and provider account identifiers are redacted.

### Layer 3: Tinman (Optional)

Requires [tinman skill](https://github.com/oliveskin/openclaw-skill-tinman).

## ⚙️ Configuration

```yaml
# ~/.openclaw/guardian.yaml
watchdog:
  day_interval_minutes: 15
  night_interval_minutes: 60
  max_consecutive_restarts: 3
  log_rotation_mb: 10
  backup_count: 4  # current + v1/v2/v3

audit:
  report_interval_hours: 2
  log_read_size_kb: 512
  history_window_hours: 2

notification:
  discord_channel: "#the-beacon"
  fallback: "macos_notification"
```

## 📊 Report Format

Example System Watchdog report:

```
🛰️ Gateway 状态
• 重启次数: 0 次
• 运行状态: 🟢 稳定

🧠 LLM 路由健康
• 主模型: moonshot/kimi-k2.5
• Fallback 链路: kimi → claude-sonnet → gemini-flash
• Provider 冷却: 0 次
• Auth 失败: 0 次

🛡️ 自愈事件
• 配置恢复: 0 次
• Gateway 重启: 0 次

🕒 定时任务
• Hourly Status: ✅ 上次运行 07:00
• Daily Brief: ✅ 上次运行 07:00
```

## 🔒 Security Policy

**Prohibited in all outputs**:
- API keys (any portion)
- Provider account identifiers (e.g., `:default` suffix)
- Secret file paths
- Authentication tokens

**Allowed**:
- Model names (`moonshot/kimi-k2.5`)
- Provider names (`moonshot`, `google`, `anthropic`)
- Public configuration

## 🔧 Troubleshooting

### Watchdog not starting
```bash
# Check plist syntax
plutil ~/Library/LaunchAgents/com.openclaw.guardian.day.plist

# Reload
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
```

### Missing audit events
```bash
# Check audit log exists
ls -la ~/.openclaw/guardian/audit.jsonl

# Verify permissions
touch ~/.openclaw/guardian/test && rm ~/.openclaw/guardian/test
```

### High token usage
Reduce probe frequency in `guardian.yaml`:
```yaml
watchdog:
  day_interval_minutes: 30  # Instead of 15
```

## 📈 Performance

**Typical monthly costs**:
- Watchdog probes: ~1M tokens
- Audit reports: ~0.4M tokens
- **Total**: ~1.5M tokens/month (~$0.50-2.00 depending on models)

## 🤝 Integration

### With Existing Skills

Guardian is designed to complement, not replace:

- **daily-brief**: Guardian monitors its execution
- **tinman**: Guardian reports security scan status
- **finance_llm_usage**: Guardian tracks routing efficiency

### Custom Alerts

Modify `layer1-watchdog/watchdog.py`:

```python
def notify(message, level="info"):
    # Add your custom notification logic
    send_to_pagerduty(message)  # Example
```

## 📝 Development

### Testing Changes

```bash
# Test health fetcher
python3 layer2-audit/health_fetcher.py

# Test watchdog manually
python3 layer1-watchdog/watchdog.py
```

### Adding New Checks

1. Add pattern to `health_fetcher.py` `LLM_PATTERNS`
2. Update analysis function
3. Add to output JSON structure
4. Update SKILL.md documentation

## 📚 References

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Tinman Security Scanner](https://github.com/oliveskin/openclaw-skill-tinman)
- [LaunchAgent Documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)

## 💬 Support

- GitHub Issues: Report bugs and feature requests
- OpenClaw Discord: Community support
- ClawHub: Find other skills

---

**Remember**: Guardian watches over your OpenClaw so you don't have to.
