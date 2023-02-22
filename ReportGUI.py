import sys
import logging as pylogger
from loguru import logger
import better_exceptions

better_exceptions.MAX_LENGTH = None
import configparser
import os
import pathlib
import threading
import tkinter
from itertools import count
from tkinter import Label
from tkinter import messagebox
from PIL import ImageTk, Image


# a small tkinter GUI for reporting logs after an execution has ended in an exception or otherwise.
# https://stackoverflow.com/a/43770948
class ImageLabel(Label):
    """a label that displays images, and plays them if they are gifs"""

    def __init__(self, master=None, cnf=None, **kw):
        Label.__init__(self, master, cnf, **kw)
        self.delay = None
        if cnf is None:
            self.cnf = {}
        self.frames = None
        self.loc = None

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except BaseException as e:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)


# a small tkinter GUI for reporting logs after an execution has ended in an exception or otherwise.
# by @zudsniper @github
class ReportGUI(threading.Thread):
    webhook = None
    exception = None
    response = None
    webhook_message = None
    embed = None
    report_truncated = None
    report = None
    root = None
    manager = None

    def __init__(self):
        super().__init__()
        # if LUCKY

        logger.info("ReportGUI initialized...")

        self.response = None
        self.webhook_message = None
        self.embed = None
        self.report_truncated = None
        self.report = None

        self.read_configs()

        self.root = tkinter.Tk()
        logger = pylogger.getLogger(__name__)
        logger.debug("Building GUI for report popup...")
        self.build()
        # THE INTENTION IS TO FREEZE THE MAIN THREAD HERE, AND ONLY UNFREEZE IT WHEN THE REPORT IS SENT
        self.logging.warning("GUI built, waiting for user to complete...")
        # Not actively displayed yet, but built to appear.

    def show(self):
        self.root.pack_propagate(False)

        self.root.mainloop()

    def hide(self):
        self.root.withdraw()
        threading.Thread.join()

    def read_configs(self):
        config = configparser.ConfigParser()
        config.read(pathlib.Path('config.ini'))

        self.webhook = config['REPORT']['webhook']

    def run(self):
        self.start()

    def survive(self):
        threading.Thread.join(self)

    def start(self):
        # self.root.attributes('-topmost', True)
        threading.Thread(target=self.thread_func)
        # self.start()

    def thread_func(self):
        self.build()
        self.create_report()
        self.survive()

    def create_report(self):
        logger = logging.getLogger("discord_webhook")
        if self.webhook is None:
            logger.error("No webhook found in config.ini, cannot send report!")
            messagebox.showerror("Error", "No webhook provided!", parent=self.root, icon="error",
                                 title="No dev webhook...", type="ok")
            return

        if self.root.body.text.get("1.0", "end-1c") == "":
            logger.error("No report provided, cannot send report!")
            messagebox.showerror("Error", "No report provided! Please describe the problem you faced, even very "
                                          "briefly if necessary.", parent=self.root, icon="info", title="No "
                                                                                                        "report...",
                                 type="ok")
            return
        else:

            if not messagebox.askyesno("Confirm", "Send error report?", parent=self.root, icon="question",
                                       title="Confirm ERROR report", type="yesno"):
                return
            else:
                # truncate report if too long for discord content
                self.report = self.root.body.text.get("1.0", "end-1c")
                self.report_truncated = self.report.truncate(self.report, 2000)

                # collect logs from log file
                log_path = pathlib.Path("logs/")
                pattern = "combined_([0-9]+)\\.log"
                log_files = [f for f in log_path.glob(pattern)]
                log_files.sort(key=lambda x: int(x.name.split("_")[1].split(".")[0]))
                log_file = log_files[-1]
                log_file_b64 = log_file.read_text().encode("base64")

                self.embed = DiscordEmbed(title="Error report",
                                          description=self.report_truncated,
                                          color=0xff0000,
                                          timestamp="now",
                                          footer="stf-report",
                                          footer_icon="https://raw.githubusercontent.com/spookytf/stf-assets/main/imgs/500x500_tp.gif")
                self.embed.set_author(name="steam: " + os.environ.get("STEAM_USERNAME"),
                                      icon_url=os.environ.get("STEAM_AVATAR_TINYLINK"), url="https://rat.church/")

                self.embed.add_embed_field(name="culprit", value=self.exception.get_exception_type())
                self.embed.add_embed_field(name="error", value=self.exception.get_exception_message())
                self.embed.add_embed_field(name="traceback", value=self.exception.get_traceback())

                self.webhook_message = DiscordWebhook(url=self.webhook,
                                                      content=self.root.body.text.get("1.0", "end-1c"))

                self.webhook_message.add_embed(embed=self.embed)
                self.webhook_message.add_file(file=log_file_b64, filename=log_file.name)

        # Report is READY -- send to the webhook

        self.response = self.webhook_message.execute()
        if self.response.status_code == 204:
            logger.info("Report sent successfully!")
            messagebox.showinfo("Success", "Report sent successfully!", parent=self.root, icon="success",
                                title="Report sent!", type="ok")
        else:
            logger.error("Report failed to send!")
            messagebox.showerror("Error", "...this is awkward...", parent=self.root, icon="error",
                                 title="Report failed to send!", type="ok")

        logger.critical("ReportGUI shutting down...")
        logger.info("Thank you for using stf-report!")

        self.root.destroy()

    def build(self):
        self.root.title("[stf-report]" + str(os.environ.get("STEAM_USERNAME")))
        self.root.geometry("300x400")
        self.root.minsize(300, 400)
        self.root.resizable(True, True)
        self.root.configure(background="#F08300")
        self.root.body = tkinter.Entry(self.root, background="#4C4C4C", foreground="black", borderwidth=2)
        self.root.body.pack(side='bottom', fill='x', expand=True, padx=10, pady=10)

        self.root.body.header = tkinter.Label(self.root.body, text="Report back to HQ!", background="#4C4C4C",
                                              foreground="white", borderwidth=2)
        self.root.body.header.pack(side='top', fill='x', expand=True, padx=10, pady=10)

        self.root.body.gif_logo = ImageLabel(self.root.body, background="#4C4C4C", foreground="white")
        self.root.body.gif_logo.pack()
        # self.root.body.gif_logo\
        #     .load("assets/img/banner-logo.gif")

        self.root.body.text = tkinter.Text(self.root.body, background="#dedede", foreground="black", borderwidth=2)
        self.root.body.text.pack(side='top', fill='x', expand=True, padx=10, pady=10)
        self.root.body.text.place(x=-10, y=10)

        self.root.button = tkinter.Button(self.root.body, text="SEND", command=self.report, height=2)
        self.root.button.pack(side='bottom', fill='x', expand=False, padx=10, pady=10)
