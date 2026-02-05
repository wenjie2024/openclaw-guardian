# Layer 3: Security Integration

## Overview

Layer 3 provides security scanning and failure mode detection by integrating with the [Tinman](https://github.com/oliveskin/openclaw-skill-tinman) skill.

## Prerequisites

Install Tinman skill:
```bash
openclaw skill install tinman
```

Or manual installation:
```bash
git clone https://github.com/oliveskin/openclaw-skill-tinman.git
# Follow tinman installation instructions
```

## Configuration

Enable Tinman integration in your guardian config:

```yaml
# ~/.openclaw/guardian.yaml
security:
  tinman_enabled: true
  daily_scan_time: "09:15"
```

## What Tinman Provides

### Daily Security Scans
- **Prompt Injection Detection**: Jailbreaks, DAN, instruction override
- **Tool Misuse Monitoring**: Unauthorized tool access, exfiltration attempts
- **Context Bleed Detection**: Cross-session data leakage
- **Failure Classification**: S0-S4 severity levels

### Attack Categories
- prompt_injection (15 patterns)
- tool_exfiltration (42 patterns)
- context_bleed (14 patterns)
- privilege_escalation (15 patterns)
- financial_attacks (26 patterns)
- And more...

## Integration with Guardian

When `tinman_enabled: true`, Guardian will:

1. Check for recent Tinman scan results
2. Include security findings in audit reports
3. Alert on S3-S4 severity issues

## Report Format

When Tinman is integrated, audit reports include:

```
🔒 安全扫描 (Tinman)
• 上次扫描: 09:15
• 分析会话: 47
• 发现威胁: 2 (S2)
• 关键威胁: 0

⚠️ 发现摘要
• S2: Tool exfiltration attempt detected
  Session: telegram/user_12345
  Mitigation: Added to sandbox denylist
```

## Manual Scan

Run Tinman scan manually:
```bash
/tinman scan --hours 24
```

View latest report:
```bash
/tinman report
```

## Without Tinman

Guardian works perfectly without Tinman. Layer 3 is optional:
- Layer 1 (Self-Healing) and Layer 2 (Audit) function independently
- Security scanning is an enhancement, not a requirement

## Contributing

If you add new security checks, please:
1. Follow Tinman's pattern format
2. Map to OpenClaw controls
3. Document severity rationale
