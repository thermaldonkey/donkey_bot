import re
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import choice, randrange

from my_socket import TwitchChatSocket
from initialize import join_room
from read import get_user, get_message, tokenize_new_data
from settings import CHANNEL, IDENTITY, POINTS_ALIAS, POINTS_COUNT, ADDED_POINTS, REMOVED_POINTS, TRANSFERRED_POINTS
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
        self.read_buffer = ''
        self.active_chatters = {}
        self.super_users = [CHANNEL]
        self.last_heist_at = datetime.now()
        self.raffle_running = False
        self.raffle_entries = []
        self.socket = TwitchChatSocket()
        join_room(self.socket)

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
        viewer = Viewer(nickname=nickname, points=100)
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
        return getattr(viewer, 'points', 100)

    def add_points(self, nickname, points):
        '''
        Adds given number of points to the viewer with the given nickname. Will add the viewer if no
        matching one already exists. Returns success bool.

        @param nickname (str) - Nickname of the viewer
        @param points (int) - Number of points to award
        @param (bool) - True if successful
        '''
        try:
            viewer = self.get_viewer(nickname) or self.add_viewer(nickname)
            viewer.points += int(points)
            self.session.commit()
            return True
        except OverflowError:
            self.session.rollback()
            self.socket.send_private_message(("Guys...I can't count that high. Can we not? "
                                              "FailFish Please don't be dumb."))
            return False

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

    def transfer_points(self, giver, receiver, points):
        '''
        Removes given number of points from the giver and adds them to the receiver. Will add either
        viewers if no matching users are found.

        @param giver (str) - Nickname of the generous viewer
        @param receiver (str) - Nickname of the lucky son of a bitch
        @param points (int) - Number of points to transfer from giver to receiver
        '''
        self.remove_points(giver, points)
        self.add_points(receiver, points)

    def record_chat_activity(self, nickname):
        '''
        Updates the given viewer's most recent chat time (stored in memory for now). Ignores the
        executing bot as well as nightbot.

        @param nickname (str) - Nickname of the viewer
        '''
        if nickname not in [IDENTITY, 'nightbot']:
            now = datetime.now()
            self.active_chatters[nickname] = now

    def prune_chat_activity(self, seconds):
        '''
        Prunes recent chatters mapping based on the given time range. Viewers must have chatted
        within the given number of seconds in order to be considered active.

        @param seconds (int) - Number of seconds to consider active chat window
        '''
        time_zero = datetime.now() - relativedelta(seconds=seconds)
        return {chatter: chat_time for chatter, chat_time in self.active_chatters.iteritems() if chat_time > time_zero}

    def setup_raffle(self):
        '''
        Initializes raffle state in chat, allowing viewers to enter the raffle.
        '''
        self.raffle_entries = []
        self.raffle_running = True
        self.socket.send_private_message(("A raffle has begun! Type !raffle in chat to enter. "
                                          "Multiple entries do not increase your chances of "
                                          "winning. Nice try though. Kappa"))

    def enter_raffle(self, viewer):
        '''
        Enters the given viewer into a raffle, assuming one is currently running.

        @param viewer (str) - Username of new raffle entry
        '''
        if self.raffle_running:
            print 'Entering {}'.format(viewer.lower())
            self.raffle_entries.append(viewer.lower())
        else:
            print 'Raffle is not running???'

    def finish_raffle(self):
        '''
        Chooses a random winner of the current raffle entries. Verifies the raffle entries and prize
        are reset.
        '''
        try:
            if self.raffle_entries:
                unique_entries = list(set(self.raffle_entries))
                winner = choice(unique_entries)
                self.socket.send_private_message(("Congratulations, {}! You won the raffle! Speak "
                                                  "up in chat to claim your prize! PogChamp").format(winner))
            else:
                print 'WHAT'
        except:
            self.socket.send_private_message('Something went wrong trying to complete the raffle, {}! panicBasket'.format(CHANNEL))
        finally:
            self.raffle_entries = []
            self.raffle_running = False

    def ready_for_another_heist(self):
        '''
        Returns True if last recorded heist finished at least 5 minutes ago. False otherwise.

        @return (bool)
        '''
        time_zero = datetime.now() - relativedelta(seconds=300)
        return self.last_heist_at <= time_zero

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

                self.record_chat_activity(user)
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
                elif re.match('^!blowkiss', message.lower()):
                    args = message.split()
                    try:
                        target = args[1]
                    except IndexError:
                        self.socket.send_private_message('USAGE: !blowkiss <name>')
                        continue

                    roll = randrange(1, 3)
                    if roll == 1:
                        response = "Kreygasm <3 ooooooh myyyyy"
                    elif roll == 2:
                        response = "WutFace what? Get away from me!!!!"

                    self.socket.send_private_message("{} blows {} a kiss. {}".format(user, target, response))
                elif re.match('^!peanutguy', message.lower()):
                    if user.lower() == CHANNEL:
                        tokens = message.split()
                        try:
                            modifier = tokens[1]
                            viewer = tokens[2]
                        except IndexError:
                            self.socket.send_private_message('USAGE: !peanutguy (add|remove) <name>')
                            continue

                        if modifier == 'add':
                            self.super_users.append(viewer.lower())
                            self.socket.send_private_message(("Congratulations {viewer}, you've been made a Peanut Guy for the stream! "
                                                              "You are now empowered to run `!{alias} add <number> <name>` and "
                                                              "`!{alias} remove <number> <name>`, but remember, with great power "
                                                              "comes great responsibility. Kappa").format(viewer=viewer, alias=POINTS_ALIAS))
                        elif modifier == 'remove':
                            self.super_users.remove(viewer.lower())
                            self.socket.send_private_message("...and now {}'s watch has ended. Resquiat in pace.".format(viewer))
                elif re.match('^!(points|{})'.format(POINTS_ALIAS), message.lower()):
                    tokens = message.split()
                    modifier = None
                    if len(tokens) > 1:
                        iterator = iter(tokens)
                        iterator.next()
                        modifier = iterator.next()
                        args = list(iterator)
                    if modifier == 'add':
                        if user.lower() in self.super_users:
                            # Adds points to the given viewer. Only callable by super users.
                            try:
                                points = args[0]
                                viewer = args[1]
                                print points
                                print viewer
                            except IndexError:
                                self.socket.send_private_message('USAGE: !{} add <amount> <name>'.format(POINTS_ALIAS))
                                continue

                            viewer = viewer.replace('@', '').lower()
                            if self.add_points(viewer, points):
                                self.socket.send_private_message(ADDED_POINTS.format(points=points, viewer=viewer, point_alias=POINTS_ALIAS))
                    elif modifier == 'remove':
                        if user.lower() in self.super_users:
                            # Removes points from the given viewer, but will never go below 0 total points.
                            # Only callable by super users.
                            try:
                                points = args[0]
                                viewer = args[1]
                            except IndexError:
                                self.socket.send_private_message('USAGE: !{} remove <amount> <name>'.format(POINTS_ALIAS))
                                continue

                            viewer = viewer.replace('@', '').lower()
                            self.remove_points(viewer, points)
                            self.socket.send_private_message(REMOVED_POINTS.format(points=points, viewer=viewer, point_alias=POINTS_ALIAS))
                    elif modifier == 'give':
                        try:
                            points = args[0]
                            viewer = args[1]
                            if not re.match(r'^\d+$', points):
                                raise TypeError

                            viewer = viewer.replace('@', '').lower()
                            user = user.lower()
                            self.transfer_points(user.lower(), viewer, points)
                            self.socket.send_private_message(TRANSFERRED_POINTS.format(giver=user, points=points, receiver=viewer, point_alias=POINTS_ALIAS))
                        except (IndexError, TypeError):
                            self.socket.send_private_message('USAGE: !{} give <amount> <name>'.format(POINTS_ALIAS))
                            continue
                    else:
                        # Command is customizable by the POINTS_ALIAS setting. Reports calling viewer's total points
                        points = self.get_points(user)
                        self.socket.send_private_message(POINTS_COUNT.format(viewer=user, points=points, point_alias=POINTS_ALIAS))
                elif re.match('^!raffle', message.lower()):
                    args = message.split()
                    try:
                        modifier = args[1]
                    except IndexError:
                        modifier = ''

                    if modifier.lower() == 'start':
                        if user.lower() == CHANNEL:
                            self.setup_raffle()
                    elif modifier.lower() == 'stop':
                        if user.lower() == CHANNEL:
                            self.finish_raffle()
                    else:
                        self.enter_raffle(user.lower())
                elif re.match('^!honkey', message.lower()):
                    # TODO holding onto this in case we want to use it later.
                    # response = requests.get('https://tmi.twitch.tv/group/user/{}/chatters'.format(CHANNEL),
                                            # headers={'Accept': 'application/json',
                                                     # 'Autorization': 'OAuth ' + STREAM_KEY,
                                                     # 'Content-Type': 'application/json'})
                    # print json.loads(response.text)
                    last_five_mins_chatters = self.prune_chat_activity(300)
                    chatters = last_five_mins_chatters.keys()
                    if CHANNEL.lower() not in chatters:
                        chatters.append(CHANNEL.lower())
                    chatters.remove(user)
                    try:
                        winner = choice(chatters)
                        if winner == CHANNEL.lower():
                            self.add_points(user.lower(), 50)
                            self.socket.send_private_message("{} about to honkey THE DONKEY Kreygasm Scored an extra 50 {}".format(user, POINTS_ALIAS))
                        else:
                            self.socket.send_private_message("{} about to honkey {}'s donkey! HONK!!! Kreygasm".format(user, winner))
                    except IndexError:
                        self.socket.send_private_message("No donkeys are around to honkey! BabyRage")

                elif re.match('^!throw', message.lower()):
                    peanuts = self.get_points(user)
                    if peanuts:
                        tokens = message.split()
                        try:
                            target = tokens[1].replace('@', '')
                        except IndexError:
                            continue

                        if target.lower() in self.active_chatters.keys():
                            self.remove_points(user, 1)
                            roll = randrange(1, 5)
                            if roll == 1:
                                self.socket.send_private_message("{} threw a peanut at {}...hit their shoe. WEAK! SwiftRage".format(user, target))
                            elif roll == 2:
                                self.socket.send_private_message("{} threw a peanut at {}...body shot! U mad bro?".format(user, target))
                            elif roll == 3:
                                self.socket.send_private_message("{} threw a peanut at {}...HEAD SHOT! PogChamp".format(user, target))
                            elif roll == 4:
                                self.socket.send_private_message("{} threw a peanut at {}...and missed. FeelsBadMan".format(user, target))
                        else:
                            self.socket.send_private_message("{} wanted to throw a peanut at {}, but they're not around. FeelsBadMan".format(user, target))
                    else:
                        self.socket.send_private_message("{} tried to throw a peanut at someone...but they don't have any! BibleThump".format(user))
                # elif re.match('^!heist', message.lower()):
                    # if not self.ready_for_another_heist:
                        # self.socket.send_private_message(("The Peanut Guy is on high alert! Better "
                                                          # "give him a few mins to calm down before "
                                                          # "attacking him mercilessly."))
                        # continue

if __name__ == '__main__':
    bot = DonkeyBot()
    while True:
        bot.the_thing_donkey_bot_does()

