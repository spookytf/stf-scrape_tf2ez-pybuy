import pika
import dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import logging
import json

global platform

from sys import platform

if platform == "linux" or platform == "linux2":
    # linux
    OS = "linux"
elif platform == "darwin":
    # OS X
    OS = "mac"
elif platform == "win32":
    # Windows...
    OS = "windows"

print(f"platform is {OS}")


def buy_item_by_id(item_id, item_price, item_hash_name):
    bot_inventory = driver.find_element(By.CLASS_NAME, "market-items")
    item_to_buy = bot_inventory.find_elements(By.XPATH, f"//div[@data-id={item_id}]")

    if len(item_to_buy) == 0:
        logging.info(f"({item_hash_name}) - Cannot find this item in bot's inventory.")
        return {
            "success": False,
            "message": "There is no such item in bot's inventory"
        }
    else:
        wagered_balance = float(driver.find_element(By.ID, "withdraw-bal").text)

        if wagered_balance < item_price: return {
            "success": False,
            "message": f"You do not have enough wagered balance for this operation. [wagered balance: ${wagered_balance}, price: ${item_price}]."
        }

        logging.info(f"({item_hash_name}) - Adding to cart.")
        item_to_buy[0].click()
        driver.find_element(By.ID, "buyItems").click()
        # TODO: we shouldn't assume the purchase was successful
        return {
            "success": True,
            "message": f"bought item {item_hash_name} for ${item_price}."
        }


def callback(ch, method, properties, body):
    message_dict = json.loads(body)
    item_hash_name = message_dict['item_hash_name']
    item_id = message_dict['item_id']

    buy_prices = message_dict['buy_prices']
    buy_usd = buy_prices['usd']
    buy_keys = buy_prices['keys']
    buy_refs = buy_prices['refs']

    sell_prices = message_dict['sell_prices']

    buyer_id = sell_prices['steamid']

    sell_usd = sell_prices['usd']
    sell_keys = sell_prices['keys']
    sell_refs = sell_prices['refs']

    logging.info(f"({item_hash_name}) - Attempting to buy for ${buy_usd}.")

    status = buy_item_by_id(item_id, buy_usd, item_hash_name)
    if status['success'] is False:
        logging.info(f"({item_hash_name}) - Can not complete order. {status['message']}")
    else:
        logging.info(f"({item_hash_name}) - item bought successfully.")

    # Discord notification there

    ch.basic_ack(delivery_tag=method.delivery_tag)


class BuyListener:
    channel = None
    config = None
    pika_host = None
    pika_port = None
    pika_username = None
    pika_password = None
    pika_queue = None

    def __init__(self, config, pika_host, pika_port, pika_username, pika_password):
        self.config = config
        self.pika_host = pika_host
        self.pika_port = pika_port
        self.pika_username = pika_username
        self.pika_password = pika_password

        self.main()

    def main(self):
        credentials = pika.PlainCredentials(self.pika_username, self.pika_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.pika_host, port=self.pika_port, credentials=credentials))
        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.config['RABBITMQ']['queue'], durable=True)

        # ---------------- Configure logging ---------------- #
        logging.basicConfig(level="INFO",
                            format='%(levelname)s %(asctime)s - %(message)s',
                            datefmt='%H:%M:%S')
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

        # ---------------- Configure CLI flags ---------------- #
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--start-maximized")

        # head = config['BROWSER']['method'].lower()

        # make sure URL ends with a slash
        scrape_url = self.config['SCRAPE']['url']
        if not scrape_url.endswith("/"):
            scrape_url = scrape_url + "/"

        # ---------------- Login process ---------------- #
        global driver
        if not OS == "windows":
            try:
                driver = uc.Chrome(options=options, executable_path=os.path.abspath("./chromedriver"))
            except:
                logging.error("Couldn't find the default Google Chrome binaries. Perhaps you haven't installed Google "
                              "Chrome?")
                logging.error("if you are on Ubuntu/Debian: make sure you have wget, then use the following command "
                              "to install the latest version of Google Chrome:")
                logging.critical("$ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb "
                                 "&& sudo dpkg -i google-chrome-stable_current_amd64.deb")
                input("Press any key to exit...")
                exit(1)
        else:
            driver = uc.Chrome(options=options)

        global wait
        wait = WebDriverWait(driver, 60)
        driver.get(scrape_url)

        login_method = self.config['LOGIN']['method'].lower()

        if login_method == "steam":
            driver.find_element(By.CLASS_NAME, "login-block").click()
            time.sleep(1)
            wait.until(EC.title_contains("TF2EASY.COM"))
        elif login_method == "cookie":
            login_cookie = os.getenv("login_cookie")
            driver.add_cookie({
                "name": "laravel_session",
                "value": login_cookie
            })
            driver.refresh()
        else:
            logging.info("You have to select login method in config.ini!")
            return
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menu-username-text')))
            if login_method == "steam":
                generated_cookie = driver.get_cookie("laravel_session")['value']
                dotenv.set_key('.env','LOGIN_COOKIE',generated_cookie)
        except:
            logging.info("Couldn't login. (Wrong cookie?)")
            return

        logging.info("Logged in!")
        driver.get(scrape_url + "market")

        # wait for page to load
        # TODO: probably want to fix this but it works for now
        time.sleep(5)

    def start(self):
        # ---------------- Start listening for messages ---------------- #
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.config['RABBITMQ']['queue'], on_message_callback=callback)

        logging.info("Waiting for messages...")
        self.channel.start_consuming()




