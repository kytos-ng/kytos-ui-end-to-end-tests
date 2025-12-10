import pytest
import time
from tests.utils.maintenance_page import MaintenancePage

@pytest.mark.parametrize("api_url",[("API_MAINTENANCE_URL", "http://localhost:18181/api/kytos/maintenance/v1/")], indirect=True)
@pytest.mark.usefixtures("driver", "base_url", "api_url", "default_timeout")
class TestMaintenance:
    """Test cases for Maintenance"""
    
    @pytest.fixture(scope="class", autouse=True) 
    def setup_class(self, request, driver, base_url, api_url, default_timeout): 
        """ Initialize MaintenancePage object once per class. """ 
        request.cls.maintenance_page = MaintenancePage(driver, base_url, api_url, default_timeout) 
        yield 
        try: 
            request.cls.maintenance_page.cleanup_test_windows() 
        except Exception as e: 
            print(f"Error during class cleanup: {e}")

    def test_001_create_maintenance_window_with_valid_data(self, maintenance_test_data):
        """
        Create Maintenance Window with a Switch
        
        Objective: Verify successful creation of a maintenance window.
        """
        for data in maintenance_test_data["valid_data"]:
            # 1. Navigate to Maintenance tab
            assert self.maintenance_page.navigate_to_maintenance_tab(), "Failed to navigate to Maintenance tab"
            
            # 2. Fill and submit form
            inserted_time = time.time()
            self.maintenance_page.fill_maintenance_form(data)
            self.maintenance_page.submit_form()
            
            # 3. Verify via API
            window_id = self.maintenance_page.verify_windows_via_api(data, inserted_time)
            assert window_id is not None, "Error creating Maintenance Window: not found in table"
            
            # 4. Verify creation
            self.maintenance_page.click_list_windows()
            window_id_text = self.maintenance_page.get_data_from_table(window_id)
            assert window_id_text != None, "Error creating window"

    def test_002_create_maintenance_window_with_invalid_data(self, maintenance_test_data):
        """Using invalid data"""

        for data in maintenance_test_data['invalid_data']:
            # 1. Navigate to Maintenance tab
            assert self.maintenance_page.navigate_to_maintenance_tab(), "Failed to navigate to Maintenance tab"
            
            # 2. Fill and submit form
            inserted_time = time.time()
            self.maintenance_page.fill_maintenance_form(data)
            self.maintenance_page.submit_form()
            
            # 3. Verify via API
            window_id = self.maintenance_page.verify_windows_via_api(data, inserted_time)
            assert window_id is None, "Maintenance Window created with invalid data"

