"""
Send arbitrary messages via bot.
"""

import re
import bot_utils

def command(msg):
    """Send arbitrary commands to the specified destination. Only works for channels right now."""
    content = msg.get("d").get("content")
    try:
        _, dest, response = content.split(None, 2)
    except ValueError:
        reply = "Invalid format, expected destination and message."
        bot_utils.reply(msg, reply)
        return
    
    if dest.startswith('<@'):
        reply = "Sorry, I don't know how to DM right now."
        bot_utils.reply(msg, reply)
        return
    
    # Dest could be a naked ID or a bracket-wrapped format
    matches = re.match(r'\<.(\d+)\>', dest)
    if matches:
        dest = matches.group(1)
    
    # Hijack the bot_utils.reply function
    fake = dict(msg)
    fake["d"]["channel_id"] = dest
    bot_utils.reply(fake, response)

COMMANDS = {
    "say": command,
}
