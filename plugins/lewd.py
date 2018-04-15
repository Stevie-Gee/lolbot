"""Lewd meter"""

from __future__ import division

import random

import bot_utils


@bot_utils.command("lewd")
def doit(msg):
    """Some people like penis too."""
    content = msg.get("d").get("content")
    if ' ' in content:
        target = content.split(' ', 1)[1]
    else:
        target = "<@%s>" % msg["d"]["author"]["id"]
    
    if '<@268286679893147649>' in content:
        lewdness = 100.0
    else:
        lewdness = random.randint(0,999) / 10
    
    bot_utils.reply(msg, "{0} is {1:0.1f}% lewd".format(target, lewdness))
