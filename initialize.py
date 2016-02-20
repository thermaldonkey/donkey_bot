import string
from my_socket import send_message

def join_room(socket):
    read_buffer = ''
    loading = True

    while loading:
        read_buffer += socket.recv(1024)
        temp = string.split(read_buffer, '\n')
        read_buffer = temp.pop()

        for line in temp:
            print(line)
            loading = not loading_complete(line)

    send_message(socket, 'Successfully joined chat!')

def loading_complete(line):
    if 'End of /NAMES list' in line:
        return True
    else:
        return False
