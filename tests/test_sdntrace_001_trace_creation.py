import pytest
from tests.utils.sdntrace_page import SDNTRACEPage

@pytest.mark.parametrize("api_url",[("API_SDNTRACE_URL", "http://localhost:18181/api/amlight/sdntrace/v1/trace")], indirect=True)
class TestSDNTraces:
    """Test cases for SDNTraces"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, driver, base_url, api_url, default_timeout):
        """Initialize SDNTRACEPage object before each test."""
        self.sdntrace_page = SDNTRACEPage(driver, base_url, api_url, default_timeout)
        
    def test_001_start_trace_with_required_params(self, sdntrace_test_data):
        """
        Start trace with minimum required fields
        """
        data = sdntrace_test_data["valid_basic_data"]
        
        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"
        
        # Fill and submit form
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_dpid_from_table()
        assert trace_dpid_text == data["dpid"], "Error starting trace - wrong dpid"
        trace_port_text = self.sdntrace_page.get_first_port_from_table()
        assert trace_port_text == data["port"], "Error starting trace - wrong port"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is not None, f"Trace '{data['dpid']}' - '{data['port']}' not found in API"

    def test_002_start_trace_with_optional_fields(self, sdntrace_test_data):
        """
        Start trace with optional fields
        """
        data = sdntrace_test_data["valid_trace"]

        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"

        # Fill and submit form with all optional fields
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_dpid_from_table()
        assert trace_dpid_text == data["dpid"], "Error starting trace - wrong dpid"
        trace_port_text = self.sdntrace_page.get_first_port_from_table()
        assert trace_port_text == data["port"], "Error starting trace - wrong port"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is not None, f"Trace '{data['dpid']}' - '{data['port']}' not found in API"

    def test_003_start_trace_with_non_existent_pdid(self, sdntrace_test_data):
        """
        Start trace with invalid DPID
        """
        data = sdntrace_test_data["non_existent_dpid"]

        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"

        # Fill and submit form with all optional fields
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_dpid_from_table()
        assert trace_dpid_text != data["dpid"], "Invalid trace started"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is None, f"Trace was found in API but dpid is wrong"

    def test_004_start_trace_with_invalid_pdid(self, sdntrace_test_data):
        """
        Start trace with invalid DPID
        """
        data = sdntrace_test_data["invalid_dpid"]

        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"

        # Fill and submit form with all optional fields
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_dpid_from_table()
        assert trace_dpid_text != data["dpid"], "Invalid trace started"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is None, f"Trace was found in API but dpid is wrong"

    @pytest.mark.xfail(reason="A trace was initiated using a non-existent port.")
    def test_005_start_trace_with_non_existent_port(self, sdntrace_test_data):
        """
        Start trace with invalid Port
        """
        data = sdntrace_test_data["non_existent_port"]

        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"

        # Fill and submit form with all optional fields
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_port_from_table()
        assert trace_dpid_text != data["port"], "Invalid trace started"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is None, f"Trace was found in API but port is wrong"

    def test_006_start_trace_with_invalid_port(self, sdntrace_test_data):
        """
        Start trace with invalid Port
        """
        data = sdntrace_test_data["invalid_port"]

        # Navigate to SDNTrace form
        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to navigate to form"

        # Fill and submit form with all optional fields
        self.sdntrace_page.fill_form(data)
        self.sdntrace_page.submit_form()

        # Original verification logic
        self.sdntrace_page.click_view_all_traces()
        trace_dpid_text = self.sdntrace_page.get_first_port_from_table()
        assert trace_dpid_text != data["port"], "Invalid trace started"

        # Verify via API
        trace = self.sdntrace_page.verify_traces_via_api(data["dpid"], data["port"])
        assert trace is None, f"Trace was found in API but port is wrong"
