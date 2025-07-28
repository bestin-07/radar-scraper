# Kerala Radar Data Collection System

A comprehensive P## 📚 Documentation

### Main Documentation
- **README.md** - This file: Main system overview and usage guide

### Detailed Documentation (in [`info/`](info/) folder)
- **[Linux Setup Guide](info/LINUX_SETUP.md)** - Complete Linux installation and configuration
- **[Linux Deployment Guide](info/LINUX_DEPLOYMENT.md)** - Production server deployment instructions
- **[Linux README](info/LINUX_README.md)** - Linux-specific documentation and scriptssystem for automated meteorological radar data collection and analysis from Kerala weather monitoring stations.

## 🎯 Overview

This professional-grade system automates the collection of multi-type radar data from Kerala meteorological sources, featuring intelligent duplicate detection, flexible scheduling, and advanced pattern analysis capabilities.

## ✨ Key Features

### 🛰️ Multi-Type Radar Support
- **CAZ** - Composite Reflectivity Z
- **PPZ** - Plan Position Indicator Z
- **PPI** - Plan Position Indicator
- **ZDR** - Differential Reflectivity
- **VP2** - Vertical Profile 2
- **3DS** - 3D Surface Analysis

### 🤖 Automated Intelligence
- **Smart Scheduling**: Hourly automated collection with custom intervals
- **Duplicate Detection**: SHA256-based image comparison prevents redundant downloads
- **Pattern Recognition**: MOSDAC timestamp analysis with ±20s flexibility
- **UTC Time Sync**: Precise timing alignment for meteorological accuracy

### 🗂️ Professional Organization
- **Structured Storage**: Organized directory hierarchy by radar type
- **Timestamped Files**: Consistent naming convention (YYYYMMDD_HHMM)
- **Error Handling**: Robust retry logic and comprehensive logging
- **Legacy Compatibility**: Backward compatible with existing data structures

## 🚀 Quick Start

### Option 1: Interactive Menu
```bash
run_radar.bat
```
*Windows batch file with user-friendly menu options*

### Option 2: Direct Execution

#### Single Download Session
```bash
python radar_scraper.py
```
*Downloads all 6 radar types immediately*

#### Automated Scheduler
```bash
python radar_scheduler.py
```
*Starts hourly automated collection*

#### Data Analysis
```bash
python radar_analyzer.py
```
*Analyzes collected data and provides insights*

## � Documentation

### Main Documentation
- **README.md** - This file: Main system overview and usage guide

### Detailed Documentation (in [`info/`](info/) folder)
- **[Linux Setup Guide](info/LINUX_SETUP.md)** - Complete Linux installation and configuration
- **[Linux Deployment Guide](info/LINUX_DEPLOYMENT.md)** - Production server deployment instructions
- **[Linux README](info/LINUX_README.md)** - Linux-specific documentation and scripts
- **[MOSDAC Configuration](info/MOSDAC_DISABLED.md)** - MOSDAC system changes and usage options
- **[Code Organization](info/ORGANIZATION_SUMMARY.md)** - Project structure and refactoring details
- **[Merge Summary](info/MERGE_SUMMARY.md)** - Code consolidation and cleanup history

## �📁 Directory Structure

```
Kerala SCRAPER/
├── radar_images/
│   ├── caz/                 # CAZ radar files
│   │   └── caz_radar_20250728_1500.gif
│   ├── ppz/                 # PPZ radar files
│   ├── ppi/                 # PPI radar files
│   ├── zdr/                 # ZDR radar files
│   ├── vp2/                 # VP2 radar files
│   ├── 3ds/                 # 3DS radar files
│   └── kochi/               # MOSDAC historical data
├── info/                    # Documentation files
│   ├── LINUX_SETUP.md      # Linux installation guide
│   ├── LINUX_DEPLOYMENT.md # Production deployment
│   └── LINUX_README.md     # Linux-specific docs
├── linux/                  # Linux deployment files
│   ├── setup_linux.sh      # Development setup
│   ├── deploy_linux.sh     # Production deployment
│   ├── run_radar_linux.sh  # Convenience runner
│   └── *.service, *.timer  # Systemd files
├── radar_scraper.py         # Main collection engine (refactored)
├── radar_scheduler.py       # Automation scheduler
├── radar_analyzer.py        # Data analysis tools
├── mosdac_only.py          # MOSDAC functions module
├── requirements.txt         # Python dependencies
└── README.md               # This documentation
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Internet connection for data downloads
- Windows/Linux/macOS compatible

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Manual Installation
```bash
pip install requests>=2.32.0 schedule>=1.2.0
```

### 🐧 Linux Deployment

For Linux servers, use the automated deployment scripts in the `linux/` folder:

#### Development Setup
```bash
chmod +x linux/setup_linux.sh
./linux/setup_linux.sh
./linux/run_radar_linux.sh --help
```

#### Production Server Deployment
```bash
chmod +x linux/deploy_linux.sh
sudo ./linux/deploy_linux.sh
systemctl status radar-scraper.timer
```

**Features:**
- ✅ Automated virtual environment setup
- ✅ Systemd service integration (runs every 10 minutes)
- ✅ Security hardening with dedicated user
- ✅ Professional logging and monitoring
- ✅ Works on Ubuntu, CentOS, Fedora

📚 **See [Linux Setup Guide](info/LINUX_SETUP.md) for complete deployment instructions**

## 🔧 Configuration

### Radar URLs
The system pulls data from:
```python
RADAR_URLS = {
    'caz': 'http://117.221.70.132/dwr/radar/images/caz_koc.gif',
    'ppz': 'http://117.221.70.132/dwr/radar/images/ppz_koc.gif',
    'ppi': 'http://117.221.70.132/dwr/radar/images/ppi_koc.gif',
    'zdr': 'http://117.221.70.132/dwr/radar/images/zdr_koc.gif',
    'vp2': 'http://117.221.70.132/dwr/radar/images/vp2_koc.gif',
    '3ds': 'http://117.221.70.132/dwr/radar/images/3ds_koc.gif'
}
```

### Scheduling Options
- **Hourly**: `run_scheduler()` - Runs every hour on the hour
- **Custom**: `run_custom_interval(30)` - Custom minute intervals
- **Manual**: Execute `radar_scraper.py` for one-time downloads

## 📊 Advanced Features

### MOSDAC Pattern Analysis
- **Reference-Based Generation**: Uses 13:23:22 UTC as anchor point
- **Interval Patterns**: 158s/761s alternating cycles with variants
- **Flexible Matching**: ±20 second tolerance for real-world timing
- **Complete Coverage**: Scans entire last hour for comprehensive data

### Duplicate Prevention
- **SHA256 Hashing**: Cryptographic comparison of image content
- **Size Verification**: File size validation before downloads
- **Overwrite Protection**: Smart detection of identical radar images

## 🔍 Usage Examples

### Basic Collection
```python
from radar_scraper import download_all_radar_types
results = download_all_radar_types()
print(f"Downloaded {sum(r['success'] for r in results.values())}/6 radar types")
```

### Custom Scheduling
```python
from radar_scheduler import run_custom_interval
run_custom_interval(15)  # Every 15 minutes
```

### Data Analysis
```python
from radar_analyzer import analyze_radar_directory
analyze_radar_directory()  # Comprehensive data report
```

## 📈 Sample Output

```
🌦️  Kerala Radar Scraper - Multi-Type Download
==================================================
🚀 Starting radar download session at 20250728_1500

📡 Downloading CAZ radar...
✅ caz: Saved radar_images\caz\caz_radar_20250728_1500.gif
   File size: 49,270 bytes

📡 Downloading PPZ radar...
🔄 ppz: Identical image exists: ppz_radar_20250728_1445.gif
   Skipping duplicate save

📊 Download Summary:
   ✅ Successful: 5/6
   📁 Saved to: radar_images

🔬 Running MOSDAC Hourly Analysis...
🎯 Target: 14:xx and 15:xx UTC (last hour coverage)
📊 Smart Scan Results: 8/16 images found
🎉 Success: 8/8 MOSDAC images
```

## 🛠️ Troubleshooting

### Common Issues
- **HTTP Errors**: Check internet connection and radar server status
- **Permission Errors**: Ensure write permissions in project directory
- **Missing Dependencies**: Run `pip install -r requirements.txt`

### Debug Mode
Add debug logging by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is for educational and research purposes. Please respect the data sources and their usage policies.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request


**Kerala Radar Data Collection System** - Professional meteorological data automation for research and analysis.
