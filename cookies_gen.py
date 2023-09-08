### IMPORTS ###
import datetime
import logging  # For printing logs
import re  # For regular expressions
import sqlite3
from urllib import parse  # For parsing urls
import random
from time import sleep

# Import Playwright and stealth for browser automation
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Import UserAgent for generating random user agent strings
from fake_useragent import UserAgent

DATABASE_NAME = "cookie_data.db"

# Configure logging & create logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('logger1')
file_handler = logging.FileHandler("logs/cookiesGen.log")
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# High level logger
logging.basicConfig(level=logging.INFO)
logger_2 = logging.getLogger('logger2')
file_handler_2 = logging.FileHandler("logs/cookiesGen2.log")
formatter_2 = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler_2.setFormatter(formatter_2)
logger_2.addHandler(file_handler_2)


def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY,
            sessionid TEXT,
            user_id TEXT,
            lsd TEXT,
            dtsg TEXT,
            hs TEXT,
            hsi TEXT,
            c TEXT,
            user_agent TEXT,
            generated TEXT,
            created_at DATETIME
        )
        """)
        conn.commit()


def save_to_db(data):
    current_time = datetime.datetime.now()

    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO cookies (sessionid, user_id, lsd, dtsg, hs, hsi, c, user_agent, generated, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*data, current_time))
        conn.commit()


def random_string():
    random_list = ["fit", "one", "fitness near me", "free shipping", "fitness", "fitness tracker", "fitness blender",
                   "fitness watches",
                   "fitness quotes", "fitness pal", "fitness singles", "fitness tracker watch", "fitness connection",
                   "free shipping code",
                   "free shipping bath and body works", "free shipping victoria secret",
                   "free shipping code bath and body works",
                   "free shipping code victoria secret", "free shipping code for amazon",
                   "free shipping code for kohls",
                   "free shipping code for bath and body works", "Blender", "Kitchen tools", "Kitchen appliances",
                   "Kitchen utensils",
                   "Kitchen gadgets", "Kitchen accessories", "Kitchen supplies", "Kitchen equipment", "Kitchenware",
                   "Kitchen items",
                   "Kitchen stuff", "Kitchen products", "Kitchen things", "Kitchen gifts", "Kitchen decor",
                   "Kitchen set", "Kitchen decor"]
    random_number = random.randint(0, len(random_list) - 1)
    advertiser_url = random_list[random_number]
    return advertiser_url


# function to generate random user agent string
def generate_user_agent():
    ua = UserAgent(browsers=['firefox'])
    # return ua.random
    return ua.firefox


# function to fetch list of proxy servers
def get_proxies():
    proxy = {
        'server': '169.197.83.74:6039',
        'username': 'y4niz',
        'password': 'z5lhc8g2',
    }

    return proxy


# Class to generate cookies
class CookieGenerator:
    """Class to generate cookies"""

    # constructor
    def __init__(self):
        """Initialize CookieGenerator class"""
        pass

    # method to generate cookies
    def generate_cookies(self):
        """Generate cookies from starting URL"""
        logger.info("Generating new cookies")

        # Get user agent and proxies
        generated_proxies = get_proxies()
        user_agent = generate_user_agent()
        advertiser_url = random_string()
        scrape_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&q={advertiser_url}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=page&media_type=all"

        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(
                headless=True,
                proxy=generated_proxies,
            )
            context = browser.new_context(user_agent=user_agent)

            # Create new page in context
            page = context.new_page()

            # Apply stealth plugin to evade bot detection
            stealth_sync(page)

            # Pass the User-Agent & viewport size
            page.set_viewport_size({"width": 1920, "height": 1080})

            # # DEBUG: TEST IP ROTATION
            # page.goto('https://api.ipify.org')
            # page.wait_for_load_state()
            # content = page.content()

            # logger.info(f"Firefox instance created with public IP: {content} and user agent: {user_agent}")

            # Capture all requests made by the browser
            requests = []
            page.on('request', lambda request: requests.append(request))

            # Navigate to URL with page_id parameter and extract cookies/response text
            try:
                page.goto(scrape_url)
            except Exception as e:
                logger.error(f"Error - Failed when opening the starting url: {e}")
                return False

            # # DEBUG: Save response text to file
            # content = BeautifulSoup(response_text, "html.parser")
            # with open("response.html", "w", encoding="utf-8") as file:
            #     content = content.prettify()
            #     file.write(content)

            # Click accept cookies button (only if it exists)
            try:
                page.click("button[data-cookiebanner='accept_button']", timeout=2000)
                page.wait_for_load_state()
            except Exception as e:
                logger.warning(f"Warning - No cookies banner found: {e}")
                logger.info(f"Cookies might have been accepted automatically -> continuing without accepting cookies")

            # Get response text and cookies
            response_text = page.content()
            cookies = page.context.cookies()

            # Check if there is a cookie with name 'datr' in the list of cookies
            if not any(cookie['name'] == 'datr' for cookie in cookies):
                logger.error(f"Error - No datr cookie found")
                return False

            try:
                user_id = re.findall(r"USER_ID\":\"(.*?)\",", response_text)[0]
                lsd = re.findall(r"LSD[^:]+:\"(.*?)\"", response_text)[0]
                dtsg = re.findall(r"DTSGInitialData[\s\S]+?token\":\"(.*?)\"", response_text)[0]
                sessionid = re.findall(r"sessionId\":\"(.*?)\",", response_text)[0]
                hs = re.findall(r"haste_session\":\"(.*?)\",", response_text)[0]
                hsi = re.findall(r"hsi\":\"(.*?)\",", response_text)[0]
            except Exception as e:
                logger.error(f"Error - Failed when extracting content from the website: {e}")
                return False

            logger.info(f"Content & cookies correctly scraped from the website")

            # Generate payload, check if this works, if not try to iniatiate a new browser instance
            logger.info(f"Generating payload")

            # Scroll to bottom to trigger requests
            page.evaluate("""window.scrollTo(0, document.body.scrollHeight)""")

            # Get last POST request
            logger.info(f"Getting last POST request")
            post_requests = [r for r in requests if
                             r.method == "POST" and 'https://www.facebook.com/ads/library/async/search_ads/?q=' in r.url]
            last_request = post_requests[-1]

            # Extract payload
            logger.info(f"Extracting payload")
            payload_text = last_request.post_data
            payload = {p.split("=")[0]: p.split("=")[1] for p in payload_text.split("&")}
            params = dict(parse.parse_qsl(parse.urlsplit(post_requests[0].url).query))
            generated = {'pageId': advertiser_url,
                         'payload': payload,
                         'params': params}

            logger.info(f"Payload correctly generated")

            # Cleanup browser context and close
            page.close()
            context.close()
            browser.close()

            c = {c['name']: c['value'] for c in cookies}

        data = (sessionid, user_id, lsd, dtsg, hs, hsi, str(c), user_agent, str(generated))
        save_to_db(data)

        return sessionid, user_id, lsd, dtsg, hs, hsi, c, user_agent, generated


# main function
def main():
    init_db()
    # Create CookieGenerator
    cookie_generator = CookieGenerator()
    j = 0
    i = 0
    iteration = 0
    # Generate cookies
    logger_2.info(f"Starting to generate cookies")
    while True:
        response = cookie_generator.generate_cookies()
        if not response:
            j += 1
            logger_2.warning(f"Warning - Failed to generate cookies {j} out of {i + 1} times")
        else:
            logger_2.info(f"Success - Generated cookies {i + 1 - j} out of {i + 1} times")
            # send response to logger_2
            logger_2.info(f"Complete response: {response}")
        iteration += 1
        logger_2.info(f"Iteration ========  {iteration}")
        sleep(20)


# Guard for module vs script usage
if __name__ == "__main__":
    main()
