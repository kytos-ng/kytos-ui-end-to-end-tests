import pytest
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the Kytos UI instance"""
    return "http://190.103.184.199:18181"


@pytest.fixture(scope="function")
def driver(base_url):
    """Setup and teardown for Chrome WebDriver"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # For headless mode (uncomment if needed)
    # options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.implicitly_wait(10)
    driver.get(base_url)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def logger():
    """Setup logging for test cases"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


@pytest.fixture
def test_data():
    """Test data for EVC creation tests"""
    return {
        "valid_circuits": [
            {
                "name": "Test_Circuit_001",
                "endpoint_a": "Switch01:eth1",
                "vlan_a": "100",
                "endpoint_z": "Switch02:eth1", 
                "vlan_z": "100"
            },
            {
                "name": "Full_Feature_Circuit",
                "endpoint_a": "Switch01:eth2",
                "vlan_a": "200",
                "endpoint_z": "Switch03:eth1",
                "vlan_z": "201",
                "service_level": "5",
                "priority": "high",
                "max_paths": "3",
                "qos_queue": "premium",
                "enable_int": True
            },
            {
                "name": "VLAN_Range_Circuit", 
                "endpoint_a": "Switch01:eth3",
                "vlan_a": "[[100, 200]]",
                "endpoint_z": "Switch02:eth3",
                "vlan_z": "[[100, 200]]"
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