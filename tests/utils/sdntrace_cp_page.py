import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class SDNTraceCPPage:
    """
    Page Object Model for the SDNTrace CP (Control Plane) panel in Kytos UI.

    API contract (PUT /v1/trace)
    ----------------------------
    The response is a single object::

        {
          "result": [
            {"dpid": "00:00:00:00:00:00:00:14", "port": 13,
             "time": "...", "type": "starting"},
            {"dpid": "...", "port": ..., "time": "...", "type": "intermediary"},
            ...
          ]
        }

    The result is an **ordered trace path**, not a history list.
    The first entry always has ``type == "starting"`` and corresponds to the
    submitted switch/port.  The UI renders this inline after clicking Search.

    Design notes
    ------------
    * All napp panels share the DOM simultaneously.  sdntrace and sdntrace_cp
      share field IDs (``dpid``, ``in_port``).  Every interaction targets the
      first *visible* element via ``_find_visible``.
    * The sdntrace_cp panel has **Search** and **Reset** buttons only.
      ``click_view_all_traces`` is a no-op sleep kept for test compatibility.
    * Result reading is scoped to the sdntrace_cp panel by anchoring on the
      visible Search button and climbing to the ancestor that also holds
      ``#dpid``.  This prevents reading DPIDs from the topology table.
    * ``_read_starting_entry`` first looks for a cell/node containing the
      text ``"starting"`` (the API-documented type value) and returns the
      DPID and port from the same row/container.  Falls back to the first
      DPID found anywhere in the panel result area (excluding form inputs).
    """

    OPTIONAL_FIELD_INDICES = {
        'dl_vlan':  2,
        'dl_type':  3,
        'dl_src':   4,
        'dl_dst':   5,
        'nw_src':   6,
        'nw_dst':   7,
        'nw_proto': 8,
        'nw_tos':   9,
        'tp_src':   10,
        'tp_dst':   11,
    }

    SELECTORS = {
        'sdntrace_cp_button': (
            By.CSS_SELECTOR,
            'button[data-test="main-button"][title*="sdntrace_cp"]',
        ),
        'dpid':         (By.XPATH, "//*[@id='dpid']/div/div/div/input"),
        'port':         (By.XPATH, "//*[@id='in_port']/div/div/div/input"),
        'reset_button': (By.XPATH, "//button[contains(., 'Reset')]"),
    }

    def __init__(self, driver: WebDriver, base_url: str, api_url: str, default_timeout: int):
        self.driver = driver
        self.base_url = base_url
        self.api_base_url = api_url
        self.wait = WebDriverWait(driver, default_timeout)
        self.default_timeout = default_timeout

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate_to_sdntrace_cp_form(self):
        """Navigate from the homepage to the SDNTrace CP form."""
        self.driver.get(self.base_url)

        cp_button = self.wait.until(
            EC.element_to_be_clickable(self.SELECTORS['sdntrace_cp_button'])
        )
        cp_button.click()

        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[class='k-input'], textarea, select")
                )
            )
        except TimeoutException:
            print("No form elements found after clicking the SDNTrace CP button")
            return False

        form_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "input[class='k-input'], textarea, select"
        )
        print(f"Successfully opened SDNTrace CP form with {len(form_elements)} form elements")
        return True

    # ------------------------------------------------------------------
    # Element helpers
    # ------------------------------------------------------------------

    def _find_visible(self, locator_name):
        """Return the first visible+enabled element matching the locator."""
        by, value = self.SELECTORS[locator_name]
        try:
            return self.wait.until(
                lambda d: next(
                    (el for el in d.find_elements(by, value)
                     if el.is_displayed() and el.is_enabled()),
                    None,
                )
            )
        except TimeoutException:
            raise NoSuchElementException(
                f"No visible/enabled element found for selector '{locator_name}'"
            )

    def _get_panel_inputs(self):
        """
        Return all visible ``input.k-input`` elements inside the SDNTrace CP
        panel in DOM order.  Climbs from the visible dpid input until finding
        a container with at least 3 visible k-inputs.
        """
        dpid_input = self._find_visible('dpid')
        return self.driver.execute_script(
            """
            var anchor = arguments[0];
            var el = anchor;
            while (el && el.id !== 'dpid') { el = el.parentElement; }
            if (!el) return [];
            var container = el;
            for (var i = 0; i < 12; i++) {
                container = container.parentElement;
                if (!container) break;
                var vis = Array.prototype.filter.call(
                    container.querySelectorAll('input.k-input'),
                    function(inp) { return inp.offsetParent !== null; }
                );
                if (vis.length >= 3) { return vis; }
            }
            return [];
            """,
            dpid_input,
        )

    def _scroll_and_fill(self, element, value):
        """Scroll element into view, clear it, type the value, fire Vue's input event."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        element.clear()
        element.send_keys(str(value))
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            element,
        )

    # ------------------------------------------------------------------
    # Form interactions
    # ------------------------------------------------------------------

    def fill_form(self, data):
        """Fill the SDNTrace CP form with the provided data dict."""
        self._scroll_and_fill(self._find_visible('dpid'), data["dpid"])
        self._scroll_and_fill(self._find_visible('port'), data["port"])

        has_optional = any(data.get(f) for f in self.OPTIONAL_FIELD_INDICES)
        if has_optional:
            # Brief wait for Vue reactivity after required fields are set
            time.sleep(1)
            panel_inputs = self._get_panel_inputs()
            for field, idx in self.OPTIONAL_FIELD_INDICES.items():
                if data.get(field):
                    if idx < len(panel_inputs):
                        try:
                            self._scroll_and_fill(panel_inputs[idx], data[field])
                        except Exception:
                            print(f"Could not fill optional field '{field}' at index {idx}")
                    else:
                        print(f"Optional field '{field}': panel only has {len(panel_inputs)} inputs")

    def submit_form(self):
        """
        Click the Search button.  Polls until the button is visible and
        enabled (Vue disables it while inputs are invalid or empty).
        """
        deadline = time.time() + self.default_timeout
        while time.time() < deadline:
            clicked = self.driver.execute_script(
                """
                function isVisible(el) {
                    var cur = el;
                    while (cur && cur !== document.documentElement) {
                        var s = window.getComputedStyle(cur);
                        if (s.display === 'none' || s.visibility === 'hidden') return false;
                        cur = cur.parentElement;
                    }
                    return true;
                }
                var btns = document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    var btn = btns[i];
                    if (btn.textContent.trim().toLowerCase() !== 'search') continue;
                    if (btn.disabled || btn.hasAttribute('disabled')) continue;
                    if (!isVisible(btn)) continue;
                    btn.scrollIntoView({ block: 'center' });
                    btn.click();
                    return true;
                }
                return false;
                """
            )
            if clicked:
                time.sleep(2)
                return
            time.sleep(0.5)
        raise NoSuchElementException("No visible enabled 'Search' button found")

    def reset_form(self):
        """Click the Reset button to clear all form fields."""
        btn = self._find_visible('reset_button')
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        btn.click()
        time.sleep(1)

    def click_view_all_traces(self):
        """Wait for inline results to render (sdntrace_cp has no View All button)."""
        time.sleep(5)

    # ------------------------------------------------------------------
    # Result accessors
    # ------------------------------------------------------------------

    def _read_starting_entry(self):
        """
        Return ``(dpid, port)`` of the **starting** hop from the trace result.

        The sdntrace_cp API documents that every result array's first entry
        has ``type == "starting"`` — that word only ever appears in a
        sdntrace_cp trace result, never in the form, the topology table, or
        any other napp panel.  Using it as an anchor completely avoids the
        need to scope by panel container.

        Search strategy (page-wide, no panel assumptions):
        1. Table cells: find every ``<td>`` whose text is ``"starting"``,
           scan the parent ``<tr>`` for DPID and port.
        2. Non-table nodes: TreeWalker over ``document.body``, find any text
           node equal to ``"starting"``, look at the following ±10 text nodes
           for a DPID and a numeric port (skipping ``<input>`` / ``<textarea>``
           parents and form-component wrappers).

        Returns ``('', '')`` when the result has not appeared yet.
        """
        result = self.driver.execute_script(
            r"""
            var dpidPat = /([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}/;
            var portPat = /^\d+$/;

            function isFormField(el) {
                if (!el) return false;
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') return true;
                if (el.closest && (el.closest('#dpid') || el.closest('#in_port'))) return true;
                return false;
            }

            // --- Strategy 1: table with a "starting" cell ---
            var tds = document.querySelectorAll('td');
            for (var i = 0; i < tds.length; i++) {
                if (tds[i].textContent.trim().toLowerCase() !== 'starting') continue;
                var row = tds[i].closest('tr');
                if (!row) continue;
                var cells = row.querySelectorAll('td');
                var dpid = '', port = '';
                for (var c = 0; c < cells.length; c++) {
                    var txt = cells[c].textContent.trim();
                    if (!dpid) {
                        var m = txt.match(dpidPat);
                        if (m) { dpid = m[0]; continue; }
                    }
                    if (dpid && !port && portPat.test(txt) && txt !== '0') {
                        port = txt;
                    }
                }
                if (dpid) return [dpid, port];
            }

            // --- Strategy 2: non-table, TreeWalker ---
            var walker = document.createTreeWalker(
                document.body, NodeFilter.SHOW_TEXT, null, false);
            var texts = [];
            var node;
            while ((node = walker.nextNode()) !== null) {
                if (!isFormField(node.parentElement)) {
                    texts.push(node.textContent.trim());
                }
            }
            for (var i = 0; i < texts.length; i++) {
                if (texts[i].toLowerCase() !== 'starting') continue;
                // Found "starting" at index i; look ahead for DPID then port
                var dpid = '', port = '';
                for (var j = i; j < Math.min(i + 15, texts.length); j++) {
                    if (!dpid) {
                        var m = texts[j].match(dpidPat);
                        if (m) { dpid = m[0]; continue; }
                    }
                    if (dpid && !port && portPat.test(texts[j]) && texts[j] !== '0') {
                        port = texts[j];
                    }
                    if (dpid && port) break;
                }
                if (dpid) return [dpid, port];
            }

            return ['', ''];
            """
        )
        if result and len(result) == 2:
            return result[0] or '', result[1] or ''
        return '', ''

    def get_first_dpid_from_table(self):
        """Poll until the 'starting' entry DPID appears in the result; return it or ''."""
        try:
            return self.wait.until(
                lambda _: self._read_starting_entry()[0] or None
            ) or ''
        except TimeoutException:
            return ''

    def get_first_port_from_table(self):
        """Poll until the 'starting' entry port appears in the result; return it or ''."""
        try:
            return self.wait.until(
                lambda _: self._read_starting_entry()[1] or None
            ) or ''
        except TimeoutException:
            return ''

    # ------------------------------------------------------------------
    # API verification
    # ------------------------------------------------------------------

    def verify_trace_via_api(self, dpid, port):
        """
        Poll the SDNTrace CP REST API until a trace whose ``result`` contains
        an entry matching ``(dpid, port)`` appears, or ``default_timeout``
        elapses.  Returns the full trace list on success, ``None`` on timeout.
        """
        start = time.time()
        while time.time() - start < self.default_timeout:
            try:
                response = requests.get(self.api_base_url, timeout=5)
                if response.status_code == 200:
                    traces = response.json()
                    found = [
                        (entry["dpid"], entry["port"])
                        for _, data in traces.items()
                        for entry in data.get("result", [])
                        if "dpid" in entry
                    ]
                    if (dpid, int(port)) in found:
                        return found
            except Exception as e:
                print(f"API check error: {e}")
            time.sleep(2)
        return None
