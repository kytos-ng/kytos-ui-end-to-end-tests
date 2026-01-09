import pytest
from tests.utils.pathfinder_page import PathfinderPage


@pytest.mark.parametrize("api_url", [("API_MEFELINE_URL", "http://localhost:18181/api/kytos/mef_eline/v2/evc/")],
                         indirect=True)
class TestPositiveEVCCreation:
    """Positive test cases for successful EVC creation"""

    @pytest.fixture(autouse=True)
    def setup_method(self, driver, base_url, api_url, default_timeout):
        """Initialize EVCPage object before each test."""
        self.pathfinder_page = PathfinderPage(driver, base_url, api_url, default_timeout)

    def test_001_calculate_basic_path(self, pathfinder_test_data):
        """
        Create Basic EVC with Minimum Required Fields

        Objective: Verify successful creation of EVC with only required fields
        """
        test_data = pathfinder_test_data["valid_data"][0]

        # Navigate to EVC creation form
        assert self.pathfinder_page.navigate_to_pathfinder_form(), "Failed to navigate to Pathfinder form"

        # Fill and submit form
        self.pathfinder_page.fill_path_form(test_data)
        self.pathfinder_page.submit_form()

        # Original verification logic
        paths=self.pathfinder_page.get_paths()
        assert paths>0, "no paths found"
        print(f"✅ TC_001 PASSED. paths calculated")

    def test_002_calculate_path_with_fields(self, pathfinder_test_data):
        """
        Create Basic EVC with Minimum Required Fields

        Objective: Verify successful creation of EVC with only required fields
            """
        test_data = pathfinder_test_data["valid_data"][1]

        # Navigate to EVC creation form
        assert self.pathfinder_page.navigate_to_pathfinder_form(), "Failed to navigate to Pathfinder form"

        # Fill and submit form
        self.pathfinder_page.fill_path_form(test_data)
        self.pathfinder_page.submit_form()

        # Original verification logic
        paths = self.pathfinder_page.get_paths()
        assert paths > 0, "no paths found"
        print(f"✅ TC_002 PASSED. paths calculated")


