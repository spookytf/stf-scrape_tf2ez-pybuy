import pika
import dotenv
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import discord_webhook
import time as time
import logging
import json
import random
import functools
import coloredlogs

# ----------------- #
#  GLOBAL VARIABLES #
# ----------------- #
global BLOCKED_CONNECTION_TIMEOUT
BLOCKED_CONNECTION_TIMEOUT = 60 * 31  # 31 minutes

global platform
global LAST_TIME
LAST_TIME = -1
global DELAY_RANGE
DELAY_RANGE = 15

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


# global ITEMS
# ITEMS = []
global discord_webhook, webhook
discord_webhook_link = os.getenv("WEBHOOK_LINK")
webhook = discord_webhook.DiscordWebhook(url=discord_webhook_link)

checked_list = []


def callback(ch, method, properties, body):
    global DELAY_RANGE, PROFIT, ITEMS_BOUGHT, ITEMS_MISSED
    # logging.debug("TIME UNTIL NEXT BUY: " + str(time.time() - LAST_TIME) + " seconds")
    if body == b'':
        logging.error("Received empty message. Moving on.")
        return
    elif body is None or body == b'null':
        logging.error("Received None message. Moving on.")
        return
    try:
        message_dict = json.loads(body)
    except:
        logging.error("Received invalid message. Moving on.")
        logging.debug(body)
        return

    # message_dict = json.loads(body)
    item_hash_name = message_dict['item_hash_name']
    item_id = message_dict['item_id']

    # if item_id in checked_list: return

    checked_list.append(item_id)
    if len(checked_list) == 80: checked_list.pop(0)

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

    # calculate profit
    profit = sell_usd - buy_usd

    # global ITEMS
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
    # global COOLDOWN, DELAY_RANGE
    # if(time.time() - LAST_TIME > COOLDOWN):

    # rand_delay = random.randint(0, DELAY_RANGE)
    # logging.debug("rand_delay: " + str(rand_delay) + " seconds")
    # time.sleep(rand_delay)
    # COOLDOWN = rand_delay
    # logging.info("COOLDOWN: " + str(COOLDOWN) + " seconds")

    # select the first item in the list (most profit) (sorted above)
    # item_id = ITEMS[0]['item']['item_id']
    # item_hash_name = ITEMS[0]['item']['item_hash_name']
    # buy_usd = ITEMS[0]['item']['buy_prices']['usd']

    # remove the item from the list
    # ITEMS.pop(0)

    # input(f"Buy some shit? Profit: ${profit} -- hit enter to continue...")  # TODO: remove this
    status = buy_item_by_id(item_id, buy_usd, item_hash_name)

    # wait(5) #TODO: stupid
    global webhook, discord_webhook
    if not status['success']:
        logging.error(f"({item_hash_name}) - Cannot complete order. {status['message']}")
        ITEMS_MISSED = ITEMS_MISSED + 1
        embed = discord_webhook.DiscordEmbed(title=f"({item_hash_name}) - N/A", description=f"{status['message']}",
                                             color='ff0000')
    else:
        logging.info(f"({item_hash_name}) - item bought successfully.")
        PROFIT = PROFIT + profit
        ITEMS_BOUGHT = ITEMS_BOUGHT + 1
        embed = discord_webhook.DiscordEmbed(title=f"({item_hash_name}) - ${profit:.2f} net",
                                             description=f"{status['message']}", color='43cf3c')

    # update GUI component (maybe)
    # global GUI_OBJECTS
    # GUI_OBJECTS['subtext_str'].set(f"Profit: ${PROFIT:.2f} | Items bought: {ITEMS_BOUGHT} | Items missed: {ITEMS_MISSED}")
    # GUI_OBJECTS['subtext_str'].config(textvariable=GUI_OBJECTS['subtext_str'])
    logging.critical(f"Profit: ${PROFIT:.2f} | Items bought: {ITEMS_BOUGHT} | Items missed: {ITEMS_MISSED}")

    # Discord notification ... above & below
    embed.set_author(name="the ghost of gambling", url="https://rat.church",
                     icon_url="https://i.imgur.com/In7Urki.jpg")
    embed.set_footer(text="END (or start?) GAMBLING NOW", icon_url="https://i.imgur.com/6Oqrqsi.jpg",
                     url="https://rat.church")
    embed.set_timestamp()
    embed.add_embed_field(name="Items bought", value=f"{ITEMS_BOUGHT}", inline=True)
    embed.add_embed_field(name="Items missed", value=f"{ITEMS_MISSED}", inline=True)
    embed.add_embed_field(name="PROFIT THIS SESSION", value=f"${PROFIT:.2f}")
    embed.add_embed_field(name="Total items", value=f"{ITEMS_BOUGHT + ITEMS_MISSED}")
    embed.add_embed_field(name="Profit per item", value=f"${PROFIT / (ITEMS_BOUGHT + ITEMS_MISSED):.2f}")

    webhook.add_embed(embed=embed)
    webhook.execute(remove_embeds=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)

    # else:
    # global ELAPSED_TIME, ELAPSED_STR
    # ELAPSED_TIME = COOLDOWN - LAST_TIME

    # if ELAPSED_STR is not None:
    # ELAPSED_STR.set("cooldown left: " + str(COOLDOWN - ELAPSED_TIME))


def msg_callback_wrapper(ch, method, properties, body):
    try:
        callback(ch, method, properties, body)
    except Exception as e:
        logging.error(f"Exception in callback: {e}")
        logging.debug(e)


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
    pika_routing_key = None
    pika_exchange = None

    def __init__(self, logging, pika_host, pika_port, pika_username, pika_password, pika_queue, pika_routing_key, pika_exchange, delay_range, scrape_url,
                 login_method):
        self.delay_range = delay_range
        logging = logging
        self.connection = None
        self.channel = None
        self.scrape_url = scrape_url
        self.pika_host = pika_host
        self.pika_port = pika_port
        self.pika_username = pika_username
        self.pika_password = pika_password
        self.pika_queue = pika_queue
        self.pika_routing_key = pika_routing_key
        self.pika_exchange = pika_exchange

        self.login_method = login_method

        # make sure URL ends with a slash

        if self.scrape_url is not None:
            if not scrape_url.endswith("/"):
                scrape_url = scrape_url + "/"

            self.main()
        else:
            logging.error("No scrape URL provided. Exiting. FRICK YOU!!!")
            exit(1)

    def delayed_passthrough(self, name, object):
        global GUI_OBJECTS
        GUI_OBJECTS[name] = object

    def init_selenium_and_login(self):

        # ---------------- Configure Driver Options ---------------- #
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--start-maximized")

        # ---------------- Init Driver, then Login ---------------- #
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
        driver.get(self.scrape_url)

        # override with dotenv
        if os.getenv("LOGIN_METHOD") is not None:
            if os.getenv("LOGIN_METHOD") != "":
                self.login_method = os.getenv("LOGIN_METHOD")
            elif os.getenv("LOGIN_METHOD") != "cookie":
                self.login_method = "steam"
            self.login_method = self.login_method.lower()

        #logging.info("login method is defined as: " + self.login_method)

        # what if cookie is invalid ya dingus
        if os.getenv("login_cookie") is not None and os.getenv("login_cookie") != "":
            logging.warn("you've set login_method to \"steam\", but your cookie is configured. Switching modes...")
            #self.login_method = "cookie"
            dotenv.set_key('.env', 'LOGIN_METHOD', 'cookie')

            logging.critical("no more login methods. fuck that.")
            # logging.info("login method is now defined as: " + self.login_method)
            login_cookie = os.getenv("login_cookie")
            driver.add_cookie({
                "name": "laravel_session",
                "value": login_cookie
            })
        else:
            driver.find_element(By.CLASS_NAME, "login-block").click()
            time.sleep(1)
            wait.until(EC.title_contains("TF2EASY.COM"))
        driver.refresh()

        # logging.warn("you're in cookie mode, but your cookie isn't set. Switching modes...")
        # self.login_method = "steam"
        # logging.info("login method is now defined as: " + self.login_method)
        # logging.warn("you will need to login to steam in the browser window that is now open.")
        # driver.get(self.scrape_url)
        # driver.find_element(By.CLASS_NAME, "login-block").click()
        # time.sleep(1)
        # wait.until(EC.title_contains("TF2EASY.COM"))
        # logging.info("Excellent, you're logged in. Changing your login_method to 'cookie' in .env")
        # dotenv.set_key('.env', 'LOGIN_METHOD', 'cookie')
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menu-username-text')))
            if self.login_method == "steam":
                generated_cookie = driver.get_cookie("laravel_session")['value']
                dotenv.set_key('.env', 'LOGIN_COOKIE', generated_cookie)
        except:
            logging.error("Couldn't login. (incorrect cookie?).")
            if os.getenv("login_cookie") is not None and os.getenv("login_cookie" != ""):
                logging.warn("found invalid cookie. Removing")
                dotenv.set_key('.env', 'LOGIN_COOKIE', '')
                #dotenv.set_key('.env', 'LOGIN_METHOD', 'steam')
                #logging.info("login method is now defined as: " + self.login_method)
                loggin.info("trying to log you in...")
                try:
                    driver.find_element(By.CLASS_NAME, "login-block").click()
                    time.sleep(1)
                    wait.until(EC.title_contains("TF2EASY.COM"))
                    logger.info("LOGGED IN SUCCESSFULLY!")
                    logger.warn("waiting for your cookie & placing it into .env...")
                    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menu-username-text')))
                    generated_cookie = driver.get_cookie("laravel_session")['value']
                    dotenv.set_key('.env', 'LOGIN_COOKIE', generated_cookie)
                    logger.info("all done. Have a nice flight.")
                except:
                    logging.critical(
                        "Failed to log you in a second time. Please check network connection & bandwidth, then restart.")
                    return
        logging.info("LOGGED IN SUCCESSFULLY!")
        driver.get(self.scrape_url + "market")

        # wait for market nav to load
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'new-item-info-holder')))


    def main(self):
        # self.init_selenium_and_login()
        global DELAY_RANGE
        DELAY_RANGE = self.delay_range
        logging.warning("Deal listener initialized.")

    def start(self):
        global BLOCKED_CONNECTION_TIMEOUT
        # ---------------- Start listening for messages ---------------- #
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.pika_host,
                                      port=self.pika_port,
                                      credentials=pika.PlainCredentials(self.pika_username, self.pika_password),
                                      virtual_host="/",
                                      channel_max=1000,
                                      connection_attempts=10,
                                      retry_delay=10,
                                      heartbeat=300,
                                      blocked_connection_timeout=BLOCKED_CONNECTION_TIMEOUT))
        self.channel = self.connection.channel()

        # this is determined by the publisher(s)
        # self.channel.confirm_delivery()

        self.channel.queue_declare(queue=self.pika_queue, durable=True, exclusive=False, auto_delete=False)
        self.channel.queue_bind(exchange=self.pika_queue, queue=self.pika_queue, routing_key=self.pika_queue)
        self.channel.basic_qos(prefetch_count=200)

        self.channel.basic_consume(on_message_callback=msg_callback_wrapper, queue=self.pika_queue, auto_ack=True,
                                   exclusive=False)
        # self.channel.consume(self.pika_queue, callback, auto_ack=False, exclusive=False)

        # clear old deals so we don't waste time
        # self.channel.queue_purge(queue=self.pika_queue)
        logging.info("Waiting for messages...")
        try:
            self.channel.start_consuming()
        except Exception as e:
            logging.error("Exception in start_consuming: " + str(e))
            self.on_closing()
            wait(3)
            self.start()

    def on_closing(self):
        if self.channel is not None:
            self.channel.stop_consuming()
            self.channel.close()
        if self.connection is not None:
            self.connection.close()
        # global driver
        # if driver is not None:
        #     driver.quit()

    def stop(self):
        if self.channel is not None:
            self.channel.stop_consuming()
            self.channel.close()
        if self.connection is not None:
            self.connection.close()
        # exit(0) # causes an exception if not here
        # global driver
        # if driver is not None:
        #     driver.quit()



