#!/usr/bin/env python3
"""
Earth Image Downloader (eimg)
A command-line tool to download Earth images from NASA's EPIC API

Copyright (c) 2025 Kozosvyst Stas (STASX)
Licensed under MIT License
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
import hashlib
import base64
import getpass
import secrets
import logging
import subprocess
import platform

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  Warning: cryptography library not installed. API encryption disabled.")
    print("Install with: pip install cryptography")

__version__ = "0.0.2"
__author__ = "Kozosvyst Stas (STASX)"

CONFIG_DIR = Path.home() / ".eimg"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEY_FILE = CONFIG_DIR / ".key"
LOGS_DIR = Path(__file__).parent / "logs"
CACHE_DIR = Path(__file__).parent / "cache"

class LogManager:
    """Manage application logging"""
    
    def __init__(self):
        self.logger = None
        self.error_logger = None
        self.status_logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            LOGS_DIR.mkdir(exist_ok=True)
        
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)
            
            logging.basicConfig(
                level=logging.INFO,
                format=log_format,
                handlers=[
                    logging.FileHandler(LOGS_DIR / "eimg.log", encoding='utf-8'),
                ],
                force=True
            )
            
            self.logger = logging.getLogger('eimg')
            self.error_logger = logging.getLogger('eimg.errors')
            self.status_logger = logging.getLogger('eimg.status')
            
            self.error_logger.propagate = False
            self.status_logger.propagate = False
            
            error_handler = logging.FileHandler(LOGS_DIR / "errors.log", encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(logging.Formatter(log_format))
            self.error_logger.addHandler(error_handler)
            
            status_handler = logging.FileHandler(LOGS_DIR / "status.log", encoding='utf-8')
            status_handler.setLevel(logging.INFO)
            status_handler.setFormatter(logging.Formatter(log_format))
            self.status_logger.addHandler(status_handler)
            
            self.logger.info("Logging system initialized")
            
        except Exception as e:
            print(f"❌ Failed to setup logging: {e}")
    
    def log_error(self, message, exception=None):
        """Log error message"""
        try:
            if self.error_logger:
                if exception:
                    self.error_logger.error(f"{message}: {exception}", exc_info=True)
                else:
                    self.error_logger.error(message)
        except Exception:
            pass
    
    def log_status(self, message):
        """Log status message"""
        try:
            if self.status_logger:
                self.status_logger.info(message)
        except Exception:
            pass
    
    def log_info(self, message):
        """Log info message"""
        try:
            if self.logger:
                self.logger.info(message)
        except Exception:
            pass

class CacheManager:
    """Manage image cache"""
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
        self.setup_cache()
    
    def setup_cache(self):
        """Setup cache directory structure"""
        try:
            CACHE_DIR.mkdir(exist_ok=True)
            (CACHE_DIR / "images").mkdir(exist_ok=True)
            (CACHE_DIR / "metadata").mkdir(exist_ok=True)
            (CACHE_DIR / "thumbnails").mkdir(exist_ok=True)
            
            if self.log_manager:
                self.log_manager.log_info("Cache directory structure created")
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to setup cache", e)
    
    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            stats = {
                'images': 0,
                'total_size': 0,
                'metadata_files': 0,
                'thumbnails': 0
            }
            
            images_dir = CACHE_DIR / "images"
            if images_dir.exists():
                for file in images_dir.glob("*.png"):
                    try:
                        stats['images'] += 1
                        stats['total_size'] += file.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
            
            metadata_dir = CACHE_DIR / "metadata"
            if metadata_dir.exists():
                stats['metadata_files'] = len(list(metadata_dir.glob("*.json")))
            
            thumbnails_dir = CACHE_DIR / "thumbnails"
            if thumbnails_dir.exists():
                stats['thumbnails'] = len(list(thumbnails_dir.glob("*.jpg")))
            
            return stats
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to get cache stats", e)
            return {}
    
    def clear_cache(self, cache_type="all"):
        """Clear cache"""
        try:
            cleared = 0
            
            if cache_type in ["all", "images"]:
                images_dir = CACHE_DIR / "images"
                if images_dir.exists():
                    for file in images_dir.glob("*.png"):
                        try:
                            file.unlink()
                            cleared += 1
                        except (OSError, FileNotFoundError):
                            continue
            
            if cache_type in ["all", "metadata"]:
                metadata_dir = CACHE_DIR / "metadata"
                if metadata_dir.exists():
                    for file in metadata_dir.glob("*.json"):
                        try:
                            file.unlink()
                            cleared += 1
                        except (OSError, FileNotFoundError):
                            continue
            
            if cache_type in ["all", "thumbnails"]:
                thumbnails_dir = CACHE_DIR / "thumbnails"
                if thumbnails_dir.exists():
                    for file in thumbnails_dir.glob("*.jpg"):
                        try:
                            file.unlink()
                            cleared += 1
                        except (OSError, FileNotFoundError):
                            continue
            
            if self.log_manager:
                self.log_manager.log_status(f"Cache cleared: {cleared} files removed")
            return cleared
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to clear cache", e)
            return 0
    
    def save_image_to_cache(self, image_data, filename, metadata=None):
        """Save image to cache"""
        try:
            if not image_data or not filename:
                return None
                
            cache_path = CACHE_DIR / "images" / filename
            with open(cache_path, 'wb') as f:
                f.write(image_data)
            
            if metadata:
                metadata_path = CACHE_DIR / "metadata" / f"{filename}.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            if self.log_manager:
                self.log_manager.log_info(f"Image cached: {filename}")
            return cache_path
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to save image to cache", e)
            return None

class SecurityManager:
    """Handle encryption and security operations"""
    
    def __init__(self):
        self.salt = b'eimg_salt_2025_stasx'
        self.crypto_available = CRYPTO_AVAILABLE
    
    def _generate_key(self, password: str) -> bytes:
        """Generate encryption key from password"""
        if not self.crypto_available:
            print("❌ Cryptography not available")
            return None
            
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
        except Exception as e:
            print(f"❌ Error generating encryption key: {e}")
            return None
    
    def encrypt_data(self, data: str, password: str) -> str:
        """Encrypt sensitive data"""
        if not self.crypto_available:
            print("❌ Encryption not available - cryptography library not installed")
            return None
            
        try:
            if not data or not password:
                return None
                
            key = self._generate_key(password)
            if not key:
                return None
            
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            return None
    
    def decrypt_data(self, encrypted_data: str, password: str) -> str:
        """Decrypt sensitive data"""
        if not self.crypto_available:
            print("❌ Decryption not available - cryptography library not installed")
            return None
            
        try:
            if not encrypted_data or not password:
                return None
                
            key = self._generate_key(password)
            if not key:
                return None
            
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = f.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            return None
    
    def hash_string(self, data: str) -> str:
        """Create SHA256 hash of string"""
        try:
            if not data:
                return None
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            print(f"❌ Hashing error: {e}")
            return None
    
    def validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format"""
        try:
            if not api_key:
                return False
                
            if len(api_key.strip()) < 20:
                return False
            
            cleaned_key = api_key.replace('-', '').replace('_', '')
            return cleaned_key.isalnum()
        except Exception:
            return False

class EarthImageDownloader:
    def __init__(self):
        try:
            self.log_manager = LogManager()
            self.cache_manager = CacheManager(self.log_manager)
            self.security = SecurityManager()
            self.config = self.load_config()
            self._master_password = None
            
            if self.log_manager:
                self.log_manager.log_info("EarthImageDownloader initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize: {e}")
            self.config = {}
            self.log_manager = None
            self.cache_manager = None
            self.security = SecurityManager()
    
    def _get_master_password(self, confirm=False):
        """Get master password for encryption"""
        try:
            if self._master_password:
                return self._master_password
            
            if confirm:
                print("🔐 Set master password for API key encryption:")
                password = getpass.getpass("Enter master password: ")
                confirm_password = getpass.getpass("Confirm master password: ")
                
                if password != confirm_password:
                    print("❌ Passwords don't match!")
                    return None
                
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long!")
                    return None
            else:
                print("🔐 Enter master password to decrypt API key:")
                password = getpass.getpass("Master password: ")
            
            self._master_password = password
            return password
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return None
        except Exception as e:
            print(f"❌ Error getting password: {e}")
            return None
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Invalid config file format: {e}")
            return {}
        except PermissionError:
            print(f"❌ Error: No permission to read config file: {CONFIG_FILE}")
            return {}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}
    
    def save_config(self):
        """Save configuration to file with proper permissions"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            if os.name != 'nt':
                try:
                    os.chmod(CONFIG_DIR, 0o700)
                except OSError:
                    pass
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            if os.name != 'nt':
                try:
                    os.chmod(CONFIG_FILE, 0o600)
                except OSError:
                    pass
            
            return True
        except PermissionError:
            print(f"❌ Error: No permission to write config file: {CONFIG_FILE}")
            return False
        except OSError as e:
            print(f"❌ Error: Could not create config directory: {e}")
            return False
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def set_api_key(self, api_key):
        """Set NASA API key with encryption"""
        try:
            if not self.security.validate_api_key_format(api_key):
                print("❌ Error: Invalid API key format. Please check your NASA API key.")
                return False
            
            if not CRYPTO_AVAILABLE:
                print("⚠️  Warning: Storing API key without encryption (cryptography not available)")
                self.config['api_key'] = api_key.strip()
                if self.save_config():
                    print(f"✅ API key saved to {CONFIG_FILE}")
                    return True
                return False
            
            master_password = self._get_master_password(confirm=True)
            if not master_password:
                return False
            
            encrypted_key = self.security.encrypt_data(api_key.strip(), master_password)
            if not encrypted_key:
                print("❌ Error: Failed to encrypt API key")
                return False
            
            self.config['encrypted_api_key'] = encrypted_key
            self.config['key_hash'] = self.security.hash_string(api_key.strip())
            self.config['encryption_version'] = '1.0'
            
            if 'api_key' in self.config:
                del self.config['api_key']
            
            if self.save_config():
                print(f"✅ Encrypted API key saved to {CONFIG_FILE}")
                print("🔐 Your API key is now encrypted and secure!")
                return True
            return False
            
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error setting API key", e)
            print(f"❌ Error setting API key: {e}")
            return False
    
    def get_api_key(self):
        """Get decrypted NASA API key"""
        try:
            if 'api_key' in self.config and 'encrypted_api_key' not in self.config:
                if not CRYPTO_AVAILABLE:
                    return self.config.get('api_key', '')
                print("⚠️  Warning: Unencrypted API key detected. Please re-set your API key for security.")
                return self.config.get('api_key', '')
            
            encrypted_key = self.config.get('encrypted_api_key')
            if not encrypted_key:
                return ''
            
            if not CRYPTO_AVAILABLE:
                print("❌ Cannot decrypt API key - cryptography library not available")
                return ''
            
            master_password = self._get_master_password()
            if not master_password:
                return ''
            
            decrypted_key = self.security.decrypt_data(encrypted_key, master_password)
            if not decrypted_key:
                print("❌ Error: Failed to decrypt API key. Check your master password.")
                return ''

            key_hash = self.security.hash_string(decrypted_key)
            stored_hash = self.config.get('key_hash')
            
            if key_hash != stored_hash:
                print("❌ Error: API key integrity check failed!")
                return ''
            
            return decrypted_key
            
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error getting API key", e)
            print(f"❌ Error getting API key: {e}")
            return ''
    
    def validate_api_key(self):
        """Validate API key by making a test request"""
        try:
            api_key = self.get_api_key()
            if not api_key:
                print("❌ No API key available for validation")
                return False
            
            print("🔑 Validating API key...")
            url = f"https://api.nasa.gov/EPIC/api/natural/images?api_key={api_key}"

            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            
            if response.status_code == 200:
                print("✅ API key is valid and working!")
                return True
            elif response.status_code == 403:
                print("❌ API key is invalid, expired, or rate limited")
                return False
            else:
                print(f"⚠️  API returned status code: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            if self.log_manager:
                self.log_manager.log_error("Network error during validation", e)
            print(f"❌ Network error during validation: {e}")
            return False
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error validating API key", e)
            print(f"❌ Error validating API key: {e}")
            return False
    
    def wipe_config(self):
        """Securely wipe configuration"""
        try:
            print("🗑️  Are you sure you want to wipe all configuration? (y/N): ", end='')
            confirm = input().strip().lower()
            
            if confirm != 'y':
                print("❌ Operation cancelled")
                return False
            
            if CONFIG_FILE.exists():
                try:
                    file_size = CONFIG_FILE.stat().st_size
                    if file_size > 0:
                        with open(CONFIG_FILE, 'wb') as f:
                            f.write(secrets.token_bytes(max(file_size, 1024)))
                            f.flush()
                            os.fsync(f.fileno())
                    
                    CONFIG_FILE.unlink()
                except Exception as e:
                    print(f"⚠️  Warning: Could not securely wipe file: {e}")
                    CONFIG_FILE.unlink()
            
            self.config = {}
            self._master_password = None
            
            print("✅ Configuration securely wiped")
            return True
            
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error wiping config", e)
            print(f"❌ Error wiping config: {e}")
            return False
    
    def get_available_dates(self, limit=10):
        """Get list of available image dates"""
        api_key = self.get_api_key()
        if not api_key:
            print("❌ Error: No API key set. Use 'python main.py set API=your_key_here'")
            return []
        
        try:
            print("📅 Fetching available dates...")
            url = f"https://api.nasa.gov/EPIC/api/natural/available?api_key={api_key}"
            
            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            dates = response.json()
            
            if not dates:
                print("❌ No dates available")
                return []
            
            print(f"📊 Found {len(dates)} available dates")
            for i, date in enumerate(dates[:limit]):
                print(f"   {i+1}. {date}")
            
            if len(dates) > limit:
                print(f"   ... and {len(dates) - limit} more")
            
            return dates
            
        except requests.HTTPError as e:
            if self.log_manager:
                self.log_manager.log_error("HTTP error getting dates", e)
            print(f"❌ HTTP error: {e}")
            return []
        except requests.RequestException as e:
            if self.log_manager:
                self.log_manager.log_error("Network error getting dates", e)
            print(f"❌ Network error: {e}")
            return []
        except json.JSONDecodeError:
            print("❌ Error: Invalid response format from API")
            return []
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Unexpected error getting dates", e)
            print(f"❌ Unexpected error: {e}")
            return []
    
    def show_metadata(self, date=None):
        """Show metadata for images"""
        api_key = self.get_api_key()
        if not api_key:
            print("❌ Error: No API key set. Use 'python main.py set API=your_key_here'")
            return False
        
        try:
            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'application/json'
            }
            
            if date:
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    print("❌ Error: Invalid date format. Use YYYY-MM-DD")
                    return False
                    
                url = f"https://api.nasa.gov/EPIC/api/natural/date/{date}?api_key={api_key}"
                print(f"📋 Metadata for {date}:")
            else:
                url = f"https://api.nasa.gov/EPIC/api/natural/images?api_key={api_key}"
                print("📋 Latest image metadata:")
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print("❌ No metadata available")
                return False
            
            for i, item in enumerate(data[:3]):
                print(f"\n🖼️  Image {i+1}:")
                print(f"   📝 Identifier: {item.get('identifier', 'N/A')}")
                print(f"   📅 Date: {item.get('date', 'N/A')}")
                print(f"   🌍 Caption: {item.get('caption', 'N/A')}")
                if 'centroid_coordinates' in item:
                    coords = item['centroid_coordinates']
                    print(f"   🎯 Coordinates: {coords.get('lat', 'N/A')}, {coords.get('lon', 'N/A')}")
                if 'dscovr_j2000_position' in item:
                    pos = item['dscovr_j2000_position']
                    print(f"   🛰️  Satellite position: x={pos.get('x', 'N/A')}, y={pos.get('y', 'N/A')}, z={pos.get('z', 'N/A')}")
            
            return True
            
        except requests.RequestException as e:
            if self.log_manager:
                self.log_manager.log_error("Network error fetching metadata", e)
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error fetching metadata", e)
            print(f"❌ Error fetching metadata: {e}")
            return False
    
    def download_by_date(self, date, output_dir='.', filename=None):
        """Download Earth image for specific date (YYYY-MM-DD format)"""
        api_key = self.get_api_key()
        if not api_key:
            print("❌ Error: No API key set. Use 'python main.py set API=your_key_here'")
            return False
        
        try:
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                print("❌ Error: Invalid date format. Use YYYY-MM-DD")
                return False
            
            print(f"🌍 Fetching Earth image for {date}...")
            url = f"https://api.nasa.gov/EPIC/api/natural/date/{date}?api_key={api_key}"
            
            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print(f"❌ No images available for {date}")
                return False
            
            image_data = data[0]
            image_name = image_data['image']
            date_formatted = date.replace('-', '/')
            image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date_formatted}/png/{image_name}.png"
            
            return self._download_image(image_url, image_name, image_data['date'], output_dir, filename)
            
        except requests.HTTPError as e:
            if "404" in str(e):
                print(f"❌ No images found for date {date}")
            else:
                if self.log_manager:
                    self.log_manager.log_error("HTTP error downloading by date", e)
                print(f"❌ HTTP error: {e}")
            return False
        except requests.RequestException as e:
            if self.log_manager:
                self.log_manager.log_error("Network error downloading by date", e)
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Unexpected error downloading by date", e)
            print(f"❌ Unexpected error: {e}")
            return False
    
    def download_latest(self, output_dir='.', filename=None):
        """Download latest Earth image"""
        api_key = self.get_api_key()
        if not api_key:
            print("❌ Error: No API key set. Use 'python main.py set API=your_key_here'")
            return False
        
        try:
            print("🌍 Fetching latest Earth image metadata...")
            url = f"https://api.nasa.gov/EPIC/api/natural/images?api_key={api_key}"
            
            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print("❌ No images available")
                return False
            
            image_data = data[0]
            image_name = image_data['image']
            date = image_data['date'].split()[0].replace('-', '/')
            image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{date}/png/{image_name}.png"
            
            return self._download_image(image_url, image_name, image_data['date'], output_dir, filename)
            
        except requests.HTTPError as e:
            if self.log_manager:
                self.log_manager.log_error("HTTP error downloading latest", e)
            print(f"❌ HTTP error: {e}")
            return False
        except requests.RequestException as e:
            if self.log_manager:
                self.log_manager.log_error("Network error downloading latest", e)
            print(f"❌ Network error: {e}")
            return False
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Unexpected error downloading latest", e)
            print(f"❌ Unexpected error: {e}")
            return False
    
    def _download_image(self, image_url, image_name, date_str, output_dir='.', filename=None, save_to_cache=True):
        """Helper method to download and save image"""
        try:
            if self.log_manager:
                self.log_manager.log_info(f"Starting download: {image_name}")
            
            print(f"📥 Downloading image: {image_name}")
            print(f"📅 Date: {date_str}")
            print(f"🔗 URL: {image_url}")
            
            headers = {
                'User-Agent': f'eimg/{__version__} (Earth Image Downloader)',
                'Accept': 'image/png'
            }
            
            img_response = requests.get(image_url, timeout=60, stream=True, headers=headers)
            img_response.raise_for_status()
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"earth_{timestamp}.png"
            
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            filename = "".join(c for c in filename if c.isalnum() or c in '._-')
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            full_path = output_path / filename
            
            total_size = int(img_response.headers.get('content-length', 0))
            downloaded = 0
            image_data = b''
            
            try:
                with open(full_path, "wb") as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            image_data += chunk
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\r📊 Progress: {progress:.1f}%", end='', flush=True)
            except IOError as e:
                print(f"\n❌ Error writing file: {e}")
                return False
            
            if save_to_cache and self.cache_manager:
                metadata = {
                    'image_name': image_name,
                    'date': date_str,
                    'url': image_url,
                    'download_time': datetime.now().isoformat(),
                    'file_size': downloaded
                }
                self.cache_manager.save_image_to_cache(image_data, filename, metadata)
            
            print(f"\n✅ Image saved to: {full_path}")
            print(f"📊 File size: {downloaded / 1024 / 1024:.2f} MB")
            
            if self.log_manager:
                self.log_manager.log_status(f"Download completed: {filename} ({downloaded} bytes)")
            return True
            
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Download failed", e)
            print(f"\n❌ Download error: {e}")
            return False
    
    def show_cache_info(self):
        """Show cache information"""
        try:
            print("💾 Cache Information:")
            print(f"   📁 Cache directory: {CACHE_DIR}")
            
            if self.cache_manager:
                stats = self.cache_manager.get_cache_stats()
                if stats:
                    print(f"   🖼️  Cached images: {stats.get('images', 0)}")
                    print(f"   📊 Total size: {stats.get('total_size', 0) / 1024 / 1024:.2f} MB")
                    print(f"   📋 Metadata files: {stats.get('metadata_files', 0)}")
                    print(f"   🔍 Thumbnails: {stats.get('thumbnails', 0)}")
            
            if CACHE_DIR.exists():
                print("   ✅ Cache directory accessible")
            else:
                print("   ❌ Cache directory not found")
                
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to show cache info", e)
            print(f"❌ Error showing cache info: {e}")
    
    def clear_cache_command(self, cache_type="all"):
        """Clear cache via command"""
        try:
            if not self.cache_manager:
                print("❌ Cache manager not available")
                return
                
            print(f"🗑️  Clearing {cache_type} cache...")
            cleared = self.cache_manager.clear_cache(cache_type)
            print(f"✅ Cleared {cleared} files from cache")
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Failed to clear cache", e)
            print(f"❌ Error clearing cache: {e}")
    
    def show_logs_info(self):
        """Show logs information"""
        try:
            print("📋 Logs Information:")
            print(f"   📁 Logs directory: {LOGS_DIR}")
            
            if LOGS_DIR.exists():
                log_files = list(LOGS_DIR.glob("*.log"))
                print(f"   📄 Log files: {len(log_files)}")
                
                for log_file in log_files:
                    try:
                        size = log_file.stat().st_size
                        print(f"      {log_file.name}: {size / 1024:.1f} KB")
                    except OSError:
                        print(f"      {log_file.name}: Unable to read size")
                    
                print("   ✅ Logs directory accessible")
            else:
                print("   ❌ Logs directory not found")
                
        except Exception as e:
            print(f"❌ Error showing logs info: {e}")
    
    def clear_logs_command(self):
        """Clear logs via command"""
        try:
            print("🗑️  Are you sure you want to clear all logs? (y/N): ", end='')
            confirm = input().strip().lower()
            
            if confirm != 'y':
                print("❌ Operation cancelled")
                return False
            
            cleared = 0
            if LOGS_DIR.exists():
                for log_file in LOGS_DIR.glob("*.log"):
                    try:
                        log_file.unlink()
                        cleared += 1
                    except OSError:
                        continue
            
            print(f"✅ Cleared {cleared} log files")
            
            if self.log_manager:
                self.log_manager.setup_logging()
                self.log_manager.log_status("Logs cleared and logging reinitialized")
            
        except Exception as e:
            print(f"❌ Error clearing logs: {e}")
    
    def open_directory(self, dir_type):
        """Open directory in file manager"""
        try:
            if dir_type == "cache":
                directory = CACHE_DIR
            elif dir_type == "logs":
                directory = LOGS_DIR
            elif dir_type == "config":
                directory = CONFIG_DIR
            else:
                print("❌ Unknown directory type. Use: cache, logs, config")
                return
            
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.run(["explorer", str(directory)], check=True)
                elif system == "Darwin":
                    subprocess.run(["open", str(directory)], check=True)
                elif system == "Linux":
                    subprocess.run(["xdg-open", str(directory)], check=True)
                else:
                    print(f"📁 Directory path: {directory}")
                    return
                
                print(f"📁 Opened {dir_type} directory")
                if self.log_manager:
                    self.log_manager.log_info(f"Opened {dir_type} directory")
            except subprocess.CalledProcessError:
                print(f"❌ Could not open directory automatically")
                print(f"📁 Manual path: {directory}")
            
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error(f"Failed to open {dir_type} directory", e)
            print(f"❌ Error opening directory: {e}")
            print(f"📁 Manual path: {directory}")
    
    def show_config(self):
        """Show current configuration"""
        try:
            print("⚙️  Current Configuration:")
            print(f"   📁 Config file: {CONFIG_FILE}")
            
            if 'encrypted_api_key' in self.config:
                print("   🔐 API key: ✅ Encrypted and stored securely")
                print(f"   🔒 Encryption version: {self.config.get('encryption_version', 'Unknown')}")
            elif 'api_key' in self.config:
                print("   ⚠️  API key: ❌ Stored in plain text (insecure!)")
                print("   💡 Tip: Re-set your API key to enable encryption")
            else:
                print("   🔑 API key: ❌ Not set")
            
            print(f"   📂 Config directory: {CONFIG_DIR}")
            print(f"   🔐 Encryption available: {'✅' if CRYPTO_AVAILABLE else '❌'}")
            
            if os.name != 'nt': 
                try:
                    if CONFIG_DIR.exists():
                        config_perms = oct(CONFIG_DIR.stat().st_mode)[-3:]
                        if config_perms == '700':
                            print("   🛡️  Directory permissions: ✅ Secure (700)")
                        else:
                            print(f"   ⚠️  Directory permissions: {config_perms} (recommend 700)")
                except OSError:
                    print("   🛡️  Directory permissions: ❓ Unknown")

            try:
                test_file = CONFIG_DIR / "test_write"
                test_file.touch()
                test_file.unlink()
                print("   ✅ Config directory is writable")
            except Exception:
                print("   ❌ Config directory is not writable")
                
        except Exception as e:
            if self.log_manager:
                self.log_manager.log_error("Error showing config", e)
            print(f"❌ Error showing config: {e}")
    
    def show_help(self):
        """Show detailed help"""
        help_text = f"""
🌍 Earth Image Downloader (eimg) v{__version__}
By {__author__}

USAGE:
  python main.py <command> [options]

COMMANDS:
  help                    Show this help message
  download               Download latest Earth image
  download-date <date>   Download image for specific date (YYYY-MM-DD)
  dates                  Show available image dates
  metadata [date]        Show image metadata (latest or for specific date)
  validate               Validate your encrypted API key
  set API=<key>          Set and encrypt NASA API key
  config                 Show current configuration
  wipe                   Securely wipe all configuration
  version                Show version information
  
CACHE MANAGEMENT:
  cache-info             Show cache information and statistics
  cache-clear [type]     Clear cache (all/images/metadata/thumbnails)
  open-cache             Open cache directory in file manager
  
LOGS MANAGEMENT:
  logs-info              Show logs information
  logs-clear             Clear all log files
  open-logs              Open logs directory in file manager
  
DIRECTORY COMMANDS:
  open-config            Open config directory in file manager
  test                   Run diagnostic tests

SECURITY FEATURES:
  🔐 API key encryption with master password
  🛡️  Secure file permissions (Unix/Linux/macOS)
  🔍 API key integrity verification
  🗑️  Secure configuration wiping

OPTIONS:
  --output, -o <dir>     Output directory (default: current directory)
  --filename, -f <name>  Output filename (default: auto-generated)
  --no-cache            Don't save to cache

EXAMPLES:
  python main.py set API=your_nasa_api_key_here
  python main.py validate
  python main.py download
  python main.py download --output ./images --filename earth_today.png
  python main.py download-date 2025-01-15
  python main.py cache-info
  python main.py cache-clear images
  python main.py open-cache
  python main.py test

LICENSE:
  MIT License - Copyright (c) 2025 {__author__}
"""
        print(help_text)

def main():
    try:
        parser = argparse.ArgumentParser(
            prog='eimg',
            description='Download Earth images from NASA EPIC API',
            add_help=False
        )
        
        parser.add_argument('command', nargs='?', default='help',
                           help='Command to execute')
        parser.add_argument('date_or_type', nargs='?',
                           help='Date for date-specific commands (YYYY-MM-DD) or cache type')
        parser.add_argument('--output', '-o', default='.', 
                   help='Output directory (default: current directory)')
        parser.add_argument('--filename', '-f',
                           help='Output filename (default: auto-generated)')
        parser.add_argument('--no-cache', action='store_true',
                           help='Don\'t save to cache')
        parser.add_argument('--help', '-h', action='store_true',
                           help='Show help')
        
        if len(sys.argv) == 1:
            EarthImageDownloader().show_help()
            return
        
        args = parser.parse_args()
        
        try:
            downloader = EarthImageDownloader()
        except Exception as e:
            print(f"❌ Failed to initialize downloader: {e}")
            return
        
        if args.help or args.command == 'help':
            downloader.show_help()
        elif args.command == 'download':
            downloader.download_latest(args.output, args.filename)
        elif args.command == 'download-date':
            if args.date_or_type:
                downloader.download_by_date(args.date_or_type, args.output, args.filename)
            else:
                print("❌ Error: Date required for download-date command. Format: YYYY-MM-DD")
        elif args.command == 'dates':
            downloader.get_available_dates()
        elif args.command == 'metadata':
            downloader.show_metadata(args.date_or_type)
        elif args.command == 'validate':
            downloader.validate_api_key()
        elif args.command == 'wipe':
            downloader.wipe_config()
        elif args.command == 'cache-info':
            downloader.show_cache_info()
        elif args.command == 'cache-clear':
            cache_type = args.date_or_type if args.date_or_type else "all"
            downloader.clear_cache_command(cache_type)
        elif args.command == 'open-cache':
            downloader.open_directory("cache")
        elif args.command == 'logs-info':
            downloader.show_logs_info()
        elif args.command == 'logs-clear':
            downloader.clear_logs_command()
        elif args.command == 'open-logs':
            downloader.open_directory("logs")
        elif args.command == 'open-config':
            downloader.open_directory("config")
        elif args.command == 'test':
            try:
                from tests.test_runner import run_all_tests
                run_all_tests()
            except ImportError:
                print("❌ Tests not available. Check if tests directory exists.")
        elif args.command.startswith('set'):
            if '=' in args.command:
                try:
                    key_value = args.command.split('=', 1)
                    if key_value[0].strip() == 'set API':
                        downloader.set_api_key(key_value[1].strip())
                    else:
                        print("❌ Invalid set command. Use: python main.py set API=your_key_here")
                except IndexError:
                    print("❌ Invalid set command format. Use: python main.py set API=your_key_here")
            else:
                print("❌ Invalid set command. Use: python main.py set API=your_key_here")
        elif args.command == 'config':
            downloader.show_config()
        elif args.command == 'version':
            print(f"🌍 eimg v{__version__} by {__author__}")
            print(f"🔐 Security features: API encryption ({'✅' if CRYPTO_AVAILABLE else '❌'}), secure permissions")
            print("💾 Cache features: Local storage, metadata tracking")
            print("📋 Logging features: Error tracking, status monitoring")
        else:
            print(f"❌ Unknown command: {args.command}")
            print("Use 'python main.py help' for available commands")
            
    except KeyboardInterrupt:
        print("\n\n⚡ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue with the error details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()