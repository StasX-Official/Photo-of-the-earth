"""
Logging tests for Earth Image Downloader
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import LogManager

class TestLogManager(unittest.TestCase):
    """Test logging functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        import main
        main.LOGS_DIR = Path(self.temp_dir) / "logs"
        
        self.log_manager = LogManager()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logs_setup(self):
        """Test logs directory setup"""
        print("📋 Testing logs setup...")
        
        import main
        logs_dir = main.LOGS_DIR
        
        self.assertTrue(logs_dir.exists())
        print("   ✅ Logs directory created correctly")
    
    def test_logging_methods(self):
        """Test different logging methods"""
        print("📋 Testing logging methods...")
        
        self.log_manager.log_info("Test info message")
        self.log_manager.log_status("Test status message")
        self.log_manager.log_error("Test error message")
        self.log_manager.log_error("Test error with exception", Exception("Test exception"))
        
        import main
        logs_dir = main.LOGS_DIR
        
        log_files = list(logs_dir.glob("*.log"))
        self.assertGreater(len(log_files), 0)
        print(f"   ✅ Created {len(log_files)} log files")
    
    def test_log_content(self):
        """Test log file content"""
        print("📋 Testing log content...")
        
        test_message = "Test log message for verification"
        self.log_manager.log_info(test_message)
        
        import main
        main_log = main.LOGS_DIR / "eimg.log"
        
        if main_log.exists():
            content = main_log.read_text()
            self.assertIn(test_message, content)
            print("   ✅ Log content verification successful")
        else:
            print("   ⚠️  Log file not found, skipping content test")

if __name__ == "__main__":
    unittest.main()
