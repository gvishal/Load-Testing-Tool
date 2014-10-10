""" A simple web crawler """
import gevent
from gevent import queue
import requests
import re

def crawler(q):
    while q.empty() != True:
        url = q.get_nowait()
        response = requests.get(url)
        print url
        for link in re.findall('<a href="(http.*?)"', response.content):
            q.put(link)
p = queue.Queue()
u = raw_input()
p.put(u)
greenlets = []
for i in xrange(1, 10000):
    greenlets.append(gevent.spawn(crawler, p))

gevent.joinall(greenlets)
