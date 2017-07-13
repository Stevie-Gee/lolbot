"""Summon boobs."""

import bot_utils

@bot_utils.command("boobs")
def doboobs(msg):
    """Everyone likes boobs."""
    reply = u"\u0460"
    bot_utils.reply(msg, reply)
