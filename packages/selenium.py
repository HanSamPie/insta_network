from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless=new")  # Run in headless mode (optional)
chrome_options.add_argument("--disable-gpu")

# Initialize ChromeDriver
service = Service(ChromeDriverManager().install())  # Auto-downloads the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open a website
driver.get("https://www.google.com")
print("Page title:", driver.title)

# Close the browser
driver.quit()
