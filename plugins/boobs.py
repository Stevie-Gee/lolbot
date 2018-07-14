"""Summon boobs."""

import bot_utils

@bot_utils.command("boobs")
def doboobs(msg):
    """Everyone likes boobs."""
    reply = u"\u0460"
    bot_utils.reply(msg, reply)

@bot_utils.command("butt")
def doboobs(msg):
    """There is no butt command"""
    reply = u"No. There will be no 'butt' command."
    bot_utils.reply(msg, reply)

@bot_utils.command("penis")
def dopenis(msg):
    """Some people like penis too."""
    reply = u"\u2570\u22c3\u256f"
    bot_utils.reply(msg, reply)
