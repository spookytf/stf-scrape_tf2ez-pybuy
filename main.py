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
import configparser

def buy_item_with_id(item_id, item_price, item_hash_name):

    bot_inventory = driver.find_element(By.CLASS_NAME,"market-items")
    item_to_buy = bot_inventory.find_elements(By.XPATH,f"//div[@data-id={item_id}]")

    if len(item_to_buy) == 0:
        logging.info(f"({item_hash_name}) - Can not find this item in bot's inventory.")
        return {
            "success" : False,
            "message" : "There is no such item in bot's inventory"
        }
    else:
        wagered_balance = float(driver.find_element(By.ID,"withdraw-bal").text)

        if wagered_balance < item_price: return{
            "success" : False,
            "message" : f"You do not have enough wagered balance for this operation. [wagered balance: ${wagered_balance}, price: ${item_price}]."
        }

        logging.info(f"({item_hash_name}) - Adding to cart.")
        item_to_buy[0].click()
        driver.find_element(By.ID,"buyItems").click()
        return{
            "success" : True,
            "message" : f""
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
    
    status = buy_item_with_id(item_id,buy_usd,item_hash_name)
    if status['success'] is False: logging.info(f"({item_hash_name}) - Can not complete order. {status['message']}")
    else: logging.info(f"({item_hash_name}) - item bought succesfully.")

    # Discord notification there

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    dotenv.load_dotenv()
    pika_host = os.getenv("pika_host")
    pika_port = int(os.getenv("pika_port"))
    pika_username = os.getenv("pika_username")
    pika_password = os.getenv("pika_password")
    credentials = pika.PlainCredentials(pika_username, pika_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=pika_host, port=pika_port, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='stf-scrape_tf2ez',durable=True)

    logging.basicConfig(level="INFO",
                    format='%(levelname)s %(asctime)s - %(message)s',
                    datefmt='%H:%M:%S')
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='stf-scrape_tf2ez', on_message_callback=callback)

    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--start-maximized")

    config = configparser.ConfigParser()
    config.read('config.ini')

    login_method = config['LOGIN']['method'].lower()
    # head = config['BROWSER']['method'].lower()

    # if head == "headless": options.add_argument("--headless")

    global driver
    driver = uc.Chrome(options=options)
    global wait
    wait = WebDriverWait(driver,60)
    driver.get("https://www.tf2easy.com/")

    if login_method == "steam":
        driver.find_element(By.CLASS_NAME,"login-block").click()
        time.sleep(1)
        wait.until(EC.title_contains("TF2EASY.COM"))
    elif login_method == "cookie":
        login_cookie = os.getenv("login_cookie")
        driver.add_cookie({
            "name" : "laravel_session",
            "value" : login_cookie
        })
        driver.refresh()
    else:
        logging.info("You have to select login method in config.ini!")
        return
    try:
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'menu-username-text'))) 
    except:
        logging.info("Can not log in.")
        return

    logging.info("Logged in!")
    driver.get("https://www.tf2easy.com/market")
    
    time.sleep(5)
    
    logging.info("Checking tf2ez inventory.")
    channel.start_consuming()

if __name__ == "__main__":
    main()