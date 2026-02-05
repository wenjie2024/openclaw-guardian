# OpenClaw Guardian

[English](#english-version) | [中文](#中文版本)

---

<a name="english-version"></a>
## 🇬🇧 English

Production-ready self-healing and monitoring for OpenClaw deployments.

### What It Does

OpenClaw Guardian provides a three-layer defense system that keeps your OpenClaw instance healthy, secure, and automatically recovering from failures without manual intervention.

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

### Installation

#### Automated Installation (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/openclaw-guardian/main/install.sh | bash
```

Or manually:

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-guardian.git
cd openclaw-guardian
./install.sh
```

#### Scheduling Configuration

**Layer 1 (Watchdog)** is automatically scheduled via macOS LaunchAgents.

**Layer 2 (System Audit)** requires you to configure a cron job:

```bash
# Every 2 hours during daytime
crontab -e
0 8-22/2 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"
```

> ⚠️ **Token Usage Notice**: More frequent health checks and reports will consume more LLM tokens. Adjust the schedule based on your stability needs and token budget.

### Features

**Layer 1: Self-Healing Watchdog**
- Health probes via external sessions spawn
- Automatic config restoration from rolling backups
- Error classification (CONFIG_ERROR, TIMEOUT, CONNECTION, AUTH_ERROR)
- Smart day/night scheduling

**Layer 2: System Audit**
- Dual log analysis (gateway.log + gateway.err.log)
- LLM health tracking (cooldown, auth failures, rate limits)
- Failover detection
- Cron job monitoring

**Layer 3: Security (Optional)**
- Integrates with Tinman for security scans
- Prompt injection detection
- Tool misuse monitoring

### Configuration

Edit `~/.openclaw/guardian.yaml`:

```yaml
watchdog:
  day_interval_minutes: 15
  night_interval_minutes: 60
  max_consecutive_restarts: 3

audit:
  report_interval_hours: 2

security:
  tinman_enabled: false
```

### License

Apache-2.0

---

<a name="中文版本"></a>
## 🇨🇳 中文

OpenClaw 生产级自愈与监控系统。

### 功能概述

OpenClaw Guardian 提供三层防护体系，确保您的 OpenClaw 实例保持健康、安全，并在故障时自动恢复，无需人工干预。

```
┌─────────────────────────────────────────┐
│  第三层：安全审计（可选）                │
│  每日扫描提示词注入、工具滥用、          │
│  上下文泄露等安全问题                    │
│  （需要安装 tinman skill）              │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  第二层：系统审计                        │
│  每 N 小时：Gateway 健康状态、           │
│  LLM 路由诊断、定时任务监控              │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  第一层：自愈探活                        │
│  健康探测、自动恢复、                    │
│  滚动配置备份                            │
└─────────────────────────────────────────┘
```

### 安装

#### 自动安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/openclaw-guardian/main/install.sh | bash
```

或手动安装：

```bash
git clone https://github.com/YOUR_USERNAME/openclaw-guardian.git
cd openclaw-guardian
./install.sh
```

#### 定时配置

**第一层（Watchdog）** 通过 macOS LaunchAgent 自动调度，无需额外配置。

**第二层（系统审计）** 需要您自行配置定时任务：

```bash
# 编辑 crontab
crontab -e

# 白天每2小时执行一次
0 8-22/2 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"

# 或每4小时一次（频率更低，Token 消耗更少）
0 */4 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"

# 或每天一次
0 9 * * * /usr/bin/python3 $HOME/.openclaw/scripts/openclaw-guardian/health_fetcher.py | openclaw message send --target "#your-channel"
```

> ⚠️ **Token 消耗提示**：更频繁的健康检查和报告会消耗更多 LLM Token。请根据您的稳定性需求和 Token 预算调整定时频率。第一层（Watchdog）独立运行，即使第二层报告频率较低也能持续保护系统。

### 功能特性

**第一层：自愈探活**
- 通过外部会话生成进行健康探测
- 从滚动备份自动恢复配置（current/v1/v2/v3）
- 错误分类（配置错误、超时、连接失败、认证失败）
- 智能昼夜调度策略

**第二层：系统审计**
- 双日志分析（gateway.log + gateway.err.log）
- LLM 健康追踪（Provider 冷却、认证失败、限流）
- Failover 链路检测
- 定时任务监控

**第三层：安全审计（可选）**
- 集成 Tinman 进行安全扫描
- 提示词注入检测
- 工具滥用监控

### 配置说明

编辑 `~/.openclaw/guardian.yaml`：

```yaml
watchdog:
  day_interval_minutes: 15      # 白天（08:00-23:00）每15分钟
  night_interval_minutes: 60    # 夜间（00:00-07:00）每60分钟
  max_consecutive_restarts: 3   # 最大连续重启次数
  log_rotation_mb: 10           # 日志轮转大小

audit:
  report_interval_hours: 2      # 通过 cron 配置实际执行频率

security:
  tinman_enabled: false         # 是否启用 Tinman 安全扫描
```

### 故障排查

**Watchdog 未运行**
```bash
# 重新加载 LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
```

**配置恢复失败**
```bash
# 查看可用备份
ls -la ~/.openclaw/config-backups/

# 手动恢复
cp ~/.openclaw/config-backups/openclaw.json.current ~/.openclaw/openclaw.json
openclaw gateway restart
```

**Token 消耗过高**
```yaml
# 在 guardian.yaml 中降低探测频率
watchdog:
  day_interval_minutes: 30  # 改为30分钟
```

### 安全策略

| 敏感信息类型 | 处理方式 |
|-------------|---------|
| API Key | 永不记录或显示 |
| Provider 账号 | 脱敏处理（如 `moonshot:default` → `moonshot`） |
| 文件路径 | 使用 `$HOME` 模板 |
| Token | 所有输出中均脱敏 |

### 许可证

Apache-2.0

---

**Remember / 请记住**: Guardian watches over your OpenClaw so you don't have to. / Guardian 守护您的 OpenClaw，让您高枕无忧。
