from read import tokenize_new_data

def join_room(socket):
    read_buffer = ''
    loading = True

    while loading:
        temp, read_buffer = tokenize_new_data(socket, read_buffer)
        for line in temp:
            print(line)
            loading = not loading_complete(line)

    socket.send_private_message('Successfully joined chat!')

def loading_complete(line):
    if 'End of /NAMES list' in line:
        return True
    else:
        return False
