import dotenv
import os
import configparser
import tkinter
import threading

from buy_listener import BuyListener


class GUI(threading.Thread):
    def __init__(self, buy_listener):
        super().__init__()
        self.thread = None
        self.buy_listener = buy_listener
        self.root = tkinter.Tk()

        self.root.title("TF2EZ_PYBUY")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.label = tkinter.Label(self.root, text="TF2EZ_PYBUY")
        self.label.pack()

        self.button = tkinter.Button(self.root, text="Start", command=self.start)
        self.button.pack()

        self.root.mainloop()

    def start(self):
        self.thread = threading.Thread(target=self.thread_func)
        self.thread.start()

    def thread_func(self):
        self.button["state"] = "disabled"
        self.label["text"] = "running..."
        # Do something
        self.buy_listener.start()

        self.label["text"] = "done"
        self.button["state"] = "normal"

    def on_closing(self):
        self.root.destroy()


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

    # ---------------- pass data to buy_listener ---------------- #
    worker = BuyListener(config, pika_host, pika_port, pika_username, pika_password)
    GUI(worker)


if __name__ == "__main__":
    main()
