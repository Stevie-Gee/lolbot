"""
Get a channel's discord ID without having to trawl through JSON.
"""

import re
import bot_utils

@bot_utils.command("channel")
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

@bot_utils.command("quitguild")
@bot_utils.admin_only
def quitguild(msg):
    """Leave a guild (server)"""
    content = msg.get("d").get("content")
    if ' ' in content:
        guildid = content.split(' ', 1)[1]
    else:
        bot_utils.reply(msg, "channel ID missing")
    
    bot_utils.HTTP_SESSION.delete("/users/@me/guilds/{guildid}".format(guildid=guildid))
    bot_utils.reply(msg, "Done")

@bot_utils.command("getguilds")
@bot_utils.admin_only
def getguilds(msg):
    """Print the list of joined guilds"""
    response = bot_utils.HTTP_SESSION.get("/users/@me/guilds")
    for guild in response.json():
        bot_utils.reply(msg, str(guild))
