# 🌍 Earth Image Downloader (eimg)

A powerful command-line tool to download stunning Earth images from NASA's EPIC (Earth Polychromatic Imaging Camera) API. Get daily full-disk images of our beautiful planet directly to your computer!

![Earth from EPIC](https://epic.gsfc.nasa.gov/archive/natural/2024/12/15/png/epic_1b_20241215013633.png)

## 🌟 Features

- 📥 **Download latest Earth images** from NASA EPIC
- 📅 **Download images by specific date** (YYYY-MM-DD format)
- 🔍 **View available image dates** and metadata
- 🔑 **Secure API key management** with validation
- 📊 **Progress tracking** during downloads
- 🛠️ **Comprehensive error handling** and user feedback
- 📁 **Configurable output** directory and filename
- 🎨 **Beautiful console output** with emojis and colors
- 🔧 **Cross-platform support** (Windows, macOS, Linux)

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.6 or higher
- Internet connection
- Free NASA API key

### 2. Installation

1. **Clone or download** this repository
2. **Install dependencies:**
   ```bash
   pip install requests
   ```

### 3. Get NASA API Key (FREE!)

1. Visit [NASA API Portal](https://api.nasa.gov/)
2. Click "Get Started" and fill out the simple form
3. Check your email for the API key
4. **No credit card required - it's completely free!**

### 4. Set up your API key

```bash
python main.py set API=your_nasa_api_key_here
```

### 5. Download your first Earth image!

```bash
python main.py download
```

## 📖 Commands Reference

### 🔑 API Key Management

```bash
# Set your NASA API key
python main.py set API=your_api_key_here

# Validate your API key
python main.py validate

# Show current configuration
python main.py config
```

### 📥 Downloading Images

```bash
# Download latest Earth image
python main.py download

# Download to specific directory
python main.py download --output ./my_earth_images

# Download with custom filename
python main.py download --filename my_earth.png

# Download image for specific date
python main.py download-date 2025-01-15

# Download specific date to custom location
python main.py download-date 2025-01-15 --output ./images --filename earth_jan15.png
```

### 📊 Information Commands

```bash
# Show available image dates
python main.py dates

# Show metadata for latest image
python main.py metadata

# Show metadata for specific date
python main.py metadata 2025-01-15

# Show help
python main.py help

# Show version
python main.py version
```

## 🛠️ Advanced Usage

### Custom Output Directory Structure

```bash
# Create organized folders
python main.py download --output "./earth_images/$(date +%Y)/$(date +%m)"
```

### Batch Download Script

Create a script to download multiple days:

```bash
#!/bin/bash
for date in 2025-01-01 2025-01-02 2025-01-03; do
    python main.py download-date $date --output "./batch_download"
    sleep 2  # Be nice to NASA's servers
done
```

### Automated Daily Download

Set up a cron job (Linux/macOS) or Task Scheduler (Windows):

```bash
# Add to crontab for daily download at 10 AM
0 10 * * * cd /path/to/eimg && python main.py download --output ./daily_earth
```

## 🔧 Configuration

The tool stores configuration in your home directory:
- **Windows:** `C:\Users\YourName\.eimg\config.json`
- **macOS/Linux:** `~/.eimg/config.json`

Example configuration:
```json
{
  "api_key": "your_nasa_api_key",
  "default_output": "./earth_images",
  "last_download": "2025-01-15"
}
```

## 🔍 Understanding EPIC Data

### What is EPIC?

EPIC (Earth Polychromatic Imaging Camera) is a 10-channel spectroradiometer aboard the DSCOVR (Deep Space Climate Observatory) spacecraft. It provides:

- **Full-disk Earth images** from ~1.5 million km away
- **Daily coverage** (usually 13-22 images per day)
- **Natural color images** showing Earth's atmosphere, land, and oceans
- **Real-time monitoring** of Earth's rotation and seasonal changes

### Image Details

- **Resolution:** ~2048x2048 pixels
- **Format:** PNG
- **Color:** Natural color (RGB)
- **Coverage:** Full Earth disk
- **Frequency:** Multiple times daily
- **Latency:** 1-2 days typical delay

### Metadata Information

Each image includes:
- **Timestamp:** When the image was captured
- **Sun/Moon positions:** Celestial coordinates
- **Satellite position:** DSCOVR spacecraft location
- **Earth coordinates:** Center point of the image
- **Rotation info:** Earth's rotation at capture time

## 🆘 Troubleshooting

### Common Issues and Solutions

#### ❌ "No API key set"
```bash
# Solution: Set your NASA API key
python main.py set API=your_key_here
python main.py validate
```

#### ❌ "Network error" / "Connection timeout"
- Check your internet connection
- Try again later (NASA servers might be busy)
- Use a VPN if you're behind a firewall

#### ❌ "No images available for date"
```bash
# Check which dates have images available
python main.py dates
```

#### ❌ "Invalid API key"
- Double-check your API key
- Generate a new one at [NASA API Portal](https://api.nasa.gov/)
- Make sure there are no extra spaces

#### ❌ "Permission denied" writing files
- Check directory permissions
- Use absolute paths
- Run with appropriate permissions

#### ❌ "File size is 0 bytes"
- The image might not be available yet
- Try a different date
- Check your internet connection

### Getting Help

1. **Run diagnostics:**
   ```bash
   python main.py config
   python main.py validate
   python main.py dates
   ```

2. **Check for updates:** Make sure you have the latest version

3. **Report issues:** Include error messages and your operating system

## 🌐 NASA EPIC Resources

- **EPIC Website:** https://epic.gsfc.nasa.gov/
- **API Documentation:** https://epic.gsfc.nasa.gov/about/api
- **NASA API Portal:** https://api.nasa.gov/
- **DSCOVR Mission:** https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/dscovr-deep-space-climate-observatory

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs** with detailed information
2. **Suggest features** that would be useful
3. **Submit pull requests** with improvements
4. **Share your awesome Earth images** downloaded with this tool!

## 📜 License

```
MIT License

Copyright (c) 2025 Kozosvyst Stas (STASX)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- **NASA** for providing the amazing EPIC API and Earth imagery
- **NOAA/DSCOVR** team for the incredible satellite mission
- **Python community** for excellent libraries
- **All contributors** who help improve this tool

## 📊 Fun Facts

- DSCOVR orbits the L1 Lagrange point between Earth and the Sun
- EPIC takes a new image approximately every 65-110 minutes
- Each image shows about 12 hours of Earth's rotation
- The spacecraft sees Earth's "dark side" during eclipses
- EPIC can capture amazing phenomena like lunar transits across Earth!

---

**Made with 💚 for Earth lovers everywhere**

*Explore our beautiful planet, one image at a time! 🌍*

Happy Earth watching! 🌍✨
