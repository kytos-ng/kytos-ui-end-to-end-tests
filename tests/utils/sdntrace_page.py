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
        'trace_table_rows': (By.CSS_SELECTOR, "div[id^='k-info-wrapper-id'] table tbody tr")
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
    
    def verify_traces_via_api(self, trace_id):
        """Verify trace via API."""
        start_time = time.time()
        while time.time() - start_time < self.default_timeout:
            try:
                response = requests.get(self.api_base_url)
                if response.status_code == 200:
                    traces = response.json()
                    traces_id = [data['request_id'] for data in traces.values()]
                    if trace_id in traces_id:
                        return trace_id
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
    
    def get_id_traces_in_table(self):
        """Return list of traces id in the table."""
        try:
            self.wait.until(EC.presence_of_element_located(self.SELECTORS['trace_table_rows']))
        except Exception as e:
            print(f"The trace table did not appear within the expected time. {e}")
            return False
        
        rows = self.driver.find_elements(*self.SELECTORS['trace_table_rows'])
        
        ids = set([int(row.find_element(By.XPATH, "./td[1]").text.strip()) for row in rows])
        return list(ids)

    def is_trace_in_table(self, list_traces, dpid, port):
        """Search for a row with dpid and port"""
        _ID_IN_ROW = "./td[1]"      
        _DPID_IN_ROW = "./td[2]"      
        _PORT_IN_ROW = "./td[5]"
        try:
            self.wait.until(EC.presence_of_element_located(self.SELECTORS['trace_table_rows']))
        except Exception as e:
            print(f"The trace table did not appear within the expected time. {e}")
            return False
        
        rows = self.driver.find_elements(*self.SELECTORS['trace_table_rows'])
        
        for row in rows:
            try:
                row_id = int(row.find_element(By.XPATH, _ID_IN_ROW).text.strip())
                row_dpid = row.find_element(By.XPATH, _DPID_IN_ROW).text.strip()
                row_port = row.find_element(By.XPATH, _PORT_IN_ROW).text.strip()
                if row_dpid == dpid and row_port == port and row_id not in list_traces:
                    return row_id
            except:
                continue  
        return None
 
    def click_fetch_button(self, list_traces, dpid, port):
        """Click on Fetch"""
        selector = (By.XPATH, "//button[.//text()[contains(., 'Fetch Trace')]]")

        fetch_button = None
        try:
            fetch_button = self.wait.until(EC.element_to_be_clickable(selector))
        except Exception:
            raise AssertionError("Fetch button not found")

        # Scroll + clic con JavaScript (infalible)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fetch_button)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", fetch_button)

        return self.is_trace_in_table(list_traces, dpid, port)

    def click_view_button_for_trace(self, trace_id):
        """Click on View button for trace_id"""
        
        buttons = self.driver.find_elements(By.XPATH, "//button[contains(normalize-space(.), 'View') or contains(. ,'View')]")
        rows = self.driver.find_elements(*self.SELECTORS['trace_table_rows'])
        trs_info = []
        for row in rows:
            loc = row.location_once_scrolled_into_view
            y = loc.get("y", loc.get("y", 0)) if isinstance(loc, dict) else row.location.get("y", 0)
            id_text = row.find_element(By.XPATH, "./td[1]").text.strip()
            trs_info.append({"element": row, "y": float(y), "id": id_text})
        if not trs_info:
            raise AssertionError(f"No table rows available to match trace_id '{trace_id}'")
        # sort trs by y (top -> bottom)
        trs_info.sort(key=lambda x: x["y"])

        for btn in buttons:
            btn_loc = btn.location_once_scrolled_into_view
            btn_y = btn_loc.get("y", btn.location.get("y", 0)) if isinstance(btn_loc, dict) else btn.location.get("y", 0)
            candidate = None
            for idx, tr in enumerate(trs_info):
                if tr["y"] > btn_y:
                    candidate = (idx, tr)
                    break
            if candidate is None:
                candidate = (len(trs_info)-1, trs_info[-1])
            idx, tr_info = candidate
            check_candidates = [tr_info]
            if idx + 1 < len(trs_info):
                check_candidates.append(trs_info[idx + 1])

            match_found = False
            for check in check_candidates:
                id_val = (check["id"] or "").strip()
                if id_val == str(trace_id):
                    match_found = True
                    break

            if match_found:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.2)
                self.driver.execute_script("arguments[0].click();", btn)
                print(f"✔ Clicked View button matched to trace_id '{trace_id}'")
                
                return self.is_trace_id_in_table(trace_id)
            
        raise AssertionError(f"Could not locate/click View for trace_id '{trace_id}'")
        
    def is_trace_id_in_table(self, trace_id):
        """check that the trace is displayed"""
        try:
            self.wait.until(EC.presence_of_element_located(self.SELECTORS['trace_table_rows']))
        except Exception as e:
            return False
        rows = self.driver.find_elements(*self.SELECTORS['trace_table_rows'])
        for row in rows:
            try:
                row_id = int(row.find_element(By.XPATH, "./td[1]").text.strip())
                if row_id == trace_id:
                    return row_id
            except:
                continue  
        return None