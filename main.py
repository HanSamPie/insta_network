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

from neo4j import GraphDatabase
import psycopg2

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

#######################NEO4J#####################
def insert_profile(profile:dict):
    def insert_user(tx, username, followers, following, followers_count, following_count):
        # Create or update the user node with counts
        tx.run(
            """
            MERGE (u:Account {username: $username})
            SET u.followers_count = $followers_count, 
                u.following_count = $following_count
            """,
            username=username,
            followers_count=followers_count,
            following_count=following_count,
        )

        # Create relationships for followers (follower -> u)
        for follower in followers:
            tx.run(
                """
                MATCH (u:Account {username: $username})
                MERGE (f:Account {username: $follower})
                MERGE (f)-[:FOLLOWS]->(u)
                """,
                follower=follower,
                username=username,
            )

        # Create relationships for following (u -> following_user)
        for following_user in following:
            tx.run(
                """
                MATCH (u:Account {username: $username})
                MERGE (f:Account {username: $following_user})
                MERGE (u)-[:FOLLOWS]->(f)
                """,
                following_user=following_user,
                username=username,
            )

    with neo4j_driver.session() as session:
        session.execute_write(
            insert_user, 
            profile["username"], 
            profile["followers"], 
            profile["following"], 
            profile["followers_count"], 
            profile["following_count"]
        )

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")
# Connect and insert data
neo4j_driver = GraphDatabase.driver(URI, auth=AUTH)


#######################POSTGRES#####################
postgres_conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="password",
    host="localhost",
    port="5432"
)
postgres_cursor = postgres_conn.cursor()

def add_item(name: str, status: str):
    """Inserts an item if it does not already exist."""
    query = """
    INSERT INTO tasks (name, status) VALUES (%s, %s)
    ON CONFLICT (name) DO NOTHING;
    """
    
    
    postgres_cursor.execute(query, (name, status))
    postgres_conn.commit()


def update_status(name: str, new_status: str):
    """Updates the status of an item if it exists."""
    query = """
    UPDATE tasks SET status = %s WHERE name = %s;
    """
    
    postgres_cursor.execute(query, (new_status, name))
    postgres_conn.commit()


def update_one_todo_to_ongoing() -> str:
    """Finds one item with status TODO, updates it to ONGOING, and returns its name."""
    select_query = "SELECT name FROM tasks WHERE status = 'TODO' LIMIT 1 FOR UPDATE SKIP LOCKED;"
    update_query = "UPDATE tasks SET status = 'ONGOING' WHERE name = %s RETURNING name;"
    # Fetch one TODO item
    postgres_cursor.execute(select_query)
    result = postgres_cursor.fetchone()

    if result:
        name = result[0]

        # Update its status to ONGOING
        postgres_cursor.execute(update_query, (name,))
        postgres_conn.commit()

        return name  # Return the updated item's name
    else:
        return None  # No TODO items found



insert_profile(scrape_profile("hansampie"))
#pprint(scrape_profile("hansampie"))

neo4j_driver.close()
postgres_cursor.close()
postgres_conn.close()
driver.quit()
