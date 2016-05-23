from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
import urllib
import re
import sys

title = 'Show Scraper'
print title.center(100, ' ')
print
'----------------------------------------------------------------------------------------------\n'

SITE_URL = "http://www.couchtuner.ag"
LIST_URL = "http://www.couchtuner.ag/tv-lists"
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

regex = re.compile('\n^(.*?):(.*?)$|,', re.MULTILINE)

def makeSoup(url):

    hdr = {'User-Agent': user_agent,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
    req = Request(url, headers=hdr)
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "lxml")
    return soup


def getSeries(listUrl):

    soup = makeSoup(listUrl)
    foundSeries = False
    while foundSeries is False:
        seriesName = raw_input("Enter the name of TV series: ")
        seriesUrl = soup.find("a", string=seriesName)

        if(seriesUrl is None):
            print "---------------------\n"
            print "TV series not found! Please try again (check capitalization)"
        else:
            foundSeries = True
            url = seriesUrl['href']
            return url


def getEpisodeList(seriesUrl):

    soup = makeSoup(seriesUrl)
    foundSeason = False
    while foundSeason is False:
        seasonNum = raw_input ("Enter the Season No. (e.g. 1): ")
        seasonName = "Season " + seasonNum
        seasonNameLbl = soup.find("p", string=seasonName)
        if seasonNameLbl is None:
            print "-------------------\n"
            print "Season not found! Please try again"
        else:
            foundSeason = True
            seasonEpList = seasonNameLbl.find_next("ul").find_all("li")
            epList = []
            for ep in seasonEpList:
                newUrl = ep.find('a')['href']
                epDict = {}
                epDict['url'] = newUrl
                epDict['text'] = ep.find('a').string
                epList.append(epDict)
            return epList


def getEpisodeVideo(ep):

    epUrl = ep['url']
    epText = ep['text']

    soup = makeSoup(epUrl)
    epLinkUrl = soup.find('a', string=epText)

    if epLinkUrl is None:
        newSoup = soup
    else:
        newSoup = makeSoup(epLinkUrl['href'])

    spanAMV = newSoup.find("span", "postTabs_titles", string="AllMyV")
    if spanAMV is None:
        spanAMV = newSoup.find("span", "postTabs_titles", string="AllMyVid")
        if spanAMV is None:
            print "AllMyVid link not found for", epText
            return
    iFrameUrl = spanAMV.find_next("iframe")['src']

    vidSoup = makeSoup(iFrameUrl)
    foundVidUrl = False
    scriptList = vidSoup.find_all('script')

    for script in scriptList:
        listVidUrl = re.findall(r'"http://.*\.mp4.*"', script.text)
        if len(listVidUrl) != 0:
            foundVidUrl = True
            listVidUrl = [url[1:-1] for url in listVidUrl]
            break
    if foundVidUrl is False:
        print "Video link not found for " + epText + '\n'
        return


    def dlProgress(count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)
        sys.stdout.write("\rDownloading " + epText + " ... %d%%" % percent)
        sys.stdout.flush()


    vidDlUrl = listVidUrl[-1]
    filename = epText + '.mp4'
    with open(filename, 'wb') as f:
        urllib.urlretrieve(vidDlUrl, filename, reporthook=dlProgress)
    print
    return


srsUrl = SITE_URL + getSeries(LIST_URL)
episodeList = getEpisodeList(srsUrl)[::-1]
print
for ep in episodeList:
    getEpisodeVideo(ep)   
