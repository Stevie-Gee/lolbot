"""
Functions that might be useful for plugins.
"""

from functools import wraps
import logging
import re
import requests
try:
    import urllib3
except:
    urllib3 = None

import config

# List of all the !commands registered, and their handler functions
COMMANDS = {}

# List of all the event handlers registered
HANDLERS = set()

# Cache DM channels we have open
DM_CACHE = {}

class DiscordSession(requests.Session):
    """Custom Requests session that adds HTTP auth header, and adds the
    base URL to any requests.
    """
    class DiscordAuth(requests.auth.AuthBase):
        """Auth class that handles Discord HTTP authentication"""
        def __init__(self, bot_token):
            self.bot_token = "Bot " + bot_token
        def __call__(self, req):
            req.headers['Authorization'] = self.bot_token
            return req
    
    def __init__(self, url_base=None, bot_token=None, *args, **kwargs):
        super(DiscordSession, self).__init__(*args, **kwargs)
        self.url_base = url_base
        self.auth = DiscordSession.DiscordAuth(bot_token)
        # Allow an automatic retry since Discord seems to ungracefully
        # drop the connection
        self.mount('https://', requests.adapters.HTTPAdapter(max_retries=1))
    
    def request(self, method, url, **kwargs):
        modified_url = self.url_base + url
        return super(DiscordSession, self).request(method, modified_url, **kwargs)

# A custom requests.Session instance
# which handles Discord's HTTP auth and URL prefix for you
# Make requests to the root-relative API paths, e.g. "/channels/"
HTTP_SESSION = DiscordSession(config.BASE_URL, config.BOT_TOKEN)

def reply(msg, response):
    """Given a MESSAGE_CREATE event from discord, and a response string,
    send the response string to whichever channel/PM the original event
    came from.
    """
    channel_id = msg.get("d").get("channel_id")
    try:
        HTTP_SESSION.post(
            "/channels/{1}/messages".format(config.BASE_URL, channel_id),
            json={"content": response},
            )
    except requests.ConnectionError as err:
        # Cloudflare will silently drop our session, and older pythons
        # don't gracefully retry this, so we'll do it ourselves
        if (isinstance(err.message, urllib3.exceptions.ProtocolError)
                and err.message.args
                and err.message.args[0].lower().startswith("connection aborted")):
            HTTP_SESSION.post(
                "/channels/{1}/messages".format(config.BASE_URL, channel_id),
                json={"content": response},
                )
        else:
            raise

def command(cword):
    """Decorator to flag a function as handling a given !command."""
    def decor(func):
        COMMANDS[cword.lower()] = func
        logging.info("Loaded command %s", cword)
        return func
    return decor

def handler(func):
    """Decorator to flag a function as handling all Discord events."""
    HANDLERS.add(func)
    logging.info("Loaded handler '%s' from %s", func.__name__, func.func_globals.get("__file__"))
    return func

def admin_only(func):
    """Decorator to flag a function as only usable by ADMINS."""
    @wraps(func)
    def decorated_f(msg):
        if msg.get("d", {}).get("author", {}).get("id") not in config.ADMINS:
            reply(msg, "Sorry, only authorised users can do this")
            return
        else:
            return func(msg)
    return decorated_f

def get_dm(user):
    """Given a userid, get a DM session id."""
    # User ID could be a naked ID or a bracket-wrapped format
    matches = re.match(r'\<@(\d+)\>', user)
    if matches:
        user = matches.group(1)
    if user in DM_CACHE:
        return DM_CACHE[user]
    
    response = HTTP_SESSION.post("/users/@me/channels",
        json={"recipient_id": user},
        )
    dest = response.json()["id"]
    DM_CACHE[user] = dest
    return dest
