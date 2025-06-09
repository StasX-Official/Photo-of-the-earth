"""
Cache management tests for Earth Image Downloader
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import CacheManager, LogManager

class TestCacheManager(unittest.TestCase):
    """Test cache management functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        import main
        main.CACHE_DIR = Path(self.temp_dir) / "cache"
        main.LOGS_DIR = Path(self.temp_dir) / "logs"
        
        self.log_manager = LogManager()
        self.cache_manager = CacheManager(self.log_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_setup(self):
        """Test cache directory setup"""
        print("💾 Testing cache setup...")
        
        import main
        cache_dir = main.CACHE_DIR
        
        self.assertTrue(cache_dir.exists())
        self.assertTrue((cache_dir / "images").exists())
        self.assertTrue((cache_dir / "metadata").exists())
        self.assertTrue((cache_dir / "thumbnails").exists())
        print("   ✅ Cache directories created correctly")
    
    def test_cache_stats(self):
        """Test cache statistics"""
        print("💾 Testing cache statistics...")
        
        stats = self.cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('images', stats)
        self.assertIn('total_size', stats)
        self.assertIn('metadata_files', stats)
        self.assertIn('thumbnails', stats)
        print("   ✅ Cache statistics working correctly")
    
    def test_save_image_to_cache(self):
        """Test saving image to cache"""
        print("💾 Testing image caching...")
        
        test_image_data = b"fake_png_data_for_testing"
        test_filename = "test_earth.png"
        test_metadata = {
            "date": "2025-01-15",
            "size": len(test_image_data)
        }
        
        cache_path = self.cache_manager.save_image_to_cache(
            test_image_data, test_filename, test_metadata
        )
        
        self.assertIsNotNone(cache_path)
        self.assertTrue(cache_path.exists())
        
        with open(cache_path, 'rb') as f:
            cached_data = f.read()
        self.assertEqual(cached_data, test_image_data)
        
        import main
        metadata_path = main.CACHE_DIR / "metadata" / f"{test_filename}.json"
        self.assertTrue(metadata_path.exists())
        
        with open(metadata_path, 'r') as f:
            cached_metadata = json.load(f)
        self.assertEqual(cached_metadata['date'], test_metadata['date'])
        print("   ✅ Image caching working correctly")
    
    def test_clear_cache(self):
        """Test cache clearing"""
        print("💾 Testing cache clearing...")
        
        import main
        images_dir = main.CACHE_DIR / "images"
        metadata_dir = main.CACHE_DIR / "metadata"
        
        test_image = images_dir / "test.png"
        test_metadata = metadata_dir / "test.json"
        
        test_image.write_text("test image")
        test_metadata.write_text("test metadata")
        
        cleared = self.cache_manager.clear_cache("all")
        self.assertGreater(cleared, 0)
        self.assertFalse(test_image.exists())
        self.assertFalse(test_metadata.exists())
        print("   ✅ Cache clearing working correctly")

if __name__ == "__main__":
    unittest.main()
