import dotenv
import os
import configparser
import tkinter
import threading
import coloredlogs, logging
import pathlib
import time
import tkinter as tk # Python 3.x
import tkinter.scrolledtext as ScrolledText

from buy_listener import BuyListener

global COOLDOWN
COOLDOWN = 0
global LAST_TIME
LAST_TIME = float(time.time())
global ELAPSED_TIME
ELAPSED_TIME = 0

LOG_COLOR_LEVEL_TO_COLOR = {
    'DEBUG': 'black',
    'INFO': 'green',
    'WARNING': 'grey',
    'ERROR': 'red',
    'CRITICAL': 'red',
}

config = None;
pika_host = None;
pika_port = None;
pika_username = None;
pika_password = None;
pika_queue = None;
scrape_url = None;

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        #logging.Handler.setFormatter(self, coloredlogs.ColoredFormatter())

        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n', record.levelname)
            self.text.tag_config(record.levelname, foreground=f"{LOG_COLOR_LEVEL_TO_COLOR[record.levelname]}")
            self.text.tag_config("CRITICAL", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['CRITICAL']}", font=("Arial", 10, "bold"))
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

class GUI(threading.Thread):
    elapsed_str = None
    def __init__(self, buy_listener):
        super().__init__()
        self.thread = None
        self.buy_listener = buy_listener
        self.build()

    # ---------------- START GUI ---------------- #
    def build(self):
        self.root = tkinter.Tk()

        self.root.title("TF2EZ_PYBUY")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.frame = tkinter.Frame(self.root)

        self.root.frame.t_label = tkinter.Label(self.root.frame, text="TF2EZ_PYBUY", font=("Arial", 13, "bold"), fg="black" )
        self.root.frame.t_label.grid(column=0, row=0, sticky="s", padx=5, pady=5, columnspan=4)
        # it was JASON that chose this font
        # and I'm not going to change it
        # because I'm not a monster
        # This was still me, JASON, who chose this font
        self.root.frame.label = tkinter.Label(self.root.frame, text="not running", font=("Comics Sans", 12), fg="black")
        self.root.frame.label.grid(column=0, row=4, sticky='ewn', padx=5, pady=5, columnspan=1)

        global ELAPSED_TIME, COOLDOWN
        self.elapsed_str = tkinter.StringVar()
        self.elapsed_str.set("cooldown left: " + str(COOLDOWN - ELAPSED_TIME))
        self.root.frame.ctn_label = tkinter.Label(self.root.frame, textvariable=self.elapsed_str, font=("Comics Sans", 12), fg="blue")
        self.root.frame.ctn_label.grid(column=0, row=5, sticky='ews', padx=5, pady=5, columnspan=1)

        self.root.frame.button = tkinter.Button(self.root.frame, text="start", command=self.start, font=("Comics Sans", 14), fg="green", state="disabled")
        self.root.frame.button.grid(column=3, row=4, sticky='ewn', padx=5, pady=5, columnspan=2)

        if os.getenv('LOGIN_COOKIE') is not None:
            self.root.frame.label = tkinter.Label(self.root.frame, text="cookie found, log in!", font=("Comics Sans", 12), fg="green")
            self.root.frame.label.grid(column=0, row=4, sticky='ewn', padx=5, pady=5, columnspan=1)
            self.root.frame.login_button = tkinter.Button(self.root.frame, text="🟡 login ", font=("Comics Sans", 14), fg="yellow", bg="black", command=self.login, state="normal")
            #self.root.frame.login_button.grid(column=3, row=5, sticky='ewn', padx=5, pady=5, columnspan=2)
        else:
            self.root.frame.login_button = tkinter.Button(self.root.frame, text="❌ not logged in", command=self.login, font=("Comics Sans", 14), fg="red", state="normal")
        self.root.frame.login_button.grid(column=3, row=5, sticky='ewn', padx=5, pady=5, columnspan=2)

        self.root.option_add('*tearOff', 'FALSE')
        self.root.frame.grid(column=0, row=0, sticky='new')
        self.root.frame.grid_columnconfigure(0, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(1, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(2, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(3, weight=1, uniform='a')

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(self.root.frame, state='disabled')
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=1, sticky='wsen', columnspan=4)

        # Create textLogger
        text_handler = TextHandler(st)

        # ---------------- END GUI ---------------- #

        if not os.path.exists("logs/tf2ez_pybuy.log"):
            pathlib.Path("logs").mkdir(parents=True, exist_ok=True)
            pathlib.Path("logs/tf2ez_pybuy.log").touch()

        # clear if log is too big
        # if fs := os.path.getsize("logs/tf2ez_pybuy.log.old") > 1000000:
        #     os.remove("logs/tf2ez_pybuy_ALL.log")

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)

        self.root.frame.pack( side = "bottom", fill = "x", expand = True, pady=10, padx=10)
        self.root.frame.pack_propagate(False)
        self.root.mainloop()

    def start(self):
        self.thread = threading.Thread(target=self.thread_func)
        self.thread.start()

    def login(self):
        threading.Thread(target=self.login_thread).start()

    def login_thread(self):
        self.root.frame.label["text"] = "logging in..."
        self.root.frame.login_button["text"] = "logging in..."
        self.root.frame.login_button["fg"] = "black"
        self.root.frame.button["state"] = "disabled"
        self.root.frame.login_button["state"] = "disabled"
        self.buy_listener.init_selenium_and_login()
        if os.getenv('LOGIN_COOKIE') is not None:
            self.root.frame.label["text"] = "logged in!"
            self.root.frame.login_button["text"] = "✅ logged in"
            self.root.frame.login_button["state"] = "disabled"
            self.root.frame.button["state"] = "normal"
        else:
            self.root.frame.label["text"] = "login failed"
            self.root.frame.label["fg"] = "red"
            self.root.frame.login_button["text"] = "❌ not logged in"
            self.root.frame.login_button["state"] = "normal"

        self.root.attributes('-topmost',True)

    def stop(self):
        self.buy_listener.stop()
        self.root.frame.label["text"] = "not running"
        self.root.frame.button.configure(text="start", command=self.start, fg="green")

    def thread_func(self):
        self.root.frame.button["state"] = "normal"
        self.root.frame.label["text"] = "running..."
        self.root.frame.button.configure(text="stop", command=self.stop, fg="red")
        # Run buy_listener to listen for messages
        # self.testing_spam_logs(100)
        self.buy_listener.start()

        # never reached
        # self.label["text"] = "done"
        # self.button["state"] = "normal"

    def on_closing(self):
        self.root.frame.quit()
        for widget in self.root.frame.winfo_children():
            widget.destroy()
        self.root.destroy()
        self.buy_listener.stop()
        exit(0)

    # ---------------- DEBUG FUNCTION  ---------------- #
    def testing_spam_logs(self, n=100):
        for i in range(n):
            if i % 5 == 0:
                logging.debug("test")
            elif i % 5 == 1:
                logging.info("test")
            elif i % 5 == 2:
                logging.warning("test")
            elif i % 5 == 3:
                logging.error("test")
            elif i % 5 == 4:
                logging.critical("test")
def main():
    # ---------------- Load variables ---------------- #
    config = configparser.ConfigParser()
    config.read('config.ini')
    dotenv.load_dotenv()

    # ---------------- Configure RabbitMQ ---------------- #
    pika_host = os.getenv("PIKA_HOST")
    pika_port = int(os.getenv("PIKA_PORT"))
    pika_username = os.getenv("PIKA_USERNAME")
    pika_password = os.getenv("PIKA_PASSWORD")

    # ---------------- Configure logging ---------------- #
    logging.basicConfig(level=os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") is not None else logging.INFO,
                        filename="logs/tf2ez_pybuy.log",
                        format='%(levelname)s %(asctime)s - %(message)s',
                        datefmt='%d %m %y %H:%M:%S')
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('undetected_chromedriver').setLevel(logging.WARNING)

    # colored logging configuration
    coloredlogs.install()
    # ---------------- pass data to buy_listener ---------------- #
    worker = BuyListener(logging, pika_host, pika_port, pika_username, pika_password, config['RABBITMQ']['queue'], int(config['TIMES']['delay_range']), config['SCRAPE']['url'], config['LOGIN']['method'])
    myGUI = GUI(worker)
    worker.delayed_passthrough(myGUI.elapsed_str)


if __name__ == "__main__":
    main()
