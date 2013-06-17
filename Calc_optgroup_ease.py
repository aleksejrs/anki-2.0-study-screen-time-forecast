#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Copyright: Aleksej, 2013
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from anki.hooks import wrap
from aqt.overview import Overview
from Card_time_forecast import getForecast
from anki.utils import fmtTimeSpan


def getThisGroupsEase(mw):
    """Get the average ease for the decks in this options group."""
    def _factor(self, idstr):
            return self.col.db.scalar("""
            select
            avg(factor) / 10.0
            from cards where did in %s and queue = 2""" % idstr)

    decks = mw.col.decks
    curDeck = decks.selected()
    conf = decks.confForDid(curDeck)
    from anki.utils import ids2str
    dids = decks.didsForConf(conf)
    return _factor(mw, ids2str(dids))


def makeEaseWarnerStrings(mw):
    """Present average ease and advice on Starting Ease configuration."""

    decks = mw.col.decks
    curDeck = decks.selected()

    if not 'conf' in decks.get(curDeck):
        # A filtered deck.
        return ''

    conf = decks.confForDid(curDeck)

    avgGrEase = getThisGroupsEase(mw)

    def getThisDeckEase(self, did):
            return self.col.db.scalar("""
            select
            avg(factor) / 10.0
            from cards where did = %s and queue = 2""" % did)


    def isDangerouslyOff(avg, ordinary, conf):
        # Is conf not between avg and ordinary (inclusive)?
        maxOKSEase = max(avg, ordinary)
        minOKSEase = min(avg, ordinary)
        return conf < minOKSEase or conf > maxOKSEase

    # Anki's default ease.
    ordinaryEase = 250
    # Current Starting Ease of the options group.
    grStartEase = conf['new']['initialFactor'] / 10

    if avgGrEase:
        # The starting ease MUST be between the average ease and the default.
        confDangerouslyOff = isDangerouslyOff(
                avgGrEase, ordinaryEase, grStartEase)

        # Do not let an extreme average ease make the starting ease extreme:
        # new cards are new, and might be very different.  Also, the average
        # ease might be based on cards which haven't had a chance to present
        # their actual eases yet.
        targetEase = (avgGrEase + ordinaryEase) / 2
        targetEase = int(targetEase)
        avgGrEase = int(avgGrEase)


        if (confDangerouslyOff or
                abs(grStartEase - targetEase) > 2 or
                abs(grStartEase - avgGrEase) > 10):
            
            if avgGrEase == grStartEase:
                avgStr = 'avg='
            else:
                avgStr = 'avg: {0}, '.format(avgGrEase)

            if grStartEase == targetEase:
                confStr = 'conf='
            else:
                confStr = 'conf: {0}, '.format(grStartEase)

            suggStr = 'sugg: {0}'.format(targetEase)
            retval = "Group's ease: {0}{1}{2}".format(avgStr, confStr, suggStr)

            if confDangerouslyOff:
                retval = "<b>{0}</b>".format(retval)
                
        else:
            retval = ''
    else:
        retval = ''


    thisDeckEase = getThisDeckEase(mw, curDeck)
    if thisDeckEase:

        thisVsAvg = abs(avgGrEase - thisDeckEase)
        if thisVsAvg > 10:
            thisRetVal = "Deck's avg ease: {0}, group's: {1}".format(
                    int(thisDeckEase), avgGrEase)

            # Is the deck's average ease too different from the option group's
            # Starting Ease (which is supposed to be based on the suggestion
            # of the above code)?  Then it may need a different options group.
            if isDangerouslyOff(thisDeckEase, ordinaryEase, grStartEase):
                thisRetVal = "<b>{0}</b>".format(thisRetVal)

            retval += '<br>' + thisRetVal

    return retval


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

    gr = makeEaseWarnerStrings(self.mw) + "<br />" + makeForecastStrings(self.mw)
    if gr == '':
        return oldRes
    else:
        return u"{0}<br/>{1}".format(oldRes, gr)


Overview._table = wrap(Overview._table, myTable, "around")

