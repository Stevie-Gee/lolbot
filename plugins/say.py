"""
Send arbitrary messages via bot.
"""

import re
import bot_utils

@bot_utils.command("say")
def command(msg):
    """Send arbitrary commands to the specified destination. Works for channels and @Users."""
    content = msg.get("d").get("content")
    try:
        _, dest, response = content.split(None, 2)
    except ValueError:
        reply = "Invalid format, expected destination and message."
        bot_utils.reply(msg, reply)
        return
    
    # User DM IDs are different from their user IDs
    if dest.startswith('<@'):
        dest = bot_utils.get_dm(dest)
    
    # Dest could be a naked ID or a bracket-wrapped format
    matches = re.match(r'\<.(\d+)\>', dest)
    if matches:
        dest = matches.group(1)
    
    # Hijack the bot_utils.reply function
    fake = dict(msg)
    fake["d"]["channel_id"] = dest
    bot_utils.reply(fake, response)
