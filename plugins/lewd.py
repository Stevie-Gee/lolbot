"""Lewd meter"""

from __future__ import division

import random

import bot_utils

# Cache previous measurements so they don't change every call
MEASUREMENTS = {}

# Method for randomly generating a lewdness
def get_lewdness(subject):
    """Measure lewdness of the subject, return a float between 0 and 100"""
    if '<@268286679893147649>' in subject or 'mina' in subject.lower():
        return random.randint(700,999) / 10
    else:
        return random.randint(0,999) / 10

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
