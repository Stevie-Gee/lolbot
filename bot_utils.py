"""
Functions that might be useful for plugins.
"""

import requests

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

def reply(msg, reply):
    """Given a MESSAGE_CREATE event from discord, and a reply string,
    send the reply string to whichever channel/PM the original event
    came from.
    """
    channel_id = msg.get("d").get("channel_id")
    HTTP_SESSION.post(
        "/channels/{0}/messages".format(channel_id),
        json={"content": reply},
        )
