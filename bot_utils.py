"""
Functions that might be useful for plugins.
"""

import logging
import requests
try:
    import urllib3
except:
    urllib3 = None

import config

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

_COMMANDS = {}
def command(cword):
    """Decorator to flag a function as handling a given !command."""
    def decor(func):
        _COMMANDS[cword.lower()] = func
        logging.info("Loaded command %s", cword)
        return func
    return decor

_HANDLERS = []
def handler(func):
    """Decorator to flag a function as handling all Discord events."""
    _HANDLERS.append(func)
    logging.info("Loaded plugin %s", func)
    return func
