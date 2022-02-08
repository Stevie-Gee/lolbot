"""Lewd meter"""

from __future__ import division

import random

import bot_utils

# Cache previous measurements so they don't change every call
MEASUREMENTS = {}

# Method for randomly generating a lewdness
def get_lewdness(subject):
    """Measure lewdness of the subject, return a float between 0 and 100"""
    return weightedrand()

def weightedrand():
    """
    Weighted random number generator.
    
    The first number determines the weighting of this row. If the weights
    sum to 100, then this number is the likelihood in % of the row being chosen.
    The second and third numbers are the range of possible values for this row.
    """
    WEIGHTS = [
        (78, 0,     500),   # weight, minval, maxval
        (15, 500,   750),
        ( 5, 750,   900),
        ( 2, 900,   999),
        ]
    weightsum = sum(i[0] for i in WEIGHTS)
    idx = random.randint(0, weightsum)
    for weight in WEIGHTS:
        if idx <= weight[0]:
            break
        idx -= weight[0]
    else:
        raise RuntimeError("Bad index %s" % idx)
    minrand, maxrand = weight[1:3]
    return random.randint(minrand, maxrand) / 10

@bot_utils.command("lewd")
def doit(msg):
    """Measure lewdness of target"""
    content = msg.get("d").get("content")
    if ' ' in content:
        target = content.split(' ', 1)[1].strip()
    else:
        target = "<@%s>" % msg["d"]["author"]["id"]
    
    try:
        lewdness = MEASUREMENTS[target]
    except KeyError:
        lewdness = MEASUREMENTS.setdefault(target, get_lewdness(target))
    
    bot_utils.reply(msg, u"{0} is {1:0.1f}% lewd".format(target, lewdness))
