import pika
import dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium import webdriver
import discord_webhook
import time as time
import logging
import json
import random

global platform


global STEAM_USERNAME
STEAM_USERNAME = None
# ------------- #
global LAST_TIME
LAST_TIME = -1
global DELAY_RANGE
DELAY_RANGE = 15
# ------------- #

global PROFIT, ITEMS_BOUGHT, ITEMS_MISSED
PROFIT = 0
ITEMS_BOUGHT = 0
ITEMS_MISSED = 0

global GUI_OBJECTS
GUI_OBJECTS = {}

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

# handle logging

logging = logging.getLogger("buyListener")
MANAGER = logging.manager;


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


#global ITEMS
#ITEMS = []
discord_webhook_link = os.getenv("WEBHOOK_LINK")
webhook = discord_webhook.DiscordWebhook(url=discord_webhook_link)

CHECK_LIST_SIZE = 80
checked_list = []
def callback(ch, method, properties, body):
    global DELAY_RANGE, PROFIT, ITEMS_BOUGHT, ITEMS_MISSED
    # logging.debug("TIME UNTIL NEXT BUY: " + str(time.time() - LAST_TIME) + " seconds")
    logging.debug(" [x] Received %r" % body)
    message_dict = json.loads(body)
    item_hash_name = message_dict['item_hash_name']
    item_id = message_dict['item_id']

    # if item_id in checked_list: return


    # keep checked_list at 80 items
    checked_list.append(item_id)
    if len(checked_list) >= CHECK_LIST_SIZE:
        checked_list.pop(0)

    buy_prices = message_dict['buy_prices']
    buy_usd = buy_prices['usd']
    buy_keys = buy_prices['keys']
    buy_refs = buy_prices['refs']

    sell_prices = message_dict['sell_prices']

    buyer_id = sell_prices['steamid']

    sell_usd = sell_prices['usd']
    sell_keys = sell_prices['keys']
    sell_refs = sell_prices['refs']

    logging.warning(f"({item_hash_name}) - Attempting to buy for ${buy_usd}.")

    # calculate profit
    profit = sell_usd - buy_usd

    #global ITEMS
    # base case: if list is empty
    # if not len(ITEMS):
    #     ITEMS.append({
    #         'profit': profit,
    #         'item': message_dict,
    #     })
    #     logging.debug(f"({item_hash_name}) - Profit: ${profit}.")
    #
    # # insert sorted by profit
    # for index, item in enumerate(ITEMS):
    #     if item['profit'] < profit:
    #         ITEMS.insert(index, {
    #             'profit': profit,
    #             'item': message_dict,
    #         })
    #         break

    # if we've elapsed the cooldown time, buy the best item.
    # TODO: what if this item is already gone by the time we finish our cooldown? @Osc44r
    #       this is a FATAL flaw... I'm refactoring.
    #global COOLDOWN, DELAY_RANGE
    #if(time.time() - LAST_TIME > COOLDOWN):

    rand_delay = random.randint(0, DELAY_RANGE)
    logging.debug("rand_delay: " + str(rand_delay) + " seconds")
    logging.warning("Waiting " + str(rand_delay) + " seconds before buying...");
    time.sleep(rand_delay)
    #COOLDOWN = rand_delay
    #logging.info("COOLDOWN: " + str(COOLDOWN) + " seconds")

    # select the first item in the list (most profit) (sorted above)
    #item_id = ITEMS[0]['item']['item_id']
    #item_hash_name = ITEMS[0]['item']['item_hash_name']
    #buy_usd = ITEMS[0]['item']['buy_prices']['usd']

    # remove the item from the list
    #ITEMS.pop(0)

    # input(f"Buy some shit? Profit: ${profit} -- hit enter to continue...")  # TODO: remove this
    status = buy_item_by_id(item_id, buy_usd, item_hash_name)

    wait(5) #TODO: stupid

    if not status['success']:
        logging.error(f"({item_hash_name}) - Cannot complete order. {status['message']}")
        ITEMS_MISSED = ITEMS_MISSED + 1
        embed = discord_webhook.DiscordEmbed(title=f"({item_hash_name}) - N/A", description=f"{status['message']}", color='ff0000')
    else:
        logging.info(f"({item_hash_name}) - item bought successfully.")
        PROFIT = PROFIT + profit
        ITEMS_BOUGHT = ITEMS_BOUGHT + 1
        embed = discord_webhook.DiscordEmbed(title=f"({item_hash_name}) - ${profit:.2f} net",
                                                      description=f"{status['message']}", color='43cf3c')

    # update GUI component (maybe)
    global GUI_OBJECTS
    GUI_OBJECTS['subtext_str'].set(f"Profit: ${PROFIT:.2f} | Items bought: {ITEMS_BOUGHT} | Items missed: {ITEMS_MISSED}")
    GUI_OBJECTS['subtext_str'].config(textvariable=GUI_OBJECTS['subtext_str'])
    logging.critical(f"Profit: ${PROFIT:.2f} | Items bought: {ITEMS_BOUGHT} | Items missed: {ITEMS_MISSED}")

    # Discord notification ... above & below
    embed.set_author(name="the ghost of gambling", url="https://rat.church",
                       icon_url="https://i.imgur.com/In7Urki.jpg")
    embed.set_footer(text="END (or start?) GAMBLING NOW", icon_url="https://i.imgur.com/6Oqrqsi.jpg",
                       url="https://rat.church")
    embed.set_timestamp()
    embed.add_embed_field(name="Items bought", value=f"{ITEMS_BOUGHT}",inline=True)
    embed.add_embed_field(name="Items missed", value=f"{ITEMS_MISSED}",inline=True)
    embed.add_embed_field(name="PROFIT THIS SESSION", value=f"${PROFIT:.2f}")
    embed.add_embed_field(name="Total items", value=f"{ITEMS_BOUGHT + ITEMS_MISSED}")
    embed.add_embed_field(name="Profit per item", value=f"${PROFIT / (ITEMS_BOUGHT + ITEMS_MISSED):.2f}")

    webhook.add_embed(embed=embed)
    webhook.execute(remove_embeds=True)

    # acknowledge message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    #else:
        #global ELAPSED_TIME, ELAPSED_STR
        #ELAPSED_TIME = COOLDOWN - LAST_TIME

    #if ELAPSED_STR is not None:
        #ELAPSED_STR.set("cooldown left: " + str(COOLDOWN - ELAPSED_TIME))

 # https://stackoverflow.com/a/63625977
def get_browser_log_entries(driver):
    """get log entreies from selenium and add to python logger before returning"""
    loglevels = { 'NOTSET':0 , 'DEBUG':10 ,'INFO': 20 , 'WARNING':30, 'ERROR':40, 'SEVERE':40, 'CRITICAL':50}

    #initialise a logger
    browserlog = logging.getLogger("tf2ez")
    #get browser logs
    slurped_logs = driver.get_log('browser')
    for entry in slurped_logs:
        #convert broswer log to python log format
        rec = browserlog.makeRecord("%s.%s"%(browserlog.name,entry['source']),loglevels.get(entry['level']),'.',0,entry['message'],None,None)
        rec.created = entry['timestamp'] /1000 # log using original timestamp.. us -> ms
        try:
            #add browser log to python log
            browserlog.handle(rec)
        except:
            print(entry)
    #and return logs incase you want them
    return slurped_logs


class BuyListener:
    # constructor passthrough configuration items
    channel = None
    config = None
    connection = None
    login_method = None
    scrape_url = None
    delay_range = None
    pika_host = None
    pika_port = None
    pika_username = None
    pika_password = None
    pika_queue = None
    text_handler = None

    def __init__(self, pika_host, pika_port, pika_username, pika_password, pika_queue, delay_range, scrape_url, login_method):
        self.delay_range = delay_range
        self.connection = None
        self.channel = None
        self.scrape_url = scrape_url
        self.pika_host = pika_host
        self.pika_port = pika_port
        self.pika_username = pika_username
        self.pika_password = pika_password
        self.pika_queue = pika_queue
        self.login_method = login_method

        # make sure URL ends with a slash

        if self.scrape_url is not None:
            if not scrape_url.endswith("/"):
                scrape_url = scrape_url + "/"

            self.main()

    # def delayed_passthrough(self, name, obj, callback=None):
    #     global GUI_OBJECTS
    #     GUI_OBJECTS[name] = obj
    #
    #     if name == 'textHandler':
    #         self.text_handler = obj
    #
    #     if name == 'subtext_str':
    #         GUI_OBJECTS['subtext_str'].set(f"Profit: ${PROFIT:.2f} | Items bought: {ITEMS_BOUGHT} | Items missed: {ITEMS_MISSED}")
    #         GUI_OBJECTS['subtext_str'].config(textvariable=GUI_OBJECTS['subtext_str'])
    #
    #     if callback is not None:
    #         callback([name, obj])
    #     else:
    #         return obj

    def init_selenium_and_login(self, login_method=None):

        logger = logging.getLogger(__name__)
        logger.setLevel(os.getenv('log_level'))
        logger.addHandler(self.text_handler)

        if os.getenv("login_method") is ["steam", "cookie"]:
            login_method = os.getenv("login_method")
        if login_method is None:
            login_method = self.login_method # default to config.ini

        # ---------------- Configure Driver Options ---------------- #
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--start-maximized")

       # global GUI_OBJECTS
        #logging.addHandler(GUI_OBJECTS['textHandler'])
        # ---------------- Init Driver, then Login ---------------- #

        if not OS == "windows":
            try:
                global driver
                caps = uc.DesiredCapabilities.CHROME.copy()
                caps['acceptInsecureCerts'] = True
                caps['goog:loggingPrefs'] = {'browser': 'ALL'}

                driver = uc.Chrome(options=options, executable_path=os.path.abspath("./chromedriver"), desired_capabilities=caps)
            except:
                logger.error("Couldn't find the default Google Chrome binaries. Perhaps you haven't installed Google "
                              "Chrome?")
                logger.error("if you are on Ubuntu/Debian: make sure you have wget, then use the following command "
                              "to install the latest version of Google Chrome:")
                logger.critical("$ wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb "
                                 "&& sudo dpkg -i google-chrome-stable_current_amd64.deb")
                input("Press any key to exit...")
                exit(1)
        else:
            driver = uc.Chrome(options=options)

            consolemsgs = get_browser_log_entries(driver)

        #TODO: intrigue
        #driver.add_virtual_authenticator()

        global wait
        wait = WebDriverWait(driver, 60)
        driver.get(self.scrape_url)

        login_method = login_method.lower()

        logger.info("login method is defined as: " + login_method)
        if login_method == "steam":
            driver.find_element(By.CLASS_NAME, "login-block").click()
            time.sleep(1)
            wait.until(EC.title_contains("TF2EASY.COM"))
            #TODO: FIX -- this does land you on steam login, but we need the AUTHENTICATED page which comes afterwards.
            # landing on the steam OpenID login page, we need to click the login button -- but
            #       we'd like to grab the steam username for error reporting as well as like
            #       a steamid64 to link to them (too hard) and a base64 of their avatar for a nice little
            #       profile picture in the embed
            STEAM_USERNAME = os.getenv("STEAM_USERNAME")
            STEAM_AVATAR_TINYLINK = os.getenv("STEAM_AVATAR_TINYLINK")

            if STEAM_USERNAME is None or STEAM_USERNAME == "":
                STEAM_USERNAME = driver.find_element(By.CLASS_NAME, "OpenID_loggedInAccount").get_property("innerText")
                logger.debug("STEAM_USERNAME = " + STEAM_USERNAME)
                os.set_key('.env', 'STEAM_USERNAME', STEAM_USERNAME)
            if STEAM_AVATAR_TINYLINK is None or STEAM_AVATAR_TINYLINK == "":
                STEAM_AVATAR_TINYLINK = driver.find_element(By.CSS_SELECTOR, "#openidForm > div > div.OpenID_UserContainer > div.playerAvatar.online > img").get_attribute("src")
                logger.debug("STEAM_AVATAR_TINYLINK = " + STEAM_AVATAR_TINYLINK)
                os.set_key('.env', 'STEAM_AVATAR_TINYLINK', STEAM_AVATAR_TINYLINK)
        elif login_method == "cookie":
            login_cookie = os.getenv("login_cookie")
            driver.add_cookie({
                "name": "laravel_session",
                "value": login_cookie
            })
            driver.refresh()
        else:
            logger.critical("You have to select login method in config.ini!") # not true anymore
            wait(6)
            logger.info("... wait... you don't need to include the login method in config.ini!!")
            logger.info("Welp, try again")
            return
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menu-username-text')))
            if login_method == "steam":
                generated_cookie = driver.get_cookie("laravel_session")['value']
                dotenv.set_key('.env', 'LOGIN_METHOD', 'cookie')
                dotenv.set_key('.env', 'LOGIN_COOKIE', generated_cookie)
                logger.info("Login method is now set to cookie and cookie is saved in .env file.")
        except:
            logger.critical("Couldn't login. (Wrong cookie?)")
            dotenv.set_key('.env', 'LOGIN_METHOD', 'steam')
            dotenv.set_key('.env', 'LOGIN_COOKIE', '')
            logger.info("Login method is now set to steam and expired cookie is removed from .env file.")
            return

        logger.info("LOGGED IN SUCCESSFULLY!")
        logger.warning("Click start to connect and begin consuming to the message queue. Click stop to disconnect.")
        logger.info("Navigating to market section...")
        driver.get(self.scrape_url + "market")

        # wait for market nav to load
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'new-item-info-holder')))

    def main(self):
        #self.init_selenium_and_login()
        global DELAY_RANGE, GUI_OBJECTS
        DELAY_RANGE = self.delay_range
        start()


    def start(self):
        logger = logging.getLogger("rabbitmq").setLevel("DEBUG")
        logger.addHandler(text_handler)
        _EARLY_LOG_HANDLER = logging.StreamHandler(sys.stdout)
        log = logging.getLogger()
        log.addHandler(_EARLY_LOG_HANDLER)
        if level is not None:
            log.setLevel(level)

        _EARLY_ERR_HANDLER = logging.StreamHandler(sys.stderr)
        log = logging.getLogger()
        log.addHandler(_EARLY_LOG_HANDLER)
        if level is not None:
            log.setLevel(level)

        _EARLY_LOG_HANDLER.setLevel(logging.getLogger().level)
        _EARLY_ERR_HANDLER.setLevel(logging.getLogger().level)
        # ---------------- Start listening for messages ---------------- #
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.pika_host, port=self.pika_port, credentials=pika.PlainCredentials(self.pika_username, self.pika_password)))
        self.channel = self.connection.channel()
        logger.info("Connected to RabbitMQ server: channel opened, declaring queue...")

        self.channel.queue_declare(queue=self.pika_queue, durable=True, auto_delete=False, exclusive=False)
        logger.info("Queue declared...")

        # TODO: Seemingly required... but why?
        self.channel.confirm_delivery()
        logger.info("confirm_delivery set...")
        # self.channel.basic_qos(prefetch_count==0)
        # logger.info("basic_qos set...")
        self.channel.basic_consume(queue=self.pika_queue, on_message_callback=callback, auto_ack=True, durable=True, exclusive=False)
        logger.info("basic_consume set up... now we must start consuming.")

        # clear old deals so we don't waste time
        # self.channel.queue_purge(queue=self.pika_queue)
        logger.warn("CONSUMING...")
        self.channel.start_consuming()

    def stop(self):
        logger.critical("STOP ISSUED -- Stopping deal listener...")
        if self.connection is not None :
            logger.error("Closing connection to RabbitMQ server...")
            self.connection.close()
        if self.channel is not None :
            logger.error("Closing channel to RabbitMQ server...")
            self.channel.stop_consuming()
            self.channel.close()
        logger.info("Deal listener stopped.")
        exit(0)
        if driver is not None:
            driver.quit()
