"""
Integration tests for Earth Image Downloader
Tests the interaction between different components
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import EarthImageDownloader

class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        import main
        main.CONFIG_DIR = Path(self.temp_dir) / ".eimg"
        main.CONFIG_FILE = main.CONFIG_DIR / "config.json"
        main.LOGS_DIR = Path(self.temp_dir) / "logs"
        main.CACHE_DIR = Path(self.temp_dir) / "cache"
        
        self.downloader = EarthImageDownloader()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_initialization(self):
        """Test full application initialization"""
        print("🔧 Testing full initialization...")
        
        self.assertIsNotNone(self.downloader.log_manager)
        self.assertIsNotNone(self.downloader.cache_manager)
        self.assertIsNotNone(self.downloader.security)
        
        import main
        self.assertTrue(main.LOGS_DIR.exists())
        self.assertTrue(main.CACHE_DIR.exists())
        print("   ✅ Full initialization successful")
    
    @patch('requests.get')
    def test_download_with_cache(self, mock_get):
        """Test download functionality with caching"""
        print("🔧 Testing download with cache...")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api_data = [{
            'image': 'test_image_123',
            'date': '2025-01-15 12:00:00'
        }]
        
        with patch.object(self.downloader, 'get_api_key', return_value='test_api_key'), \
             patch('requests.get') as mock_api_get:

            mock_api_response = MagicMock()
            mock_api_response.status_code = 200
            mock_api_response.json.return_value = api_data
            mock_api_response.raise_for_status.return_value = None
            
            def side_effect(url, **kwargs):
                if 'images?api_key=' in url:
                    return mock_api_response
                else:
                    return mock_response
            
            mock_api_get.side_effect = side_effect
            
            result = self.downloader.download_latest(self.temp_dir, "test_earth.png")
            
            self.assertTrue(result)
            
            output_file = Path(self.temp_dir) / "test_earth.png"
            self.assertTrue(output_file.exists())
            
            stats = self.downloader.cache_manager.get_cache_stats()
            self.assertGreater(stats['images'], 0)
            
        print("   ✅ Download with cache working correctly")
    
    def test_error_handling(self):
        """Test error handling across components"""
        print("🔧 Testing error handling...")
        
        result = self.downloader.validate_api_key()
        self.assertFalse(result)
        
        result = self.downloader.cache_manager.save_image_to_cache(None, None)
        self.assertIsNone(result)
        
        print("   ✅ Error handling working correctly")

if __name__ == "__main__":
    unittest.main()
