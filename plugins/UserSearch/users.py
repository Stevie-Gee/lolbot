"""
Allows you to search for users on the website based on username. Also contains
an auto-join search feature and an alias dict to allow you to map IRC nicks to
forum usernames.
"""
import time
import urllib
import urllib2
from plugins import Plugin, Command, UnlistedCommand

alias_file = 'plugins/UserSearch/aliases.conf'

# Dictionary to map discord usernames to site usernames
ALIASES = {}

def getalias(nick):
    """
    If the given nick has an alias, returns the alias. Otherwise, returns
    the original nick."""
    if nick.lower() in ALIASES:
        return ALIASES[nick.lower()]
    else:
        return nick

def readaliases():
    """Reads the aliases file into a python dict."""
    # TODO: Use json instead
    with open(alias_file) as f:
        for line in f:
            key, ALIASES[key] = line.strip().split(' ', 1)

def writealiases():
    """Writes the current contents of the alias dict to file."""
    # TODO: Use with() syntax
    try:
        f = open(alias_file, 'w')
        for key, value in ALIASES.iteritems():
            f.write("%s %s\n" % (key, value))
        f.close()
    except Exception, e:
        print str(e)

def add(alias, nick):
    """
    Adds a new alias to the dict, overwriting a previous alias if it existed.
    """
    ALIASES[alias.lower()] = nick.lower()
    writealiases()

def remove(alias):
    """
    Removes an existing alias. Returns True on success or False on failure.
    """
    if alias.lower() in ALIASES:
        del ALIASES[alias.lower()]
        writealiases()
        return True
    else:
        return False



class UserSearch(Command):
    """Queries a database for the requested user (or the sender)."""
    def __init__(self):
        self.command = 'u'
        self.aliases = ['user']
    
    def call(self, msg, server):
        if msg.commargs:
            nick = msg.commargs
        else:
            nick = msg.nick
        try:
            result = search(nick)
        except urllib2.URLError:
            server.replyto(msg, "There was an error contacting the database. Please try again later.")
            return
        
        if result:
            server.replyto(msg, result[0])
        else:
            server.replyto(msg, "User not found.")
    
    def help(self, msg, server):
        return "Search for a user by nickname."

class UserJoin(Plugin):
    """Handles the auto-search when a user joins a channel."""
    def __init__(self):
        self.commands = ['JOIN']
    
    def call(self, msg, server):
        # Make sure the channel is a uchannel, and make sure we're not responding
        # to ourselves joining the channel
        uchannels = getattr(server.getconfig(), 'uchannels', [])
        if msg.trailing not in uchannels or msg.nick == server.getnick():
            return
        
        try:
            result = search(msg.nick)
        except urllib2.URLError:
            result = None
        
        if result:
            server.replyto(msg, result[0])
            if result[1]['usergroupid'] in ['11', '49']:
                server.send("MODE %s +v %s" % (msg.channel, msg.nick))
        else:
            server.replyto(msg, "Welcome to LRU!")

def search(nick):
    """
    Attempts to find a user by nickname. If user is found, will return a
    tuple containing a formatted string displaying info about the user, and the
    uinfo dict. If the user is not found, returns None.
    
    Will throw a urllib2.URLError if the request fails.
    """
    url = "https://www.lolicit.org/ircdb.php"
    password = 'iJ9xls4qa4ZU9lXHGM5vxGEmNHLmmIeg'
    timeout = 3
    
    # Check for trailing underscore and remove
    if nick.endswith('_'):
        nick = nick[:-1]
    nick = getalias(nick)
    
    req = urllib2.Request(url)
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    postvars = urllib.urlencode({'password': password, 'user': nick})
    result = urllib2.urlopen(req, postvars, timeout).read()
    
    # Try replacing underscores with spaces
    if not result and '_' in nick:
        nick = nick.replace('_', ' ')
        nick = getalias(nick)
        postvars = urllib.urlencode({'password': password, 'user': nick})
        result = urllib2.urlopen(url, postvars, timeout).read()
    
    if not result:
        return None
    
    # result is a string returning various columns for the specified user
    # Columns are separated by newlines, and key/value pairs are separated by a space
    result = result.strip()
    uinfo = {}
    for line in result.split('\n'):
        key, uinfo[key] = line.split(' ', 1)
    
    #Please note this method does not take leap years into account
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
    timestring = timestring.strip()
    
    returnstring = "\x0307[\x0304User Search\x0307] \x0307%s \x0314[%s] \x0307[\x0304Posts \x0303%s \x0304Reputation \x0303%s\x0307] \x0307[\x0304Member for \x0303%s\x0307] \x0314https://www.lolicit.org/member.php?u=%s" % (uinfo['username'], uinfo['usertitle'], uinfo['posts'], uinfo['reputation'], timestring, uinfo['userid'])
    returnstring = unicode(returnstring).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    return (returnstring, uinfo)

class AddAlias(UnlistedCommand):
    """Adds an alias to the alias list."""
    def __init__(self):
        self.command = 'alias'
        self.aliases = ['addalias']
    
    def call(self, msg, server):
        if not server.isowner(msg):
            server.replyto(msg, "ACCESS DENIED")
            return
        
        if msg.commargs and ' ' in msg.commargs:
            alias, nick = msg.commargs.strip().split(' ', 1)
            add(alias, nick)
            server.replyto(msg, "%s is now %s" % (alias, nick))
        else:
            server.replyto(msg, "Not enough parameters.")

class DeAlias(UnlistedCommand):
    """Removes an alias."""
    def __init__(self):
        self.command = 'dealias'
    
    def call(self, msg, server):
        if not server.isowner(msg):
            server.replyto(msg, "ACCESS DENIED")
            return
        
        if msg.commargs:
            if remove(msg.commargs):
                server.replyto(msg, "Alias deleted.")
            else:
                server.replyto(msg, "'%s' never had an alias." % msg.commargs)
        else:
            server.replyto(msg, "Not enough parameters.")


# On import, read aliases from config
readaliases()
