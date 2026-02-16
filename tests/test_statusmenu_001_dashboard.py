import time

import pytest
from tests.utils.statusmenu_page import StatusmenuPage


@pytest.mark.parametrize("api_url", [("API_MEFELINE_URL", "http://localhost:18181/api/kytos/mef_eline/v2/evc/")],
                         indirect=True)
class TestStatusMenu:
    """Positive test cases for successful status checks"""

    @pytest.fixture(autouse=True)
    def setup_method(self, driver, base_url, api_url, default_timeout):
        """Initialize Status menu object before each test."""
        self.statusmenu_page = StatusmenuPage(driver, base_url, api_url, default_timeout)

    def test_001_check_switches(self):

        # Navigate to status menu
        assert self.statusmenu_page.navigate_to_statusmenu(), "Failed to navigate to Pathfinder form"

        # check number of switches,links and interfaces and filters
        assert self.statusmenu_page.check_switches(), "switches data not consistent"
        assert self.statusmenu_page.check_switches_filters(), "switch filters not working"
        assert self.statusmenu_page.check_links(), "links data not consistent"
        assert self.statusmenu_page.check_links_filters(), "links filters not working"
        assert self.statusmenu_page.check_interfaces(), "interfaces data not consistent"
        assert self.statusmenu_page.check_interfaces_filters(), "interfaces filters not working"
