"""
Security tests for Earth Image Downloader
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import SecurityManager, EarthImageDownloader

class TestSecurityManager(unittest.TestCase):
    """Test security functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.security = SecurityManager()
        self.test_data = "test_api_key_12345"
        self.test_password = "test_password_123"
    
    def test_encryption_decryption(self):
        """Test encryption and decryption"""
        print("🔐 Testing encryption/decryption...")
        
        encrypted = self.security.encrypt_data(self.test_data, self.test_password)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, self.test_data)
        
        decrypted = self.security.decrypt_data(encrypted, self.test_password)
        self.assertEqual(decrypted, self.test_data)
        print("   ✅ Encryption/decryption working correctly")
    
    def test_wrong_password(self):
        """Test decryption with wrong password"""
        print("🔐 Testing wrong password protection...")
        
        encrypted = self.security.encrypt_data(self.test_data, self.test_password)
        decrypted = self.security.decrypt_data(encrypted, "wrong_password")
        self.assertIsNone(decrypted)
        print("   ✅ Wrong password protection working")
    
    def test_hash_string(self):
        """Test string hashing"""
        print("🔐 Testing string hashing...")
        
        hash1 = self.security.hash_string(self.test_data)
        hash2 = self.security.hash_string(self.test_data)
        hash3 = self.security.hash_string("different_data")
        
        self.assertIsNotNone(hash1)
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
        print("   ✅ String hashing working correctly")
    
    def test_api_key_validation(self):
        """Test API key format validation"""
        print("🔐 Testing API key validation...")
        
        self.assertTrue(self.security.validate_api_key_format("abcdefghijklmnopqrstuvwxyz1234567890"))
        self.assertTrue(self.security.validate_api_key_format("ABC123DEF456GHI789JKL012MNO345PQR678"))
        
        self.assertFalse(self.security.validate_api_key_format(""))
        self.assertFalse(self.security.validate_api_key_format("short"))
        self.assertFalse(self.security.validate_api_key_format(None))
        print("   ✅ API key validation working correctly")

class TestEarthImageDownloader(unittest.TestCase):
    """Test main application functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_config_dir = Path.home() / ".eimg"
        
        import main
        main.CONFIG_DIR = Path(self.temp_dir) / ".eimg"
        main.CONFIG_FILE = main.CONFIG_DIR / "config.json"
        
        self.downloader = EarthImageDownloader()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_operations(self):
        """Test configuration operations"""
        print("⚙️ Testing configuration operations...")
        
        self.assertEqual(self.downloader.config, {})
        
        self.downloader.config['test_key'] = 'test_value'
        self.assertTrue(self.downloader.save_config())
        
        new_downloader = EarthImageDownloader()
        self.assertEqual(new_downloader.config.get('test_key'), 'test_value')
        print("   ✅ Configuration operations working correctly")

if __name__ == "__main__":
    unittest.main()
