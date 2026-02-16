# Register stores hex
register = []

def init():
    global register
    register = []
    for i in range(13):
        register.append(0)


def set_register(index, data):
    register[index] = data


def get_register(index):
    return register[index]
