import socket
from settings import HOST, PORT, PASS, IDENTITY, CHANNEL

def open_socket():
    s = socket.socket()
    s.connect((HOST, PORT))
    s.send('PASS {}\r\n'.format(PASS))
    s.send('NICK {}\r\n'.format(IDENTITY))
    s.send('JOIN #{}\r\n'.format(CHANNEL))

    return s

def send_message(socket, message):
    message_temp = 'PRIVMSG #{} :{}\r\n'.format(CHANNEL, message)
    socket.send(message_temp)
    print('Sent: {}'.format(message_temp))
