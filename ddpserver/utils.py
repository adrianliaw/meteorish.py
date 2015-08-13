import random
import logging

UNMISTAKABLE_CHARS = "23456789ABCDEFGHJKLMNPQRSTWXYZabcdefghijkmnopqrstuvwxyz"


def gen_id(chars=17):
    res = ""
    for i in range(chars):
        res += random.choice(UNMISTAKABLE_CHARS)
    return res

logger = logging.getLogger("ddpserver")
