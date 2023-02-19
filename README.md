# stf-scrape_tf2ez-pybuy

This is a Python-based scraper for purchasing undervalued items on tf2easy.com. The application is designed to communicate with stf-scrape_tf2ez using rabbitmq.

## Prerequisites

To use stf-scrape_tf2ez-pybuy, you must have the following:

- Python 3.7 or higher
- An active account on tf2easy.com
- A pika broker running with username and password

## Installation

To install stf-scrape_tf2ez-pybuy, simply clone the repository to your local machine:

`git clone https://github.com/your-username/stf-scrape_tf2ez-pybuy.git`

## Configuration

The `config.ini` file contains only one option under `[LOGIN]`:

`method = cookie/steam`


If you select `cookie`, you will need to add the cookie in the `.env` file. However, it will not require steam login every time you launch the program. Selecting `steam` will do the opposite.

You will also need to create a `.env` file in the following format:

```
pika_host =
pika_port =
pika_username =
pika_password =
login_cookie =
```
If you have any questions or require further assistance, please feel free to contact the project owner.

[![banner-logo](https://user-images.githubusercontent.com/16076573/192673098-48467c36-2d96-43ca-bc02-5ec993989ceb.gif)](https://spooky.tf/)    
*spooky.tf*  
**ALL RIGHTS RESERVED**
