import random


def safe_int(string):
    try:
        if string.startswith('0x'):
            return int(string[2:], 16)
        elif string.startswith('0b'):
            return int(string[2:], 2)
        else:
            return int(string)
    except ValueError:
        out = 0
        for x in string:
            out ^= ord(x)
        return out


def safe_float(string):
    try:
        return float(string)
    except ValueError:
        return random.random()
        
def ent2list(string, exclude=set()):
    return [x for x in string.split("\n") if x and x not in exclude]
    
def list2ent(l):
    return "\n".join(l)
