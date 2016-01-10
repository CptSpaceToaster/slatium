import json
import slacker
import websocket

from .side import Side
from ..dicts import Dualdict


def a_function(api_token, ping_interval):
    print('api_token: {0}'.format(api_token))
    print('ping_interval: {0}'.format(ping_interval))
    lacker = slacker.Slacker(api_token)

    rtm_response = lacker.rtm.start().body

    # Register Slack Users
    users = Dualdict()
    for user in rtm_response['users']:
        users.add(user['id'], user['name'], SlackUser(**user))

    # Register Slack Channels
    channels = Dualdict()
    for channel in rtm_response['channels']:
        channels.add(channel['id'], channel['name'], SlackChannel(**channel))

    websocket = websocket.WebSocketApp(rtm_response['url'], on_message=self.handle_event, on_error=self.handle_error)
    del self._target
    self._target = self.websocket.run_forever


class SlackSide(Side):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def close(self):
        # Attempt to close out of politeness
        try:
            self.websocket.close()
        except Exception as e:
            # But I could care less, unless the NAT is on fire or something
            if 'NAT on fire' in str(e):
                # Nahhh, still don't care
                pass

    def send_message(self, channel, username, message):
        s_chan = self.get_channel_id(channel)
        s_name = username
        s_text = message
        self.slacker.chat.post_message(channel=s_chan, text=s_text, username=s_name)

    def handle_error(self, w_socket, exception):
        self.close()

    def handle_event(self, w_socket, raw):
        if raw:
            # Things come in as raw json
            kwargs = json.loads(raw)
            # 'type' should exist for any valid event
            event_type = kwargs['type']
            # remove 'type' from kwargs
            del kwargs['type']

            # callback the appropriate handler (if it exists)
            try:
                print('looking for handle_{0}({1})'.format(event_type, kwargs))
                getattr(self, 'handle_{0}'.format(event_type))(**kwargs)
            except AttributeError:
                pass

            # if callback:
            #     try:
            #        callback(self, *args)
            #    except Exception as e:
            #        error("error from callback {}: {}".format(callback, e))
            #        if isEnabledForDebug():
            #            _, _, tb = sys.exc_info()
            #            traceback.print_tb(tb)
            # if 'channel' in J and self.get_channel(J['channel']) in self.bot_channels.values():
            #     if 'user' in J and self.get_user(J['user']) in self.slack_users.values():
            #          logger.info('{0} - {1}: {2}'.format(self.bot_channel_ids[J['channel']], self.get_user(J['user'])['name'], J['text']))
            #         payload = {
            #             'channel': self.bot_channel_ids[J['channel']].title() + 'Chat',
            #             'markers': self.marker_str(),
            #             'message': '/me {0}: {1}'.format(self.get_user(J['user'])['name'], J['text'])
            #         }

            #        headers = {'content-type': 'application/x-www-form-urlencoded'}

            #        r = self.session.post('https://www.playinitium.com/messager', data=payload, headers=headers)
            #        if r.status_code != 200:
            #            log('Initium Chat Error: ' + str(r.status_code) + ' ' + r.reason + ' - ' + r.text)

    def handle_message(self, channel=None, user=None, text=None, subtype=None, edited=None, **kwargs):
        """
        The slack API can be a little grody at times.  You'll either get user
        set to an user_id (like 'USLACKBOT'), or you'll get username set to the
        human readable name, crammed in kwargs, because it only shows up on
        bot_message subtypes for now.

        I'm just dumping all bot_messages for now
        """
        if subtype == 'bot_message' or subtype == 'message_changed' or user == 'USLACKBOT':
            return
        if channel.startswith('D'):
            if text.lower() in ['restart', 'reload']:
                print('Reloading configuration')
                self.close()
            if text.lower() in ['stop', 'close']:
                print('Stoping')
                self.needs_exit.set()

        if channel.startswith('C'):
            print('handling message')

    def handle_channel_created(self, channel=None):
        print('Adding new channel')
        self.channels.add(channel['id'], channel['name'], SlackChannel(**channel))

    def handle_channel_rename(self, channel=None):
        self.channels.update(channel['id'], channel['name'])
        self.channels[channel['id']].created = channel['created']

    def handle_channel_archive(self, channel=None):
        self.channels[channel].is_archived = True

    def handle_channel_unarchive(self, channel=None):
        self.channels[channel].is_archived = False

    def handle_user_change(self, user=None):
        self.users[user['id']] = SlackUser(user)

    def handle_team_join(self, user=None):
        self.users[user['id']] = SlackUser(user)

    def handle_team_migration_started(self):
        self.close()


class SlackElement():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SlackUser(SlackElement):
    pass


class SlackChannel(SlackElement):
    pass
