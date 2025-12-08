import pytest
from tests.utils.evc_page import EVCPage

@pytest.mark.parametrize("api_url",[("API_MEFELINE_URL", "http://localhost:18181/api/kytos/mef_eline/v2/evc/")], indirect=True)
class TestPositiveEVCCreation:
    """Positive test cases for successful EVC creation"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, driver, base_url, api_url, default_timeout):
        """Initialize EVCPage object before each test."""
        self.evc_page = EVCPage(driver, base_url, api_url, default_timeout)

    def teardown_method(self):
        """Cleanup after each test."""
        test_circuits = [
            "Test_Circuit_001",
            "Full_Feature_Circuit", 
            "VLAN_Range_Circuit",
            "Performance_Test_Circuit"
        ]
        for circuit in test_circuits:
            self.evc_page.cleanup_test_circuit(circuit)
    
    def test_001_create_basic_evc_minimum_fields(self, evc_test_data):
        """
        Create Basic EVC with Minimum Required Fields
        
        Objective: Verify successful creation of EVC with only required fields
        """
        circuit_data = evc_test_data["valid_circuits"][0] 
        
        # Navigate to EVC creation form
        assert self.evc_page.navigate_to_evc_form(), "Failed to navigate to EVC creation form"
        
        # Fill and submit form
        self.evc_page.fill_circuit_form(circuit_data)
        self.evc_page.submit_form()

        # Original verification logic
        self.evc_page.click_list_installed_evcs()
        evc_created_text = self.evc_page.get_first_evc_name_from_table()
        assert evc_created_text == circuit_data["name"], "Error creating circuit"

        # Verify via API
        circuit_id = self.evc_page.verify_circuit_via_api(circuit_data["name"])
        assert circuit_id is not None, f"Circuit '{circuit_data['name']}' not found in API"
        
        print(f"✅ TC_001 PASSED. EVC with circuit id {circuit_id} created and verified successfully")

    def test_002_create_evc_all_optional_fields(self, evc_test_data):
        """
        Create EVC with All Optional Fields

        Objective: Verify EVC creation with all fields populated
        """
        circuit_data = evc_test_data["valid_circuits"][1]

        # Navigate to EVC creation form
        assert self.evc_page.navigate_to_evc_form(), "Failed to navigate to EVC creation form"

        # Fill and submit form with all optional fields
        self.evc_page.fill_circuit_form(circuit_data)
        self.evc_page.submit_form()

        # Verify via API
        circuit_id = self.evc_page.verify_circuit_via_api(circuit_data["name"])
        assert circuit_id is not None, f"Circuit '{circuit_data['name']}' not found in API"

        print(f"✅ TC_002 PASSED: Full-feature circuit created with ID {circuit_id}")

    def test_003_create_evc_vlan_range(self, evc_test_data):
        """
        Create EVC with VLAN Range

        Objective: Verify EVC creation with VLAN range notation
        """
        circuit_data = evc_test_data["valid_circuits"][2]

        # Navigate to EVC creation form
        assert self.evc_page.navigate_to_evc_form(), "Failed to navigate to EVC creation form"

        # Fill and submit form with VLAN ranges
        self.evc_page.fill_circuit_form(circuit_data)
        self.evc_page.submit_form()

        # Verify via API
        circuit_id = self.evc_page.verify_circuit_via_api(circuit_data["name"])
        assert circuit_id is not None, f"Circuit '{circuit_data['name']}' not found in API"

        print(f"✅ TC_003 PASSED: VLAN range circuit created with ID {circuit_id}")
