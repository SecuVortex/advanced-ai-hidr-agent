# 🚀 Quick Start Guide

Get HIDR up and running in 5 minutes!

## Step 1: Clone & Install

```bash
git clone https://github.com/yourusername/hidr-system.git
cd hidr-system
pip install -r requirements.txt
```

## Step 2: Configure (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys (optional)
# MalwareBazaar: https://bazaar.abuse.ch/api/
# VirusTotal: https://www.virustotal.com/gui/my-apikey
```

## Step 3: Run

```bash
# Windows (Run as Administrator)
python production_gui.py

# Linux/Mac
sudo python production_gui.py
```

## Step 4: First Scan

1. Click **Processes** tab
2. Click **Start Scan**
3. View results in real-time

## Step 5: Configure Trusted Paths (Recommended)

1. Go to **Settings** tab
2. Scroll to **Trusted Paths**
3. Click **Add Path** and select directories with legitimate software
4. Click **Save Settings**

## That's it! 🎉

Your system is now protected by HIDR.

### Next Steps

- **Reports Tab**: View statistics and export reports
- **Settings Tab**: Adjust thresholds and add API keys
- **Auto-Scan**: Enable periodic scanning (Settings → Auto-Scan)

### Need Help?

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/Secuvortex/hidr-system/issues)
- 📧 Email: secuvortex@gmail.com
