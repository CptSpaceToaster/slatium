#!/usr/bin/python3.4
import argparse
from bs4 import BeautifulSoup
import json
import os
import requests
import signal
import sys
import time

# Config options
parser = argparse.ArgumentParser(description="Slatium - A Python based bot for Initium Chat Services- http://playinitium.com")
parser.add_argument("-s", "--slack", dest="slack_enabled", action="store_true",
                    help="Fork all of the logged messages to a slack incoming webhook (default=false)")
parser.add_argument("-c", "--config", dest="config_file", default="cfg.json",
                    help="Configuration to use (default=cfg.json)")
args = parser.parse_args()


# Global session
s = None

# Configuration dictionary
cfg = {}


class ChatMessage:
    def __init__(self, user, text):
        self.user = user
        self.test = text


def log(txt):
    print("[{0}] {1}".format(time.strftime("%H:%M:%S"), txt))


def login():
    global s

    log("Sending Authentication")
    payload = {"type": "login",
               "rtm": "",
               "email": cfg["email"],
               "password": cfg["pw"]}

    login = s.post("http://www.playinitium.com/ServletUserControl", data=payload)

    if login.status_code != 200:
        log("Error: Login returned unexpected error code: " + str(login.status_code) + ": " + login.reason + " - ")
        exit(1)


def get_room_chat(roomID, init_marker):
    global s
    return s.get("http://www.playinitium.com/chat?roomId={0}&marker={1}".format(roomID, init_marker))


def init_cfg():
    global cfg

    log("Reading Config")
    if os.path.isfile(args.config_file):
        with open(args.config_file, encoding="utf-8") as data_file:
            cfg = json.loads(data_file.read())
    else:
        print("Error: " + args.config_file + " not found")
        exit(1)


def init_session():
    global s
    log("Starting session")
    s = requests.session()


def slack_msg(usr, txt):
    # Post a message to slack (if it's enabled at startup with --slack)
    if args.slack_enabled:
        # Create the content we want to send to slack, via incoming webhook
        payload = {'channel': cfg["slack_channel"],
                   'username': usr,
                   'text': txt,
                   'icon_emoji': cfg["slack_icon_emoji"]
                   }

        # Slack accepts json payloads
        headers = {'content-type': 'application/json'}

        # shipit.jpg
        r = requests.post(cfg["slack_url"], data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            log("Error: " + str(r.status_code) + " " + r.reason + " - " + r.text)


def update_cfg():
    global cfg
    with open(args.config_file, "w") as f:
        json.dump(cfg, f, sort_keys=True, ensure_ascii=False, indent=4, separators=(",", ": "))
        f.write("\n")


def keyboard_interrupt_handler(signal, frame):
    print("")
    log("Exiting")
    sys.exit(0)


def sighup_handler(signal, frame):
    init_session()
    login()
    log("Configuration reset")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    init_cfg()
    init_session()

    if "marker" in cfg:
        log("Found marker: " + str(cfg["marker"]))
    else:
        marker = str(int(time.time() * 1000))
        log("Marker was missing, using epoch: " + marker)
        cfg["marker"] = marker
        update_cfg()

    login()
    # TODO: Make room configurable
    log("Initialization complete.")
    log("Monitoring: Aera")
    try:
        while True:
            try:
                # Aera
                response = get_room_chat("L5629499534213120", cfg["marker"])
                # print(str(response.status_code) + " " + response.reason)
                if response.text:
                    content = json.loads(response.text)
                    soup = BeautifulSoup(content["messages"], "html.parser")

                    for_later = []
                    for e in soup.find_all("span"):
                        if "chatMessage-time" in e["class"]:
                            msg = ChatMessage("", "")
                        if "chatMessage-nickname" in e["class"]:
                            msg.user = e.text.strip()
                        if "chatMessage-text" in e["class"]:
                            if not msg.user:
                                msg.user = e.text.strip()
                            else:
                                msg.text = e.text.strip()
                                for_later.insert(0, msg)

                    for msg in for_later:
                        if msg.text == "":
                            # Hacks
                            msg.text = " "

                        log(msg.user + ": " + msg.text)
                        slack_msg(msg.user, msg.text)

                    cfg["marker"] = content["marker"]
                    update_cfg()

                time.sleep(10)

            # This happens after a while
            except ConnectionResetError:
                sighup_handler()

    except ConnectionRefusedError as e:
        log("Connection to the Firefox Webdriver was lost")

    sys.exit(0)
