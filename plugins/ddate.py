"""
Print today's Discordian date.
"""

import time
import config

WEEKDAYS = ['Sweetmorn',
            'Boomtime',
            'Pungenday',
            'Prickle-Prickle',
            'Setting Orange']

SEASONS = ['Chaos',
           'Discord',
           'Confusion',
           'Bureaucracy',
           'Aftermath']

def call(msg):
    """When this command is called, respond with today's Discordian date."""
    day, weekday, season, year, istib = ddate()
    if istib:
        result = "Today is St. Tib's day in the YOLD %s" % year
    else:
        result = ("Today is %s, the %s day of %s in the YOLD %s" % 
                  (WEEKDAYS[weekday], day, SEASONS[season], year))
    
    channel_id = msg.get("d").get("channel_id")
    config.HTTP_SESSION.post(
        "/channels/{0}/messages".format(channel_id),
        json={"content": result},
        )

def ddate():
    """Return today's discordian date as a tuple of
    (ordinal day of month, day of week, season, year, St Tibbs Day <bool>)
    """
    date = time.localtime()
    istib = False
    year = date[0]
    day = date[7] - 1
    # Every fourth year is a leap year
    # Except every hundred years it isn't
    # Except every four hundred years it is again
    isleap = (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)
    if isleap:
        if day + 1 == 60:
            istib = True
        elif day + 1 > 60:
            day -= 1
    weekday = day % 5
    season = day // 73
    year += 1166
    day = day % 73 + 1
    
    if day in (11, 12, 13):
        day = "%sth" % day
    elif day % 10 == 1:
        day = "%sst" % day
    elif day % 10 == 2:
        day = "%snd" % day
    elif day % 10 == 3:
        day = "%srd" % day
    else:
        day = "%sth" % day
    
    return day, weekday, season, year, istib

COMMANDS = {
    "ddate": call,
}
