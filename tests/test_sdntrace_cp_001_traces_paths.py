import pytest
from tests.utils.sdntrace_cp_page import SDNTraceCPPage


@pytest.mark.parametrize(
    "api_url",
    [("API_SDNTRACE_CP_URL", "http://190.103.184.198:18181/api/amlight/sdntrace_cp/v1/trace")],
    indirect=True,
)
class TestSDNTraceCP:
    """End-to-end test cases for the SDNTrace CP (Control Plane) tab in Kytos NG UI."""

    @pytest.fixture(autouse=True)
    def setup_method(self, driver, base_url, api_url, default_timeout):
        """Instantiate SDNTraceCPPage before every test in this class."""
        self.page = SDNTraceCPPage(driver, base_url, api_url, default_timeout)

    # ------------------------------------------------------------------
    # Positive tests
    # ------------------------------------------------------------------

    def test_001_open_sdntrace_cp_form(self):
        """
        Verify that the SDNTrace CP form opens correctly.

        Objective: Confirm that clicking the SDNTrace CP button renders the form
        with at least one interactive input element.
        """
        assert self.page.navigate_to_sdntrace_cp_form(), (
            "SDNTrace CP form did not open – no input elements found"
        )

    @pytest.mark.xfail(reason="CP trace returns empty result when no OpenFlow flows are installed on the switch.")
    def test_002_start_trace_with_required_params(self, sdntrace_cp_test_data):
        """
        Start a control-plane trace using only the mandatory fields (dpid + port).

        Objective: Verify a trace is triggered and its entry appears both in the
        UI table and via the REST API.
        """
        data = sdntrace_cp_test_data["valid_basic_data"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_dpid_from_table() == data["dpid"], (
            "Table shows wrong DPID after trace submission"
        )
        assert self.page.get_first_port_from_table() == data["port"], (
            "Table shows wrong port after trace submission"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is not None, (
            f"Trace dpid='{data['dpid']}' port='{data['port']}' not found via API"
        )

    @pytest.mark.xfail(reason="CP trace returns empty result when no OpenFlow flows are installed on the switch.")
    def test_003_start_trace_with_all_optional_fields(self, sdntrace_cp_test_data):
        """
        Start a control-plane trace with all optional Ethernet/IP/Transport fields.

        Objective: Ensure the form accepts and submits the full set of optional
        parameters and that the resulting trace is recorded correctly.
        """
        data = sdntrace_cp_test_data["valid_full_data"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_dpid_from_table() == data["dpid"], (
            "Table shows wrong DPID after full-field trace submission"
        )
        assert self.page.get_first_port_from_table() == data["port"], (
            "Table shows wrong port after full-field trace submission"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is not None, (
            f"Full-field trace dpid='{data['dpid']}' port='{data['port']}' not found via API"
        )

    def test_004_reset_form_clears_fields(self, sdntrace_cp_test_data):
        """
        Verify that the Reset button clears previously entered values.

        Objective: After filling the form and clicking Reset, all inputs should
        return to their default (empty) state.
        """
        data = sdntrace_cp_test_data["valid_basic_data"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.reset_form()

        # After reset the dpid field should be empty (use _find_visible to get the right element)
        dpid_elem = self.page._find_visible('dpid')
        assert dpid_elem.get_attribute("value") == "", (
            "DPID field was not cleared after Reset"
        )

    # ------------------------------------------------------------------
    # Negative tests
    # ------------------------------------------------------------------

    def test_005_start_trace_with_non_existent_dpid(self, sdntrace_cp_test_data):
        """
        Attempt to start a trace for a switch that is not present in the topology.

        Objective: The UI should not record a successful trace for an unknown DPID,
        and the API should return no matching entry.
        """
        data = sdntrace_cp_test_data["non_existent_dpid"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_dpid_from_table() != data["dpid"], (
            "A trace entry appeared for a non-existent DPID"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is None, "API returned a trace for a non-existent DPID"

    def test_006_start_trace_with_invalid_dpid(self, sdntrace_cp_test_data):
        """
        Attempt to start a trace with a syntactically invalid DPID value.

        Objective: The system should reject or ignore the request; no trace entry
        should appear for the invalid DPID in the API.
        """
        data = sdntrace_cp_test_data["invalid_dpid"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_dpid_from_table() != data["dpid"], (
            "A trace entry appeared for an invalid DPID"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is None, "API returned a trace for an invalid DPID"

    def test_007_start_trace_with_non_existent_port(self, sdntrace_cp_test_data):
        """
        Attempt to start a trace referencing a port that does not exist on the switch.

        Objective: The system should not record a trace for a port that is absent
        in the topology.
        """
        data = sdntrace_cp_test_data["non_existent_port"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_port_from_table() != data["port"], (
            "A trace entry appeared for a non-existent port"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is None, "API returned a trace for a non-existent port"

    def test_008_start_trace_with_invalid_port(self, sdntrace_cp_test_data):
        """
        Attempt to start a trace supplying a non-numeric port value.

        Objective: The system should reject or ignore the request; no trace for
        the invalid port value should appear in the API.
        """
        data = sdntrace_cp_test_data["invalid_port"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()
        assert self.page.get_first_port_from_table() != data["port"], (
            "A trace entry appeared for an invalid port value"
        )

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is None, "API returned a trace for an invalid port value"

    def test_009_start_trace_with_invalid_nw_tos(self, sdntrace_cp_test_data):
        """
        Attempt to start a trace with an out-of-range nw_tos value.

        Objective: The system should not accept a ToS value outside the valid
        range (0-15); no trace should be recorded.
        """
        data = sdntrace_cp_test_data["invalid_nw_tos"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        trace = self.page.verify_trace_via_api(data["dpid"], data["port"])
        assert trace is None, "API returned a trace for an invalid nw_tos value"

    @pytest.mark.xfail(reason="CP trace returns empty result when no OpenFlow flows are installed on the switch.")
    def test_010_view_all_traces_lists_previous_results(self, sdntrace_cp_test_data):
        """
        Verify that 'View All Traces' shows previously submitted traces.

        Objective: After a successful trace, clicking 'View All Traces' must
        render a table whose first row corresponds to the most recent trace.
        """
        data = sdntrace_cp_test_data["valid_basic_data"]

        assert self.page.navigate_to_sdntrace_cp_form(), "Failed to navigate to SDNTrace CP form"

        self.page.fill_form(data)
        self.page.submit_form()

        self.page.click_view_all_traces()

        dpid_text = self.page.get_first_dpid_from_table()
        port_text = self.page.get_first_port_from_table()

        assert dpid_text != "", "Trace table appears to be empty after View All Traces"
        assert port_text != "", "Port column is empty in the trace results table"
