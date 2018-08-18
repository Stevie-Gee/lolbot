"""Random number generator."""

import random
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
        maxval = long(parts[1])
    else:
        minval = long(parts[1])
        maxval = long(parts[2])
    
    if minval > maxval:
        minval, maxval = maxval, minval
    randno = random.randint(minval, maxval)
    
    if minval == maxval:
        bot_utils.reply(msg, "Your number is %s. What a surprise." % randno)
    else:
        bot_utils.reply(msg, "Your number is %s." % randno)

@bot_utils.command("d4")
@bot_utils.command("d6")
@bot_utils.command("d8")
@bot_utils.command("d10")
@bot_utils.command("d12")
@bot_utils.command("d20")
@bot_utils.command("d100")
def dicecmd(msg):
    """Roll one or more dice (you can specify how many to roll)"""
    content = msg.get("d").get("content")
    parts = content.split()
    sides = int(parts[0].strip(config.COMMAND_CHAR).strip('dD'))
    try:
        count = int(parts[1])
        if count > 100:
            bot_utils.reply(msg, "I don't have that many dice...")
            return
    except ValueError:
        bot_utils.reply(msg, "I can only roll a numeric number of dice")
        return
    except IndexError:
        count = 1
    
    rolls = [str(random.randint(1, sides)) for _ in range(count)]
    rollstr = "You rolled %s" % (", ".join(rolls))
    bot_utils.reply(msg, rollstr)
