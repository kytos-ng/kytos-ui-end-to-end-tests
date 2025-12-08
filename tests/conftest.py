import os
import pytest
import time
import requests
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --- Environment Variable Loading ---
try:
    from dotenv import load_dotenv
    # Find the .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    print(f"Loaded environment variables from: {env_path}")
except ImportError:
    print("python-dotenv not installed, using default values")
except Exception as e:
    print(f"Error loading .env file: {e}")

# --- Fixtures for Configuration ---

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Kytos UI."""
    return os.getenv('BASE_URL', 'http://localhost:18181')

@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for the Kytos API."""
    return os.getenv('API_BASE_URL', 'http://localhost:18181/api/kytos/mef_eline/v2/evcs/')

@pytest.fixture(scope="session")
def default_timeout():
    """Default timeout for Selenium waits."""
    return int(os.getenv('DEFAULT_TIMEOUT', '10'))

# --- Fixture for WebDriver Setup ---

@pytest.fixture(scope="function")
def driver(default_timeout):
    """
    Pytest fixture to set up and tear down the Selenium WebDriver (ChromeDriver).
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    
    # Headless mode controlled by environment variable (default to true)
    if os.getenv("HEADLESS", "true").lower() != "false":
        options.add_argument("--headless=new")
        
    # Use the specified path for chromedriver
    try:
        service = Service("/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
        print("\nChromeDriver successfully initialized.")
    except Exception as e:
        print(f"\nError initializing ChromeDriver: {e}")
        # Fallback to system path if service path fails
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(default_timeout)
    
    yield driver

    print("\nClosing ChromeDriver.")
    driver.quit()

# --- Fixture for Test Data ---

@pytest.fixture
def test_data():
    """Test data for EVC creation tests"""
    return {
        "valid_circuits": [
            {
                "name": "Test_Circuit_001",
                "endpoint_a": "00:00:00:00:00:00:00:18:13",
                "endpoint_a_field": "00:00:00:00:00:00:00:18: mia_s18-eth13",
                "vlan_a": "104",
                "endpoint_z": "00:00:00:00:00:00:00:18:8",
                "endpoint_z_field": "00:00:00:00:00:00:00:18: mia_s18-eth8",
                "vlan_z": "100"
            },
            {
                "name": "Full_Feature_Circuit",
                "endpoint_a": "00:00:00:00:00:00:00:18:13",
                "endpoint_a_field": "00:00:00:00:00:00:00:18: mia_s18-eth13",
                "vlan_a": "104",
                "endpoint_z": "00:00:00:00:00:00:00:18:8",
                "endpoint_z_field": "00:00:00:00:00:00:00:18: mia_s18-eth8",
                "vlan_z": "100",
                "service_level": "5",
                "priority": "high",
                "max_paths": "3",
                "qos_queue": "premium",
                "enable_int": True
            },
            {
                "name": "VLAN_Range_Circuit",
                "endpoint_a": "00:00:00:00:00:00:00:18:13",
                "vlan_a": "[100, 200]",
                "endpoint_z": "00:00:00:00:00:00:00:18:8",
                "vlan_z": "[100, 200]"
            }
        ],
        "invalid_circuits": [
            {
                "name": "",
                "endpoint_a": "Switch01:eth1",
                "vlan_a": "100",
                "endpoint_z": "Switch02:eth1",
                "vlan_z": "100",
                "expected_error": "Circuit Name is required"
            },
            {
                "name": "Invalid_VLAN_Test",
                "endpoint_a": "Switch01:eth1",
                "vlan_a": "invalid_vlan",
                "endpoint_z": "Switch02:eth1",
                "vlan_z": "100",
                "expected_error": "Invalid VLAN format"
            },
            {
                "name": "Invalid_Endpoint_Test",
                "endpoint_a": "NonExistentSwitch:eth1",
                "vlan_a": "100",
                "endpoint_z": "Switch02:eth1",
                "vlan_z": "100",
                "expected_error": "Endpoint not found"
            }
        ],
        "boundary_test": {
            "max_vlan": "4094",
            "invalid_vlan": "4095",
            "long_name": "a" * 256
        }
    }