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
    Page Object Model for the Status menu page in Kytos UI.
    Encapsulates all UI interactions and locators.
    """
    SELECTORS = {
        # Navigation
        'statusmenu_button': (By.CSS_SELECTOR, 'button[data-test="main-button"][title="Status Menu"]')
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
        """Navigate from homepage to Status menu form."""
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

    def check_switches_filters(self):
        switchName_Filter=self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/table/thead/tr[2]/th[1]/input")
        switchName_Filter.click()
        filter_test_value=os.getenv('switch_filter_value')
        switchName_Filter.send_keys(filter_test_value)
        table = self.driver.find_element(By.XPATH, "//table[@data-test='switch_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_switches_filter = len(rows)
        name_flag=0
        if num_switches_filter==0:
            name_flag=1
        else:
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[1].text)
                if cells[1].text==filter_test_value:
                    name_flag=1

        for _ in range(len(filter_test_value)):
            switchName_Filter.send_keys(Keys.BACKSPACE)

        switchStatus_Filter=self.driver.find_element(By.XPATH, "//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/table/thead/tr[2]/th[2]/input")
        switchStatus_Filter.click()
        switchStatus_Filter.send_keys('up')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='switch_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_switches_filter = len(rows)
        status_flag = 0
        if num_switches_filter == 0:
            status_flag = 1
        else:
            status_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[2].text)
                if cells[2].text != 'UP':
                    status_flag = 0

        for _ in range(2):
            switchStatus_Filter.send_keys(Keys.BACKSPACE)

        switchEnabled_Filter=self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/table/thead/tr[2]/th[4]/input")
        switchEnabled_Filter.click()
        switchEnabled_Filter.send_keys('true')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='switch_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_switches_filter = len(rows)
        enabled_flag = 0
        if num_switches_filter == 0:
            enabled_flag = 1
        else:
            enabled_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[4].text)
                if cells[4].text != 'true':
                    enabled_flag = 0

        switch_table=self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/label")
        switch_table.click()
        time.sleep(2)

        if name_flag==1 and status_flag==1 and enabled_flag==1:
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

    def check_links_filters(self):
        linkName_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/table/thead/tr[2]/th[1]/input")
        linkName_Filter.click()
        filter_test_value = os.getenv('link_filter_value')
        linkName_Filter.send_keys(filter_test_value)
        table = self.driver.find_element(By.XPATH, "//table[@data-test='link_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_links_filter = len(rows)
        name_flag = 0
        if num_links_filter == 0:
            name_flag = 1
        else:
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[1].text)
                if cells[1].text == filter_test_value:
                    name_flag = 1

        for _ in range(len(filter_test_value)):
            linkName_Filter.send_keys(Keys.BACKSPACE)

        linkStatus_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/table/thead/tr[2]/th[2]/input")
        linkStatus_Filter.click()
        linkStatus_Filter.send_keys('up')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='link_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_links_filter = len(rows)
        status_flag = 0
        if num_links_filter == 0:
            status_flag = 1
        else:
            status_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[2].text)
                if cells[2].text != 'UP':
                    status_flag = 0

        for _ in range(2):
            linkStatus_Filter.send_keys(Keys.BACKSPACE)

        linkEnabled_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/table/thead/tr[2]/th[4]/input")
        linkEnabled_Filter.click()
        linkEnabled_Filter.send_keys('true')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='link_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_links_filter = len(rows)
        enabled_flag = 0
        if num_links_filter == 0:
            enabled_flag = 1
        else:
            enabled_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 6, f"Expected 6 tds, found {len(cells)}"
                print(cells[4].text)
                if cells[4].text != 'true':
                    enabled_flag = 0

        link_table = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[2]/label")
        link_table.click()
        time.sleep(2)

        if name_flag == 1 and status_flag == 1 and enabled_flag == 1:
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

    def check_interfaces_filters(self):
        interfaceNode_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div/div[2]/table/thead/tr[2]/th[1]/input")
        interfaceNode_Filter.click()
        filter_test_value = os.getenv('interface_filter_value')
        interfaceNode_Filter.send_keys(filter_test_value)
        table = self.driver.find_element(By.XPATH, "//table[@data-test='interface_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_interface_filter = len(rows)
        name_flag = 0
        if num_interface_filter == 0:
            name_flag = 1
        else:
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 7, f"Expected 7 tds, found {len(cells)}"
                print(cells[1].text)
                if cells[1].text == filter_test_value:
                    name_flag = 1

        for _ in range(len(filter_test_value)):
            interfaceNode_Filter.send_keys(Keys.BACKSPACE)

        interfaceStatus_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div/div[2]/table/thead/tr[2]/th[3]/input")
        interfaceStatus_Filter.click()
        interfaceStatus_Filter.send_keys('up')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='interface_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_interface_filter = len(rows)
        status_flag = 0
        if num_interface_filter == 0:
            status_flag = 1
        else:
            status_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 7, f"Expected 7 tds, found {len(cells)}"
                print(cells[3].text)
                if cells[3].text != 'UP':
                    status_flag = 0

        for _ in range(2):
            interfaceStatus_Filter.send_keys(Keys.BACKSPACE)

        interfaceEnabled_Filter = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div/div[2]/table/thead/tr[2]/th[5]/input")
        interfaceEnabled_Filter.click()
        interfaceEnabled_Filter.send_keys('true')

        table = self.driver.find_element(By.XPATH, "//table[@data-test='interface_table']")
        rows = table.find_elements(By.XPATH, ".//tbody/tr")
        num_interface_filter = len(rows)
        enabled_flag = 0
        if num_interface_filter == 0:
            enabled_flag = 1
        else:
            enabled_flag = 1
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                assert len(cells) == 7, f"Expected 7 tds, found {len(cells)}"
                print(cells[5].text)
                if cells[5].text != 'true':
                    enabled_flag = 0

        interface_table = self.driver.find_element(By.XPATH,"//*[@id='app']/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div[3]/label")
        interface_table.click()
        time.sleep(2)

        if name_flag == 1 and status_flag == 1 and enabled_flag == 1:
            return True