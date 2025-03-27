from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

from humancursor import WebCursor
# from https://github.com/saadejazz/humanTyper
from packages.typer import Typer
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

cursor = WebCursor(driver)
ty = Typer(accuracy = 0.90, correction_chance = 0.70, typing_delay = (0.06, 0.09), distance = 2)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]"))
)

search_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Search')]")
x = search_element.location["x"]
y = search_element.location["y"]


cursor.click_on(search_element)


WebDriverWait(driver, 2).until(
    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search input']"))
)
search_input_element = driver.find_element(By.XPATH, "//input[@aria-label='Search input']")
ty.send(search_input_element, "@hansampie")
sleep(1)

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'hansampie')]"))
)
profile_element = driver.find_element(By.XPATH, "//span[contains(text(), 'hansampie')]")
cursor.click_on(profile_element)
sleep(1)

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'followers')]"))
)
followers_element = driver.find_element(By.XPATH, "//span[contains(text(), 'followers')]")
cursor.click_on(followers_element)
sleep(1)

try:
    while True:
        scrollbar = driver.find_element(By.XPATH, "//div[@data-visualcompletion='loading-state']")
        cursor.scroll_into_view_of_element(scrollbar)
        sleep(0.2)
except NoSuchElementException:
    
    pass
# cursor.control_scroll_bar(scrollbar, 1)

dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
text = dialog.find_elements(By.XPATH, ".//span[string-length(text()) > 0]")
text = text[1:]
names = []

# TODO some people dont have name so I have to find the tag
for i, t in enumerate(text): 
    if i%2 == 0:
        names.append(t.text)
        print(t.text)
print(len(names))


sleep(30)
driver.quit()
