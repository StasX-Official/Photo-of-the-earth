"""
Test runner for Earth Image Downloader (eimg)
Executes all tests and provides debugging information
"""

import sys
import os
import unittest
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all tests with detailed output"""
    print("🧪 Starting eimg test suite...")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    class VerboseTestResult(unittest.TextTestResult):
        def startTest(self, test):
            super().startTest(test)
            print(f"🔍 Running: {test._testMethodName}")
        
        def addSuccess(self, test):
            super().addSuccess(test)
            print(f"✅ PASS: {test._testMethodName}")
        
        def addError(self, test, err):
            super().addError(test, err)
            print(f"❌ ERROR: {test._testMethodName}")
            print(f"   {err[1]}")
        
        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"❌ FAIL: {test._testMethodName}")
            print(f"   {err[1]}")
    
    runner = unittest.TextTestRunner(
        resultclass=VerboseTestResult,
        verbosity=2,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("🧪 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    run_all_tests()
