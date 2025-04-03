from pprint import pprint
from time import sleep, time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
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
        pprint(profile)
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

MAX_DEPTH =  1 # only queries to follows of my follows

def add_user(name: str, status: str, depth: int):
    """Add a new task with a specified depth."""
    query = """
    INSERT INTO tasks (name, status, depth)
    VALUES (%s, %s, %s)
    ON CONFLICT (name) DO NOTHING;
    """


    postgres_cursor.execute(query, (name, status, depth))
    postgres_conn.commit()

def update_status(name: str, new_status: str):
    """Updates the status of an item if it exists."""
    query = """
    UPDATE tasks SET status = %s WHERE name = %s;
    """
    
    postgres_cursor.execute(query, (new_status, name))
    postgres_conn.commit()


def update_one_todo_to_ongoing() -> tuple:
    """Finds one item with status TODO, updates it to ONGOING, and returns its name and depth."""
    # Query to fetch one TODO item, along with its depth
    select_query = """
    SELECT name, depth FROM tasks WHERE status = 'TODO' AND depth <= %s
    ORDER BY depth LIMIT 1 FOR UPDATE SKIP LOCKED;
    """
    
    # Query to update the task's status
    update_query = "UPDATE tasks SET status = 'ONGOING' WHERE name = %s RETURNING name, depth;"
    
    # Fetch one TODO item
    postgres_cursor.execute(select_query, (MAX_DEPTH,))
    result = postgres_cursor.fetchone()

    if result:
        name, depth = result  # Extract name and depth

        # Update its status to ONGOING
        postgres_cursor.execute(update_query, (name,))
        postgres_conn.commit()

        return name, depth  # Return the updated item's name and depth
    else:
        return None  # No TODO items found or MAX_DEPTH reached


def count_todo_items() -> int:
    """Returns the total number of TODO items in the database."""
    query = "SELECT COUNT(*) FROM tasks WHERE status = 'TODO';"


    postgres_cursor.execute(query)
    count = postgres_cursor.fetchone()[0]  # Get the first column from the result
    return count

def format_time(time: int) -> str:
    hours = int(time // 3600)
    minutes = int((time % 3600) // 60)
    seconds = int(time % 60)

    if hours > 0:
        formatted_time = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        formatted_time = f"{minutes}m {seconds}s"
    else:
        formatted_time = f"{seconds}s"

    return formatted_time

num_done = 0
num_todo = 0
average = 0

with tqdm(total=num_todo, desc="Scraping Profiles") as pbar:
    while (result := update_one_todo_to_ongoing()) is not None:
        username, depth = result
        start_time = time()
        
        if depth <= MAX_DEPTH:
            profile = scrape_profile(username)
            insert_profile(profile)

            for follower in profile['followers']:
                add_user(follower, "TODO", depth + 1)
            for follows in profile['following']:
                add_user(follows, "TODO", depth + 1)
    
        update_status(username, "DONE")

        time_since = time() - start_time
        average = (average * num_done + time_since) / (num_done + 1)
        num_todo = count_todo_items()
        
        # Update the progress bar total dynamically
        pbar.total = num_todo
        pbar.n = num_done  # Keep track of progress
        pbar.last_print_n = num_done  # Update the print position to avoid misalignment

        # Update the progress bar and additional stats
        pbar.set_postfix({
            'Avg Time (s)': f'{average:.2f}',
            'Time Left': format_time(average * num_todo),
        })
        
        # Refresh the progress bar display
        pbar.update(1)


neo4j_driver.close()
postgres_cursor.close()
postgres_conn.close()
driver.quit()
