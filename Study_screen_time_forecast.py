#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Copyright: Aleksej, 2013
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from anki.hooks import wrap
from aqt.overview import Overview
from Card_time_forecast import getForecast
from anki.utils import fmtTimeSpan


def makeForecastStrings(mw):

    ids = mw.col.findCards('deck:current is:review -is:suspended')

    if len(ids) > 5000:
        return ''

    years = 10
    forecast_days = 365.25 * years

    total = 0
    for cid in ids:
        f = getForecast(mw, mw.col.getCard(cid), forecast_days)
        if f:
            total += f

    per_day = total / forecast_days
    if per_day > 0:
        per_day_text = u" ({0}/day)".format(fmtTimeSpan(per_day, short=True))
    else:
        per_day_text = ''
    return u"Next {0}Y: {1}".format(years, fmtTimeSpan(total, short=True), per_day_text)




def myTable(self, _old):

    oldRes = _old(self)

    gr = makeForecastStrings(self.mw)
    if gr == '':
        return oldRes
    else:
        return u"{0}<br/>{1}".format(oldRes, gr)


Overview._table = wrap(Overview._table, myTable, "around")

