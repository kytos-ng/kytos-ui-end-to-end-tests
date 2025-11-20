#!/usr/bin/env python3
"""
WebDriver configuration for Mac ARM64 compatibility
This handles ChromeDriver issues on Apple Silicon Macs
"""

import pytest
import platform
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_chrome_options():
    """Configure Chrome options for testing"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    # Uncomment for headless mode:
    # options.add_argument("--headless")
    
    return options


def setup_chromedriver():
    """Setup ChromeDriver with Mac ARM64 compatibility"""
    options = get_chrome_options()
    
    # Method 1: Try using system chromedriver first (most reliable)
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Using system ChromeDriver")
        return driver
    except Exception as e:
        print(f"❌ System ChromeDriver failed: {e}")
    
    # Method 2: Try specific paths for Mac ARM64
    if platform.system() == 'Darwin':
        possible_paths = [
            "/opt/homebrew/bin/chromedriver",  # Homebrew on ARM64
            "/usr/local/bin/chromedriver",     # Traditional location
            "/Applications/chromedriver",      # Manual installation
            "/usr/bin/chromedriver"            # System location
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                try:
                    service = Service(path)
                    driver = webdriver.Chrome(service=service, options=options)
                    print(f"✅ Using ChromeDriver at: {path}")
                    return driver
                except Exception as e:
                    print(f"❌ ChromeDriver at {path} failed: {e}")
                    continue
    
    # Method 3: Try webdriver-manager as last resort
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        # Force fresh download to avoid corrupted files
        driver_path = ChromeDriverManager(cache_valid_range=1).install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print(f"✅ Using webdriver-manager ChromeDriver at: {driver_path}")
        return driver
    except Exception as e:
        print(f"❌ webdriver-manager failed: {e}")
    
    # If all else fails, provide helpful error message
    raise Exception("""
    ❌ Failed to setup ChromeDriver. Try these solutions:
    
    1. Install ChromeDriver via Homebrew (recommended for Mac ARM64):
       brew install chromedriver
    
    2. Download ChromeDriver manually:
       - Go to https://chromedriver.chromium.org/
       - Download the ARM64 version for Mac
       - Place it in /opt/homebrew/bin/ or /usr/local/bin/
       - Make it executable: chmod +x /path/to/chromedriver
    
    3. Install via pip:
       pip install webdriver-manager --upgrade
    
    4. Use Firefox instead (add this to your test file):
       from selenium.webdriver.firefox.service import Service
       from webdriver_manager.firefox import GeckoDriverManager
       
       service = Service(GeckoDriverManager().install())
       driver = webdriver.Firefox(service=service)
    """)


@pytest.fixture(scope="function")
def driver():
    """Setup WebDriver with proper error handling"""
    driver = setup_chromedriver()
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()