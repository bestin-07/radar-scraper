# 🐧 Kerala Radar Scraper - Linux Deployment Guide

## Quick Start

### 1. For Development/Testing
```bash
# Make setup script executable
chmod +x setup_linux.sh

# Run automated setup
./setup_linux.sh

# Test the installation
./run_radar_linux.sh --help
```

### 2. For Production Server Deployment
```bash
# Make deployment script executable (requires root)
chmod +x deploy_linux.sh

# Deploy as system service
sudo ./deploy_linux.sh
```

## 📋 What You Get

### Development Setup (`./setup_linux.sh`)
- ✅ Python virtual environment in `venv/`
- ✅ All dependencies installed
- ✅ Executable scripts ready
- ✅ Directory structure created
- ✅ Manual execution ready

### Production Deployment (`sudo ./deploy_linux.sh`)
- ✅ System service installation
- ✅ Dedicated service user (`radar`)
- ✅ Automatic timer (every 10 minutes)
- ✅ Security hardening
- ✅ Systemd integration
- ✅ Log management

## 🚀 Usage Examples

### Manual Execution
```bash
# Activate environment and run
source venv/bin/activate
./radar_scraper.py                 # All radars
./radar_scraper.py --no-mosdac     # IMD only
./radar_scraper.py --mosdac-only   # MOSDAC only

# Or use convenience script
./run_radar_linux.sh               # All radars
./run_radar_linux.sh --no-mosdac   # IMD only
```

### Systemd Service Management
```bash
# Check service status
systemctl status radar-scraper.timer

# View recent logs
journalctl -u radar-scraper.service -f

# Manual trigger
sudo systemctl start radar-scraper.service

# Stop/start timer
sudo systemctl stop radar-scraper.timer
sudo systemctl start radar-scraper.timer
```

### Cron Alternative (if not using systemd)
```bash
# Edit crontab
crontab -e

# Add entry for every 10 minutes
*/10 * * * * cd /path/to/radar-scraper && ./run_radar_linux.sh >/dev/null 2>&1
```

## 📊 Monitoring & Logs

### Real-time Monitoring
```bash
# Watch service logs
journalctl -u radar-scraper.service -f

# Check timer schedule
systemctl list-timers radar-scraper.timer

# View recent activity
journalctl -u radar-scraper.service --since "1 hour ago"
```

### File System Monitoring
```bash
# Check downloaded images
ls -la /opt/radar-scraper/radar_images/*/

# Monitor disk usage
du -sh /opt/radar-scraper/radar_images/

# Check latest downloads
find /opt/radar-scraper/radar_images/ -name "*.gif" -mtime -1 -ls
```

## 🔧 Troubleshooting

### Common Issues

#### Permission Problems
```bash
# Fix ownership (if deployed as service)
sudo chown -R radar:radar /opt/radar-scraper/

# Fix script permissions
chmod +x setup_linux.sh deploy_linux.sh run_radar_linux.sh radar_scraper.py
```

#### Python Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Network Connectivity
```bash
# Test IMD radar connectivity
curl -I http://117.221.70.132/dwr/radar/images/caz_koc.gif

# Test MOSDAC connectivity
curl -I https://mosdac.gov.in/

# Check for proxy/firewall issues
export http_proxy=http://proxy:port   # if behind proxy
export https_proxy=http://proxy:port
```

#### Service Issues
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Check service file syntax
sudo systemd-analyze verify /etc/systemd/system/radar-scraper.service

# View detailed service status
sudo systemctl status radar-scraper.service -l
```

## 📁 File Structure

```
radar-scraper/
├── 🐍 Python Files
│   ├── radar_scraper.py          # Main application
│   ├── mosdac_only.py            # MOSDAC functions
│   └── requirements.txt          # Dependencies
├── 🐧 Linux Scripts
│   ├── setup_linux.sh            # Development setup
│   ├── deploy_linux.sh           # Production deployment
│   └── run_radar_linux.sh        # Convenience runner
├── ⚙️ System Files
│   ├── radar-scraper.service     # Systemd service
│   └── radar-scraper.timer       # Systemd timer
├── 📚 Documentation
│   ├── LINUX_SETUP.md           # Detailed Linux guide
│   └── README.md                 # General readme
└── 📊 Data
    ├── radar_images/             # Downloaded images
    │   ├── caz/                 # CAZ radar images
    │   ├── ppz/                 # PPZ radar images
    │   ├── ppi/                 # PPI radar images
    │   ├── zdr/                 # ZDR radar images
    │   ├── vp2/                 # VP2 radar images
    │   ├── 3ds/                 # 3DS radar images
    │   └── kochi/               # MOSDAC images
    └── known_timestamps.json    # MOSDAC cache
```

## 🔒 Security Features (Production Deployment)

- **Dedicated User**: Runs as `radar` user (no shell access)
- **Minimal Permissions**: Read-only system access
- **Protected Directories**: Only writes to designated image folders
- **No Network Servers**: Only makes outbound HTTP requests
- **Systemd Security**: NoNewPrivileges, ProtectSystem, PrivateTmp

## 📈 Performance Notes

- **CPU Usage**: Minimal (I/O bound operations)
- **Memory Usage**: ~50MB peak
- **Disk Usage**: ~40-60KB per radar image
- **Network**: ~6MB download per 10-minute cycle (IMD + MOSDAC)
- **Storage Growth**: ~864MB per day (all radars, 10-minute intervals)

## 🚨 Production Considerations

1. **Disk Space**: Monitor `/opt/radar-scraper/radar_images/` growth
2. **Log Rotation**: Systemd handles automatic log rotation
3. **Backup**: Consider backing up `known_timestamps.json`
4. **Monitoring**: Set up alerts for service failures
5. **Updates**: Stop timer before updating scripts

## 📞 Support Commands

```bash
# Full system check
./run_radar_linux.sh --help

# Test network connectivity
curl -f http://117.221.70.132/dwr/radar/images/caz_koc.gif > /dev/null

# Check Python environment
source venv/bin/activate && python3 -c "import requests; print('✅ OK')"

# Service health check
systemctl is-active radar-scraper.timer && echo "✅ Timer active"
```

---

**Ready to deploy? Choose your option:**
- 🧪 **Development**: `./setup_linux.sh`
- 🚀 **Production**: `sudo ./deploy_linux.sh`
