import re
import string
import sys

from my_socket import open_socket, send_message
from initialize import join_room
from read import get_user, get_message
from settings import CHANNEL

def check_obj(obj, count):
    if obj:
        if count:
            return 'CURRENT OBJ: {}. {} left!'.format(obj, count)
        else:
            return 'CURRENT OBJ: {}'.format(obj)
    else:
        return 'Hey {} the people want an OBJ to check!'.format(CHANNEL)

AFK = False
OBJ = None
OBJ_COUNT = 0
s = open_socket()
join_room(s)
read_buffer = ''
private_msg = re.compile('PRIVMSG #{}'.format(CHANNEL))

while True:
    read_buffer += s.recv(1024)
    temp = string.split(read_buffer, '\n')
    read_buffer = temp.pop()

    if not len(temp):
        print('Socket must have closed')
        sys.exit()
    for line in temp:
        print(line)
        if line.startswith('PING'):
            response = line.replace('PING', 'PONG') + '\n'
            print('Responded to ping with {}'.format(response))
            s.send(response)
        elif private_msg.search(line):
            user = get_user(line)
            message = get_message(line)
            print('{} typed: {}'.format(user, message))

            if re.match('^!afk', message.lower()):
                if user.lower() == CHANNEL:
                    print('{} going AFK'.format(CHANNEL))
                    AFK = True
                    send_message(s, 'Have a nice break, {}!'.format(CHANNEL))
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
            elif re.match('^!back', message.lower()):
                if user.lower() == CHANNEL:
                    if AFK:
                        print('{} is back!'.format(CHANNEL))
                        AFK = False
                        send_message(s, 'wb {}!'.format(CHANNEL))
                    else:
                        print('{} is confused, or testing things'.format(CHANNEL))
                        send_message(s, "{}, you've literally been here the entire time FailFish".format(CHANNEL))
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
            elif user.lower() not in [CHANNEL, 'donkey_bot'] and AFK:
                print('{} needs more donkeylove!'.format(user))
                send_message(s, "{} is currently AFK. Don't worry, he'll be back soon!".format(CHANNEL))
            elif re.match('^!obj', message.lower()):
                print('someone is checking our OBJ')
                send_message(s, check_obj(OBJ, OBJ_COUNT))
            elif re.match('^!setobj', message.lower()):
                if user.lower() == CHANNEL:
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = tokens[-1]
                        OBJ = ' '.join(tokens[1:-1])
                    else:
                        OBJ = ' '.join(tokens[1:])
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
            elif re.match('^!incobj', message.lower()):
                if user.lower() == CHANNEL:
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = str(int(OBJ_COUNT) + int(tokens[-1]))
                    else:
                        send_message(s, "That ain't a number brah")
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))
            elif re.match('^!decobj', message.lower()):
                if user.lower() == CHANNEL:
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = str(int(OBJ_COUNT) - int(tokens[-1]))
                    else:
                        send_message(s, "That ain't a number brah")
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only {}".format(user, CHANNEL))

