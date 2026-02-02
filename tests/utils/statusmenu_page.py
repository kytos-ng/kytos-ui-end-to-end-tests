import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class StatusmenuPage:
    """
    Page Object Model for the EVC creation and management page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """
    SELECTORS = {
        # Navigation
        'statusmenu_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Status Menu"]'),

        # Form fields
        'source_input': (By.XPATH, "//*[@id='source']/div/div/div/input"),
        'destination_input': (By.XPATH, "//*[@id='destination']/div/div/div/input"),
        'paths': (By.XPATH,"//*[@id='app']/section[2]/div[1]/div/button[1]"),
        'path_table': (By.CLASS_NAME,"k-property-panel"),
        'bandwidth': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[5]/div[3]/input"),
        'reliability': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[6]/div[3]/input"),
        'delay': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[7]/div[3]/input"),

        # Optional fields
        'utilization': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[8]/div[3]/input"),
        'priority': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[9]/div[3]/input"),
        'spf_max_paths': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[14]/div/div/input"),
        'spf_max_path_cost': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[15]/div/div/input"),

        # Buttons
        'submit_button': (By.XPATH, "//*[@id='app']/div[1]/div/div[7]/div/div/div/div/div[16]/button")
    }

    def __init__(self, driver: WebDriver, base_url: str, api_url: str, default_timeout: int):
        self.driver = driver
        self.base_url = base_url
        self.api_base_url = api_url
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    def _find(self, locator_name):
        """Helper to find an element by locator name."""
        by, value = self.SELECTORS[locator_name]
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def navigate_to_statusmenu(self):
        """Navigate from homepage to EVC creation form."""
        print("Navigating to Status Menu...")
        self.driver.get(self.base_url)

        # Wait for page to load
        time.sleep(3)

        # Click the Napp Pathfinder button to open the request circuit form
        statusmenu_button = self.wait.until(EC.element_to_be_clickable(self.SELECTORS['statusmenu_button']))
        statusmenu_button.click()

        # Wait for the form to appear
        time.sleep(2)

        return True

    def check_switches(self):

        table = self.driver.find_element(By.XPATH, "//table[@data-test='switch_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        num_switches_ui=len(rows)

        try:
            response = requests.get(os.getenv('API_SWITCHES_URL'))
            if response.status_code == 200:
                switches = response.json()
        except Exception as e:
            print(f"API check error: {e}")

        # Get count of switches
        num_switches_api = len(switches['switches'])
        print(f"Number of switches: {num_switches_api}")

        if num_switches_ui==num_switches_api:
            return True

    def check_links(self):
        table = self.driver.find_element(By.XPATH, "//table[@data-test='link_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        num_links_ui = len(rows)

        try:
            response = requests.get(os.getenv('API_LINKS_URL'))
            if response.status_code == 200:
                links = response.json()
        except Exception as e:
            print(f"API check error: {e}")

        # Get count of links
        num_links_api = len(links['links'])
        print(f"Number of links: {num_links_api}")

        if num_links_ui == num_links_api:
            return True


    def check_interfaces(self):
        table = self.driver.find_element(By.XPATH, "//table[@data-test='interface_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")

        num_interfaces_ui = len(rows)

        try:
            response = requests.get(os.getenv('API_INTERFACES_URL'))
            if response.status_code == 200:
                interfaces = response.json()
        except Exception as e:
            print(f"API check error: {e}")

        # Get count of interfaces
        num_interfaces_api = len(interfaces['interfaces'])
        print(f"Number of interfaces: {num_interfaces_api}")

        if num_interfaces_ui == num_interfaces_api:
            return True
