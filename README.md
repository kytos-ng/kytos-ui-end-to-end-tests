# Kytos UI End-to-End Tests

This repository contains end-to-end (E2E) tests for the Kytos UI, organized by NApp (Network Application). The tests are written using Python and `pytest` with `Selenium` for browser automation. It covers:

- ✅ NApp mef-eline
- ✅ NApp pathfinder
- ✅ NApp maintenance
- ✅ NApp sdntrace
- ✅ NApp sdntrace_cp

Documentation: https://docs.google.com/document/d/13e6SSp5CKdxAmwXBl39f3AvIot_rDG6WltE3k0qtgoM/edit?tab=t.0. 

## Target System

- **Kytos UI Instance**
- **API Endpoint**: 
    - `POST /api/kytos/mef_eline/v2/evc/`
    - `POST /api/amlight/sdntrace/v1/traces/`
    - `POST /api/kytos/maintenance/v1/`

## Prerequisites

1. **Python 3.8+**
3.  **Kytos UI** accessible (default: `http://localhost:18181`)
4.  **Chrome/Firefox** browser installed
5.  **ChromeDriver** installed and accessible. The test setup attempts to use `/usr/local/bin/chromedriver` or falls back to `webdriver-manager`.

## Detailed System Setup Guides

The following sections provide detailed instructions for setting up the necessary environment components on different operating systems.

### For Debian/Ubuntu Linux Systems

```bash
# 1. Update System Packages
sudo apt update && sudo apt upgrade -y

# 2. Install Python and Dependencies
sudo apt install -y python3 python3-pip python3-venv

# Verify Python installation
python3 --version
pip3 --version

# 3. Install Git
sudo apt install -y git

# 4. Install Google Chrome
# Download and install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Verify Chrome installation
google-chrome --version

# 5. Install ChromeDriver
# Install ChromeDriver via package manager
sudo apt install -y chromium-chromedriver

# Alternatively, install via curl (gets latest version)
# CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
# wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
# unzip chromedriver_linux64.zip
# sudo mv chromedriver /usr/local/bin/chromedriver
# sudo chmod +x /usr/local/bin/chromedriver

# Verify ChromeDriver installation
chromedriver --version

# 6. Clone the Repository
git clone https://github.com/kytos-ng/kytos-ui-end-to-end-tests.git  # Replace with actual repository URL
cd kytos-ui-end-to-end-tests

# 7. Create Python Virtual Environment (Recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# 8. Install Python Dependencies
pip3 install -r requirements.txt

# Verify installation
python3 -c "import selenium; print(f'Selenium version: {selenium.__version__}')"

# 9. Setup Environment Configuration
cp .env.example .env

# Edit configuration (optional - defaults should work)
nano .env  # or use your preferred editor

# The default .env contains:
# BASE_URL=http://localhost:18181
# API_BASE_URL=http://localhost:18181/api/kytos/mef_eline/v2/evc/
# DEFAULT_TIMEOUT=10

# 10. Verify Installation
# Test Chrome and ChromeDriver
google-chrome --headless --disable-gpu --no-sandbox --remote-debugging-port=9222 &
sleep 2
pkill -f chrome

# Test Selenium WebDriver
python3 -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
driver.get('https://www.google.com')
print('✅ Selenium WebDriver working correctly')
driver.quit()
"

# Test pytest
python3 -m pytest --version
```

### For macOS Systems

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Dependencies
brew install python3 git

# Install Google Chrome
brew install --cask google-chrome

# Install ChromeDriver
brew install chromedriver

# Verify installations
python3 --version
git --version
google-chrome --version
chromedriver --version
```
**Continue with Common Steps**
Follow steps 6-10 from the Linux instructions above.

### For Windows Systems

#### 1. **Install Python**
- Download Python 3.8+ from https://python.org/downloads/
- During installation, check "Add Python to PATH"
- Verify: Open Command Prompt and run `python --version`

#### 2. **Install Git**
- Download Git from https://git-scm.com/download/win
- Install with default settings

#### 3. **Install Google Chrome**
- Download from https://www.google.com/chrome/
- Install with default settings

#### 4. **Install ChromeDriver**
```cmd
# Option 1: Use pip to install webdriver-manager (recommended)
pip install webdriver-manager

# Option 2: Manual installation
# Download ChromeDriver from https://chromedriver.chromium.org/
# Extract chromedriver.exe and place it in your PATH
```

#### 5. **Continue with Project Setup**
```cmd
# Clone repository
git clone <repository-url>
cd kytos-ui-end-to-end-tests

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env

# Verify installation
python -c "import selenium; print('Selenium installed successfully')"
```

## Troubleshooting Installation

### Chrome/ChromeDriver Issues
```bash
# Check Chrome installation
google-chrome --version

# Check ChromeDriver installation
chromedriver --version

# If versions don't match, update ChromeDriver

# Linux/macOS with Homebrew:
brew upgrade chromedriver

# Linux with apt:
sudo apt update && sudo apt upgrade chromium-chromedriver
```

### Python Dependencies Issues
```bash
# Upgrade pip
pip3 install --upgrade pip

# Clean install dependencies
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt

# Check for conflicts
pip3 check
```

### Permission Issues (Linux/macOS)
```bash
# Make ChromeDriver executable
sudo chmod +x /usr/local/bin/chromedriver

# Fix Python PATH issues
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Running Tests

### Direct Pytest Usage

You can run pytest directly:

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_mefeline_001_evc_creation.py

# Verbose output with HTML report
pytest -v --html=reports/report.html
```

You can also use run_tests.py:

```bash
# All tests
python run_tests.py

# Run specific test
python run_tests.py --test test_001_create_basic_evc_minimum_fields

# Run with reporting
python run_tests.py --html-report --junit-xml

# Headless mode
python run_tests.py --headless

# Parallel execution
python run_tests.py --parallel 4

# Different browser
python run_tests.py --browser firefox

# Verbose output
python run_tests.py --verbose

# Smoke tests only
python run_tests.py --suite smoke
```

## Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow existing naming convention: `test_[NApp]_[number]_description.py`
3. Use page objects for UI interaction
4. Include API validation
5. Add proper cleanup in teardown

### Test Data
- Add new test data to `test/conftest.py`
- Use descriptive names for test scenarios
- Include expected error messages for negative tests

## Troubleshooting

### Common Issues

1. **WebDriver not found**
   ```bash
   pip install webdriver-manager
   ```

2. **Timeouts**
   - Increase timeouts in `.evc`
   - Check network connectivity to Kytos instance

3. **Element not found**
   - Verify DOM selectors with analysis script
   - Check if UI has changed

4. **API errors**
   - Verify Kytos instance is running
   - Check API endpoint accessibility

### Getting Help

1. Check test execution logs
2. Review HTML test reports
3. Verify DOM selectors are current
4. Ensure Kytos UI instance is accessible

## License

This test suite is designed for testing the Kytos UI
