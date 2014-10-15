"""To read urls (testing performance of I/O bound task"""
"""By : Kavya"""

from multiprocessing import Pool

import time
import urllib2

def millis():
    """gives the number of milliseconds"""
    return int(round(time.time() * 1000))

def http_gets(url):
    """ Reads the  html page and returns time taken to respond"""
    start_time = millis()
    result = {"url": url, "data": urllib2.urlopen(url, timeout=10).read()[:100]}
    print url + " took " + str(millis() - start_time) + " ms"
    return result

URLS_LIST = ['http://www.google.com/', 'https://www.quora.com/', 'http://www.bing.com/', "https://www.facebook.com/"]
URLS_LIST = URLS_LIST * 10
POOL = Pool(processes=5)

START_TIME = millis()
RESULTS = POOL.map(http_gets, URLS_LIST)
print "\nTotal took " + str(millis() - START_TIME) + " ms\n"

#for iterator in results:
#    print iterator
