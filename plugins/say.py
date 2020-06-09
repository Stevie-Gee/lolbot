"""
Send arbitrary messages via bot.
"""

import re
import bot_utils

@bot_utils.command("say")
@bot_utils.admin_only
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

@bot_utils.command("blink")
@bot_utils.admin_only
def blink(msg):
    """Send arbitrary message to the destination, then delete the message"""
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
    response = bot_utils.reply(fake, response)
    msg_id = response.json()['id']
    chan_id = response.json()['channel_id']
    bot_utils.HTTP_SESSION.request('DELETE',
        '/channels/{0}/messages/{1}'.format(chan_id, msg_id))
