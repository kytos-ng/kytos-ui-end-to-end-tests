#!/usr/bin/env python3
"""
Complete EVC Creation Test Suite for Kytos UI
All test cases (TC_001 through TC_017) in a single file without page objects.

Before running these tests, you need to update the selectors below with actual ones from the Kytos UI.
To find the selectors:
1. Navigate to http://190.103.184.199:18181/
2. Go to the EVC creation form
3. Inspect each element to get the actual selectors
4. Update the SELECTORS dictionary below with the real values

Run with: pytest test_all_evc_creation.py -v
"""

import pytest
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import platform
import os


# =============================================================================
# SELECTORS - UPDATE THESE WITH ACTUAL VALUES FROM THE KYTOS UI
# =============================================================================
SELECTORS = {
    # Navigation (actual selectors found)
    'mef_eline_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Mef-Eline"]'),
    
    # Form fields (Based on exploration - these are examples, update as needed)
    'circuit_name_input': (By.ID, "name-input"),  # Generic text area found
    'endpoint_a_input': (By.XPATH, "//*[@id='endpoint-a-input']/div/div/div/input"),  # Kytos uses k-input class
    'endpoint_z_input': (By.XPATH, "//*[@id='endpoint-z-input']/div/div/div/input"),
    'vlan_a_input': (By.ID, "endpoint-a-tag-value"),
    'vlan_z_input': (By.ID, "endpoint-z-tag-value"),
    
    # Optional fields (Kytos UI patterns)
    'service_level_select': (By.CSS_SELECTOR, "select[class='k-dropdown__select']"),
    'priority_select': (By.CSS_SELECTOR, "select[class='k-dropdown__select']"),
    'max_paths_input': (By.CSS_SELECTOR, "input[class='k-input']"),
    'qos_queue_select': (By.CSS_SELECTOR, "select[class='k-select__select']"),
    'enable_int_checkbox': (By.CSS_SELECTOR, "input[type='checkbox']"),
    
    # Buttons (Kytos uses k-button class)
    'submit_button': (By.XPATH, "//*[@id='app']/div[1]/div/div[5]/div/div/button"),
    'cancel_button': (By.CSS_SELECTOR, "button[class*='k-button']"),
    
    # Messages (Generic patterns)
    'evc_form_message_title': (By.CLASS_NAME, "notification-text notification-title"),
    'evc_form_message_description': (By.CLASS_NAME, "notification-text notification-description"),
    'validation_error': (By.CSS_SELECTOR, ".validation-error, [class*='error']"),
}

# Test Configuration
BASE_URL = "http://190.103.184.199:18181"
API_BASE_URL = "http://190.103.184.199:18181/api/kytos/mef_eline/v2/evc/"
DEFAULT_TIMEOUT = 10


# =============================================================================
# FIXTURES
# =============================================================================
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
    
    print("Setting up ChromeDriver...")
    
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
    
    3. Clear webdriver-manager cache and reinstall:
       rm -rf ~/.wdm
       pip install webdriver-manager --upgrade
    """)


@pytest.fixture(scope="function")
def driver():
    """Setup WebDriver with proper error handling"""
    driver = setup_chromedriver()
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


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


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def navigate_to_evc_form(driver):
    """Navigate from homepage to EVC creation form"""
    print("Navigating to EVC creation form...")
    driver.get(BASE_URL)
    
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    
    try:
        # Wait for page to load
        time.sleep(3)
        
        # Click the MEF E-Line button to open the request circuit form
        print("Looking for MEF E-Line button...")
        mef_button = wait.until(EC.element_to_be_clickable(SELECTORS['mef_eline_button']))
        print("Found MEF E-Line button, clicking...")
        mef_button.click()
        
        # Wait for the form to appear
        time.sleep(2)
        
        # Verify that form elements are now visible
        print("Checking for form elements after clicking MEF button...")
        form_elements = driver.find_elements(By.CSS_SELECTOR, "input[class='k-input'], textarea, select")
        
        if len(form_elements) > 0:
            print(f"✅ Successfully opened MEF form with {len(form_elements)} form elements")
            return True
        else:
            print("❌ No form elements found after clicking MEF button")
            return False
            
    except TimeoutException as e:
        print(f"❌ Failed to find MEF E-Line button: {e}")
        print("Current URL:", driver.current_url)
        print("Page title:", driver.title)
        
        # Print available buttons for debugging
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons on page:")
        for i, button in enumerate(buttons[:10]):  # Show first 10 buttons
            title = button.get_attribute('title') or ''
            text = button.text.strip()
            data_test = button.get_attribute('data-test') or ''
            print(f"  {i+1}. Title: '{title}' | Text: '{text}' | data-test: '{data_test}'")
        
        return False
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        print("Current URL:", driver.current_url)
        print("Page title:", driver.title)
        return False


def fill_circuit_form(driver, circuit_data):
    """Fill the EVC creation form with provided data"""
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)
    
    # Fill circuit name
    name_input = wait.until(EC.presence_of_element_located(SELECTORS['circuit_name_input']))
    name_input.clear()
    name_input.send_keys(circuit_data["name"])
    
    # Fill endpoint A
    endpoint_a_input = driver.find_element(*SELECTORS['endpoint_a_input'])
    endpoint_a_input.clear()
    endpoint_a_input.send_keys(circuit_data["endpoint_a"])
    time.sleep(3)
    
    # Fill endpoint Z
    endpoint_z_input = driver.find_element(*SELECTORS['endpoint_z_input'])
    endpoint_z_input.clear()
    endpoint_z_input.send_keys(circuit_data["endpoint_z"])
    
    # Fill VLAN A
    vlan_a_input = driver.find_element(*SELECTORS['vlan_a_input'])
    vlan_a_input.clear()
    vlan_a_input.send_keys(str(circuit_data["vlan_a"]))
    
    # Fill VLAN Z
    vlan_z_input = driver.find_element(*SELECTORS['vlan_z_input'])
    vlan_z_input.clear()
    vlan_z_input.send_keys(str(circuit_data["vlan_z"]))
    
    # Fill optional fields if provided
    if circuit_data.get("service_level"):
        try:
            service_select = Select(driver.find_element(*SELECTORS['service_level_select']))
            service_select.select_by_value(circuit_data["service_level"])
        except NoSuchElementException:
            print("Service level field not found")
    
    if circuit_data.get("priority"):
        try:
            priority_select = Select(driver.find_element(*SELECTORS['priority_select']))
            priority_select.select_by_visible_text(circuit_data["priority"])
        except NoSuchElementException:
            print("Priority field not found")
    
    if circuit_data.get("max_paths"):
        try:
            max_paths_input = driver.find_element(*SELECTORS['max_paths_input'])
            max_paths_input.clear()
            max_paths_input.send_keys(circuit_data["max_paths"])
        except NoSuchElementException:
            print("Max paths field not found")
    
    if circuit_data.get("qos_queue"):
        try:
            qos_select = Select(driver.find_element(*SELECTORS['qos_queue_select']))
            qos_select.select_by_visible_text(circuit_data["qos_queue"])
        except NoSuchElementException:
            print("QoS queue field not found")
    
    if circuit_data.get("enable_int"):
        try:
            int_checkbox = driver.find_element(*SELECTORS['enable_int_checkbox'])
            if not int_checkbox.is_selected():
                int_checkbox.click()
        except NoSuchElementException:
            print("Enable INT checkbox not found")


def submit_form(driver):
    """Submit the EVC creation form"""
    submit_button = driver.find_element(*SELECTORS['submit_button'])
    submit_button.click()
    time.sleep(2)  # Wait for submission


def get_form_messages(driver):
    """Get success/error messages from the form"""
    messages = {}
    
    try:
        success_element = driver.find_element(*SELECTORS['evc_form_message_title'])
        messages['success'] = success_element.text
    except NoSuchElementException:
        messages['success'] = None
    
    try:
        error_element = driver.find_element(*SELECTORS['error_message'])
        messages['error'] = error_element.text
    except NoSuchElementException:
        messages['error'] = None
    
    try:
        validation_elements = driver.find_elements(*SELECTORS['validation_error'])
        messages['validation_errors'] = [elem.text for elem in validation_elements]
    except NoSuchElementException:
        messages['validation_errors'] = []
    
    return messages


def verify_circuit_via_api(circuit_name, timeout=30):
    """Verify circuit was created via API"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(API_BASE_URL)
            if response.status_code == 200:
                circuits = response.json()
                for circuit_id, circuit_data in circuits.items():
                    if circuit_data.get('name') == circuit_name:
                        return circuit_id
            time.sleep(2)
        except Exception as e:
            print(f"API check error: {e}")
            time.sleep(2)
    return None


def cleanup_test_circuit(circuit_name):
    """Clean up test circuit via API"""
    try:
        response = requests.get(API_BASE_URL)
        if response.status_code == 200:
            circuits = response.json()
            for circuit_id, circuit_data in circuits.items():
                if circuit_data.get('name') == circuit_name:
                    delete_response = requests.delete(f"{API_BASE_URL}{circuit_id}")
                    if delete_response.status_code in [200, 204]:
                        print(f"Cleaned up circuit: {circuit_name}")
                    break
    except Exception as e:
        print(f"Cleanup error: {e}")


# =============================================================================
# POSITIVE TEST CASES (TC_001-003)
# =============================================================================
class TestPositiveEVCCreation:
    """Positive test cases for successful EVC creation"""
    
    def teardown_method(self, method):
        """Cleanup after each test"""
        # Clean up any circuits that were created
        test_circuits = [
            "Test_Circuit_001",
            "Full_Feature_Circuit", 
            "VLAN_Range_Circuit",
            "Performance_Test_Circuit"
        ]
        for circuit in test_circuits:
            cleanup_test_circuit(circuit)
    
    def test_tc_001_create_basic_evc_minimum_fields(self, driver, test_data):
        """
        TC_CREATE_EVC_001: Create Basic EVC with Minimum Required Fields
        
        Objective: Verify successful creation of EVC with only required fields
        """
        print("\\n=== TC_001: Create Basic EVC with minimum required fields ===")
        
        circuit_data = test_data["valid_circuits"][0]  # Test_Circuit_001
        
        # Navigate to EVC creation form
        assert navigate_to_evc_form(driver), "Failed to navigate to EVC creation form"
        
        # Fill and submit form
        fill_circuit_form(driver, circuit_data)
        submit_form(driver)
        time.sleep(3)

        list_installed_evcs=driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[5]/div/div/div[2]/div/button")
        list_installed_evcs.click()
        time.sleep(3)
        evc_created=driver.find_element(By.XPATH,"//*[@id='mef-table-list-circuit']/tbody/tr/td[1]")
        print(evc_created.text)
        evc_created_text=evc_created.text
        assert evc_created_text==circuit_data["name"],"error creating circuit"

        # Verify via API
        circuit_id = verify_circuit_via_api(circuit_data["name"])
        assert circuit_id is not None, f"Circuit '{circuit_data['name']}' not found in API"
        
        print(f"✅ TC_001 PASSED. EVC with circuit id "+circuit_id+" created and deleted successfully")
    





# =============================================================================
# RUN INSTRUCTIONS
# =============================================================================
if __name__ == "__main__":
    print("""
    ================================================================================
    KYTOS UI EVC CREATION TEST SUITE
    ================================================================================
    
    BEFORE RUNNING THESE TESTS:
    
    1. Update the SELECTORS dictionary at the top of this file with actual selectors
       from your Kytos UI at http://190.103.184.199:18181/
    
    2. To find the selectors:
       - Navigate to the EVC creation form in your browser
       - Right-click on each form element and select "Inspect Element"
       - Note the id, class, or other attributes
       - Update the SELECTORS dictionary accordingly
    
    3. Test the navigation by updating the navigate_to_evc_form() function
    
    RUNNING THE TESTS:
    
    # Run all tests
    pytest test_all_evc_creation.py -v
    
    # Run specific test class
    pytest test_all_evc_creation.py::TestPositiveEVCCreation -v
    
    # Run specific test
    pytest test_all_evc_creation.py::TestPositiveEVCCreation::test_tc_001_create_basic_evc_minimum_fields -v
    
    # Run with HTML report
    pytest test_all_evc_creation.py -v --html=report.html
    
    # Run performance tests only
    pytest test_all_evc_creation.py -m performance -v
    
    ================================================================================
    """)