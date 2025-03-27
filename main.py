from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from humancursor import WebCursor
from human_typer import Human_typer

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


WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]"))
)

search_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Search')]")
print(search_element.location)
search_element.click()

WebDriverWait(driver, 2).until(
    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search input']"))
)

search_input_element = driver.find_element(By.XPATH, "//input[@aria-label='Search input']")
search_input_element.send_keys("asdf")

print("clicked?")
sleep(50)
driver.quit()
