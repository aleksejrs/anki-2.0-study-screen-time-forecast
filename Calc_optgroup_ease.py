#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# Copyright: Aleksej, 2013
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from anki.hooks import wrap
from aqt.overview import Overview

def getEase(mw):
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


def grease(mw):
    """Present average ease and advice on Starting Ease configuration."""

    decks = mw.col.decks
    curDeck = decks.selected()

    if not 'conf' in decks.get(curDeck):
        # A filtered deck.
        return ''

    conf = decks.confForDid(curDeck)

    avgEase = getEase(mw)

    def thisDeckEase(self, did):
            return self.col.db.scalar("""
            select
            avg(factor) / 10.0
            from cards where did = %s and queue = 2""" % did)


    def dangerouslyOff(avg, ordinary, conf):
        # Is conf not between avg and ordinary (inclusive)?
        maxOKSEase = max(avg, ordinary)
        minOKSEase = min(avg, ordinary)
        return conf < minOKSEase or conf > maxOKSEase

    # Anki's default ease.
    ordinaryEase = 250
    # Current Starting Ease of the options group.
    groupsval = conf['new']['initialFactor'] / 10

    if avgEase:
        # The starting ease MUST be between the average ease and the default.
        confDangerouslyOff = dangerouslyOff(avgEase, ordinaryEase, groupsval)

        # Do not let an extreme average ease make the starting ease extreme:
        # new cards are new, and might be very different.  Also, the average
        # ease might be based on cards which haven't had a chance to present
        # their actual eases yet.
        targetEase = (avgEase + ordinaryEase) / 2
        targetEase = int(targetEase)
        avgEase = int(avgEase)


        if (confDangerouslyOff or
                abs(groupsval - targetEase) > 2 or
                abs(groupsval - avgEase) > 10):
            
            if avgEase == groupsval:
                avgStr = 'avg='
            else:
                avgStr = 'avg: {0}, '.format(avgEase)

            if groupsval == targetEase:
                confStr = 'conf='
            else:
                confStr = 'conf: {0}, '.format(groupsval)

            suggStr = 'sugg: {0}'.format(targetEase)
            retval = "Group's ease: {0}{1}{2}".format(avgStr, confStr, suggStr)

            if confDangerouslyOff:
                retval = "<b>{0}</b>".format(retval)
                
        else:
            retval = ''
    else:
        retval = ''

    # Is the deck's avg ease too different from the option group's startease?
    # FIXME: this seems to confuse groupsval and avgEase!
    thisEase = thisDeckEase(mw, curDeck)
    if thisEase:
        thisDangerouslyOff = dangerouslyOff(thisEase, ordinaryEase, groupsval)

        thisVsAvg = abs(avgEase - thisEase)
        if thisVsAvg > 10:
            thisRetVal = "Deck's avg ease: {0}, group's: {1}".format(int(thisEase), avgEase)

            if thisDangerouslyOff:
                thisRetVal = "<b>{0}</b>".format(thisRetVal)

            retval += '<br>' + thisRetVal

    return retval


def myTable(self, _old):

    oldRes = _old(self)

    gr = grease(self.mw)
    if gr == '':
        return oldRes
    else:
        return u"{0}<br/>{1}".format(oldRes, gr)


Overview._table = wrap(Overview._table, myTable, "around")

