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

def main():

    dotenv.load_dotenv()
    pika_host = os.getenv("pika_host")
    pika_port = int(os.getenv("pika_port"))
    pika_username = os.getenv("pika_username")
    pika_password = os.getenv("pika_password")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=pika_host, port=pika_port, credentials=pika.PlainCredentials(pika_username, pika_password)))
    logging.basicConfig(level="INFO",
                    format='%(levelname)s %(asctime)s - %(message)s',
                    datefmt='%H:%M:%S')
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    
    driver = uc.Chrome()
    wait = WebDriverWait(driver,10*60)
    driver.get("https://www.tf2easy.com/")
    driver.find_element(By.CLASS_NAME,"login-block").click()
    time.sleep(1)
    wait.until(EC.title_contains("TF2EASY.COM"))
    logging.info("Logged in!")
    driver.get("https://www.tf2easy.com/market")
    input()

if __name__ == "__main__":
    main()