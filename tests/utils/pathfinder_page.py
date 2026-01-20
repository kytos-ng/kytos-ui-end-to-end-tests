import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class PathfinderPage:
    """
    Page Object Model for the EVC creation and management page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """
    SELECTORS = {
        # Navigation
        'napp_pathfinder_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Napp Pathfinder"]'),

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

    def navigate_to_pathfinder_form(self):
        """Navigate from homepage to EVC creation form."""
        print("Navigating to Pathfinder form...")
        self.driver.get(self.base_url)

        # Wait for page to load
        time.sleep(3)

        # Click the Napp Pathfinder button to open the request circuit form
        pathfinder_button = self.wait.until(EC.element_to_be_clickable(self.SELECTORS['napp_pathfinder_button']))
        pathfinder_button.click()

        # Wait for the form to appear
        time.sleep(2)

        # Verify that form elements are now visible
        form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[class='k-input'], textarea, select")

        if len(form_elements) > 0:
            print(f"✅ Successfully opened Pathfinder form with {len(form_elements)} form elements")
            return True
        else:
            print("❌ No form elements found after clicking pathfinder button")
            return False

    def fill_path_form(self, test_data):
        """Fill the EVC creation form with provided data."""

        # Fill source
        source_input = self.wait.until(EC.presence_of_element_located(self.SELECTORS['source_input']))
        source_input.clear()
        source_input.send_keys(test_data["source"])
        source_input.send_keys(Keys.ENTER)

        # Fill destination
        destination_input = self.driver.find_element(*self.SELECTORS['destination_input'])
        destination_input.clear()
        destination_input.send_keys(test_data["destination"])
        destination_input.send_keys(Keys.ENTER)
        time.sleep(3)

        # Fill optional fields if provided
        if test_data.get("bandwidth"):
            try:
                bandwidth = self.driver.find_element(*self.SELECTORS['bandwidth'])
                bandwidth.clear()
                bandwidth.send_keys(str(test_data["bandwidth"]))
            except NoSuchElementException:
                print("Bandwidth field not found")

        if test_data.get("reliability"):
            try:
                reliability = self.driver.find_element(*self.SELECTORS['reliability'])
                reliability.clear()
                reliability.send_keys(str(test_data["reliability"]))
            except NoSuchElementException:
                print("reliability field not found")

        if test_data.get("delay"):
            try:
                delay = self.driver.find_element(*self.SELECTORS['delay'])
                delay.clear()
                delay.send_keys(str(test_data["delay"]))
            except NoSuchElementException:
                print("delay field not found")

        if test_data.get("utilization"):
            try:
                utilization = self.driver.find_element(*self.SELECTORS['utilization'])
                utilization.clear()
                utilization.send_keys(str(test_data["utilization"]))
            except NoSuchElementException:
                print("utilization field not found")

        if test_data.get("priority"):
            try:
                priority = self.driver.find_element(*self.SELECTORS['priority'])
                priority.clear()
                priority.send_keys(str(test_data["priority"]))
            except NoSuchElementException:
                print("priority field not found")

        if test_data.get("spf_max_paths"):
            try:
                spf_max_paths = self.driver.find_element(*self.SELECTORS['spf_max_paths'])
                spf_max_paths.clear()
                spf_max_paths.send_keys(str(test_data["spf_max_paths"]))
            except NoSuchElementException:
                print("spf_max_paths field not found")

        if test_data.get("spf_max_path_cost"):
            try:
                spf_max_path_cost = self.driver.find_element(*self.SELECTORS['spf_max_path_cost'])
                spf_max_path_cost.clear()
                spf_max_path_cost.send_keys(str(test_data["spf_max_path_cost"]))
            except NoSuchElementException:
                print("spf_max_path_cost field not found")


    def submit_form(self):
        """Submit the EVC creation form."""
        submit_button = self.driver.find_element(*self.SELECTORS['submit_button'])
        submit_button.click()
        time.sleep(2)

    def get_paths(self):
        """print paths."""
        paths = self.driver.find_element(*self.SELECTORS['paths'])
        paths.click()
        path_table=self.driver.find_elements(*self.SELECTORS['path_table'])

        for el in path_table:
            print(el.text)

        return len(path_table)
