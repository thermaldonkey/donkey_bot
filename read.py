def get_user(line):
    tokens = line.split(':', 2)
    user = tokens[1].split('!', 1)[0]
    return user

def get_message(line):
    tokens = line.split(':', 2)
    message = tokens[2]
    return message
