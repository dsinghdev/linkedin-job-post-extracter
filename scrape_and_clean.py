# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# from tqdm import tqdm  # Progress bar library
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Set up WebDriver
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# # Log into LinkedIn
# driver.get('https://www.linkedin.com/login')
# time.sleep(2)
# username = driver.find_element(By.ID, 'username')
# password = driver.find_element(By.ID, 'password')
# username.send_keys('name@gmail.com')  # Enter your LinkedIn email here
# password.send_keys('password')  # Enter your LinkedIn password here
# password.send_keys(Keys.RETURN)

# # Search for your term
# time.sleep(2)
# search_url = 'https://www.linkedin.com/search/results/content/?keywords=ai%20ml%20developer%20hiring'
# driver.get(search_url)
# time.sleep(2)

# # Scroll and load more posts
# scroll_times = 200  # Increase scroll times to load more data
# print("Scrolling through the page...")
# for i in tqdm(range(scroll_times), desc="Scrolling"):  # Use tqdm to show progress
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(3)  # Increase wait time slightly to allow posts to load

# # Extract posts and expand one by one
# posts = driver.find_elements(By.CLASS_NAME, 'feed-shared-update-v2')  # Class for posts

# # Open a CSV file to save the data
# with open('linkedin_posts_with_links_v1.csv', mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Post_Content', 'Post_Link'])  # Column headers for post content and URL

#     # Loop through each post
#     for idx, post in enumerate(tqdm(posts, desc="Processing posts")):
#         try:
#             # Click on the button with the appropriate class to expand content
#             more_button = WebDriverWait(post, 5).until(
#                 EC.element_to_be_clickable((By.CLASS_NAME, "feed-shared-inline-show-more-text__see-more-less-toggle"))
#             )
#             more_button.click()
#             time.sleep(1)  # Allow time for content to expand
#         except Exception as e:
#             print(f"No 'see more' button in post {idx}: {e}")

#         # Extract the expanded post content
#         post_content = post.text
        
#         # Extract the post URL
#         try:
#             post_link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
#         except Exception as e:
#             post_link = "Link not found"
#             print(f"Couldn't extract link for post {idx}: {e}")
        
#         # Save the expanded content and the post link to the CSV
#         writer.writerow([post_content, post_link])

# # Close the browser
# driver.quit()

# print("Data saved to linkedin_posts_with_links.csv successfully.")

import os
import csv
import re
import time
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
load_dotenv(override=True)

# -------------------------------
# CONFIGURATIONS AND CREDENTIALS
# -------------------------------
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Check that both are present
if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError("Environment variables LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set before running this script.")

SEARCH_URL = "https://www.linkedin.com/search/results/content/?keywords=ai%20ml%20developer%20hiring"

SCROLL_TIMES = 20  # Adjust as needed
WAIT_BETWEEN_SCROLLS = 3

# Ensure output directory exists
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RAW_DATA_FILE = os.path.join(OUTPUT_DIR, "linkedin_posts_raw.csv")
CLEANED_DATA_FILE = os.path.join(OUTPUT_DIR, "cleaned_linkedin_posts.csv")


# -------------------------------
# STEP 1: EXTRACT POSTS FROM LINKEDIN
# -------------------------------
def extract_linkedin_posts():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get('https://www.linkedin.com/login')
        time.sleep(2)
        
        # Login
        username = driver.find_element(By.ID, 'username')
        password = driver.find_element(By.ID, 'password')
        username.send_keys(LINKEDIN_EMAIL)
        password.send_keys(LINKEDIN_PASSWORD)
        password.send_keys(Keys.RETURN)
        
        time.sleep(2)
        driver.get(SEARCH_URL)
        time.sleep(2)

        # Scroll to load posts
        for _ in range(SCROLL_TIMES):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(WAIT_BETWEEN_SCROLLS)

        # Extract posts
        posts = driver.find_elements(By.CLASS_NAME, 'feed-shared-update-v2')

        with open(RAW_DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Post_Content', 'Post_Link'])
            for idx, post in enumerate(posts):
                # Try to expand "see more"
                try:
                    more_button = WebDriverWait(post, 1).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "feed-shared-inline-show-more-text__see-more-less-toggle"))
                    )
                    more_button.click()
                    time.sleep(0.5)
                except:
                    pass

                post_content = post.text
                # Try to get a link from the post
                try:
                    post_link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except:
                    post_link = "Link not found"

                writer.writerow([post_content, post_link])
    finally:
        driver.quit()

# -------------------------------
# STEP 2: CLEAN THE EXTRACTED DATA
# -------------------------------
def clean_post_content(post_content):
    lines = post_content.strip().split('\n')

    # Check last lines for 'reposts'
    if lines and lines[-1].strip().endswith('reposts'):
        cleaned_content_lines = lines[:-3]
    else:
        cleaned_content_lines = lines[:-2] if len(lines) > 2 else lines

    cleaned_content = "\n".join(cleaned_content_lines).strip()

    name_pattern = r'^(.*?)\n'
    post_content_pattern = r'Follow\n(.*)'
    
    name_match = re.search(name_pattern, cleaned_content)
    main_content_match = re.search(post_content_pattern, cleaned_content, re.DOTALL)

    name = name_match.group(1) if name_match else 'N/A'
    main_content = main_content_match.group(1).strip() if main_content_match else 'N/A'

    return {"Name": name, "Post_Content": main_content}

def clean_data():
    with open(RAW_DATA_FILE, mode='r', encoding='utf-8') as infile, open(CLEANED_DATA_FILE, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['Name', 'Post_Content', 'Post_Link'])
        for row in reader:
            cleaned = clean_post_content(row['Post_Content'])
            writer.writerow([cleaned['Name'], cleaned['Post_Content'], row['Post_Link']])

if __name__ == "__main__":
    print("Extracting LinkedIn posts...")
    extract_linkedin_posts()
    print("Cleaning extracted posts...")
    clean_data()
    print("Data extraction and cleaning completed.")
    print(f"Cleaned data saved in {CLEANED_DATA_FILE}.")
