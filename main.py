from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium_stealth import stealth

# Set Chrome options
options = Options()
#options.add_argument("--headless=new")  # Run in headless mode (optional)
options.add_argument("user-data-dir=/home/hannes-piechulek/.config/google-chrome")

# Initialize ChromeDriver
service = Service(ChromeDriverManager().install())  # Auto-downloads the driver
driver = webdriver.Chrome(service=service, options=options)

# set stealth options
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Linux x86_64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# Open website
driver.get("https://www.instagram.com")

sleep(30)
driver.quit()
