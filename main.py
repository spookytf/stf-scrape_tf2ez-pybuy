import signal
import dotenv
import sys
import os
import configparser
import tkinter
import threading
import coloredlogs, logging
import pathlib
import time
import tkinter as tk # Python 3.x
from tkextrafont import Font
import tkinter.scrolledtext as ScrolledText
import multiprocessing

from buy_listener import BuyListener
from ReportGUI import ReportGUI

__version__ = "v2.6.9-nice" # update this when you update the version in setup.py


# ---------------- START CONFIG ---------------- #
global REPORT_WEBHOOK
REPORT_WEBHOOK = None
# garbage variables

global LAST_TIME
LAST_TIME = float(time.time())
global DELAY_RANGE
DELAY_RANGE = 60
#DELAY_RANGE = tk.IntVar()
#DELAY_RANGE.set(45)

global GUI_OBJECTS
GUI_OBJECTS = {}

# Real variables
LOG_COLOR_LEVEL_TO_COLOR = {
    'DEBUG': 'black',
    'INFO': '#434343',
    'RABBIT': '#a7176e',
    'SUCCESS': '#006500',
    'WARNING': '#c1c100',
    'ERROR': 'red',
    'CRITICAL': '#700000',
}

config = None
pika_host = None
pika_port = None
pika_username = None
pika_password = None
pika_queue = None
scrape_url = None

# ---------------- END VARIABLES ---------------- #

# MANAGER = logging.Manager("tf2ez_pybuy_" + __version__)
# MANAGER.getLogger().setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# MANAGER.getLogger().setLevel(logging.DEBUG)

# GUI configurations
# configure a custom font jason what are you doing

class ResizeHandler(threading.Thread):

    window = None
    aspect_ratio = 1
    width = 0
    height = 0  # int(self.width / self.aspect_ratio)
    dim_lcm = 0
    # I'm way too fucking far in now... function to calculate the LCM. Seems reasonable.
    def lcm(self, a, b):
        if(a == 0 or b == 0):
            return 0

        if a > b:
            greater = a
        else:
            greater = b
        while (True):
            if ((greater % a == 0) and (greater % b == 0)):
                lcm = greater
                break
            greater += 1
        return lcm

    def __init__(self, window, aspect_ratio=1.0, g_width=500, g_height=500):
        super().__init__()
        self.window = window


        # ... this code makes a cool shape
        if aspect_ratio is None:
            self.aspect_ratio = g_width / g_height
        else:
            self.aspect_ratio = aspect_ratio
            if g_width is None:
                if g_height is not None:
                    self.width = g_height * self.aspect_ratio
                    self.height = g_height
                else:
                    self.height = g_width / self.aspect_ratio
            else:
                self.width = g_width

        self.dim_lcm = self.lcm(self.width, self.height)

        self.start()

    def start(self):
        self.thread = threading.Thread(target=self.thread_func)

        # this is intended for a main tkinter window, not a frame
        # that is using grid... NOT ANYTHING ELSE!


    def stop(self):
        self.thread.join() # wait for it to finish very nicely

    def thread_func(self):

        # self.dim_lcm = lcm(self.width, self.height)
        #
        # if self.width * self.height < self.dim_lcm:
        #     int_width = self.dim_lcm
        #     int_height = self.aspect_ratio * self.dim_lcm
        # else:
        #     int_width = self.width / self.dim_lcm
        #     int_height = self.height / self.dim_lcm
        # maintain ASPECT RATIO
        def on_resize(event):
            w, h = event.width, event.height
            w1, h1 = self.window.winfo_width(), self.window.winfo_height()
            logging.debug(f"on_resize: {w}x{h} | {w1}x{h1}")
            w1, h1  # must follow ASPECT_RATIO (w1/h1 = ASPECT_RATIO)
            if w > self.aspect_ratio * h:
                # self.window.rowconfigure(0, weight=1)
                # self.window.rowconfigure(1, weight=0)
                self.window.columnconfigure(0, weight=h)
                self.window.columnconfigure(1, weight=w - h)
            elif w < self.aspect_ratio * h:
                self.window.rowconfigure(0, weight=w)
                self.window.rowconfigure(1, weight=h - w)
                # self.window.columnconfigure(0, weight=1)
                # self.window.columnconfigure(1, weight=0)
            else:
                w_lcm = self.lcm(w, h)

                if w * h < w_lcm:
                    int_width = w_lcm
                    int_height = self.aspect_ratio * w_lcm
                else:
                    int_width = w / w_lcm
                    int_height = h / w_lcm

                self.window.rowconfigure(0, weight=1)
                self.window.rowconfigure(int_width, weight=0)
                self.window.rowconfigure(0, weight=1)
                self.window.columnconfigure(int_height, weight=0)

        # TODO: no idea if this will work with the way mainloop is handled
        self.window.bind("<Configure>", self.on_resize)

logging.getLogger(__name__).setLevel(logging.DEBUG)

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logger = logging.getLogger(__name__)
        logging.Handler.__init__(self)
        #logging.getLogger().addHandler(logging.Handler)

        #logging.Handler.setFormatter(self, coloredlogs.ColoredFormatter())

        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal', background="#242424", foreground="#434343", font=("Arial", 10, "bold"))
            self.text.insert(tk.END, msg + '\n', record.levelname)
            # self.text.tag_config(record.levelname, foreground=f"{LOG_COLOR_LEVEL_TO_COLOR[record.levelname]}")
            self.text.tag_config("CRITICAL", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['CRITICAL']}", background="#b0b0b0", font=("Arial", 10, "bold"))
            self.text.tag_config("ERROR", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['ERROR']}", background="black")
            self.text.tag_config("WARNING", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['WARNING']}", background="black")
            self.text.tag_config("SUCCESS", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['SUCCESS']}", background="black")
            self.text.tag_config("RABBIT", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['RABBIT']}", background="#b0b0b0")
            self.text.tag_config("INFO", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['INFO']}", background="#b0b0b0", font=("Arial", 10, "bold"))
            self.text.tag_config("DEBUG", foreground=f"{LOG_COLOR_LEVEL_TO_COLOR['DEBUG']}",background="#b0b0b0", font=("Arial", 10, "italic"))
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

# ----------------------------------------------------------- #

class GUI(threading.Thread):
    buyListener = None
    textHandler = None
    def __init__(self):
        super().__init__()
        self.thread = None
        self.build()

    def set_worker(self, worker, text_handler):
        self.buyListener = worker
        self.textHandler = text_handler
        logger = logging.getLogger(__name__)
        logger.addHandler(text_handler)
        logger.setLevel("DEBUG")


    # ---------------- START GUI ---------------- #
    def build(self):
        self.root = tkinter.Tk()
        global SPOOKY_FONT
        SPOOKY_FONT = Font(file=pathlib.Path('assets/font/IMFellEnglishSC-Regular.ttf'), family="IM Fell English SC")
        # self.root.wm_title("SPOOKYSCRAPE TF2EZ PYBUY" + " " + __version__)
        self.root.title("SPOOKYSCRAPE TF2EZ PYBUY" + " " + __version__)
        #self.root.option_add("*Font", (SPOOKY_FONT))
        self.root.geometry("800x550")
        self.root.resizable(False, True)
        self.root.minsize(800, 550)
        self.root.configure(background="black")
        self.root.iconbitmap(pathlib.Path("assets/img/logo/spookyscrape.ico"))
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        logger = logging.getLogger(__name__)
        logger.addHandler(self.textHandler)

        self.root.frame = tkinter.Frame(self.root, highlightcolor="#bfbfbf", bg="#1b1b1b", relief="sunken", borderwidth=2)
        self.root.frame.grid(row=0, column=0, sticky='ewsn')
        ##self.root.frame.configure(background="#242424")

        self.root.frame.t_label = tkinter.Label(self.root.frame, text="PYBUY " + __version__, font=("IM Fell English SC", 14), fg="orange", bg="black")
        self.root.frame.t_label.grid(column=0, row=0, sticky="n", padx=5, pady=5, columnspan=4)
        # it was JASON that chose this font
        # and I'm not going to change it
        # because I'm not a monster
        # This was still me, JASON, who chose this font
        self.root.frame.label = tkinter.Label(self.root.frame, text="not running", font=("Comics Sans", 12), fg="black")
        self.root.frame.label.grid(column=0, row=4, sticky='ewn', padx=5, pady=5, columnspan=1)

        self.subtext_str = tkinter.StringVar()
        self.subtext_str.set("by Oscar & Jason of SpookyTF")
        self.root.frame.ctn_label = tkinter.Label(self.root.frame, textvariable=self.subtext_str, font=("Comics Sans", 10), fg="orange", bg="black")
        self.root.frame.ctn_label.grid(column=0, row=5, sticky='ews', padx=5, pady=5, columnspan=1)

        self.root.frame.button = tkinter.Button(self.root.frame, text="start", command=self.start, font=("Comics Sans", 14), fg="red", bg="#242424", relief="sunken", borderwidth=2)
        self.root.frame.button['state'] = 'disabled'
        self.root.frame.button.grid(column=3, row=4, sticky='ewn', padx=5, pady=5, columnspan=2)

        #global DELAY_RANGE
        #self.root.frame.delay_scale = tkinter.Scale(self.root.frame, from_=0, to=360, orient=tkinter.HORIZONTAL, label="delay range (s)", font=("Comics Sans", 12), fg="orange", bg="black", length=200, variable=DELAY_RANGE, command=self.update_delay_range)
        #self.root.frame.delay_scale.grid(column=0, row=6, sticky='ews', padx=5, pady=5, columnspan=4)

        self.display_log = tk.StringVar()
        self.root.frame.label = tkinter.Label(self.root.frame, textvariable=self.display_log, font=("Comics Sans", 12), fg="green")

        if os.getenv('LOGIN_METHOD') == "cookie" and os.getenv('LOGIN_COOKIE') is not None:
            self.display_log.set("cookie found, log in!")
            self.root.frame.label.configure(fg="white", bg="green")

            self.root.frame.login_button['state'] = 'normal'
            self.root.frame.login_button.configure(self.root.frame, text="🟡 login ", font=("Comics Sans", 14), fg="yellow", bg="black", command=self.login)
            #self.root.frame.login_button.grid(column=3, row=5, sticky='ewn', padx=5, pady=5, columnspan=2)
        else:
            self.root.frame.login_button = tkinter.Button(self.root.frame, text="❌ not logged in", command=self.login, font=("Arial", 14, "bold"), fg="red")
            self.root.frame.login_button['state'] = 'normal'
        self.root.frame.login_button.grid(column=3, row=5, sticky='ewn', padx=5, pady=5, columnspan=2)

        self.root.option_add('*tearOff', 'FALSE')
        self.root.frame.grid(column=0, row=0, sticky='new')
        self.root.frame.grid_columnconfigure(0, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(1, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(2, weight=1, uniform='a')
        self.root.frame.grid_columnconfigure(3, weight=1, uniform='a')

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(self.root.frame, state='disabled', bg="#242424", fg="#434343")
        st.configure(font='TkFixedFont')
        st.grid(column=0, row=1, sticky='wsen', columnspan=4)
        st.grid_columnconfigure(0, weight=1)
        st.grid_rowconfigure(0, weight=1)

        # Create textLogger
        text_handler = TextHandler(st)
        self.textHandler = text_handler
        logging.getLogger(__name__).addHandler(text_handler)

        if not os.path.exists("logs/tf2ez_pybuy.log"):
            pathlib.Path("logs").mkdir(parents=True, exist_ok=True)
            pathlib.Path("logs/tf2ez_pybuy.log").touch()

        # clear if log is too big
        # if fs := os.path.getsize("logs/tf2ez_pybuy.log.old") > 1000000:
        #     os.remove("logs/tf2ez_pybuy_ALL.log")

        # Add the handler to logger
        # MANAGER.getLogger('tf2ez_pybuy_combined').setLevel(gui).addHandler(text_handler);
        logger.addHandler(text_handler)
        logger.addHandler(logging.FileHandler(pathlib.Path("logs/combined_" + str(time.time()) + ".log"), "a", "utf-8", True, "DEBUG"))
        # shouldn't ever actually "append"


        self.root.frame.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        self.root.pack_propagate(True)
        #self.root.frame.pack(fill="x", expand = True,  pady=10, padx=10)
        #self.root.frame.pack(fill="both", expand=True)

        # self.root.frame.pack(side="bottom", fill="x", expand=True, pady=10, padx=10)
        # self.root.frame.pack_propagate(False)

        # TODO: Remove this, it was an experiment to understand how these fucking GUIs work

        # # ------------- MAKE RESPONSIVE ----------- #
        #
        # # everything is in a frame
        # self.root.frame.grid(row=0, column=0, sticky='ewsn')
        #
        # # root level buttons & labels
        # self.root.frame.t_label.grid(column=0, row=0, sticky="n", padx=5, pady=5, columnspan=4)
        #
        # self.root.frame.label.grid(column=0, row=4, sticky='ewn', padx=5, pady=5, columnspan=1)
        #
        # self.root.frame.ctn_label.grid(column=0, row=5, sticky='ews',padx=5, columnspan=1)
        #
        # self.root.frame.button.grid(column=3, row=4, sticky='ewn', padx=5, pady=5, columnspan=2)
        #
        # self.root.frame.login_button.grid(column=3, row=5, sticky='sew', padx=5, columnspan=2)
        #
        # # logs text widget & scrollbar layout
        # self.root.frame.grid(column=0, row=0, sticky='new')
        # self.root.frame.grid_columnconfigure(0, weight=1, uniform='a')
        # self.root.frame.grid_columnconfigure(1, weight=1, uniform='a')
        # self.root.frame.grid_columnconfigure(2, weight=1, uniform='a')
        # self.root.frame.grid_columnconfigure(3, weight=1, uniform='a')
        #
        # # Add text widget to display logging info
        # st.grid(column=0, row=1, sticky='wsen', columnspan=4)

        # Start the ResizeHandler to make the GUI responsive
        # AND maintain aspect ratio in grid layout. This is
        # EXTREME overkill for a simple GUI, but I wanted it. :)
        # ......
        # ...... and ACTUALLY, it was a HUGE waste of time!
        # lol. I'm keeping it in though, because it's cool.
        # resize_handler = ResizeHandler(self.root, 1.6, 8, 5)
        # resize_handler.start()

        self.root.configure(bg="#F08300")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)


        self.root.mainloop()
        # ---------------- END GUI ---------------- #


    def login(self):
        threading.Thread(target=self.login_thread).run()

    def login_thread(self):
        self.root.frame.label["text"] = "logging in..."
        self.root.frame.login_button["text"] = "logging in..."
        self.root.frame.login_button["fg"] = "black"
        self.root.frame.button["state"] = "disabled"
        self.root.frame.login_button["state"] = "disabled"
        logged_in = False

        login_method = os.getenv('LOGIN_METHOD')

        while not logged_in:
            try:
                logging.warning("Initializing Selenium Webdriver, logging in...")
                buyListener.init_selenium_and_login(login_method)
                logged_in = True
            except:
                self.root.frame.label["text"] = "login failed"
                self.root.frame.label["fg"] = "white"
                self.root.frame.login_button["text"] = "❌ not logged in"
                self.root.frame.login_button["bg"] = "red"
                #self.root.frame.login_button.after(500, lambda: self.root.frame.login_button.configure(bg="#4C4C4C"))
                self.root.frame.login_button["state"] = "normal"
                self.root.frame.button["state"] = "disabled"
                self.root.frame.login_button["bg"] = "red"
                #self.root.frame.button["bg"] = "#434343"
                #    .configure(bg="#242424", relief="sunken", borderwidth=2)
                return
        if os.getenv('LOGIN_COOKIE') is not None:
            self.root.frame.label["text"] = "logged in!"
            self.root.frame.login_button["text"] = "✅ logged in"
            self.root.frame.login_button["state"] = "disabled"
            self.root.frame.login_button["bg"] = "green"
            self.root.frame.button["state"] = "normal"
            #self.root.frame.button.configure(bg="#4C4C4C", relief="raised", borderwidth=1)
        else:
            self.root.frame.label["text"] = "try again -- invalid cookie"
            self.root.frame.label["fg"] = "white"
            self.root.frame.login_button["text"] = "❌ cookie expired"
            self.root.frame.login_button["state"] = "normal"
            self.root.frame.login_button["bg"] = "red"
            #self.root.frame.login_button.after(500, lambda: self.root.frame.login_button.configure(bg="#4C4C4C"))

        self.root.attributes('-topmost',True)

    def start(self):
        self.thread = threading.Thread(target=self.thread_func)
        self.run()
        #self.thread.start()

    def thread_func(self):
        logging.addHandler(self.textHandler)
        self.root.frame.button["state"] = "normal"
        self.root.frame.label["text"] = "running..."
        self.root.frame.button.configure(text="stop", command=self.stop, fg="red", font=("Arial", 14, "bold"))
        # Run buyListener to listen for messages
        # self.testing_spam_logs(100)
        logging.info("starting...")
        self.buyListener.start()



        # never reached
        # ^^ this is a lie, it is reached when the thread is stopped!
        # self.label["text"] = "done"
        # self.button["state"] = "normal"

    def stop(self):
        self.buyListener.stop()
        self.root.frame.label["text"] = "stopping..."
        self.root.frame.label.configure(fg="black", bg="#AF7C04")
        self.root.frame.button["state"] = "disabled"
        logging.warning("stopped.");
        self.root.frame.label.after(500, lambda: self.root.frame.label.configure(fg="black", bg="white"))
        self.root.frame.button.after(500, lambda: self.root.frame.button.configure(text="start", command=self.start, fg="green"))
        #self.root.frame.button.configure(text="start", command=self.start, fg="green")


    def on_closing(self):
        self.root.frame.quit()
        for widget in self.root.frame.winfo_children():
            widget.destroy()
        self.root.destroy()
        if self.buyListener is not None:
            self.buyListener.stop()
        exit(0)

    def update_delay_range(self):
        global DELAY_RANGE
        self.buyListener.delayed_passthrough["delay_range"] = DELAY_RANGE.get()

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

    def throw_exception(self):
        raise IOError("test", "lots of testing")
def main():
    # ---------------- Load variables ---------------- #
    config = configparser.ConfigParser()
    config.read(pathlib.Path('config.ini'))
    dotenv.load_dotenv()

    # ---------------- Configure RabbitMQ ---------------- #
    pika_host = os.getenv("PIKA_HOST")
    pika_port = int(os.getenv("PIKA_PORT"))
    pika_username = os.getenv("PIKA_USERNAME")
    pika_password = os.getenv("PIKA_PASSWORD")

    # ---------------- Configure logging ---------------- #

    level = os.getenv('log_level')
    if level is None:
        level = "INFO"

    gui_level = os.getenv('gui_log_level') if os.getenv('gui_log_level') is not None else level
    term_level = os.getenv('term_log_level') if os.getenv('term_log_level') is not None else level
    file_level = os.getenv('file_log_level') if os.getenv('file_log_level') is not None else level

    # colored logging configuration
    # coloredlogs.install(level)

    # def addHandlers(logger, hdlrs):
    #     for hdlr in hdlrs:
    #         logger.addHandler(hdlr)
    #
    # def addAllHandlers(logger):
    #     addHandlers(logger, [ logging.Handler(),
    #                            logging.FileHandler('logs/tf2ez_pybuy.log', 'a'),
    #                            logging.FileHandler('logs/combined_' + str(time.time_ns()) + '.log', 'w')])

    myGUI = GUI()

    logging.basicConfig(level=logging.DEBUG    ,
                        filename="logs/tf2ez_pybuy.log",
                        format='%(levelname)s %(asctime)s - %(message)s',
                        datefmt='%d %m %y %H:%M:%S')

    logging.getLogger().addHandler(myGUI.textHandler)

    logging.getLogger('urllib3').setLevel("DEBUG").addHandler(myGUI.textHandler)
    logging.getLogger('selenium').setLevel("DEBUG").addHandler(myGUI.textHandler)
    logging.getLogger('undetected_chromedriver').setLevel("DEBUG").addHandler(myGUI.textHandler)

    coloredlogs.auto_install()

    logging.getLogger(__name__).addHandler(myGUI.textHandler)
    
    # ---------------- pass data to buyListener ---------------- #
    global DELAY_RANGE
    DELAY_RANGE = int(config['TIMES']['delay_range'])

    global REPORT_WEBHOOK
    REPORT_WEBHOOK = config['REPORT']['webhook']

    # ---------------- Start GUI && worker ---------------- #

    worker = BuyListener(pika_host, pika_port, pika_username, pika_password, config['RABBITMQ']['queue'], int(config['TIMES']['delay_range']), config['SCRAPE']['url'], config['LOGIN']['method'])
    myGUI.set_vals(worker, myGUI.text_handler)
    #worker.delayed_passthrough('textHandler', myGUI.textHandler)
    worker.delayed_passthrough('subtext_str', myGUI.subtext_str)

def handler(signum, frame):
    logger = logging.getLogger()
    if signal == signal.SIGINT:
        logger.warning('Killed by user')
        sys.exit(0)
    if signal == signal.SIGTERM:
        logger.critical('Killed by SIGTERM')
        reportgui = ReportGUI()
        reportgui.run()



if __name__ == "__main__":
        # signal.signal(signal.SIGINT, handler)
        main()



