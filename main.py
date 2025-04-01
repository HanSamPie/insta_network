from pprint import pprint
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

from humancursor import WebCursor
from packages.typer import Typer
from selenium_stealth import stealth


# Set Chrome options
options = Options()
options.add_argument("user-data-dir=/home/hannes-piechulek/.config/google-chrome")

# Initialize ChromeDriver
service = Service(ChromeDriverManager().install())
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

# Define human cursor and typer
cursor = WebCursor(driver)
ty = Typer(accuracy = 0.90, correction_chance = 0.70, typing_delay = (0.06, 0.09), distance = 2)

# Open website
driver.get("https://www.instagram.com")

def search_profile(username: str):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]")))
    search_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Search')]")
    cursor.click_on(search_element)

    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search input']")))
    search_input_element = driver.find_element(By.XPATH, "//input[@aria-label='Search input']")
    ty.send(search_input_element, f"@{username}")
    sleep(random.uniform(0.5, 1))

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'hansampie')]")))
    profile_element = driver.find_element(By.XPATH, "//span[contains(text(), 'hansampie')]")
    cursor.click_on(profile_element)
    sleep(random.uniform(0.5, 1))


def get_follow_count() -> tuple[int, int]:
    """
    returns first the followers count and second the following count
    """

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//ul/li[2]/div/a/span/span/span')))
    followers_count = driver.find_element(By.XPATH, '//ul/li[2]/div/a/span/span/span').text

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//ul/li[3]/div/a/span/span/span')))
    following_count = driver.find_element(By.XPATH, '//ul/li[3]/div/a/span/span/span').text

    return int(followers_count), int(following_count)

def get_usernames(followers=False, following=False) -> list[str]:
    path = "followers" if followers == True else "following"

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{path}')]")))
    followers_element = driver.find_element(By.XPATH, f"//span[contains(text(), '{path}')]")
    cursor.click_on(followers_element)
    sleep(random.uniform(0.5, 1))

    try:
        while True:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//div[@data-visualcompletion='loading-state']")))
            scrollbar = driver.find_element(By.XPATH, "//div[@data-visualcompletion='loading-state']")
            cursor.scroll_into_view_of_element(scrollbar)
            sleep(random.uniform(0.1, 0.3))
    except TimeoutException:
        pass

    dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")
    username_elements = dialog.find_elements(By.XPATH, '//span[contains(@class, "_ap3a") and contains(@class, "_aaco") and contains(@class, "_aacw") and contains(@class, "_aacx") and contains(@class, "_aad7") and contains(@class, "_aade")]')
    usernames = [ element.text for element in username_elements]

    close_button_element = dialog.find_element(By.XPATH, "//button[contains(@class, '_abl-')]")
    cursor.click_on(close_button_element)
    sleep(random.uniform(0.5, 1))

    return usernames

def scrape_profile(username: str) -> dict:
    profile = {
        'username': username
    }
    search_profile(username)
    profile['followers_count'], profile['following_count'] = get_follow_count()
    if profile['followers_count'] > 2000 or profile['following_count'] > 2000:
        return profile

    profile['followers'] = get_usernames(followers=True)
    profile['following'] = get_usernames(following=True)

    followers_not_equal = len(profile['followers']) != profile['followers_count']
    following_not_equal =  len(profile['following']) != profile['following_count']

    if followers_not_equal or following_not_equal:
        print(profile)
        raise ValueError("Follow count mismatch!")
    
    return profile
    
pprint(scrape_profile("hansampie"))

driver.quit()
