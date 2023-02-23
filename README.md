# `stf-scrape_tf2ez-pybuy`
### <u>v2.1.0b4</u>
This is a Python-based scraper for purchasing undervalued items on tf2easy.com. The application is designed to communicate with stf-scrape_tf2ez using rabbitmq.

> Written by [@Osc44r](https://github.com/Osc44r) & [@zudsniper](https://github.com/zudsniper), software developers at [**SpookyTF**](https://spooky.tf/)    

## Prerequisites

To use `stf-scrape_tf2ez-pybuy`, you must have the following:

- `Python 3.7` or higher
- An active `Steam` account on `tf2easy.com`
- **A `rabbitmq` instance... CONFIGURED...**
> [@zudsniper](https://github.com/zudsniper) had a hard time with this. If you need help, contact him.
- A user on that instance with username and password
- A Discord text channel with webhook link

## Installation
To install `stf-scrape_tf2ez-pybuy`, simply clone the repository to your local machine:

```shell
$ git clone https://github.com/your-username/stf-scrape_tf2ez-pybuy.git
```

## Configuration
### `@Deprecated`

~~The `config.ini` file contains only one option under `[LOGIN]:~~
 > _this file is being phased out in favor of a `.env` file based environment. Still, it will be used for non-sensitive parameters, or as default values on the rare occasion._
```ini
[LOGIN]

method = cookie/steam
```

If you select `cookie`, you will need to add the `laravel_session` cookie in the `.env` file. However, it will not require steam login every time you launch the program. Selecting `steam` will do the opposite.

You will also need to create a `.env` file in the following format:

```ini
PIKA_HOST=
PIKA_PORT=
PIKA_USERNAME=
PIKA_PASSWORD=
PIKA_QUEUE=
PIKA_EXCHANGE=
PIKA_ROUTING_KEY=
LOGIN_COOKIE=
WEBHOOK_LINK=
```

If you have any questions or require further assistance, please feel free to contact the project owner.

---

[![banner-logo](https://user-images.githubusercontent.com/16076573/192673098-48467c36-2d96-43ca-bc02-5ec993989ceb.gif)](https://spooky.tf/)    
*spooky.tf*  
**ALL RIGHTS RESERVED**
