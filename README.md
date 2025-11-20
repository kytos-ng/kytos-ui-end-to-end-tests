# Kytos UI End-to-End Tests

Comprehensive Selenium-based end-to-end test suite for Kytos UI and MEF E-Line EVC (Ethernet Virtual Circuit) functionality.

## Overview

This test suite implements automated tests for the Kytos UI based on the test cases documented in https://docs.google.com/document/d/13e6SSp5CKdxAmwXBl39f3AvIot_rDG6WltE3k0qtgoM/edit?tab=t.0. It covers:

- ✅ MEF-ELINE
- ✅ Napp Pathfinder
- ✅ Napp SDNTrace

## Target System

- **Kytos UI Instance**
- **API Endpoint**: `POST /api/kytos/mef_eline/v2/evc/`

## Prerequisites

### System Requirements
- Python 3.8+
- Chrome/Firefox browser
- Internet connectivity to Kytos UI instance
- Git (for cloning repository)

## Installation

### For Debian/Ubuntu Linux Systems

#### 1. **Update System Packages**
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. **Install Python and Dependencies**
```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify Python installation
python3 --version
pip3 --version
```

#### 3. **Install Git (if not already installed)**
```bash
sudo apt install -y git
```

#### 4. **Install Google Chrome**
```bash
# Download and install Google Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Verify Chrome installation
google-chrome --version
```

#### 5. **Install ChromeDriver**
```bash
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
```

#### 6. **Clone the Repository**
```bash
# Clone the test repository
git clone https://github.com/kytos-ng/kytos-ui-end-to-end-tests.git  # Replace with actual repository URL
cd kytos-ui-end-to-end-tests

# Or if you have the project files already
cd kytos-ui-end-to-end-tests
```

#### 7. **Create Python Virtual Environment (Recommended)**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify virtual environment is active (prompt should show (venv))
which python3
```

#### 8. **Install Python Dependencies**
```bash
# Install required packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import selenium; print(f'Selenium version: {selenium.__version__}')"
```

#### 9. **Setup Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional - defaults should work)
nano .env  # or use your preferred editor

# The default .env contains:
# BASE_URL=http://190.103.184.199:18181
# API_BASE_URL=http://190.103.184.199:18181/api/kytos/mef_eline/v2/evc/
# DEFAULT_TIMEOUT=10
```

#### 10. **Verify Installation**
```bash
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

#### 1. **Install Homebrew (if not already installed)**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. **Install Dependencies**
```bash
# Install Python and Git
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

#### 3. **Continue with Common Steps**
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

## Common Setup (All Platforms)

### Environment Configuration

The tests use environment variables for configuration. The `.env` file contains:

```env
# Kytos UI Instance URL
BASE_URL=http://190.103.184.199:18181

# MEF E-Line API Endpoint
API_BASE_URL=http://190.103.184.199:18181/api/kytos/mef_eline/v2/evc/

# Test timeout settings
DEFAULT_TIMEOUT=10
```

### Virtual Environment (Recommended)

Using a virtual environment isolates project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate (when done)
deactivate
```

### Troubleshooting Installation

#### Chrome/ChromeDriver Issues
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

#### Python Dependencies Issues
```bash
# Upgrade pip
pip3 install --upgrade pip

# Clean install dependencies
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt

# Check for conflicts
pip3 check
```

#### Permission Issues (Linux/macOS)
```bash
# Make ChromeDriver executable
sudo chmod +x /usr/local/bin/chromedriver

# Fix Python PATH issues
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

## Running Tests

### Basic Usage

1. **Run all tests**:
   ```bash
   python run_tests.py
   ```
   ```

2. **Run specific test**:
   ```bash
   python run_tests.py --test test_tc_001_create_basic_evc_minimum_fields
   ```

3. **Run with reporting**:
   ```bash
   python run_tests.py --html-report --junit-xml
   ```

### Advanced Options

```bash
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

### Direct Pytest Usage

You can also run pytest directly:

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_positive_evc_creation.py

# Tests with specific marker
pytest -m positive

# Verbose output with HTML report
pytest -v --html=reports/report.html
```

## Configuration

### Test Data
Test data is configured in `conftest.py`:
- Valid circuit configurations
- Invalid test cases with expected errors
- Boundary test values

### Environment Variables
- `HEADLESS=true` - Run in headless mode
- `BROWSER=CHROME|FIREFOX` - Browser selection

### Timeouts
- Default element wait: 10 seconds
- Long operations: 30 seconds
- API verification: 30 seconds

## API Integration

The test suite validates both UI behavior and API responses:

- **Circuit Creation**: Verifies API returns 201 Created with circuit_id
- **Circuit Verification**: Confirms circuit appears in API listing
- **Data Validation**: Checks API payload matches UI input
- **Cleanup**: Removes test circuits after each test


### Console Output
Real-time test progress with:
- Test status and timing
- API response validation
- Error details and screenshots

## Debugging

### Failed Tests
1. Check HTML report for screenshots
2. Examine console logs
3. Verify API responses in test output
4. Check DOM selectors are still valid


### API Issues
- Verify Kytos instance is accessible
- Check API endpoint availability
- Validate test data against current API schema

## Contributing

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow existing naming convention: `test_[category]_evc_creation.py`
3. Use page objects for UI interaction
4. Include API validation
5. Add proper cleanup in teardown


### Test Data
- Add new test data to `conftest.py`
- Use descriptive names for test scenarios
- Include expected error messages for negative tests


## Troubleshooting

### Common Issues

1. **WebDriver not found**
   ```bash
   pip install webdriver-manager
   ```

2. **Timeouts**
   - Increase timeouts in `conftest.py`
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
