#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Copyright: Aleksej, 2013
# License: GNU Affero General Public License, version 3 only; http://www.gnu.org/licenses/agpl.html

#from time import clock
import random

from anki.hooks import wrap
from aqt.overview import Overview
from anki.utils import fmtTimeSpan

try:
    from Card_time_forecast import getForecast
except:
    raise ImportError('''

AN ADD-ON NEEDS ANOTHER ADD-ON.

"Study screen time forecast" failed to import the Card_time_forecast.py
module.  You probably need to install the "Card time forecast" add-on,
which you can get (as of Nov 2015) from
https://ankiweb.net/shared/info/2189699505 or
https://github.com/aleksejrs/anki-2.0-card-time-forecast

If that doesn't help, please see the README file for contact info to
sent feedback to.''')

#### SETTINGS ###############################################################
#

# If the deck contains more cards, take a random sample of this many,
# and multiply the result for an approximation.
MAX_CARDS_TO_USE = 1500


# Do not show forecast for these decks.  Use when you need speed and no daily
# forecast.

# complete names, a comma-separated list
DECKS_WITHOUT_FORECAST_FULLNAMES = ()
# Example:
# DECKS_WITHOUT_FORECAST_FULLNAMES = ('/')

# prefixes, a comma-separated list
DECKS_WITHOUT_FORECAST_PREFIXES = ()
# Example:
# DECKS_WITHOUT_FORECAST_PREFIXES = ('~filt::prio')

# We could change MAX_CARDS_TO_USE per-deck instead, but it affects precision
# too much to want the result.

#
#############################################################################


def getTotalForIds(mw, ids, forecast_days):
    """Return forecast in seconds for cards listed in ids."""
    total = 0
    for cid in ids:

        # Anki 2.0.15 logs getCard operations, which makes this add-on very
        # slow, so we need to disable that.  2.0.16 will not do that.
        try:
            the_card = mw.col.getCard(cid, log=False)
        except TypeError:    # It's not Anki 2.0.15.
            the_card = mw.col.getCard(cid)

        f = getForecast(mw, the_card, forecast_days)
#        f = getForecast(mw, mw.col.getCard(cid, log=False), forecast_days)
        if f:
            total += f
    return total


def makeForecastStrings(mw):

    # Skip decks specified in the special list variables.
    if mw.col.decks.get(mw.col.conf['curDeck'])['name'] in DECKS_WITHOUT_FORECAST_FULLNAMES:
        return ""
    if mw.col.decks.get(mw.col.conf['curDeck'])['name'].startswith(DECKS_WITHOUT_FORECAST_PREFIXES):
        return ""

    ids = mw.col.findCards('deck:current is:review -is:suspended')

    years = 10
    forecast_days = 365.2425 * years

    if len(ids) > MAX_CARDS_TO_USE:
#        stime = clock()
        multiplier = len(ids) / float(MAX_CARDS_TO_USE)
        ids = random.sample(ids, MAX_CARDS_TO_USE)
        total = getTotalForIds(mw, ids, forecast_days) * multiplier
#        print "{0}s for {1} cards".format(clock() - stime, len(ids))
        totalText = u"Next {0}Y: ≈{1}".format(years, fmtTimeSpan(total, short=True))
#        totalText = u"Next {0}Y: ≈{1}".format(years, total / 3600)
    else:
        total = getTotalForIds(mw, ids, forecast_days)
        totalText = u"Next {0}Y: {1}".format(years, fmtTimeSpan(total, short=True))

    if total == 0:
        return ''

    per_day = total / forecast_days
    if per_day >= 5:
        per_day_text = u" ({0}/day)".format(fmtTimeSpan(per_day, short=True))
    else:
        per_day_text = ''
    return u"{0} {1}".format(totalText, per_day_text)


def myTable(self, _old):

    oldRes = _old(self)

    gr = makeForecastStrings(self.mw)
    return u"{0}<br/>{1}".format(oldRes, gr)


Overview._table = wrap(Overview._table, myTable, "around")

