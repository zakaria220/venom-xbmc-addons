# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
# Arias800
import re
import requests
import string
import json
import resources.sites.freebox


from resources.lib.comaddon import addon
from resources.lib.epg import cePg
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.util import cUtil

from resources.lib.util import Quote
from datetime import datetime, timedelta

SITE_IDENTIFIER = 'channelstream'
SITE_NAME = 'Channel Stream'
SITE_DESC = 'iptv'

URL_MAIN = 'https://channelstream.me'

TV_FRENCH = (URL_MAIN + "/chaine-tv.php", 'showMovies')

UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'


def load():
    oGui = cGui()

    liste = []
    liste.append(['Généralistes', 'Chaîne de télévision généraliste', 'tv.png'])
    liste.append(['Cinéma', 'Chaîne consacrée aux Film', 'films.png'])
    liste.append(['Sport', 'Chaîne Sportive', 'sport.png'])
    liste.append(['Science et Nature', 'Chaîne axés sur les sciences', 'buzz.png'])


    for sTitle, sFiltre, sIcon in liste:
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', TV_FRENCH[0])
        oOutputParameterHandler.addParameter('sFiltre', sFiltre)
        oGui.addDir(SITE_IDENTIFIER, TV_FRENCH[1], sTitle, sIcon, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showMovies():
    oGui = cGui()
    oParser = cParser()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sFiltre = oInputParameterHandler.getValue('sFiltre')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    sHtmlContent = oParser.abParse(sHtmlContent, sFiltre, '<!-- Type Chaîne -->')
    sPattern = 'location.href = \'\.(.+?)\'.+?src=\'(.+?)\'.+?<div align="center">(.+?)</div>'

    aResult = oParser.parse(sHtmlContent, sPattern)

    EPG = cePg().get_epg('', 'direct')

    if (aResult[0] == True):
        for aEntry in aResult[1]:
            if not "+18" in str(aEntry[2]):
                sTitle = aEntry[2]
                
                if 'Canal + Série' in sTitle:
                    sTitle = 'Canal + Séries'
                
                sUrl2 = URL_MAIN + aEntry[0]
                sThumb = URL_MAIN + '/' + aEntry[1]

                sDesc = getEPG(EPG, sTitle)

                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl2)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumb', sThumb)

                oGui.addMisc(SITE_IDENTIFIER, 'showHoster', sTitle, sThumb, sThumb, sDesc, oOutputParameterHandler)

    oGui.setEndOfDirectory()


def showHoster():
    oGui = cGui()
    oParser = cParser()

    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumb = oInputParameterHandler.getValue('sThumb')

    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    info = cePg().getChannelEpg(sTitle)
    sDesc = info['plot']

    sMovieTitle = info['title']
    if not sMovieTitle:
        sMovieTitle = sTitle

    sMeta = 0
    sCat = info['media_type']
    if sCat:
        if 'Film' in sCat : sMeta = 1
        if 'Série' in sCat : sMeta = 2
    sYear = info['year']
    coverUrl = info['cover_url']
    if coverUrl :
        sThumb = coverUrl

    # Double Iframe a passer.
    sPattern = '<iframe.+?src="([^"]+)"'
    iframeURL = oParser.parse(sHtmlContent, sPattern)[1][0]

    oRequestHandler = cRequestHandler(iframeURL)
    sHtmlContent = oRequestHandler.request()

    sPattern = '<iframe.+?src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    
    if not aResult[1]:    # Pas de flux
        oGui.setEndOfDirectory()
        return
    
    iframeURL1 = aResult[1][0]
    sHosterUrl = iframeURL1

    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('sMovieTitle', sMovieTitle)
    oOutputParameterHandler.addParameter('sThumbnail', sThumb)
    oOutputParameterHandler.addParameter('sYear', sYear)
    oOutputParameterHandler.addParameter('sDesc', sDesc)

    oGuiElement = cGuiElement()
    oGuiElement.setTitle(sMovieTitle)
    oGuiElement.setDescription(sDesc)
    oGuiElement.setFileName(sMovieTitle)
    oGuiElement.setSiteName(resources.sites.freebox.SITE_IDENTIFIER)
    oGuiElement.setFunction('play__')
    oGuiElement.setIcon('tv.png')
    oGuiElement.setMeta(sMeta)
    oGuiElement.setThumbnail(sThumb)
    oGuiElement.setDirectTvFanart()
    oGuiElement.setCat(sMeta)

#     oGui.CreateSimpleMenu(oGuiElement, oOutputParameterHandler, resources.sites.freebox.SITE_IDENTIFIER, SITE_IDENTIFIER, 'direct_epg', 'Guide tv Direct')
#     oGui.CreateSimpleMenu(oGuiElement, oOutputParameterHandler, resources.sites.freebox.SITE_IDENTIFIER, SITE_IDENTIFIER, 'soir_epg', 'Guide tv Soir')
    if addon().getSetting('enregistrement_activer') == 'true':
        oGui.CreateSimpleMenu(oGuiElement, oOutputParameterHandler, resources.sites.freebox.SITE_IDENTIFIER, SITE_IDENTIFIER, 'enregistrement', 'Enregistrement')
    
    # Menu pour les films
    if sMeta == 1 :
        oGui.createContexMenuinfo(oGuiElement, oOutputParameterHandler)
        oGui.createContexMenuba(oGuiElement, oOutputParameterHandler)
        oGui.createContexMenuSimil(oGuiElement, oOutputParameterHandler)
        oGui.createContexMenuWatch(oGuiElement, oOutputParameterHandler)

    if 'dailymotion' in sHosterUrl:
        oOutputParameterHandler.addParameter('sHosterIdentifier', 'dailymotion')
        oOutputParameterHandler.addParameter('sMediaUrl', sHosterUrl)
        oOutputParameterHandler.addParameter('siteUrl', sHosterUrl)
        oOutputParameterHandler.addParameter('sFileName', sMovieTitle)
        oGuiElement.setFunction('play')
        oGuiElement.setSiteName('cHosterGui')
        oGui.addHost(oGuiElement, oOutputParameterHandler)
        cGui.CONTENT = 'movies'
        oGui.setEndOfDirectory()
        return


    oRequestHandler = cRequestHandler(iframeURL1)
    oRequestHandler.addHeaderEntry('User-Agent', UA)
    oRequestHandler.addHeaderEntry('Referer', iframeURL)
    sHtmlContent2 = oRequestHandler.request()

    sPattern2 = 'var\s+cid[^\'"]+[\'"]{1}([0-9]+)'
    aResult = re.findall(sPattern2, sHtmlContent2)

    if aResult:
        str2 = aResult[0]
        datetoken = int(getTimer()) * 1000
        
        jsonUrl = 'https://telerium.tv/streams/'+str2+'/'+str(datetoken)+'.json'
        tokens = getRealTokenJson(jsonUrl,iframeURL1)
        m3url = tokens['url']
        nxturl = 'https://telerium.tv' + tokens['tokenurl']
        
        realtoken = getRealTokenJson(nxturl, iframeURL1)[10][::-1]
    
        try:
            m3url = m3url.decode("utf-8")
        except:
            pass
    
        sHosterUrl = 'https:' + m3url + realtoken
        sHosterUrl += '|User-Agent=' + UA + '&Referer=' + Quote(iframeURL1) + '&Sec-Fetch-Mode=cors&Origin=https://telerium.tv'


    oOutputParameterHandler.addParameter('siteUrl', sHosterUrl)
    oGui.addFolder(oGuiElement, oOutputParameterHandler)

    cGui.CONTENT = 'movies'
    oGui.setEndOfDirectory()


def getRealTokenJson(link, referer):
#     cookies = {'ChorreameLaJa': '100',
#                'setVolumeSize': '100',
#                'NoldoTres': '100'}

    cookies = {'elVolumen': '100',
               '__ga':'100'}

    headers = {'Host': 'telerium.tv',
               'User-Agent': UA,
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
               'X-Requested-With': 'XMLHttpRequest',
               'Referer': referer}

    realResp = requests.get(link, headers=headers, cookies=cookies, verify=False).content  # [1:-1]

    return json.loads(realResp)

def getTimer():
    datenow = datetime.utcnow().replace(second=0, microsecond=0)
    datenow = datenow + timedelta(days=1)
    epoch = datetime(1970, 1, 1)
        
    return (datenow - epoch).total_seconds() // 1
    
def getEPG(EPG, sTitle):

    oParser = cParser()

    sTitle = sTitle.replace('+', 'plus')
    sTitle = cUtil().CleanName(sTitle)
    sTitle = re.sub('[^%s]' % (string.ascii_lowercase + string.digits), '', sTitle.lower())
    
    sPattern = '(.+?)\/>(.+?)<'
    aResult = oParser.parse(EPG, sPattern)
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sChannel = aEntry[0]
            
            sChannel = re.sub('[^%s]' % (string.ascii_lowercase + string.digits), '', sChannel.lower())
            if sChannel == sTitle:
                sDesc = aEntry[1].replace('[COLOR khaki]', '\r\n\t[COLOR khaki]')
                sDesc = sDesc.replace('[/COLOR]', '[/COLOR]\r\n')
                return sDesc

    return ''


