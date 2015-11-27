#!/usr/bin/python3.4
import argparse
import json
import requests
import signal
import slacker
import sys
import time
import threading
import websocket

from bs4 import BeautifulSoup


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

        # Slack bridge/websocket
        self.slacker = slacker.Slacker(cfg['api_token'])
        R = self.slacker.rtm.start().body

        self.slack_channels = {}
        self.slack_channel_ids = {}
        for channel in R['channels']:
            if not channel['is_archived']:
                self.slack_channels[channel['name']] = channel
                self.slack_channel_ids[channel['id']] = channel
                print('Registered: {0}: {1}'.format(channel['name'], channel['id']))

        self.slack_users = {}
        self.slack_user_ids = {}
        for user in R['users']:
            if not user['deleted'] and user['id'] != 'USLACKBOT':
                self.slack_users[user['name']] = user
                self.slack_user_ids[user['id']] = user
                print('Registered: {0}: {1}'.format(user['name'], user['id']))

        self.bot_channels = {}
        self.bot_channel_ids = {}
        for key, channel in cfg['slack_channels'].items():
            C = self.get_channel(channel)
            assert(C is not None)
            self.bot_channels[key] = C
            self.bot_channel_ids[C['id']] = key

        print('Opening websocket')
        self.websocket = websocket.WebSocketApp(R['url'], on_message=self.handle_message)
        self.ws_thread = threading.Thread(target=self.websocket.run_forever, kwargs={'ping_interval': 30})
        self.ws_thread.start()

        # Login to the initium chat servlet
        self.login()

    def get_channel(self, id_or_name):
        return self.slack_channels.get(id_or_name, self.slack_channel_ids.get(id_or_name, None))

    def get_user(self, id_or_name):
        return self.slack_users.get(id_or_name, self.slack_user_ids.get(id_or_name, None))

    def handle_message(self, socket, message):
        # print(message)
        J = json.loads(message)
        if 'type' in J and J['type'] == 'message':
            if 'channel' in J and self.get_channel(J['channel']) in self.bot_channels.values():
                if 'user' in J and self.get_user(J['user']) in self.slack_users.values():
                    # print('Sending: {0}: {1} to {2}'.format(self.get_user(J['user'])['name'], J['text'], self.bot_channel_ids[J['channel']]))
                    log('{0} - {1}: {2}'.format(self.bot_channel_ids[J['channel']], self.get_user(J['user'])['name'], J['text']))
                    payload = {
                        'channel': self.bot_channel_ids[J['channel']].title() + 'Chat',
                        'markers': self.marker_str(),
                        'message': '/me {0}: {1}'.format(self.get_user(J['user'])['name'], J['text'])
                    }

                    headers = {'content-type': 'application/x-www-form-urlencoded'}

                    r = self.session.post('https://www.playinitium.com/messager', data=payload, headers=headers)
                    if r.status_code != 200:
                        log('Initium Chat Error: ' + str(r.status_code) + ' ' + r.reason + ' - ' + r.text)

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

    def get_chat(self, init=False):
        t = 'https://www.playinitium.com/messager?markers={0}'.format(self.marker_str())
        # log(t)
        m = self.session.get(t)
        if m.status_code != 200:
            log('Chat is NOT OK right now')
        for messages, group in zip(m.json(), self.groups):
            # log('parsing: {}'.format(group))
            if messages is None:
                continue
            self.parse_chat(messages, group, init)

    def parse_chat(self, l, group, init):
        if group not in ['global', 'location']:
            return
        if len(l) == 0:
            return
        for message in l:
            name = BeautifulSoup(message['nickname'], 'lxml')
            if name.text == '':
                continue
            msg = BeautifulSoup(message['message'], 'lxml')
            log('{0} - {1}: {2}'.format(group, name.text, msg.text))
            # Catch empty messages
            if not msg.text:
                msg.text = ' '
            if not init:
                self.slacker.chat.post_message(channel=self.bot_channels[group]['id'], text=msg.text, username=name.text)
        self.markers[group] = str(message['marker'])


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
    # Config options
    parser = argparse.ArgumentParser(description='Slatium - A Python based bot for Initium Chat Services- https://playinitium.com')
    parser.add_argument('-c', '--config', dest='config_file', default='cfg.json',
                        help='Configuration to use (default=cfg.json)')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    signal.signal(signal.SIGHUP, sighup_handler)

    with open(args.config_file) as f:
        cfg = json.loads(f.read())

    print(cfg)

    I = initium_message_client(cfg)
    while(1):
        time.sleep(5)
        I.get_chat()

    sys.exit(0)
