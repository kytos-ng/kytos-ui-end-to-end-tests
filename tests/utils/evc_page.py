import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class EVCPage:
    """
    Page Object Model for the EVC creation and management page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """
    SELECTORS = {
        # Navigation
        'mef_eline_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Mef-Eline"]'),
        
        # Form fields
        'circuit_name_input': (By.ID, "name-input"),
        'endpoint_a_input': (By.XPATH, "//*[@id='endpoint-a-input']/div/div/div/input"),
        'endpoint_z_input': (By.XPATH, "//*[@id='endpoint-z-input']/div/div/div/input"),
        'vlan_a_input': (By.ID, "endpoint-a-tag-value"),
        'vlan_z_input': (By.ID, "endpoint-z-tag-value"),
        
        # Optional fields
        'service_level_select': (By.ID, "service-level-input"),
        'priority_select': (By.ID, "sb-priority-input"),
        'max_paths_input': (By.ID, "max_paths"),
        'qos_queue_select': (By.XPATH, "//*[@id='mef_eline_toolbar_form']/label/select"),
        'enable_int_checkbox': (By.XPATH, "//span[contains(text(),'INT')]/preceding-sibling::input"), 
        
        # Buttons
        'submit_button': (By.XPATH, "//button[contains(., 'Request') and not(@disabled)]"),
        'cancel_button': (By.CSS_SELECTOR, "button[class*='k-button']"),
        
        # Messages
        'evc_form_message_title': (By.CLASS_NAME, "notification-text notification-title"),
        'evc_form_message_description': (By.CLASS_NAME, "notification-text notification-description"),
        'validation_error': (By.CSS_SELECTOR, ".validation-error, [class*='error']"),

        # List installed EVC button
        'list_installed_evcs_button': (By.XPATH, "//button[contains(., 'List installed EVC') and not(@disabled)]"),
        # EVC table element for verification
        'evc_table_first_row_name': (By.XPATH,"//*[@id='mef-table-list-circuit']/tbody/tr/td[1]")
    }

    def __init__(self, driver: WebDriver, base_url: str, api_base_url: str, default_timeout: int):
        self.driver = driver
        self.base_url = base_url
        self.api_base_url = api_base_url
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    def _find(self, locator_name):
        """Helper to find an element by locator name."""
        by, value = self.SELECTORS[locator_name]
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def navigate_to_evc_form(self):
        """Navigate from homepage to EVC creation form."""
        print("Navigating to EVC creation form...")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Click the MEF E-Line button to open the request circuit form
        mef_button = self.wait.until(EC.element_to_be_clickable(self.SELECTORS['mef_eline_button']))
        mef_button.click()
        
        # Wait for the form to appear
        time.sleep(2)
        
        # Verify that form elements are now visible
        form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[class='k-input'], textarea, select")
        
        if len(form_elements) > 0:
            print(f"✅ Successfully opened MEF form with {len(form_elements)} form elements")
            return True
        else:
            print("❌ No form elements found after clicking MEF button")
            return False

    def fill_circuit_form(self, circuit_data):
        """Fill the EVC creation form with provided data."""
        
        # Fill circuit name
        name_input = self.wait.until(EC.presence_of_element_located(self.SELECTORS['circuit_name_input']))
        name_input.clear()
        name_input.send_keys(circuit_data["name"])
        
        # Fill endpoint A
        endpoint_a_input = self.driver.find_element(*self.SELECTORS['endpoint_a_input'])
        endpoint_a_input.clear()
        endpoint_a_input.send_keys(circuit_data["endpoint_a"])
        time.sleep(3)
        
        # Fill endpoint Z
        endpoint_z_input = self.driver.find_element(*self.SELECTORS['endpoint_z_input'])
        endpoint_z_input.clear()
        endpoint_z_input.send_keys(circuit_data["endpoint_z"])
        
        # Fill VLAN A
        vlan_a_input = self.driver.find_element(*self.SELECTORS['vlan_a_input'])
        vlan_a_input.clear()
        vlan_a_input.send_keys(str(circuit_data["vlan_a"]))
        
        # Fill VLAN Z
        vlan_z_input = self.driver.find_element(*self.SELECTORS['vlan_z_input'])
        vlan_z_input.clear()
        vlan_z_input.send_keys(str(circuit_data["vlan_z"]))
        
        # Fill optional fields if provided
        if circuit_data.get("service_level"):
            try:
                service_select = self.driver.find_element(*self.SELECTORS['service_level_select'])
                service_select.clear()
                service_select.send_keys(str(circuit_data["service_level"]))
            except NoSuchElementException:
                print("Service level field not found")
        
        if circuit_data.get("priority"):
            try:
                priority_select = self.driver.find_element(*self.SELECTORS['priority_select'])
                priority_select.clear()
                priority_select.send_keys(str(circuit_data["priority"]))
            except NoSuchElementException:
                print("Priority field not found")

        if circuit_data.get("max_paths"):
            try:
                max_paths_input = self.driver.find_element(*self.SELECTORS['max_paths_input'])
                max_paths_input.clear()
                max_paths_input.send_keys(circuit_data["max_paths"])
            except NoSuchElementException:
                print("Max paths field not found")

        if circuit_data.get("enable_int"):
            try:
                int_checkbox = self.driver.find_element(*self.SELECTORS['enable_int_checkbox'])
                int_checkbox.click()
            except NoSuchElementException:
                print("Enable INT checkbox not found")

        if circuit_data.get("qos_queue"):
            try:
                qos_select = self.driver.find_element(*self.SELECTORS['qos_queue_select'])
                qos_select.click()
                qos_select_value=self.driver.find_element(By.XPATH,"//*[@id='mef_eline_toolbar_form']/label/select/option[4]")
                qos_select_value.click()
            except NoSuchElementException:
                print("QoS queue field not found")

    def submit_form(self):
        """Submit the EVC creation form (Original submit_form logic)."""
        submit_button = self.driver.find_element(*self.SELECTORS['submit_button'])
        submit_button.click()
        time.sleep(2)

    def get_form_messages(self):
        """Get success/error messages from the form."""
        messages = {}

        try:
            success_element = self.driver.find_element(*self.SELECTORS['evc_form_message_title'])
            messages['success'] = success_element.text
        except NoSuchElementException:
            messages['success'] = None
        
        try:
            error_element = self.driver.find_element(*self.SELECTORS['error_message'])
            messages['error'] = error_element.text
            pass
        except NoSuchElementException:
            messages['error'] = None
        
        try:
            validation_elements = self.driver.find_elements(*self.SELECTORS['validation_error'])
            messages['validation_errors'] = [elem.text for elem in validation_elements]
        except NoSuchElementException:
            messages['validation_errors'] = []
        
        return messages

    def verify_circuit_via_api(self, circuit_name):
        """Verify circuit was created via API."""
        start_time = time.time()
        while time.time() - start_time < self.default_timeout:
            try:
                response = requests.get(self.api_base_url)
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

    def cleanup_test_circuit(self, circuit_name):
        """Clean up test circuit via API."""
        try:
            response = requests.get(self.api_base_url)
            if response.status_code == 200:
                circuits = response.json()
                for circuit_id, circuit_data in circuits.items():
                    if circuit_data.get('name') == circuit_name:
                        delete_response = requests.delete(f"{self.api_base_url}{circuit_id}")
                        if delete_response.status_code in [200, 204]:
                            print(f"Cleaned up circuit: {circuit_name}")
                        break
        except Exception as e:
            print(f"Cleanup error: {e}")

    def click_list_installed_evcs(self):
        """Clicks the 'List installed EVC' button."""
        list_button = self.driver.find_element(*self.SELECTORS['list_installed_evcs_button'])
        list_button.click()
        time.sleep(3) # Wait for the list to load

    def get_first_evc_name_from_table(self):
        """Gets the name of the first EVC in the installed EVC table."""
        evc_created = self.driver.find_element(*self.SELECTORS['evc_table_first_row_name'])
        return evc_created.text