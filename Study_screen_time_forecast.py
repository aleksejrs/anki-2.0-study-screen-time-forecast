#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Copyright: Aleksej, 2013
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

#from time import clock
from anki.hooks import wrap
from aqt.overview import Overview
from Card_time_forecast import getForecast
from anki.utils import fmtTimeSpan
import random

# If the deck contains more cards, take a random sample of this many.
MAX_CARDS_TO_USE = 1500


def getTotalForIds(mw, ids, forecast_days):
    """Return forecast in seconds for cards listed in ids."""
    total = 0
    for cid in ids:
        f = getForecast(mw, mw.col.getCard(cid), forecast_days)
        if f:
            total += f
    return total


def makeForecastStrings(mw):

    ids = mw.col.findCards('deck:current is:review -is:suspended')

    years = 10
    forecast_days = 365.25 * years

    if len(ids) > MAX_CARDS_TO_USE:
#        stime = clock()
        multiplier = len(ids) / MAX_CARDS_TO_USE
        ids = random.sample(ids, MAX_CARDS_TO_USE)
        total = getTotalForIds(mw, ids, forecast_days) * multiplier
#        print "{0}s for {1} cards".format(clock() - stime, len(ids))
        totalText = u"Next {0}Y: ≈{1}".format(years, fmtTimeSpan(total, short=True))
#        totalText = u"Next {0}Y: ≈{1}".format(years, total / 3600)
    else:
        total = getTotalForIds(mw, ids, forecast_days)
        totalText = u"Next {0}Y: {1}".format(years, fmtTimeSpan(total, short=True))

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

