"""
Return info about a user on the site.

config.py directives:
* USERSEARCH_URL: URL to search for users
* USERSEARCH_PW: Password parameter to send with requests
* USERSEARCH_ALIASES_FNAME: Path for storing aliases file
* USERSEARCH_TIMEOUT: Timeout for https requests
"""

import re
import requests
import time

import bot_utils
import config

# Persistent https session
SESSION = requests.Session()

# Dictionary to map discord IDs to site usernames
ALIASES = {}

# Extra kwargs to pass to the http handler
HTTP_KWARGS = getattr(config, "USERSEARCH_HTTP_KWARGS", {})


def command_search(msg):
    """Receive a discord message, process and reply."""
    # Get either the first argument after the command, or the userID
    # of the sender if no args provided
    if ' ' in msg["d"].get("content"):
        nick = msg["d"].get("content").split(None, 1)[1]
    else:
        nick = "<@{0}>".format(msg["d"].get("author", {}).get("id"))
    
    # If we have a discord ID, try to convert it to a site nickname
    if re.match(r'\<\@(\d+)\>', nick):
        nick = ALIASES.get(nick[2:-1], '')
        if not nick:
            bot_utils.reply(msg, "Discord user has no mapping to site")
            return
    
    # Do search
    try:
        results = search_nick(nick)
        bot_utils.reply(msg, prettyprint(results))
    except ValueError:
        bot_utils.reply(msg, "Unknown username")
    except:
        bot_utils.reply(msg, "Error sending")

def prettyprint(uinfo):
    """Given a results dict from the site, return a nice string."""
    # Please note this method does not take leap years into account
    joindate = long(uinfo['joindate'])
    timestring = ''
    if time.time() > joindate:
        joinlength = long(time.time()) - joindate
    else:
        joinlength = joindate - long(time.time())
        timestring = '-'
    if joinlength / 31536000 != 0:
        timestring += str(joinlength / 31536000)+'y '
    if (joinlength / 86400)%365 != 0:
        timestring += str((joinlength / 86400)%365)+'d '
    if (joinlength / 3600)%24 != 0:
        timestring += str((joinlength / 3600)%24)+'h '
    if (joinlength / 60)%60 != 0:
        timestring += str((joinlength / 60)%60)+'m '
    if joinlength%60 != 0:
        timestring += str(joinlength%60)+'s '
    uinfo["timestring"] = timestring.strip()
    uinfo["url"] = config.USERSEARCH_PUBLIC_URL
    
    returnstring = "**{username}** - *{usertitle}* | **{posts}** posts | **{reputation}** rep | Member for **{timestring}** {url}{userid}"
    return returnstring.format(**uinfo)

def command_add(msg):
    """Add a new alias."""
    if msg["d"].get("author", {}).get("id") not in config.ADMINS:
        bot_utils.reply(msg, "Sorry, only authorised users can do this")
        return
    
    if msg["d"].get("content").count(" ") < 2:
        bot_utils.reply(msg, "Invalid format")
        return
    
    _, uid, nick = msg["d"].get("content").split(" ", 2)
    if not re.match(r'\<\@(\d+)\>', uid):
        bot_utils.reply(msg, "Invalid format")
        return
    uid = uid[2:-1]
    
    ALIASES[uid] = nick
    write_aliases(config.USERSEARCH_ALIASES_FNAME)
    bot_utils.reply(msg, "<@{0}> is now {1} on the site".format(uid, nick))

def command_del(msg):
    """Remove an alias."""
    if msg["d"].get("author", {}).get("id") not in config.ADMINS:
        bot_utils.reply(msg, "Sorry, only authorised users can do this")
        return
    
    if msg["d"].get("content").count(" ") != 1:
        bot_utils.reply(msg, "Invalid format")
        return
    
    uid = msg["d"].get("content").split(" ")[1]
    if not re.match(r'\<\@(\d+)\>', uid):
        bot_utils.reply(msg, "Invalid format")
        return
    uid = uid[2:-1]
    
    if uid in ALIASES:
        del ALIASES[uid]
        write_aliases(config.USERSEARCH_ALIASES_FNAME)
        bot_utils.reply(msg, "Alias deleted")
    else:
        bot_utils.reply(msg, "User has no alias")

def read_aliases(fname):
    """Read aliases from file."""
    global ALIASES
    ALIASES = {}
    with open(fname) as f:
        for line in f:
            key, ALIASES[key] = line.strip().split(' ', 1)

def write_aliases(fname):
    """Write aliases to file."""
    with open(fname, 'w') as f:
        for key, value in ALIASES.iteritems():
            f.write("%s %s\n" % (key, value))

def search_nick(nick):
    """
    Search the site for info about the user. If found, return a dict
    of their info.
    
    Raises ValueError if request fails or if user not found.
    """
    # Send HTTP request, raise an error if the request fails
    response = SESSION.post(
        config.USERSEARCH_URL,
        data={'password': config.USERSEARCH_PW, 'user': nick},
        timeout=getattr(config, "USERSEARCH_TIMEOUT", 3),
        **HTTP_KWARGS
        )
    response.raise_for_status()
    
    # Parse result - empty string means no match
    # TODO: Should be status 404, not empty string
    result = response.text.strip()
    if not result:
        raise ValueError("User not found")
    
    # result is a string returning various columns for the specified user
    # Columns are separated by newlines, and key/value pairs are separated by a space
    uinfo = {}
    for line in result.split('\n'):
        key, uinfo[key] = line.split(' ', 1)
    return uinfo

COMMANDS = {
    "usersearch": command_search,
    "u": command_search,
    "addalias": command_add,
    "dealias": command_del,
    "delalias": command_del,
}

# On init, read aliases from file
try:
    read_aliases(config.USERSEARCH_ALIASES_FNAME)
# If file doesn't exist, write it
except IOError:
    write_aliases(config.USERSEARCH_ALIASES_FNAME)
