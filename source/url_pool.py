from multiprocessing import Process, Pool
import time
import urllib2
 
def millis():
    return int(round(time.time() * 1000))	
	
def http_gets(url):
    start_time = millis()
    result = {"url": url, "data": urllib2.urlopen(url, timeout=10).read()[:100]}
    print url + " took " + str(millis() - start_time) + " ms"
    return result

urls = ['http://www.google.com/', 'https://www.quora.com/', 'http://www.bing.com/', "https://www.facebook.com/"]
urls = urls * 10
pool = Pool(processes=5)
	 
start_time = millis()
results = pool.map(http_gets, urls)
	 
print "\nTotal took " + str(millis() - start_time) + " ms\n"
	 
for result in results:
    print result
	
