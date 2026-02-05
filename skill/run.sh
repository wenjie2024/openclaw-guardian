#!/bin/bash

# System Watchdog Reporter
# Usage: ./run.sh
# This script collects health data and generates a Chinese audit report via LLM.

# Portable paths - works for any user
HOME_DIR="$HOME"
OPENCLAW_BIN="${HOME_DIR}/.npm-global/bin/openclaw"
SCRIPTS_DIR="${HOME_DIR}/.openclaw/scripts/openclaw-guardian"
HEALTH_FETCHER="${SCRIPTS_DIR}/health_fetcher.py"

# Fallback: try system openclaw if npm-global not found
if [ ! -f "$OPENCLAW_BIN" ]; then
    OPENCLAW_BIN=$(command -v openclaw 2>/dev/null || echo "/usr/local/bin/openclaw")
fi

# 1. Pre-fetch Health Data (2 hour window)
echo "📥 Fetching system health data from logs..."
if [ -f "$HEALTH_FETCHER" ]; then
    HEALTH_DATA_JSON=$("$HEALTH_FETCHER" 2>/dev/null || echo '{"error": "fetch_failed"}')
else
    HEALTH_DATA_JSON='{"error": "health_fetcher.py not found", "path": "'"$HEALTH_FETCHER"'"}'
fi

# 2. Define Task
TASK_PROMPT="你现在是 OpenClaw 系统监察员。请根据下方提供的过去 2 小时的系统健康快照，生成一份中文审计报告。

汇报要求：
1. **必须使用中文**。
2. **深度自省**：
    - 分析 Gateway 是否重启（如果是 SIGUSR1，说明是正常的配置重载；否则可能是崩溃）。
    - 分析 LLM Fallback 情况（统计次数，指出具体报错原因）。
    - 检查定时任务执行实况（哪些成功，哪些耗时过长）。
3. **适配手机端**：单级列表，粗体关键词，Emoji 导航。
4. **排除噪音**：不需要再追踪 GitHub Stars。

附加数据（过去 2 小时真实快照）：
${HEALTH_DATA_JSON}

输出格式：
【🛰️ Gateway 状态审计】
- 运行情况摘要。
- 重启记录及原因判定。

【🧠 模型路由审计】
- Fallback 事件统计。
- 失败原因深度解析（如 API 限流或响应超时）。

【🕒 定时任务追踪】
- 核心任务的最近运行状态。
- 异常耗时或失败预警。

【⚠️ 综合健康评估】
- 一句话总结系统当前是否健康。

生成时间：$(date)"

# 3. Dispatch Agent
$OPENCLAW_BIN agent \
  --session-id "watchdog-$(date +%Y-%m-%d-%H)" \
  --message "$TASK_PROMPT" \
  --thinking high \
  --channel discord \
  --reply-to "1467890964843597988" \
  --deliver

echo "✅ Watchdog report dispatched."
