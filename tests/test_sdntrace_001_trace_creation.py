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

    def test_007_multiple_traces_and_fetch_functionality(self, sdntrace_test_data):
        """
        Start multiple traces, verify they appear in the table,
        test the 'Fetch' button refreshes the trace result
        and test the 'View' button shows correct details.
        """
        trace1_data = sdntrace_test_data["valid_basic_data"]
        trace2_data = sdntrace_test_data["valid_trace"]

        assert self.sdntrace_page.navigate_to_sdntrace_form(), "Failed to open SDNTrace form"

        self.sdntrace_page.click_view_all_traces()
        list_traces = self.sdntrace_page.get_id_traces_in_table()

        # Step 1: Start first trace 
        self.sdntrace_page.fill_form(trace1_data)
        self.sdntrace_page.submit_form()

        # Step 2: Start second trace 
        self.sdntrace_page.fill_form(trace2_data)
        self.sdntrace_page.submit_form()

        # Step 3: Click "Fetch" button to refresh results
        fetch_id = self.sdntrace_page.click_fetch_button(list_traces, trace2_data["dpid"], trace2_data["port"])
        assert fetch_id is not None, "Trace not found with Fetch Trace"

        # Step 4: Verify both appear
        self.sdntrace_page.click_view_all_traces()
        id_trace1 = self.sdntrace_page.is_trace_in_table(list_traces, trace1_data["dpid"], trace1_data["port"])
        assert id_trace1 is not None, "First trace not found in table"
        id_trace2 = self.sdntrace_page.is_trace_in_table(list_traces, trace2_data["dpid"], trace2_data["port"])
        assert id_trace2 is not None, "Second trace not found in table"

        # Step 5: Click "View" on the second trace
        view_id = self.sdntrace_page.click_view_button_for_trace(id_trace2)
        assert view_id is not None, "Trace not found with Fetch Trace"

        # Verify via API
        api_trace = self.sdntrace_page.verify_traces_via_api(trace1_data["dpid"], trace1_data["port"])
        assert api_trace is not None, f"Trace '{id_trace1}' not found in API"
    
        api_trace = self.sdntrace_page.verify_traces_via_api(trace2_data["dpid"], trace2_data["port"])
        assert api_trace is not None, f"Trace '{id_trace2}' not found in API"