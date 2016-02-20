def tokenize_new_data(socket, the_buffer):
    the_buffer += socket.recv(1024)
    data_tokens = the_buffer.split('\n')
    the_buffer = data_tokens.pop()
    return (data_tokens, the_buffer)

def get_user(line):
    tokens = line.split(':', 2)
    user = tokens[1].split('!', 1)[0]
    return user

def get_message(line):
    tokens = line.split(':', 2)
    message = tokens[2]
    return message
