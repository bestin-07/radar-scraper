# 🐧 Linux Deployment Files

This folder contains all Linux-specific deployment files for the Kerala Radar Scraper.

## 📁 Contents

| File | Purpose |
|------|---------|
| `setup_linux.sh` | Development setup script |
| `deploy_linux.sh` | Production deployment script |
| `run_radar_linux.sh` | Convenience runner script |
| `radar-scraper.service` | Systemd service file |
| `radar-scraper.timer` | Systemd timer file |
| `LINUX_SETUP.md` | Technical documentation |
| `LINUX_DEPLOYMENT.md` | Quick deployment guide |

## 🚀 Quick Start

### Development Setup
```bash
chmod +x linux/setup_linux.sh
./linux/setup_linux.sh
```

### Production Deployment
```bash
chmod +x linux/deploy_linux.sh
sudo ./linux/deploy_linux.sh
```

### Run Manually
```bash
./linux/run_radar_linux.sh
```

## 📚 Documentation

- **[LINUX_DEPLOYMENT.md](LINUX_DEPLOYMENT.md)** - Quick deployment guide
- **[LINUX_SETUP.md](LINUX_SETUP.md)** - Detailed technical documentation

## 🔗 Dependencies

All scripts automatically handle:
- Python 3.8+ virtual environment
- Required Python packages (requests)
- Directory structure creation
- Permission setup

No manual dependency installation required!
