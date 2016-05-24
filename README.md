# Show Scraper

## About

showScraper is a simple scraper that downloads all episodes from any season of a TV series. Video
streams are sourced from [AllMyVideos.net](http://allmyvideos.net/v/) streams hosted on
[Couchtuner](http://www.couchtuner.ag/).


## Installation

For this program you will need to
[install](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) the Python module BeautifulSoup. You can do easily by
running the following command:

```
$ sudo apt-get install python-bs4
```

or

```
$ sudo pip install beautifulsoup4
```

If you don’t have the system package manager or `pip` installed, you can download the [Beautiful Soup 4 source
tarball](https://www.crummy.com/software/BeautifulSoup/bs4/download/4.0/)
and install it with `setup.py`.

```
$ python setup.py install
```

## Running

To run the program, simply run

```
python scrape.py
```

Enter the name of the show (capitalization as it occurs on
[Couchtuner](http://www.couchtuner.ag/tv-lists/)) and the season whose episodes you wish to download, and you're good to
go!
