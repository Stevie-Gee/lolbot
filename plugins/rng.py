"""Random number generator."""

import random
import re

import bot_utils
import config


@bot_utils.command("rng")
def call(msg):
    """Returns a random integer.
    
    If no args given, returns a number between 1 and 100.
    If one arg given, returns a number between 1 and <arg>.
    If two args given, returns a number between <arg1> and <arg2>."""
    content = msg.get("d").get("content")
    parts = content.split()
    if len(parts) == 1:
        minval = 1
        maxval = 100
    elif len(parts) == 2:
        minval = 1
        maxval = int(parts[1])
    else:
        minval = int(parts[1])
        maxval = int(parts[2])
    
    if minval > maxval:
        minval, maxval = maxval, minval
    randno = random.randint(minval, maxval)
    
    if minval == maxval:
        bot_utils.reply(msg, "Your number is %s. What a surprise." % randno)
    else:
        bot_utils.reply(msg, "Your number is %s." % randno)


@bot_utils.command("d6")
def dicecmd(msg):
    """
    Roll one or more dice, you can specify the number of sides and how many to roll.
    e.g. to roll two D6s: !2d6"""
    
    # This is just a placeholder for the help command
    return


bot_utils.RECOMMANDS.append(r"(\d*)d(\d+)")
@bot_utils.handler
def all_dice_cmd(msg):
    """
    The real handler for arbitrary dice rolls
    """
    if msg.get("t") != "MESSAGE_CREATE":
        return
    content = msg.get("d").get("content")
    
    if not content.startswith(config.COMMAND_CHAR):
        return
    
    content = content.lstrip(config.COMMAND_CHAR)
    match = re.match(r"(\d*)d(\d+)", content, re.I)
    
    if not match:
        return
    
    try:
        sides = int(match.group(2))
        if match.group(1):
            count = int(match.group(1))
        else:
            count = 1
        if count > 100:
            bot_utils.reply(msg, "I don't have that many dice...")
            return
        elif count < 1:
            bot_utils.reply(msg, "You rolled nothing!")
            return
    except:
        # Badly-formed command, ignore it
        return
    
    rolls = [str(random.randint(1, sides)) for _ in range(count)]
    rollstr = "You rolled %s" % (", ".join(rolls))
    bot_utils.reply(msg, rollstr)
