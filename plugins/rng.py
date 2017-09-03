"""Random number generator."""

import random
import bot_utils


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
