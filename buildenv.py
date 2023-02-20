#!/usr/bin/env python3

# BUILD SCRIPTS ARE FUCKING INSANE FOR PYTHON WHAT THE FUCK
# -- @zudsniper on GitHub

RABBITMQ_QUEUE = "stf-scrape_tf2ez-pybuy"
LOGIN_METHOD = "steam" # steam or cookie
SCRAPE_URL = "https://tf2ez.com/"
DELAY_RANGE = 30 # seconds

def load_env():
    RABBITMQ_QUEUE = "stf-scrape_tf2ez-pybuy"
    LOGIN_METHOD = "steam" # steam or cookie
    SCRAPE_URL = "https://tf2ez.com/"
    DELAY_RANGE = 30 # seconds

def get_env(name):
    if name == "RABBITMQ_QUEUE":
        return RABBITMQ_QUEUE
    elif name == "LOGIN_METHOD":
        return LOGIN_METHOD
    elif name == "SCRAPE_URL":
        return SCRAPE_URL
    elif name == "DELAY_RANGE":
        return DELAY_RANGE
    else:
        return None

def set_env(name, value):
    if name == "RABBITMQ_QUEUE":
        RABBITMQ_QUEUE = value
    elif name == "LOGIN_METHOD":
        LOGIN_METHOD = value
    elif name == "SCRAPE_URL":
        SCRAPE_URL = value
    elif name == "DELAY_RANGE":
        DELAY_RANGE = value
    else:
        return None

def get_ini_env(method_login = "steam"):
    config = {
        "RABBITMQ": { queue: "stf-scrape_tf2ez-pybuy"},
        "LOGIN": {method: method_login},
        "SCRAPE": { url: "https://tf2ez.com/" },
        "TIMES": {delay_range: 30}
    }
    return config;