"""
Get a user's discord ID without having to trawl through JSON.
"""

import re
import bot_utils

@bot_utils.command("uid")
def command(msg):
    """Return the Discord ID of the mentioned user, or the ID of the user who sent the message."""
    content = msg.get("d").get("content")
    if ' ' in content:
        arg = content.split()[1]
        matches = re.match(r'\<\@(\d+)\>', arg)
        if matches:
            reply = "Discord UserID %s" % matches.group(1)
        else:
            reply = "Invalid format"
    else:
        userid = msg["d"]["author"]["id"]
        reply = "Discord UserID %s" % userid
    bot_utils.reply(msg, reply)
