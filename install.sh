#!/bin/bash
# OpenClaw Guardian - Installation Script
# This script sets up the three-layer monitoring system

set -e

echo "🛡️  OpenClaw Guardian Installation"
echo "==================================="

# Configuration
GUARDIAN_DIR="${HOME}/.openclaw/guardian"
SCRIPTS_DIR="${HOME}/.openclaw/scripts/openclaw-guardian"
LAUNCHAGENTS_DIR="${HOME}/Library/LaunchAgents"
CONFIG_BACKUP_DIR="${HOME}/.openclaw/config-backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_openclaw() {
    if ! command -v openclaw &> /dev/null; then
        print_error "OpenClaw CLI not found. Please install OpenClaw first."
        exit 1
    fi
    print_success "OpenClaw CLI found"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.10+."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc) -eq 0 ]]; then
        print_error "Python 3.10+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION found"
}

setup_directories() {
    echo ""
    echo "📁 Setting up directories..."
    
    mkdir -p "$GUARDIAN_DIR"
    mkdir -p "$SCRIPTS_DIR"
    mkdir -p "$CONFIG_BACKUP_DIR"
    
    print_success "Created Guardian directories"
}

install_watchdog() {
    echo ""
    echo "🔧 Installing Layer 1: Self-Healing Watchdog..."
    
    # Get script directory
    SCRIPT_SOURCE="${BASH_SOURCE[0]}"
    while [ -L "$SCRIPT_SOURCE" ]; do
        SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)
        SCRIPT_SOURCE=$(readlink "$SCRIPT_SOURCE")
        [[ $SCRIPT_SOURCE != /* ]] && SCRIPT_SOURCE="$SCRIPT_DIR/$SCRIPT_SOURCE"
    done
    SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)
    
    # Copy watchdog script
    cp "$SCRIPT_DIR/layer1-watchdog/watchdog.py" "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/watchdog.py"
    print_success "Installed watchdog.py"
    
    # Install LaunchAgents
    for plist in "$SCRIPT_DIR"/layer1-watchdog/*.plist; do
        if [ -f "$plist" ]; then
            filename=$(basename "$plist")
            # Replace template variables in plist
            sed -e "s|{{HOME}}|$HOME|g" \
                -e "s|{{USER}}|$USER|g" \
                "$plist" > "$LAUNCHAGENTS_DIR/$filename"
            print_success "Installed $filename"
        fi
    done
    
    # Load LaunchAgents
    launchctl load "$LAUNCHAGENTS_DIR/com.openclaw.guardian.day.plist" 2>/dev/null || print_warning "Day schedule already loaded"
    launchctl load "$LAUNCHAGENTS_DIR/com.openclaw.guardian.night.plist" 2>/dev/null || print_warning "Night schedule already loaded"
    
    print_success "Watchdog installed and scheduled"
}

install_audit() {
    echo ""
    echo "📊 Installing Layer 2: System Audit..."
    
    # Get script directory
    SCRIPT_SOURCE="${BASH_SOURCE[0]}"
    while [ -L "$SCRIPT_SOURCE" ]; do
        SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)
        SCRIPT_SOURCE=$(readlink "$SCRIPT_SOURCE")
        [[ $SCRIPT_SOURCE != /* ]] && SCRIPT_SOURCE="$SCRIPT_DIR/$SCRIPT_SOURCE"
    done
    SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)
    
    # Copy health fetcher
    cp "$SCRIPT_DIR/layer2-audit/health_fetcher.py" "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR/health_fetcher.py"
    print_success "Installed health_fetcher.py"
    
    print_warning "Remember to update your cron job to use: $SCRIPTS_DIR/health_fetcher.py"
}

install_config() {
    echo ""
    echo "⚙️  Installing default configuration..."
    
    if [ ! -f "$HOME/.openclaw/guardian.yaml" ]; then
        cat > "$HOME/.openclaw/guardian.yaml" << 'EOF'
# OpenClaw Guardian Configuration

watchdog:
  day_interval_minutes: 15      # 08:00-23:00
  night_interval_minutes: 60    # 00:00-07:00
  max_consecutive_restarts: 3
  log_rotation_mb: 10
  backup_count: 4

audit:
  report_interval_hours: 2
  log_read_size_kb: 512
  history_window_hours: 2

security:
  tinman_enabled: false
  daily_scan_time: "09:15"

notification:
  discord_channel: "#the-beacon"
  fallback: "macos_notification"
EOF
        print_success "Created default configuration"
    else
        print_warning "Configuration already exists, skipping"
    fi
}

verify_installation() {
    echo ""
    echo "🔍 Verifying installation..."
    
    # Check files exist
    if [ -f "$SCRIPTS_DIR/watchdog.py" ]; then
        print_success "watchdog.py installed"
    else
        print_error "watchdog.py not found"
    fi
    
    if [ -f "$SCRIPTS_DIR/health_fetcher.py" ]; then
        print_success "health_fetcher.py installed"
    else
        print_error "health_fetcher.py not found"
    fi
    
    # Check LaunchAgents
    if launchctl list | grep -q "com.openclaw.guardian.day"; then
        print_success "Day schedule loaded"
    else
        print_error "Day schedule not loaded"
    fi
    
    if launchctl list | grep -q "com.openclaw.guardian.night"; then
        print_success "Night schedule loaded"
    else
        print_warning "Night schedule not yet active (will start at 00:00)"
    fi
    
    # Test Python scripts
    if python3 -m py_compile "$SCRIPTS_DIR/watchdog.py" 2>/dev/null; then
        print_success "watchdog.py syntax OK"
    else
        print_error "watchdog.py has syntax errors"
    fi
    
    if python3 -m py_compile "$SCRIPTS_DIR/health_fetcher.py" 2>/dev/null; then
        print_success "health_fetcher.py syntax OK"
    else
        print_error "health_fetcher.py has syntax errors"
    fi
}

print_summary() {
    echo ""
    echo "==================================="
    echo "🎉 Installation Complete!"
    echo "==================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. View watchdog logs:"
    echo "   tail -f ~/.openclaw/guardian/watchdog.log"
    echo ""
    echo "2. Check LaunchAgent status:"
    echo "   launchctl list | grep com.openclaw.guardian"
    echo ""
    echo "3. Update your System Watchdog cron job to use:"
    echo "   ~/.openclaw/scripts/openclaw-guardian/health_fetcher.py"
    echo ""
    echo "4. (Optional) Install Tinman for Layer 3 security:"
    echo "   openclaw skill install tinman"
    echo ""
    echo "Documentation: https://github.com/YOUR_USERNAME/openclaw-guardian"
    echo ""
}

# Main installation flow
main() {
    check_openclaw
    check_python
    setup_directories
    install_watchdog
    install_audit
    install_config
    verify_installation
    print_summary
}

main "$@"
