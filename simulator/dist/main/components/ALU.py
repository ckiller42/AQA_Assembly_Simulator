def add(x: int, y: int):
    return x + y


def sub(x: int, y: int):
    return x - y


def nand(x: int, y: int):
    return ~(x & y)


def orr(x: int, y: int):
    return x | y


def lsr(x: int, y: int):
    return x >> y


def lsl(x: int, y: int):
    return x << y


def xor(x: int, y: int):
    return x ^ y


def isEqual(x: int, y: int):
    return 1 if x == y else 0


def isGreat(x: int, y: int):
    return 1 if x > y else 0


def Not(x: int):
    return (1 << len(bin(x)[2:])) - 1 - x


def increment(x: int):
    return x + 1
