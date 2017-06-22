"""
Print today's Discordian date.
"""

import time
import bot_utils

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

@bot_utils.command("ddate")
def call(msg):
    """Discordianism is cool."""
    day, weekday, season, year, istib = ddate()
    if istib:
        result = "Today is St. Tib's day in the YOLD %s" % year
    else:
        result = ("Today is %s, the %s%s day of %s in the YOLD %s" %
                  (WEEKDAYS[weekday], day, ordinalise(day), SEASONS[season], year))
    bot_utils.reply(msg, result)

def ddate():
    """Return today's discordian date as a tuple of
    (day of month, day of week, season, year, St Tibbs Day <bool>)
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
    
    return day, weekday, season, year, istib

def ordinalise(number):
    """Given a cardinal number less than 100, respond with the ordinal suffix.
    e.g. 1 -> st, 12 -> th, 53 -> rd.
    """
    if number in (11, 12, 13):
        return "th"
    elif number % 10 == 1:
        return "st"
    elif number % 10 == 2:
        return "nd"
    elif number % 10 == 3:
        return "rd"
    else:
        return "th"
