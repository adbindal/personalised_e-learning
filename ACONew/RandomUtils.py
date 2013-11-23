import sys, random

def getDouble():
    " Get a random double number "
    return random.random()

def getInt(limit):
    " Get a random int x such that 0 <= x < limit "
    return random.randint(0, limit-1)

def getLong(limit):
    " Get a random long int x such that 0 <= x < limit "
    return random.randint(0, limit-1)

def getRange(low, high):
    " Get a random int x such that low <= x <= high "
    return random.randint(low, high)
