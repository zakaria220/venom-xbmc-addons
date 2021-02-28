# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
# Ovni-crea

import re

from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.comaddon import progress

SITE_IDENTIFIER = 'lsdb'
SITE_NAME = 'Liveset Database (bêta)'
SITE_DESC = 'liveset podcast et autre de musique électronique'

URL_MAIN = 'https://lsdb.eu'  # Pas de / car peut poser probleme

URL_SEARCH = (URL_MAIN + '/search?q=', 'showMovies')
URL_SEARCH_MISC = (URL_SEARCH[0], 'showMovies')
FUNCTION_SEARCH = 'showMovies'

NETS_NEWS =  (URL_MAIN + '/livesets', 'showMovies')
NETS_GENRES = (True, 'showGenres')
NETS_EVENTS = (URL_MAIN + '/events/index/1', 'showEvents')
NETS_SHOWS = (URL_MAIN + '/events/index/2', 'showShows')
NETS_PODCAST = (URL_MAIN + '/events/index/3', 'showPodcast')
NETS_PROMO = (URL_MAIN + '/events/index/4', 'showPromo')


def load():
    oGui = cGui()

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_NEWS[1], 'Les nouveaux liveset', 'news.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_GENRES[1], 'Les genres musicaux', 'genres.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_EVENTS[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_EVENTS[1], 'Les évènements ', 'annees.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_SHOWS[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_SHOWS[1], 'Les shows', 'replay.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_PODCAST[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_PODCAST[1], 'Les podcasts', 'replay.png', oOutputParameterHandler)

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', NETS_PROMO[0])
    oGui.addDir(SITE_IDENTIFIER, NETS_PROMO[1], 'Les promotions', 'replay.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
        sUrl = URL_SEARCH[0] + sSearchText
        showMovies(sUrl)
        oGui.setEndOfDirectory()
        return


def showGenres():
    oGui = cGui()

    liste = []
    liste.append(['Acid', URL_MAIN + '/genre/acid/'])
    liste.append(['Crossbreed', URL_MAIN + '/genre/crossbreed/'])
    liste.append(['Darkstep', URL_MAIN + '/genre/darkstep/'])
    liste.append(['Drum and bass', URL_MAIN + '/genre/drumnbass/'])
    liste.append(['Dubstep', URL_MAIN + '/genre/dubstep/'])
    liste.append(['Early hardcore', URL_MAIN + '/genre/earlyhardcore /'])
    liste.append(['Early hardstyle', URL_MAIN + '/genre/earlyhardstyle/'])
    liste.append(['Early terror', URL_MAIN + '/genre/earlyterror/'])
    liste.append(['Happy hardcore', URL_MAIN + '/genre/happyhardcore/'])
    liste.append(['Hardcore', URL_MAIN + '/genre/hardcore/'])
    liste.append(['Hardstyle', URL_MAIN + '/genre/hardstyle/'])
    liste.append(['Hardtek', URL_MAIN + '/genre/hardtek'])
    liste.append(['Industrial hardcore', URL_MAIN + '/genre/industrialhardcore/'])
    liste.append(['Jump', URL_MAIN + '/genre/jump/'])
    liste.append(['Oldschool', URL_MAIN + '/genre/oldschool/'])
    liste.append(['Speedcore', URL_MAIN + '/genre/speedcore/'])
    liste.append(['Tek', URL_MAIN + '/genre/tek/'])
    liste.append(['Terror', URL_MAIN + '/genre/terror/'])
    liste.append(['Trance', URL_MAIN + '/genre/trance/'])
    liste.append(['UK Happy hardcore', URL_MAIN + '/genre/ukhappyhardcore/'])
    liste.append(['UK Hardcore', URL_MAIN + '/genre/ukhardcore/'])
    liste.append(['Classic hardstyle', URL_MAIN + '/tag/classic-hardstyle/'])
    liste.append(['Euphoric hardstyle', URL_MAIN + '/tag/euphoric-hardstyle/'])
    liste.append(['Raw Hardstyle', URL_MAIN + '/tag/raw-hardstyle/'])

    for sTitle, sUrl in liste:

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovies(sSearch=''):
    oGui = cGui()
    if sSearch:
        sUrl = sSearch
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<a href="([^"]+)">\s*<time datetime=.+?</time>\s*<span class=".+?<i class=".+?></i>\s*([^"]+)</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult)) #Commenter ou supprimer cette ligne une fois fini

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sTitle = aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addMisc(SITE_IDENTIFIER, 'showIsdb', sTitle, 'replay.png', '', '', oOutputParameterHandler)

        progress_.VSclose(progress_)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('page=([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()


def showIsdb():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<a href="([^"]+)" class="split button expand text-left.+?> *([^<> ]+)*[.].+?<'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult)) #Commenter ou supprimer cette ligne une fois fini

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sHoster = aEntry[1].capitalize()
            sThumb = 'special://home/addons/plugin.video.tvwatch2/resources/art/replay.png'

            sTitle = ('%s [COLOR coral]%s[/COLOR]') % (sMovieTitle, sHoster)

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
            oOutputParameterHandler.addParameter('sThumb', sThumb)
            oGui.addLink(SITE_IDENTIFIER, 'showHosters', sTitle, sThumb, '', oOutputParameterHandler)

        progress_.VSclose(progress_)

        oGui.setEndOfDirectory()


def showEvents():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<i class=".+?"></i>\s* <a href="([^"]+)">\s*([^"]+)\s*</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sTitle = aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'annees.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('page=([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showEvents', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def showShows():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<i class=".+?"></i>\s* <a href="([^"]+)">\s*([^"]+)\s*</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sTitle = aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'replay.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('page=([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showShows', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def showPodcast():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<i class=".+?"></i>\s* <a href="([^"]+)">\s*([^"]+)\s*</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sTitle = aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'replay.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('page=([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showPodcast', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def showPromo():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sPattern = '<i class=".+?"></i>\s* <a href="([^"]+)">\s*([^"]+)\s*</a>'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult))

    if (aResult[0] == False):
        oGui.addText(SITE_IDENTIFIER)

    if (aResult[0] == True):
        total = len(aResult[1])
        progress_ = progress().VScreate(SITE_NAME)

        for aEntry in aResult[1]:
            progress_.VSupdate(progress_, total)
            if progress_.iscanceled():
                break

            sUrl2 = URL_MAIN + aEntry[0]
            sTitle = aEntry[1]

            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl2)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'replay.png', oOutputParameterHandler)

        progress_.VSclose(progress_)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            number = re.search('page=([0-9]+)', sNextPage).group(1)
            oGui.addNext(SITE_IDENTIFIER, 'showPromo', '[COLOR teal]Page ' + number + ' >>>[/COLOR]', oOutputParameterHandler)

        oGui.setEndOfDirectory()


def __checkForNextPage(sHtmlContent):
    oParser = cParser()
    sPattern = '<li class="active"><a href="">.+?</a></li><li><a href="([^"]+)">.+?</a>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        return URL_MAIN + aResult[1][0]

    return False


def showHosters():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()

    oParser = cParser()
    sPattern = '<br />\s*<a href="([^"]+)">.+?</a>.+?<br />'

    aResult = oParser.parse(sHtmlContent, sPattern)
    # VSlog(str(aResult))

    if (aResult[0] == True):
        for aEntry in aResult[1]:

            sHosterUrl = aEntry
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, sThumb)

    oGui.setEndOfDirectory()
