"""Surprise buttsecks."""

import bot_utils

@bot_utils.command("surprisebuttsecks")
def doit(msg):
    """What do you think this does?"""
    content = msg.get("d").get("content")
    if ' ' in content:
        target = content.split(' ', 1)[1]
    else:
        target = "<@%s>" % msg["d"]["author"]["id"]
    bot_utils.reply(msg, "*sneaks up behind %s and gives them surprisebuttsecks.*" % target)
