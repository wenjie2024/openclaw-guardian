# OpenClaw Guardian

三层自愈与监控系统，确保 OpenClaw 稳定运行。

## 功能概述

| 层级 | 功能 | 触发方式 |
|-----|------|---------|
| **Layer 1** | 自愈探活 | LaunchAgent 每 15 分钟 |
| **Layer 2** | 中文审计报告 | OpenClaw Cron 任务 |
| **Layer 3** | 安全扫描（可选） | 需安装 Tinman |

---

## 安装方法

### 方法 1：Bot 安装（推荐）

给 OpenClaw Bot 发送 GitHub 链接：

```
帮我安装这个 https://github.com/anchor-jevons/openclaw-guardian
```

或者：

```
安装 openclaw-guardian，地址是 https://github.com/anchor-jevons/openclaw-guardian
```

Bot 会自动：
1. 克隆项目到临时目录
2. 运行 `install.sh`
3. 配置定时任务
4. 清理临时文件

### 方法 2：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/anchor-jevons/openclaw-guardian.git
cd openclaw-guardian

# 2. 运行安装脚本
./install.sh

# 3. 验证安装
launchctl list | grep com.openclaw.guardian
```

---

## 安装后目录结构

```
~/.openclaw/
├── scripts/openclaw-guardian/     # 脚本
│   ├── watchdog.py
│   └── health_fetcher.py
├── skills/system-watchdog/        # Skill
│   ├── SKILL.md
│   └── run.sh
├── guardian/                      # 运行时数据
│   ├── watchdog.log
│   └── watchdog-audit.jsonl
└── config-backups/                # 配置备份

~/Library/LaunchAgents/
├── com.openclaw.guardian.day.plist
└── com.openclaw.guardian.night.plist
```

---

## 配置

编辑 `~/.openclaw/guardian.yaml`：

```yaml
watchdog:
  day_interval_minutes: 15      # 白天每 15 分钟
  night_interval_minutes: 60    # 夜间每 60 分钟
  max_consecutive_restarts: 3

audit:
  report_interval_hours: 2

security:
  tinman_enabled: false         # 可选
```

---

## 故障排查

**Watchdog 未运行**
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.guardian.day.plist
```

**查看日志**
```bash
tail -f ~/.openclaw/guardian/watchdog.log
```

---

## 卸载

```bash
# 停止定时任务
launchctl unload ~/Library/LaunchAgents/com.openclaw.guardian.*.plist

# 删除文件
rm -rf ~/.openclaw/scripts/openclaw-guardian
rm -rf ~/.openclaw/skills/system-watchdog
rm -rf ~/.openclaw/guardian
rm ~/Library/LaunchAgents/com.openclaw.guardian.*.plist
```

---

## License

Apache-2.0
