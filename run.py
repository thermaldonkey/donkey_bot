import re
import string
import sys

from my_socket import open_socket, send_message
from initialize import join_room
from read import get_user, get_message

def check_obj(obj, count):
    if obj:
        if count:
            return 'CURRENT OBJ: {}. {} left!'.format(obj, count)
        else:
            return 'CURRENT OBJ: {}'.format(obj)
    else:
        return 'Hey thermaldonkey the people want an OBJ to check!'

AFK = False
OBJ = None
OBJ_COUNT = 0
s = open_socket()
join_room(s)
read_buffer = ''
private_msg = re.compile('PRIVMSG #thermaldonkey')

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
                if user.lower() == 'thermaldonkey':
                    print('thermaldonkey going AFK')
                    AFK = True
                    send_message(s, 'Have a nice break, thermaldonkey!')
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only thermaldonkey".format(user))
            elif re.match('^!back', message.lower()):
                if user.lower() == 'thermaldonkey':
                    if AFK:
                        print('thermaldonkey is back!')
                        AFK = False
                        send_message(s, 'wb thermaldonkey!')
                    else:
                        print('thermaldonkey is confused, or testing things')
                        send_message(s, "thermaldonkey, you've literally been here the entire time FailFish")
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only thermaldonkey".format(user))
            elif user.lower() not in ['thermaldonkey', 'donkey_bot'] and AFK:
                print('{} needs more donkeylove!'.format(user))
                send_message(s, "thermaldonkey is currently AFK. Don't worry, he'll be back soon!")
            elif re.match('^!obj', message.lower()):
                print('someone is checking our OBJ')
                send_message(s, check_obj(OBJ, OBJ_COUNT))
            elif re.match('^!setobj', message.lower()):
                if user.lower() == 'thermaldonkey':
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = tokens[-1]
                        OBJ = ' '.join(tokens[1:-1])
                    else:
                        OBJ = ' '.join(tokens[1:])
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only thermaldonkey".format(user))
            elif re.match('^!incobj', message.lower()):
                if user.lower() == 'thermaldonkey':
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = str(int(OBJ_COUNT) + int(tokens[-1]))
                    else:
                        send_message(s, "That ain't a number brah")
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only thermaldonkey".format(user))
            elif re.match('^!decobj', message.lower()):
                if user.lower() == 'thermaldonkey':
                    tokens = message.split()
                    if re.match(r'^\d+$', tokens[-1]):
                        OBJ_COUNT = str(int(OBJ_COUNT) - int(tokens[-1]))
                    else:
                        send_message(s, "That ain't a number brah")
                else:
                    print('viewers are confused brah')
                    send_message(s, "Sorry for the confusion {} That's a command for only thermaldonkey".format(user))

