"""Lewd meter"""

from __future__ import division

import random

import bot_utils

# Cache previous measurements so they don't change every call
MEASUREMENTS = {}

@bot_utils.command("lewd")
def doit(msg):
    """Measure lewdness of target"""
    content = msg.get("d").get("content")
    if ' ' in content:
        target = content.split(' ', 1)[1].strip()
    else:
        target = "<@%s>" % msg["d"]["author"]["id"]
    
    if target in MEASUREMENTS:
        lewdness = MEASUREMENTS[target]
    elif '<@268286679893147649>' in target or 'mina' in target.lower():
        lewdness = random.randint(700,999) / 10
        MEASUREMENTS[target] = lewdness
    else:
        lewdness = random.randint(0,999) / 10
        MEASUREMENTS[target] = lewdness
    
    bot_utils.reply(msg, "{0} is {1:0.1f}% lewd".format(target, lewdness))
