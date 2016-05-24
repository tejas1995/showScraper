from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
import urllib
import re
import sys

# Print title
title = 'Show Scraper'
print title.center(100, ' ')
print '----------------------------------------------------------------------------------------------\n'

# Set base URLs
SITE_URL = "http://www.couchtuner.ag"
LIST_URL = "http://www.couchtuner.ag/tv-lists"
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'


def makeSoup(url):
    '''
    Make soup for a given URL
    '''
    hdr = {'User-Agent': user_agent,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
    req = Request(url, headers=hdr)
    html = urlopen(req).read()
    soup = BeautifulSoup(html, "lxml")
    return soup


def getSeries(listUrl):
    '''
    Get the series name from user
    Returns URL of series's season listing
    '''
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
    '''
    Get the season number from user
    Returns list of episode URLs & names
    '''
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
    '''
    Given an episode URL and text
    Download the video from AllMyV/AllMyVid
    '''
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
    response = urlopen(vidDlUrl)
    CHUNK = 1024 * 1024
    file_size_dl = 0
    meta = response.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Total Bytes:", file_size

    with open(filename, 'wb') as f:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            file_size_dl += len(chunk)
            f.write(chunk)
            percent = file_size_dl*100/file_size
            sys.stdout.write("Downloading " + epText + " ... %d%%" % percent)
            sys.stdout.write("\tDownloaded bytes: " + str(file_size_dl))
            sys.stdout.flush()
            print '\r',
        # urllib.urlretrieve(vidDlUrl, filename, reporthook=dlProgress)
    print
    return


srsUrl = SITE_URL + getSeries(LIST_URL) # Get series URL
episodeList = getEpisodeList(srsUrl)[::-1] # Reverse episode listing to go from 1-n
print
for ep in episodeList:
    getEpisodeVideo(ep) # Get the video for episode ep

print 'Download completed!\n\n'
