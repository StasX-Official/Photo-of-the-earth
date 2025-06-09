# 📚 Earth Image Downloader - Learning Guide

Welcome to the comprehensive learning guide for the Earth Image Downloader (eimg)! This tutorial will take you from beginner to advanced user.

## 📖 Table of Contents

1. [🚀 Getting Started](#-getting-started)
2. [🔐 Security & Encryption](#-security--encryption)
3. [📥 Basic Downloads](#-basic-downloads)
4. [📅 Working with Dates](#-working-with-dates)
5. [🔍 Understanding Metadata](#-understanding-metadata)
6. [🛠️ Advanced Usage](#️-advanced-usage)
7. [🤖 Automation & Scripting](#-automation--scripting)
8. [🔧 Troubleshooting](#-troubleshooting)
9. [🌍 Understanding NASA EPIC](#-understanding-nasa-epic)
10. [💡 Pro Tips & Best Practices](#-pro-tips--best-practices)

---

## 🚀 Getting Started

### Lesson 1: First-Time Setup

**Objective:** Get your environment ready and download your first Earth image.

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your NASA API key:**
   - Visit [https://api.nasa.gov/](https://api.nasa.gov/)
   - Fill out the simple form (takes 2 minutes)
   - Check your email for the API key
   - **It's completely free!**

3. **Set up your API key securely:**
   ```bash
   python main.py set API=your_nasa_api_key_here
   ```
   - You'll be prompted to create a master password
   - This encrypts your API key for security
   - Remember your master password!

4. **Test your setup:**
   ```bash
   python main.py validate
   ```

5. **Download your first Earth image:**
   ```bash
   python main.py download
   ```

**🎯 Exercise:** Download 3 Earth images and save them in a folder called "my_earth_collection"

<details>
<summary>💡 Solution</summary>

```bash
mkdir my_earth_collection
python main.py download --output ./my_earth_collection --filename earth_1.png
python main.py download --output ./my_earth_collection --filename earth_2.png
python main.py download --output ./my_earth_collection --filename earth_3.png
```
</details>

---

## 🔐 Security & Encryption

### Lesson 2: Understanding Security Features

**Objective:** Learn how your data is protected and master security commands.

#### Why Security Matters
- API keys are sensitive credentials
- Unencrypted storage is a security risk
- eimg protects your data with industry-standard encryption

#### Security Features in eimg:

1. **🔐 API Key Encryption:**
   - Uses AES-256 encryption via Fernet
   - Master password protection
   - PBKDF2 key derivation with 100,000 iterations

2. **🛡️ File Permissions:**
   - Config directory: 700 (owner only)
   - Config file: 600 (owner read/write only)
   - Windows: Uses NTFS permissions

3. **🔍 Integrity Verification:**
   - SHA-256 hashing of API keys
   - Detects tampering or corruption

#### Security Commands:

```bash
# Check security status
python main.py config

# Re-encrypt with new password
python main.py set API=your_key_here

# Securely wipe all data
python main.py wipe
```

**🎯 Exercise:** Set up encryption, check your config, then practice secure wiping and re-setup.

---

## 📥 Basic Downloads

### Lesson 3: Mastering Download Commands

**Objective:** Learn all the ways to download Earth images.

#### Download Latest Image:
```bash
# Basic download
python main.py download

# Custom location
python main.py download --output ./downloads

# Custom filename
python main.py download --filename "earth_$(date +%Y%m%d).png"

# Both custom location and filename
python main.py download --output ./images --filename today_earth.png
```

#### Understanding File Naming:
- Default: `earth_YYYYMMDD_HHMMSS.png`
- Always use `.png` extension
- Avoid special characters in filenames

**🎯 Exercise:** Create a folder structure like this and download images:
```
earth_archive/
├── 2025/
│   ├── january/
│   └── february/
└── latest/
```

<details>
<summary>💡 Solution</summary>

```bash
mkdir -p earth_archive/2025/january
mkdir -p earth_archive/2025/february
mkdir -p earth_archive/latest

python main.py download --output ./earth_archive/latest
python main.py download --output ./earth_archive/2025/january --filename jan_earth.png
```
</details>

---

## 📅 Working with Dates

### Lesson 4: Date-Specific Downloads

**Objective:** Master downloading images from specific dates and understanding date availability.

#### Check Available Dates:
```bash
python main.py dates
```

#### Download Specific Date:
```bash
# Download image from January 15, 2025
python main.py download-date 2025-01-15

# With custom location
python main.py download-date 2025-01-15 --output ./historical
```

#### Date Format Rules:
- Format: `YYYY-MM-DD`
- Example: `2025-01-15` (January 15, 2025)
- Only dates with available images work

#### Understanding Date Availability:
- Images typically available 1-2 days after capture
- Some dates may not have images due to:
  - Satellite maintenance
  - Technical issues
  - Data processing delays

**🎯 Exercise:** Create a "this week" collection with images from the last 7 available dates.

<details>
<summary>💡 Solution</summary>

```bash
mkdir this_week
python main.py dates  # Note the available dates
# Then download from recent dates:
python main.py download-date 2025-01-14 --output ./this_week --filename day1.png
python main.py download-date 2025-01-13 --output ./this_week --filename day2.png
# Continue for more dates...
```
</details>

---

## 🔍 Understanding Metadata

### Lesson 5: Working with Image Metadata

**Objective:** Learn to extract and interpret image metadata.

#### View Latest Metadata:
```bash
python main.py metadata
```

#### View Specific Date Metadata:
```bash
python main.py metadata 2025-01-15
```

#### Understanding Metadata Fields:

1. **📝 Identifier:** Unique image ID
2. **📅 Date:** Capture timestamp (UTC)
3. **🌍 Caption:** Brief description
4. **🎯 Coordinates:** Earth center point (lat/lon)
5. **🛰️ Satellite Position:** DSCOVR spacecraft location

#### Metadata Example:
```
🖼️  Image 1:
   📝 Identifier: 20250115133633
   📅 Date: 2025-01-15 13:36:33
   🌍 Caption: This image was taken by NASA's EPIC camera onboard the NOAA DSCOVR spacecraft
   🎯 Coordinates: 12.34, -67.89
   🛰️ Satellite position: x=1234567, y=-987654, z=543210
```

**🎯 Exercise:** Compare metadata from 3 different dates and note the differences in coordinates and satellite position.

---

## 🛠️ Advanced Usage

### Lesson 6: Power User Techniques

**Objective:** Learn advanced techniques for efficient image management.

#### Batch Processing with Shell Scripts:

**Linux/macOS:**
```bash
#!/bin/bash
# download_batch.sh

dates=(2025-01-10 2025-01-11 2025-01-12 2025-01-13)
output_dir="./batch_download"

mkdir -p "$output_dir"

for date in "${dates[@]}"; do
    echo "Downloading $date..."
    python main.py download-date "$date" --output "$output_dir" --filename "earth_$date.png"
    sleep 2  # Be nice to NASA's servers
done

echo "Batch download complete!"
```

**Windows PowerShell:**
```powershell
# download_batch.ps1

$dates = @("2025-01-10", "2025-01-11", "2025-01-12", "2025-01-13")
$outputDir = "./batch_download"

New-Item -ItemType Directory -Path $outputDir -Force

foreach ($date in $dates) {
    Write-Host "Downloading $date..."
    python main.py download-date $date --output $outputDir --filename "earth_$date.png"
    Start-Sleep 2
}

Write-Host "Batch download complete!"
```

#### Organized Directory Structure:
```bash
# Create organized structure
python main.py download --output "./earth_images/$(date +%Y)/$(date +%m)/daily"
```

**🎯 Exercise:** Create a script that downloads the last 5 available images and organizes them by year and month.

---

## 🤖 Automation & Scripting

### Lesson 7: Automating Downloads

**Objective:** Set up automated daily downloads.

#### Cron Job Setup (Linux/macOS):

1. **Edit crontab:**
   ```bash
   crontab -e
   ```

2. **Add daily download at 10 AM:**
   ```bash
   0 10 * * * cd /path/to/eimg && python main.py download --output ./daily_earth
   ```

3. **Add weekly cleanup:**
   ```bash
   0 0 * * 0 find /path/to/eimg/daily_earth -name "*.png" -mtime +30 -delete
   ```

#### Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 10:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `main.py download --output ./daily_earth`
7. Start in: `C:\path\to\eimg`

#### Python Automation Script:
```python
#!/usr/bin/env python3
# auto_download.py

import os
import sys
import subprocess
from datetime import datetime, timedelta

def auto_download():
    """Automated download with error handling"""
    try:
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d")
        output_dir = f"./auto_downloads/{timestamp}"
        
        # Run download
        result = subprocess.run([
            sys.executable, "main.py", "download",
            "--output", output_dir,
            "--filename", f"earth_{timestamp}.png"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Auto-download successful: {output_dir}")
        else:
            print(f"❌ Auto-download failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Auto-download error: {e}")

if __name__ == "__main__":
    auto_download()
```

**🎯 Exercise:** Set up an automated download that runs every day and keeps only the last 10 images.

---

## 🔧 Troubleshooting

### Lesson 8: Solving Common Issues

**Objective:** Diagnose and fix common problems.

#### Diagnostic Commands:
```bash
# Check overall status
python main.py config

# Validate API key
python main.py validate

# Check available dates
python main.py dates

# Test network connectivity
ping epic.gsfc.nasa.gov
```

#### Common Issues & Solutions:

1. **❌ "No API key set"**
   ```bash
   # Solution:
   python main.py set API=your_key_here
   ```

2. **❌ "Failed to decrypt API key"**
   ```bash
   # You forgot your master password
   # Solution: Wipe and re-set
   python main.py wipe
   python main.py set API=your_key_here
   ```

3. **❌ "Network error"**
   ```bash
   # Check internet connection
   ping google.com
   
   # Try with different DNS
   nslookup epic.gsfc.nasa.gov 8.8.8.8
   ```

4. **❌ "Permission denied"**
   ```bash
   # Linux/macOS: Fix permissions
   chmod 755 /path/to/output/directory
   
   # Windows: Run as administrator or check folder permissions
   ```

5. **❌ "No images available for date"**
   ```bash
   # Check what dates are available
   python main.py dates
   ```

**🎯 Exercise:** Intentionally break your setup (wrong API key, bad permissions) and practice fixing each issue.

---

## 🌍 Understanding NASA EPIC

### Lesson 9: The Science Behind the Images

**Objective:** Understand the technology and science behind EPIC images.

#### DSCOVR Mission:
- **Launch:** February 11, 2015
- **Location:** L1 Lagrange point (1.5 million km from Earth)
- **Purpose:** Solar wind monitoring and Earth observation

#### EPIC Camera Specifications:
- **Spectral Channels:** 10 (317.5nm to 779.5nm)
- **Resolution:** 2048×2048 pixels
- **Field of View:** 0.62°
- **Earth Angular Size:** ~0.5°

#### Image Processing:
1. **Raw Data:** 10 spectral channels captured
2. **Color Composition:** RGB channels (red: 680nm, green: 551nm, blue: 443nm)
3. **Geometric Correction:** Account for Earth's rotation
4. **Radiometric Calibration:** Ensure color accuracy

#### What You're Seeing:
- **Clouds:** Water vapor and ice crystals
- **Land:** Vegetation (green), deserts (brown), ice (white)
- **Oceans:** Deep blue water
- **Atmosphere:** Thin blue haze around Earth's edge

#### Unique Phenomena to Look For:
- **Lunar Transits:** Moon passing in front of Earth
- **Aurora:** Green glow at poles (rare but possible)
- **Seasonal Changes:** Ice coverage, vegetation patterns
- **Weather Systems:** Hurricanes, cyclones, storm fronts

**🎯 Exercise:** Download images from different seasons and compare vegetation patterns between summer and winter.

---

## 💡 Pro Tips & Best Practices

### Lesson 10: Expert Techniques

**Objective:** Master advanced techniques and best practices.

#### Performance Optimization:

1. **Batch Downloads:**
   ```bash
   # Add delays to be respectful to NASA servers
   python main.py download-date 2025-01-15
   sleep 5
   python main.py download-date 2025-01-14
   ```

2. **Storage Management:**
   ```bash
   # Compress old images
   find ./earth_images -name "*.png" -mtime +30 -exec gzip {} \;
   
   # Create thumbnails for previews
   mogrify -resize 256x256 -quality 80 -format jpg ./earth_images/*.png
   ```

3. **Network Optimization:**
   - Use wired connection for large downloads
   - Avoid peak hours (US business hours)
   - Consider using a download manager for very large batches

#### Quality Control:

1. **Verify Downloads:**
   ```bash
   # Check file sizes (should be ~1-3 MB)
   ls -lh ./earth_images/*.png
   
   # Check for corruption
   file ./earth_images/*.png
   ```

2. **Metadata Validation:**
   ```bash
   # Compare timestamps with expected dates
   python main.py metadata 2025-01-15
   ```

#### Advanced Organization:

1. **Smart Naming:**
   ```bash
   # Include metadata in filename
   python main.py download --filename "earth_$(date +%Y%m%d)_UTC.png"
   ```

2. **Database Catalog:**
   ```python
   # Create a simple catalog
   import json
   from datetime import datetime
   
   catalog = {
       "downloaded": datetime.now().isoformat(),
       "images": [
           {"date": "2025-01-15", "filename": "earth_20250115.png", "size_mb": 2.3},
           {"date": "2025-01-14", "filename": "earth_20250114.png", "size_mb": 2.1}
       ]
   }
   
   with open("catalog.json", "w") as f:
       json.dump(catalog, f, indent=2)
   ```

#### Security Best Practices:

1. **Regular Backups:**
   ```bash
   # Backup your config (encrypted)
   cp ~/.eimg/config.json ~/.eimg/config.backup.json
   ```

2. **Master Password Management:**
   - Use a strong, unique password
   - Consider a password manager
   - Never share your master password

3. **Regular Security Checks:**
   ```bash
   # Check file permissions regularly
   python main.py config
   ```

#### Creative Uses:

1. **Time-lapse Creation:**
   ```bash
   # Download sequential images
   for i in {01..15}; do
       python main.py download-date "2025-01-$i" --filename "frame_$i.png"
   done
   
   # Create video with ffmpeg
   ffmpeg -r 2 -i frame_%02d.png -vcodec libx264 earth_timelapse.mp4
   ```

2. **Seasonal Comparison:**
   ```bash
   # Download same date from different years
   python main.py download-date 2024-06-21 --filename summer_2024.png
   python main.py download-date 2024-12-21 --filename winter_2024.png
   ```

3. **Educational Projects:**
   - Weather pattern analysis
   - Seasonal change documentation
   - Climate visualization
   - Astronomy education

**🎯 Final Exercise:** Create a complete Earth monitoring system that downloads daily images, organizes them by month, creates weekly summaries, and maintains a searchable catalog.

---

## 🏆 Graduation Project

Congratulations on completing the learning guide! For your final project, create an advanced Earth monitoring system that includes:

1. **Automated daily downloads** with error recovery
2. **Intelligent storage management** with compression
3. **Metadata database** for searching images
4. **Web interface** to browse your collection
5. **Alert system** for interesting phenomena
6. **Backup and synchronization** across devices

### Example Project Structure:
```
earth_monitor/
├── config/
│   ├── settings.json
│   └── credentials.encrypted
├── data/
│   ├── images/
│   │   ├── 2025/
│   │   │   ├── 01/
│   │   │   └── 02/
│   │   └── metadata.db
│   └── thumbnails/
├── scripts/
│   ├── auto_download.py
│   ├── cleanup.py
│   └── web_server.py
├── logs/
│   └── earth_monitor.log
└── web/
    ├── index.html
    ├── viewer.js
    └── styles.css
```

Share your completed project and inspire others to explore our beautiful planet! 🌍✨

---

**Happy learning and Earth watching! 🚀**

*Remember: Every image you download captures a unique moment in Earth's history. You're not just collecting pictures – you're preserving memories of our living planet!*
