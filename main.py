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
parser = argparse.ArgumentParser(description='Slatium - A Python based bot for Initium Chat Services- https://playinitium.com')
parser.add_argument('-s', '--slack', dest='slack_enabled', action='store_true',
                    help='Fork all of the logged messages to a slack incoming webhook (default=false)')
parser.add_argument('-c', '--config', dest='config_file', default='cfg.json',
                    help='Configuration to use (default=cfg.json)')
parser.add_argument('-r', '--rooms', dest='rooms', default='AngryToaster',
                    help='Select which rooms you would like to connect to (default=AngryToaster)')
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
    print('[{0}] {1}'.format(time.strftime('%H:%M:%S'), txt))


def login():
    global s

    log('Sending Authentication')
    payload = {'type': 'login',
               'rtm': '',
               'email': cfg['email'],
               'password': cfg['pw']}

    login = s.post('https://www.playinitium.com/ServletUserControl', data=payload)

    if login.status_code != 200:
        log('Error: Login returned unexpected error code: ' + str(login.status_code) + ': ' + login.reason + ' - ')
        sys.exit(1)


def get_room_chat(roomID, init_marker):
    global s
    return s.get('https://www.playinitium.com/chat?roomId={0}&marker={1}'.format(roomID, init_marker))


def init_cfg():
    global cfg

    log('Reading Config')
    if os.path.isfile(args.config_file):
        with open(args.config_file, encoding='utf-8') as data_file:
            cfg = json.loads(data_file.read())
    else:
        print('Error: ' + args.config_file + ' not found')
        sys.exit(1)

    # Check the config for a "rooms" dictionary
    if 'rooms' not in cfg:
        print('Error: The configuration is missing a Room dictionary')
        print('Example: ', end='\n\n')
        print('   "rooms": {')
        print('        "Aera": {')
        print('            "id": "L5629499534213120"')
        print('        }')
        print('    }', end='\n\n')
        sys.exit(1)

    if 'email' not in cfg:
        print('Error: "email": is missing in the config')
        sys.exit(1)

    if 'pw' not in cfg:
        print('Error: "pw": is missing in the config')
        sys.exit(1)

    if 'uname' not in cfg:
        print('Error: "uname": is missing in the config')
        sys.exit(1)

    if args.slack_enabled and 'slack_channel' not in cfg:
        print('Error: "slack_channel": is missing in the config')
        sys.exit(1)

    if args.slack_enabled and 'slack_icon_emoji' not in cfg:
        print('Error: "slack_icon_emoji": is missing in the config')
        sys.exit(1)

    if args.slack_enabled and 'slack_url' not in cfg:
        print('Error: "slack_url": is missing in the config')
        sys.exit(1)


def init_session():
    global s
    log('Starting session')
    s = requests.session()


def slack_msg(room, usr, txt):
    # Create the content we want to send to slack, via incoming webhook
    payload = {'channel': cfg['slack_channel'][room],
               'username': usr,
               'text': txt,
               'icon_emoji': cfg['slack_icon_emoji']
               }

    # Slack accepts json payloads
    headers = {'content-type': 'application/json'}

    # shipit.jpg
    r = requests.post(cfg['slack_url'], data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        log('Error: ' + str(r.status_code) + ' ' + r.reason + ' - ' + r.text)


def update_cfg():
    global cfg
    with open(args.config_file, 'w') as f:
        json.dump(cfg, f, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
        f.write('\n')


def keyboard_interrupt_handler(signal, frame):
    print('')
    log('Exiting')
    sys.exit(0)


def sighup_handler(signal, frame):
    init_session()
    login()
    log('Configuration reset')


def parse_rooms(raw_rooms):
    global cfg
    ret = []

    for raw_room in raw_rooms.split(','):
        raw_room = raw_room.strip()
        if raw_room in cfg['rooms']:
            if 'id' not in cfg['rooms'][raw_room]:
                print('Error: ' + raw_room + ' is missing it\'s "id": tag')
                sys.exit(1)
            if args.slack_enabled and raw_room not in cfg['slack_channel']:
                print('Error: "slack_channel": does not have an entry for "' + raw_room + '":')
                sys.exit(1)
            ret.append(raw_room)
        else:
            print('Error: ' + raw_room + ' missing')
            sys.exit(1)
    return ret


if __name__ == '__main__':
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    init_cfg()
    init_session()

    rooms = parse_rooms(args.rooms)

    for room in rooms:
        if 'marker' in cfg['rooms'][room]:
            log('[' + room + '] Found marker: ' + str(cfg['rooms'][room]['marker']))
        else:
            marker = str(int(time.time() * 1000))
            log('[' + room + '] Marker was missing, using epoch: ' + marker)

            cfg['rooms'][room]['marker'] = marker
            update_cfg()

    login()
    log('Initialization complete.')
    log('Monitoring: ' + str(rooms))
    try:
        while True:
            try:
                for room in rooms:
                    response = get_room_chat(cfg['rooms'][room]['id'], cfg['rooms'][room]['marker'])
                    # print(str(response.status_code) + ' ' + response.reason)
                    if response.text:
                        content = json.loads(response.text)
                        soup = BeautifulSoup(content['messages'], 'html.parser')

                        for_later = []
                        for e in soup.find_all('span'):
                            if 'chatMessage-time' in e['class']:
                                msg = ChatMessage('', '')
                            if 'chatMessage-nickname' in e['class']:
                                msg.user = e.text.strip()
                            if 'chatMessage-text' in e['class']:
                                if not msg.user:
                                    msg.user = e.text.strip()
                                else:
                                    msg.text = e.text.strip()
                                    for_later.insert(0, msg)

                        for msg in for_later:
                            if msg.text == '':
                                # Hacks
                                msg.text = ' '

                            log('[' + room + '] ' + msg.user + ': ' + msg.text)
                            # Post a message to slack (if it's enabled at startup with --slack)
                            if args.slack_enabled:
                                slack_msg(room, msg.user, msg.text)

                        cfg['rooms'][room]['marker'] = str(content['marker'])
                        update_cfg()

                time.sleep(10)

            # This happens after a while
            except ConnectionResetError:
                # Reload configuration
                sighup_handler()

    # TODO: This might not actually happen ...
    except ConnectionRefusedError as e:
        log('Connection was lost')

    sys.exit(0)
