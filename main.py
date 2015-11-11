#!/usr/bin/python3.4
import argparse
from bs4 import BeautifulSoup
import json
import requests
import signal
import sys
import time

# Config options
parser = argparse.ArgumentParser(description='Slatium - A Python based bot for Initium Chat Services- https://playinitium.com')
parser.add_argument('-s', '--slack', dest='slack_enabled', action='store_true',
                    help='Fork all of the logged messages to a slack incoming webhook (default=false)')
parser.add_argument('-c', '--config', dest='config_file', default='cfg.json',
                    help='Configuration to use (default=cfg.json)')
parser.add_argument('-r', '--rooms', dest='rooms', default='AngryToaster',
                    help='Select which rooms you would like to connect to (default=AngryToaster)')
args = parser.parse_args()


# TODO: Logger pls
def log(txt):
    print('[{0}] {1}'.format(time.strftime('%H:%M:%S'), txt))


class initium_message_client():
    def __init__(self, cfg):
        log('Starting session')
        self.session = requests.session()
        self.cfg = cfg
        self.groups = ['global', 'location', 'group', 'party', 'private', 'notification']
        self.markers = {}
        for g in self.groups:
            self.markers[g] = 'null'

    def marker_str(self):
        ret = self.markers[self.groups[0]]
        for g in self.groups[1:]:
            ret += ',' + self.markers[g]
        return ret

    def login(self):
        log('Sending Authentication')
        payload = {'type': 'login',
                   'rtm': '',
                   'email': self.cfg['email'],
                   'password': self.cfg['pw']}

        login = self.session.post('https://www.playinitium.com/ServletUserControl', data=payload)

        if login.status_code != 200:
            log('Error: Login returned unexpected error code: ' + str(login.status_code) + ': ' + login.reason + ' - ')
            sys.exit(1)

        log('Fetching Chat')
        self.get_chat(init=True)

    def get_chat(self, slack=False, init=False):
        t = 'https://www.playinitium.com/messager?markers={0}'.format(self.marker_str())
        # log(t)
        m = self.session.get(t)
        if m.status_code != 200:
            log('Chat is NOT OK right now')
        for messages, group in zip(m.json(), self.groups):
            # log('parsing: {}'.format(group))
            if messages is None:
                continue
            self.parse_chat(messages, group, slack)

    def parse_chat(self, l, group, slack):
        # TODO:
        if group != 'global':
            return
        if len(l) == 0:
            return
        for message in l:
            name = BeautifulSoup(message['nickname'], 'lxml')
            msg = BeautifulSoup(message['message'], 'lxml')
            log('{0}: {1}'.format(name.text, msg.text))
            if slack:
                self.slack_msg(name.text, msg.text, group)
        self.markers[group] = str(message['marker'])

    def slack_msg(self, usr, txt, group):
        # Create the content we want to send to slack, via incoming webhook
        payload = {'channel': cfg['slack_channel'][group],
                   'username': usr,
                   'text': txt,
                   'icon_emoji': cfg['slack_icon_emoji']
                   }

        # Slack accepts json payloads
        headers = {'content-type': 'application/json'}

        # shipit.jpg
        r = requests.post(cfg['slack_url'], data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            log('Slack Error: ' + str(r.status_code) + ' ' + r.reason + ' - ' + r.text)


def keyboard_interrupt_handler(signal, frame):
    print('')
    log('Exiting')
    sys.exit(0)


def sighup_handler(signal, frame):
    # init_session()
    # login()
    log('Configuration reset')


def save_cfg(filename, cfg):
    with open(filename, 'w') as f:
        f.write(json.dumps(cfg), sort_keys=True, indent=4)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    signal.signal(signal.SIGHUP, sighup_handler)

    with open(args.config_file) as f:
        cfg = json.loads(f.read())

    print(cfg)

    I = initium_message_client(cfg)
    I.login()
    while(1):
        time.sleep(5)
        I.get_chat(slack=True)

    sys.exit(0)
