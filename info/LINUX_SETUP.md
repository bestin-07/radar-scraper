# Kerala Radar Scraper - Linux Dependencies

## System Requirements

- **Operating System**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 9+, etc.)
- **Python**: 3.8 or higher
- **Internet**: Active connection for downloading radar data

## Dependencies

### System Packages (install via package manager)

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv curl wget
```

#### CentOS/RHEL:
```bash
sudo yum install python3 python3-pip curl wget
# or for newer versions:
sudo dnf install python3 python3-pip curl wget
```

#### Fedora:
```bash
sudo dnf install python3 python3-pip curl wget
```

### Python Packages (installed automatically by setup script)

- **requests** (2.31.0+): HTTP library for downloading radar images
  ```bash
  pip install requests
  ```

## Quick Setup

### 1. Download and Setup
```bash
# Clone or download the radar scraper files
# Make setup script executable
chmod +x setup_linux.sh

# Run setup (installs everything automatically)
./setup_linux.sh
```

### 2. Manual Setup (if needed)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install requests

# Make scripts executable
chmod +x radar_scraper.py
chmod +x run_radar_linux.sh

# Create image directories
mkdir -p radar_images/{caz,ppz,ppi,zdr,vp2,3ds,maxz}
```

## Usage

### Option 1: Direct Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Run radar scraper
./radar_scraper.py                 # All radar types
./radar_scraper.py --help          # Show help
```

### Option 2: Convenience Script
```bash
# Use the runner script (handles venv automatically)
./run_radar_linux.sh               # All radar types
```

## Automation with Cron

### Add to crontab for automatic execution:

```bash
# Edit crontab
crontab -e

# Add one of these lines:

# Run every 10 minutes (recommended)
*/10 * * * * cd /path/to/radar-scraper && source venv/bin/activate && ./radar_scraper.py >/dev/null 2>&1

# Run every 30 minutes
*/30 * * * * cd /path/to/radar-scraper && ./run_radar_linux.sh >/dev/null 2>&1

# Run hourly at 5 minutes past the hour (IMD only - faster)
5 * * * * cd /path/to/radar-scraper && ./run_radar_linux.sh

# Run every 2 hours
0 */2 * * * cd /path/to/radar-scraper && ./run_radar_linux.sh
```

## File Locations

After setup, your directory structure will be:
```
radar-scraper/
├── venv/                          # Python virtual environment
├── radar_images/                  # Downloaded radar images
│   ├── caz/                      # CAZ radar images
│   ├── ppz/                      # PPZ radar images
│   ├── ppi/                      # PPI radar images
│   ├── zdr/                      # ZDR radar images
│   ├── vp2/                      # VP2 radar images
│   ├── 3ds/                      # 3DS radar images
│   └── maxz/                     # MAXZ radar images
├── radar_scraper.py              # Main scraper script
├── setup_linux.sh               # Setup script
├── run_radar_linux.sh           # Convenience runner
└── requirements.txt              # Python dependencies
```

## Troubleshooting

### Permission Issues
```bash
# Make scripts executable
chmod +x setup_linux.sh run_radar_linux.sh radar_scraper.py

# Fix directory permissions
chmod -R 755 radar_images/
```

### Python Issues
```bash
# If python3 command not found
which python3
# or try:
python --version

# If virtual environment issues
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install requests
```

### Network Issues
```bash
# Test connectivity
curl -I http://117.221.70.132/dwr/radar/images/caz_koc.gif

# Check if behind firewall/proxy
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
```

### Log Files
```bash
# Run with logging
./radar_scraper.py 2>&1 | tee radar_scraper.log

# Check for errors
tail -f radar_scraper.log
```

## Performance Notes

- **Disk Space**: Each radar image is ~40-60KB. Plan accordingly for long-term storage.
- **Bandwidth**: Script downloads 7 radar images per run.
- **CPU Usage**: Minimal - mostly I/O bound operations.
- **Memory Usage**: Very low - typically under 50MB.

## Security Notes

- Script only makes outbound HTTP requests to known radar servers
- No sensitive data is stored or transmitted
- All files are saved locally in the radar_images directory
- Virtual environment isolates Python dependencies
