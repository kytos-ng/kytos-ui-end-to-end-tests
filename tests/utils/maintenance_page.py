import time
import requests
from datetime import datetime, timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class MaintenancePage:
    """
    Page Object Model for maintenance page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """

    SELECTORS = {
        # Navigation
        'maintenance_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Maintenace"]'),
        
        # Form fields
        'description': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/div[1]/input"),
        'start_time': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/div[2]/div[1]/input"),
        'end_time': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/div[2]/div[2]/input"),
        'time_date': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/div[3]"), 
        
        'switches': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/label[1]/select"),
        'interfaces': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/label[2]/select"),
        'links': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/label[3]/select"),

        'force': (By.XPATH, "//*[@id='app']/div[1]/div/div[3]/div/div[1]/div/div[4]/label/span"),
        
        # Buttons
        'submit_button': (By.XPATH, "//button[contains(., 'Create Maintenance Window') and not(@disabled)]"),
        'reset_button': (By.XPATH, "//button[contains(., 'Reset') and not(@disabled)]"),
        'list_windows_button': (By.XPATH, "//button[contains(., 'List Maintenance Windows') and not(@disabled)]"),
        
        # Messages
        'form_message_title': (By.CLASS_NAME, "notification-text notification-title"),
        'form_message_description': (By.CLASS_NAME, "notification-text notification-description"),
        'validation_error': (By.CSS_SELECTOR, ".validation-error, [class*='error']"),
        
        'list_windows_button': (By.XPATH, "//button[contains(., 'List Maintenance Windows') and not(@disabled)]")
    }

    def __init__(self, driver: WebDriver, base_url: str, api_url: str, default_timeout: int):
        self.driver = driver
        self.base_url = base_url
        self.api_base_url = api_url
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    def navigate_to_maintenance_tab(self):
        """Navigate from homepage to Create Maintenance Windows form."""
        print("Navigating to Create Maintenance Windows form...")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Click the Maintenance button to open the request form
        maintenance_button = self.wait.until(EC.element_to_be_clickable(self.SELECTORS['maintenance_button']))
        maintenance_button.click()
        
        # Wait for the form to appear
        time.sleep(2)
        
        # Verify that form elements are now visible
        form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[class='k-input'], textarea, select")
        
        if len(form_elements) > 0:
            print(f"✅ Successfully opened Maintenance form with {len(form_elements)} form elements")
            return True
        else:
            print("❌ No form elements found after clicking Maintenance button")
            return False

    def fill_maintenance_form(self, data):
        """Fill the maintenance form with provided data."""

        start_time_input = self.driver.find_element(*self.SELECTORS['start_time'])
        start_time_input.clear()
        start_time_input.send_keys(data["start_time"])
        
        end_time_input = self.driver.find_element(*self.SELECTORS['end_time'])
        end_time_input.clear()
        end_time_input.send_keys(data["end_time"])

        time.sleep(3)

        # Fill optional fields if provided
        if data.get('description'):
            try:
                service_select = self.driver.find_element(*self.SELECTORS['description'])
                service_select.clear()
                service_select.send_keys(str(data['description']))
            except NoSuchElementException:
                print("Description not found")

        for field in ['switches', 'interfaces', 'links']:
            if field in data:
                item_select = Select(self.driver.find_element(*self.SELECTORS[field]))
                for item in data[field]:
                    item_select.select_by_visible_text(item)

        force_checkbox = self.driver.find_element(*self.SELECTORS['force'])
        force_checkbox.click()
        
    def submit_form(self):
        """Submit the window creation form."""
        submit_button = self.driver.find_element(*self.SELECTORS['submit_button'])
        submit_button.click()
        time.sleep(2)

    def reset_fields(self):
        """Clicks the 'Reset Fields' button."""
        submit_button = self.driver.find_element(*self.SELECTORS['reset_button'])
        submit_button.click()
        time.sleep(2)

    def get_form_messages(self):
        """Get success/error messages from the form."""
        messages = {}

        try:
            success_element = self.driver.find_element(*self.SELECTORS['form_message_title'])
            messages['success'] = success_element.text
        except NoSuchElementException:
            messages['success'] = None
        
        try:
            error_element = self.driver.find_element(*self.SELECTORS['form_message_description'])
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
    
    def verify_windows_via_api(self, data, inserted_time):
        """Verify windows was created via API."""
        start_time = time.time()
        while time.time() - start_time < self.default_timeout:
            try:
                response = requests.get(self.api_base_url)
                if response.status_code == 200:
                    windows = response.json()
                    for window in windows: 
                        dt2 = datetime.fromtimestamp(inserted_time, tz=timezone.utc)
                        dt2 = dt2.strftime("%Y-%m-%dT%H:%M:%S%z")
                        if window.get('inserted_at') > dt2 \
                            and window.get('description') == data['description'] \
                            and window.get('start') == data['start_time'] \
                                and window.get('end') == data['end_time']:
                            return window.get('id')
                time.sleep(2)
            except Exception as e:
                print(f"API check error: {e}")
                time.sleep(2)
        return None

    def cleanup_test_windows(self):
        """Clean up test window via API."""
        try:
            response = requests.get(self.api_base_url)
            if response.status_code == 200:
                windows = response.json()
                for window in windows:
                    delete_response = requests.delete(f"{self.api_base_url}{window.get('id')}")
                    if delete_response.status_code == 200:
                        print(f"Cleaned up window: {window.get('id')}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    def click_list_windows(self):
        """Clicks the 'List Maintenance Windows' button."""
        list_button = self.driver.find_element(*self.SELECTORS['list_windows_button'])
        list_button.click()
        time.sleep(3) # Wait for the list to load

    def get_data_from_table(self, window_id):
        """Gets the id of the window in the table."""
        rows_locator = (By.XPATH, "//*[@id='maintenance-table-list-windows']/tbody/tr")
        try:
            rows = self.driver.find_elements(*rows_locator)
            for row in rows:
                first_col = row.find_element(By.XPATH, "./td[1]")
                row_id = first_col.text
                if row_id == window_id:
                    return row_id

        except NoSuchElementException:
            print("Element not found")
        return None
