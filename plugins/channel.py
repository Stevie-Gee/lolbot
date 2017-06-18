"""
Get a channel's discord ID without having to trawl through JSON.
"""

import re
import bot_utils

def command(msg):
    """Return the Discord ID of the mentioned channel, or the ID of the channel where the message was sent."""
    content = msg.get("d").get("content")
    if ' ' in content:
        arg = content.split()[1]
        matches = re.match(r'\<\#(\d+)\>', arg)
        if matches:
            reply = "Discord channel ID %s" % matches.group(1)
        else:
            reply = "Invalid format"
    else:
        userid = msg["d"]["channel_id"]
        reply = "Discord channel ID %s" % userid
    bot_utils.reply(msg, reply)

COMMANDS = {
    "channel": command,
}
