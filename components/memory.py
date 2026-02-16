# Memory stores hex
memory = []

def init():
    global memory
    memory = []
    for i in range(10000):
        memory.append(0)


def set_memory(index, data):
    memory[index] = data


def get_memory(index):
    return memory[index]
