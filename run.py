import re
import sys
import json
import requests

from my_socket import TwitchChatSocket
from initialize import join_room
from read import get_user, get_message, tokenize_new_data
from settings import CHANNEL
from settings import STREAM_PASS

def check_obj(obj, count):
    if obj:
        if count:
            return 'CURRENT OBJ: {}. {} left!'.format(obj, count)
        else:
            return 'CURRENT OBJ: {}'.format(obj)
    else:
        return 'Hey {} the people want an OBJ to check!'.format(CHANNEL)

class DonkeyBot(object):
    private_msg = re.compile('PRIVMSG #{}'.format(CHANNEL))

    def __init__(self):
        self.afk = False
        self.obj = None
        self.obj_count = 0
        self.socket = TwitchChatSocket()
        join_room(self.socket)
        self.read_buffer = ''

    def the_thing_donkey_bot_does(self):
        temp, self.read_buffer = tokenize_new_data(self.socket, self.read_buffer)

        if not len(temp):
            print('Socket must have closed')
            sys.exit()
        for line in temp:
            print(line)
            if line.startswith('PING'):
                response = line.replace('PING', 'PONG') + '\n'
                self.socket.send(response)
            elif self.private_msg.search(line):
                user = get_user(line)
                message = get_message(line)

                if re.match('^!afk', message.lower()):
                    if user.lower() == CHANNEL:
                        self.afk = True
                        self.socket.send_private_message('Have a nice break, {}!'.format(CHANNEL))
                    else:
                        self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
                elif re.match('^!back', message.lower()):
                    if user.lower() == CHANNEL:
                        if self.afk:
                            self.afk = False
                            self.socket.send_private_message('wb {}!'.format(CHANNEL))
                        else:
                            self.socket.send_private_message("{}, you've literally been here the entire time FailFish".format(CHANNEL))
                    else:
                        self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
                elif user.lower() not in [CHANNEL, 'donkey_bot'] and self.afk:
                    self.socket.send_private_message("{} is currently AFK. Don't worry, he'll be back soon!".format(CHANNEL))
                elif re.match('^!obj', message.lower()):
                    self.socket.send_private_message(check_obj(self.obj, self.obj_count))
                elif re.match('^!setobj', message.lower()):
                    if user.lower() == CHANNEL:
                        tokens = message.split()
                        if re.match(r'^\d+$', tokens[-1]):
                            self.obj_count = tokens[-1]
                            self.obj = ' '.join(tokens[1:-1])
                        else:
                            self.obj = ' '.join(tokens[1:])
                    else:
                        self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
                elif re.match('^!incobj', message.lower()):
                    if user.lower() == CHANNEL:
                        tokens = message.split()
                        if re.match(r'^\d+$', tokens[-1]):
                            self.obj_count = str(int(self.obj_count) + int(tokens[-1]))
                        else:
                            self.socket.send_private_message("That ain't a number brah")
                    else:
                        self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
                elif re.match('^!decobj', message.lower()):
                    if user.lower() == CHANNEL:
                        tokens = message.split()
                        if re.match(r'^\d+$', tokens[-1]):
                            self.obj_count = str(int(self.obj_count) - int(tokens[-1]))
                        else:
                            self.socket.send_private_message("That ain't a number brah")
                    else:
                        self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
                elif re.match('^!title', message.lower()):
                	if user.lower() == CHANNEL:
                		tokens = message.split()
                		r = requests.put('https://api.twitch.tv/kraken/channels/xcouchleaguex', data=json.dumps({'channel': {'status': message[7:], 'delay': 0 }}), headers={'Accept': 'application/vnd.twitchtv.v3+json', 'Authorization': 'OAuth '+STREAM_PASS, 'Content-Type': 'application/json'})
                		self.socket.send_private_message("Ok, I've updated the stream title.");
                	else:
                		self.socket.send_private_message("Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))

if __name__ == '__main__':
    bot = DonkeyBot()
    while True:
        bot.the_thing_donkey_bot_does()

