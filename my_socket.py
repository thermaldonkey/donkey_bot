import socket
from settings import HOST, PORT, PASS, IDENTITY, CHANNEL

class TwitchChatSocket(object):
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.socket.send('PASS {}\r\n'.format(PASS))
        self.socket.send('NICK {}\r\n'.format(IDENTITY))
        self.socket.send('JOIN #{}\r\n'.format(CHANNEL))

    def recv(self, *args):
        return self.socket.recv(*args)

    def send_private_message(self, message):
        message_temp = 'PRIVMSG #{} :{}\r\n'.format(CHANNEL, message)
        self.socket.send(message_temp)
        print('Sent: {}'.format(message_temp))
