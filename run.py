import re
import sys

from my_socket import TwitchChatSocket
from initialize import join_room
from read import get_user, get_message, tokenize_new_data
from settings import CHANNEL, POINTS_ALIAS, POINTS_COUNT, ADDED_POINTS, REMOVED_POINTS
from db import connect
from models import Viewer

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
        self.session = connect()
        self.afk = False
        self.obj = None
        self.obj_count = 0
        self.socket = TwitchChatSocket()
        join_room(self.socket)
        self.read_buffer = ''

    def get_viewer(self, nickname):
        '''
        Returns the first Viewer with the given nickname.

        @param nickname (str) - Nickname for the requested viewer
        @return (Viewer,None)
        '''
        return self.session.query(Viewer).filter_by(nickname=nickname).first()

    def add_viewer(self, nickname):
        '''
        Adds a new viewer with the given nickname.

        @param nickname (str) - Nickname for the new viewer
        @return (Viewer)
        '''
        viewer = Viewer(nickname=nickname)
        self.session.add(viewer)
        self.session.commit()
        return viewer

    def get_points(self, user):
        '''
        Returns the point count for a viewer with the given nickname.

        @param user (str) - Nickname of the viewer whose points are requested
        @return (int)
        '''
        viewer = self.get_viewer(user)
        return getattr(viewer, 'points', 0)

    def add_points(self, nickname, points):
        '''
        Adds given number of points to the viewer with the given nickname. Will add the viewer if no
        matching one already exists.

        @param nickname (str) - Nickname of the viewer
        @param points (int) - Number of points to award
        '''
        viewer = self.get_viewer(nickname) or self.add_viewer(nickname)
        viewer.points += int(points)
        self.session.commit()

    def remove_points(self, nickname, points):
        '''
        Removes given number of points from the viewer with the given nickname. Will add the viewer
        if no matching one already exists.

        @param nickname (str) - Nickname of the viewer
        @param points (int) - Number of points to demerit
        '''
        viewer = self.get_viewer(nickname) or self.add_viewer(nickname)
        viewer.points = max(viewer.points - int(points), 0)
        self.session.commit()

    def the_thing_donkey_bot_does(self):
        temp, self.read_buffer = tokenize_new_data(self.socket, self.read_buffer)

        if not len(temp):
            print('Socket must have closed')
            sys.exit()
        for line in temp:
            print(line)
            if line.startswith('PING'):
                self.socket.send_pong(line)
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
                elif re.match('^!(points|{})'.format(POINTS_ALIAS), message.lower()):
                    tokens = message.split()
                    modifier = None
                    if len(tokens) > 1:
                        iterator = iter(tokens)
                        iterator.next()
                        modifier = iterator.next()
                        args = list(iterator)
                    if modifier == 'add':
                        if user.lower() == CHANNEL:
                            # Adds points to the given viewer. Only callable by the broadcaster.
                            points, viewer = args
                            self.add_points(viewer, points)
                            self.socket.send_private_message(ADDED_POINTS.format(points=points, viewer=viewer, point_alias=POINTS_ALIAS))
                        else:
                            self.socket.send_private_message("{} suh dude? You know you can't do that!".format(user))
                    elif modifier == 'remove':
                        if user.lower() == CHANNEL:
                            # Removes points from the given viewer, but will never go below 0 total points.
                            # Only callable by the broadcaster.
                            points, viewer = args
                            self.remove_points(viewer, points)
                            self.socket.send_private_message(REMOVED_POINTS.format(points=points, viewer=viewer, point_alias=POINTS_ALIAS))
                        else:
                            self.socket.send_private_message("{} suh dude? You know you can't do that!".format(user))
                    else:
                        # Command is customizable by the POINTS_ALIAS setting. Reports calling viewer's total points
                        points = self.get_points(user)
                        self.socket.send_private_message(POINTS_COUNT.format(viewer=user, points=points, point_alias=POINTS_ALIAS))

if __name__ == '__main__':
    bot = DonkeyBot()
    while True:
        bot.the_thing_donkey_bot_does()

