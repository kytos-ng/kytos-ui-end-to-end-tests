import os
import pytest
import datetime
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
def api_url(request) -> str:
    """Base URL for the Kytos API."""
    env_var, default = request.param
    return os.getenv(env_var, default)

@pytest.fixture(scope="session")
def default_timeout():
    """Default timeout for Selenium waits."""
    return int(os.getenv('DEFAULT_TIMEOUT', '10'))

# --- Fixture for WebDriver Setup ---

@pytest.fixture(scope="session")
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
def evc_test_data():
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


@pytest.fixture
def sdntrace_test_data():
    """Test data for SDNTrace"""
    return {
        "valid_data": [
            {
                "dpid": "00:00:00:00:00:00:00:14",
                "port": "13"
            },
            {
                "dpid": "00:00:00:00:00:00:00:14",
                "port": "13",
                "dl_vlan": "300",
                "dl_type": "2048",
                "dl_src": "1",
                "dl_dst": "a1:b2:c3:d4:e5:f6",
                "nw_src": "10.10.10.1",
                "nw_dst": "10.10.10.254",
                "nw_proto": "6",        
                "nw_tos": "2",
                "tp_src": "1234",
                "tp_dst": "80",
            }
        ],
        "invalid_data": [
            {
                "dpid": "00:00:00:00:00:00:00:01",
                "port": "13"
            },
            {
                "dpid": "ff:ff:ff:ff:ff:ff:ff:ff",
                "port": "13"
            },
            # {
            #     "dpid": "00:00:00:00:00:00:00:18",
            #     "port": "9999"
            # },
            {
                "dpid": "00:00:00:00:00:00:00:18",
                "port": "a"
            }
        ]
    }

def get_future_time_data(days_from_now=2):
    """Generates start and end time data for a maintenance window in the near future."""
    # The format required is 'yyyy-mm-ddThh:mm:ss+0000'
    
    now = datetime.datetime.now(datetime.timezone.utc)
    start_time = now + datetime.timedelta(days=days_from_now)
    end_time = now + datetime.timedelta(days=days_from_now, hours=1)

    time_format = "%Y-%m-%dT%H:%M:%S+0000"
    
    start_time_str = start_time.strftime(time_format) 
    end_time_str = end_time.strftime(time_format)
    
    return {
        "start_time": start_time_str,
        "end_time": end_time_str
    }

@pytest.fixture
def maintenance_test_data():
    """Test data for maintenance"""
    time_data = get_future_time_data()
    time_data_past = time_data.copy()
    time_data_past["start_time"] = time_data_past["start_time"].replace("2025", "2024")
    time_data_wrong_format = time_data.copy()
    time_data_wrong_format["start_time"] = time_data_wrong_format["start_time"].split('T')[0]
    
    return {
        "valid_data": [
            {**{
                "description": "Valid data",
                "switches": ["MIA-MI1-SW14"],
                "interfaces": ["00:00:00:00:00:00:00:14:32"],
                "links": ["e879d80c5907429087330d24ac29f6fc78513c02bb21f91212d0dd0db89a7d55"],
            }, **get_future_time_data(3)},
            {**{
                "description": "Valid data - multiple switches",
                "switches": ["MIA-MI1-SW14","SJU-H787-SW02"],
            }, **get_future_time_data(4)}
        ],
        "invalid_data": [
            {**{
                "description": "Invalid data - empty lists",
                "switches": [],
            }, **time_data},
            {**{
                "description": "Invalid data - past time",
                "switches": ["MIA-MI1-SW14"],
            }, **time_data_past},
            {**{
                "description": "Invalid data - unexpected time format",
                "switches": ["MIA-MI1-SW14"],
            }, **time_data_wrong_format}
        ]
    }
