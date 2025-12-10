import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class SDNTRACEPage:
    """
    Page Object Model for the management page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """
    SELECTORS = {
        # Navigation
        'sdntrace_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Napp sdntrace"]'),
        
        # Form fields
        'dpid': (By.XPATH, "//*[@id='dpid']/div/div/div/input"), 
        'port': (By.XPATH, "//*[@id='in_port']/div/div/div/input"),
        
        # Optional fields
        # Eth Parameters
        'dl_vlan': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div[1]/input"),
        'dl_type': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div[2]/input"),
        'dl_src': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div[3]/input"),
        'dl_dst': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[2]/div/div[4]/input"),
        #  IP Parameters
        'nw_src': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[3]/div/div[1]/div/div[1]/input"),
        'nw_dst': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[3]/div/div[1]/div/div[2]/input"),
        'nw_proto': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[3]/div/div[2]/input"),
        'nw_tos': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[3]/div/div[3]/input"),
        # tP Parameters
        'tp_src': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[4]/div/div[1]/input"),
        'tp_dst': (By.XPATH, "//*[@id='app']/div[1]/div/div[6]/div/div/div[1]/div/div[4]/div/div[2]/input"),

        # Buttons
        'submit_button': (By.XPATH, "//button[contains(., 'Start Trace') and not(@disabled)]"),
        'reset_button': (By.XPATH, "//button[contains(., 'Reset') and not(@disabled)]"),
        'view_all_traces_button': (By.XPATH, "//button[contains(., 'View All Traces') and not(@disabled)]"),
        
        # Messages
        'form_message_title': (By.CLASS_NAME, "notification-text notification-title"),
        'form_message_description': (By.CLASS_NAME, "notification-text notification-description"),
        'validation_error': (By.CSS_SELECTOR, ".validation-error, [class*='error']"),

        # Table element for verification
        'trace_table_first_row_dpid': (By.XPATH,"//*[@id='k-info-wrapper-id']/div/div/div[1]/div/div/table/tbody/tr[1]/td[2]"),
        'trace_table_first_row_port': (By.XPATH,"//*[@id='k-info-wrapper-id']/div/div/div[1]/div/div/table/tbody/tr[1]/td[5]")
    }

    def __init__(self, driver: WebDriver, base_url: str, api_url: str, default_timeout: int):
        self.driver = driver
        self.base_url = base_url
        self.api_base_url = api_url
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    def navigate_to_sdntrace_form(self):
        """Navigate from homepage to SDNTrace form."""
        self.driver.get(self.base_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Click the SDNTrace button to open the form
        mef_button = self.wait.until(EC.element_to_be_clickable(self.SELECTORS['sdntrace_button']))
        mef_button.click()
        
        # Wait for the form to appear
        time.sleep(2)
        
        # Verify that form elements are now visible
        form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[class='k-input'], textarea, select")
        
        if len(form_elements) > 0:
            print(f"✅ Successfully opened form with {len(form_elements)} form elements")
            return True
        else:
            print("❌ No form elements found after clicking the button")
            return False

    def fill_form(self, data):
        """Fill the form with provided data."""
        
        # Fill DPID
        name_input = self.wait.until(EC.presence_of_element_located(self.SELECTORS['dpid']))
        name_input.clear()
        name_input.send_keys(data["dpid"])
        
        # Fill Port
        endpoint_a_input = self.driver.find_element(*self.SELECTORS['port'])
        endpoint_a_input.clear()
        endpoint_a_input.send_keys(data["port"])
        time.sleep(3)
        
        # Fill optional fields if provided
        for field in ['dl_vlan', 'dl_type', 'dl_src', 'dl_src', 'dl_dst', 'nw_src', 'nw_dst', 'nw_proto', 'nw_tos', 'tp_src', 'tp_dst']:
            if data.get(field):
                try:
                    service_select = self.driver.find_element(*self.SELECTORS[field])
                    service_select.clear()
                    service_select.send_keys(str(data[field]))
                except NoSuchElementException:
                    print(f"{field} not found")
        
    def submit_form(self):
        """Submit the form."""
        submit_button = self.driver.find_element(*self.SELECTORS['submit_button'])
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

    def verify_traces_via_api(self, dpid, port):
        """Verify trace via API."""
        start_time = time.time()
        while time.time() - start_time < self.default_timeout:
            try:
                response = requests.get(self.api_base_url)
                if response.status_code == 200:
                    traces = response.json()
                    traces = [(entry["dpid"], entry["port"]) for _, data in traces.items() for entry in data["result"] if "dpid" in entry]
                    if (dpid, int(port)) in traces:
                        return traces
                time.sleep(2)
            except Exception as e:
                print(f"API check error: {e}")
                time.sleep(2)
        return None

    def click_view_all_traces(self):
        """Clicks the 'View All Traces' button."""
        list_button = self.driver.find_element(*self.SELECTORS['view_all_traces_button'])
        list_button.click()
        time.sleep(3) # Wait for the list to load

    def get_first_dpid_from_table(self):
        """Gets the first trace in the table."""
        trace_dpid = self.driver.find_element(*self.SELECTORS['trace_table_first_row_dpid'])
        return trace_dpid.text
    
    def get_first_port_from_table(self):
        """Gets the first trace in the table."""
        trace_dpid = self.driver.find_element(*self.SELECTORS['trace_table_first_row_port'])
        return trace_dpid.text