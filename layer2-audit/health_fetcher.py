#!/usr/bin/env python3
"""
OpenClaw Health Fetcher - LLM-Aware Version
Reads gateway.log and gateway.err.log to capture comprehensive system health.
"""
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from collections import defaultdict

HOME = os.path.expanduser("~")
OPENCLAW_BIN = os.path.join(HOME, ".npm-global", "bin", "openclaw")
# Support alternative install locations
if not os.path.exists(OPENCLAW_BIN):
    alternative_paths = [
        "/usr/local/bin/openclaw",
        "/opt/homebrew/bin/openclaw",
    ]
    for alt_path in alternative_paths:
        if os.path.exists(alt_path):
            OPENCLAW_BIN = alt_path
            break

LOG_DIR = os.path.join(HOME, ".openclaw", "logs")

# LLM Error patterns for structured analysis
LLM_PATTERNS = {
    "provider_cooldown": r"No available auth profile for (\w+).*in cooldown",
    "provider_unavailable": r"No available auth profile for (\w+).*unavailable",
    "auth_fail": r"authentication_error|Invalid bearer token|401",
    "rate_limit": r"rate limit|429|quota exceeded|You exceeded",
    "timeout": r"timed out|timeout",
    "failover_error": r"FailoverError.*LLM",
    "profile_timeout": r"Profile (\S+).*timed out",
}


def read_log_file_tail(log_path, max_bytes=512*1024, hours=2):
    """Read recent lines from a log file within time window."""
    if not os.path.exists(log_path):
        return []
    
    since_time = datetime.now(timezone.utc).astimezone() - timedelta(hours=hours)
    relevant_lines = []
    
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            read_size = min(file_size, max_bytes)
            f.seek(file_size - read_size)
            lines = f.readlines()
            
            for line in lines:
                match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                if match:
                    try:
                        # Parse UTC timestamp and convert to local time
                        log_time_str = match.group(1)
                        log_time = datetime.fromisoformat(log_time_str).replace(tzinfo=timezone.utc).astimezone()
                        if log_time > since_time:
                            relevant_lines.append(line)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading {log_path}: {e}", file=os.sys.stderr)
        
    return relevant_lines


def analyze_llm_health(lines):
    """Analyze LLM-related health indicators from log lines."""
    stats = {
        "cooldown_events": [],
        "auth_failures": [],
        "rate_limits": [],
        "timeouts": [],
        "failover_errors": [],
        "providers_affected": set(),
        "profiles_timed_out": set(),
    }
    
    for line in lines:
        # Provider cooldown/unavailable
        cooldown_match = re.search(LLM_PATTERNS["provider_cooldown"], line, re.I)
        if cooldown_match:
            provider = cooldown_match.group(1)
            stats["providers_affected"].add(provider)
            stats["cooldown_events"].append({
                "timestamp": extract_timestamp(line),
                "provider": provider,
                "status": "cooldown"
            })
            continue
        
        unavailable_match = re.search(LLM_PATTERNS["provider_unavailable"], line, re.I)
        if unavailable_match:
            provider = unavailable_match.group(1)
            stats["providers_affected"].add(provider)
            stats["cooldown_events"].append({
                "timestamp": extract_timestamp(line),
                "provider": provider,
                "status": "unavailable"
            })
            continue
        
        # Auth failures
        if re.search(LLM_PATTERNS["auth_fail"], line, re.I):
            stats["auth_failures"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:150]
            })
            continue
        
        # Rate limits
        if re.search(LLM_PATTERNS["rate_limit"], line, re.I):
            stats["rate_limits"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:150]
            })
            continue
        
        # Timeouts
        if re.search(LLM_PATTERNS["timeout"], line, re.I):
            stats["timeouts"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:150]
            })
            continue
        
        # Failover errors
        if re.search(LLM_PATTERNS["failover_error"], line, re.I):
            stats["failover_errors"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:200]
            })
            continue
        
        # Profile timeouts - only capture provider name, not full profile (security)
        profile_match = re.search(LLM_PATTERNS["profile_timeout"], line, re.I)
        if profile_match:
            profile = profile_match.group(1)
            # Extract only provider name (e.g., "moonshot" from "moonshot:default")
            provider_only = profile.split(":")[0] if ":" in profile else profile
            stats["profiles_timed_out"].add(provider_only)
    
    return stats


def extract_timestamp(line):
    """Extract HH:MM from log line timestamp."""
    match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})', line)
    return match.group(1)[11:16] if match else "--:--"


def analyze_gateway_logs(lines):
    """Analyze gateway.log for restarts and basic events."""
    stats = {
        "restarts": [],
        "fallbacks": [],
        "model_switches": [],
    }
    
    restart_patterns = [r"SIGUSR1", r"Starting gateway", r"Restarting"]
    fallback_patterns = [r"fallback", r"switching to"]
    model_patterns = [r"agent model:\s+(\S+)", r"using model:\s+(\S+)"]
    
    for line in lines:
        # Restarts
        if any(re.search(p, line, re.I) for p in restart_patterns):
            stats["restarts"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:100]
            })
        
        # Fallback hints
        if any(re.search(p, line, re.I) for p in fallback_patterns):
            stats["fallbacks"].append({
                "timestamp": extract_timestamp(line),
                "detail": line.strip()[:100]
            })
        
        # Model usage tracking
        for pattern in model_patterns:
            match = re.search(pattern, line, re.I)
            if match:
                stats["model_switches"].append({
                    "timestamp": extract_timestamp(line),
                    "model": match.group(1)
                })
    
    return stats


def get_watchdog_audit_events(hours=2):
    """Read watchdog audit events from the past N hours."""
    audit_path = os.path.expanduser("~/clawd/watchdog-audit.jsonl")
    if not os.path.exists(audit_path):
        return []
    
    since_time = datetime.now() - timedelta(hours=hours)
    events = []
    
    try:
        with open(audit_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    event_time = datetime.fromisoformat(event.get("timestamp", ""))
                    if event_time > since_time:
                        events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception as e:
        print(f"Error reading audit file: {e}", file=os.sys.stderr)
    
    return events


def summarize_watchdog_events(events):
    """Summarize watchdog events for the report."""
    summary = {
        "config_recoveries": [],
        "gateway_restarts": [],
        "total_events": len(events)
    }
    
    for event in events:
        event_type = event.get("type")
        status = event.get("status")
        details = event.get("details", {})
        timestamp = event.get("timestamp", "")[11:16]
        
        if event_type == "config_recovery":
            summary["config_recoveries"].append({
                "time": timestamp,
                "from": details.get("restored_from", "unknown"),
                "hash": details.get("config_hash", "unknown")[:8]
            })
        elif event_type == "gateway_restart":
            summary["gateway_restarts"].append({
                "time": timestamp,
                "status": status,
                "reason": details.get("reason", "unknown"),
                "attempt": details.get("attempt", 0)
            })
    
    return summary


def get_cron_status():
    """Get cron jobs status by reading cron jobs.json directly (avoids CLI hang)."""
    try:
        # Read cron jobs from dedicated cron directory
        cron_jobs_path = os.path.expanduser("~/.openclaw/cron/jobs.json")
        if not os.path.exists(cron_jobs_path):
            return {"error": "Cron jobs file not found", "jobs": []}
        
        with open(cron_jobs_path, 'r', encoding='utf-8') as f:
            cron_data = json.load(f)
        
        jobs = cron_data.get("jobs", [])
        
        # Format job info
        formatted_jobs = []
        for job in jobs:
            schedule = job.get("schedule", {})
            payload = job.get("payload", {})
            state = job.get("state", {})
            
            # Format schedule display
            sched_kind = schedule.get("kind", "unknown")
            if sched_kind == "cron":
                sched_display = f"cron {schedule.get('expr', '')}"
                if schedule.get("tz"):
                    sched_display += f" @ {schedule['tz']}"
            elif sched_kind == "every":
                every_ms = schedule.get("everyMs", 0)
                sched_display = f"every {every_ms // 60000}m" if every_ms else "unknown"
            elif sched_kind == "at":
                at_ms = schedule.get("atMs", 0)
                sched_display = f"at {at_ms}" if at_ms else "unknown"
            else:
                sched_display = sched_kind
            
            formatted_jobs.append({
                "id": job.get("id", "unknown"),
                "name": job.get("name", "unnamed"),
                "schedule": sched_display,
                "enabled": job.get("enabled", True),
                "sessionTarget": job.get("sessionTarget", "main"),
                "payloadKind": payload.get("kind", "unknown"),
                "lastRunAtMs": state.get("lastRunAtMs"),
                "lastStatus": state.get("lastStatus")
            })
        
        return {"jobs": formatted_jobs}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc(), "jobs": []}


def main():
    hours = 4
    
    # Read both log files
    gateway_lines = read_log_file_tail(
        os.path.join(LOG_DIR, "gateway.log"), 
        max_bytes=512*1024, 
        hours=hours
    )
    error_lines = read_log_file_tail(
        os.path.join(LOG_DIR, "gateway.err.log"), 
        max_bytes=256*1024,  # Smaller for error log
        hours=hours
    )
    
    # Analyze
    gateway_stats = analyze_gateway_logs(gateway_lines)
    llm_stats = analyze_llm_health(error_lines + gateway_lines)
    watchdog_events = get_watchdog_audit_events(hours=hours)
    watchdog_summary = summarize_watchdog_events(watchdog_events)
    cron_data = get_cron_status()
    
    # Summarize cron jobs
    cron_summary = []
    if "jobs" in cron_data:
        for job in cron_data["jobs"]:
            # Format last run time
            last_run_ms = job.get("lastRunAtMs")
            last_run_str = None
            if last_run_ms:
                last_run_dt = datetime.fromtimestamp(last_run_ms / 1000)
                last_run_str = last_run_dt.strftime("%m-%d %H:%M")
            
            cron_summary.append({
                "name": job.get("name"),
                "schedule": job.get("schedule"),
                "enabled": job.get("enabled"),
                "lastStatus": job.get("lastStatus"),
                "lastRun": last_run_str,
                "payloadKind": job.get("payloadKind")
            })
    
    # Build comprehensive output
    output = {
        "window_hours": hours,
        "data_sources": {
            "gateway_log_lines": len(gateway_lines),
            "error_log_lines": len(error_lines)
        },
        "gateway": {
            "restart_count": len(gateway_stats["restarts"]),
            "restart_details": gateway_stats["restarts"][-3:],
        },
        "llm_health": {
            "providers_affected": sorted(list(llm_stats["providers_affected"])),
            "profiles_timed_out": sorted(list(llm_stats["profiles_timed_out"])),
            "cooldown_count": len(llm_stats["cooldown_events"]),
            "cooldown_events": llm_stats["cooldown_events"][-5:],
            "auth_failure_count": len(llm_stats["auth_failures"]),
            "rate_limit_count": len(llm_stats["rate_limits"]),
            "timeout_count": len(llm_stats["timeouts"]),
            "failover_error_count": len(llm_stats["failover_errors"]),
            "recent_failover_errors": [
                {"time": e["timestamp"], "detail": e["detail"][:100]} 
                for e in llm_stats["failover_errors"][-3:]
            ],
            "model_switches": gateway_stats["model_switches"][-5:],
        },
        "cron_jobs": cron_summary,
        "watchdog_self_healing": watchdog_summary
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
