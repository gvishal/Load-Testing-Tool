""" A simple web crawler CodedBy: Pooja Shamili G"""
import gevent
from gevent import queue
import requests
import re

def crawler(q_queue):
    """The actual crawler using gevent"""
    while q_queue.empty() != True:
        url = q_queue.get_nowait()
        response = requests.get(url)
        print url
        for link in re.findall('<a href="(http.*?)"', response.content):
            q_queue.put(link)
P_QUEUE = queue.Queue()
U_INP = raw_input()
P_QUEUE.put(U_INP)
GREEN_LETS = []
for i in xrange(1, 10000):
    GREEN_LETS.append(gevent.spawn(crawler, P_QUEUE))

gevent.joinall(GREEN_LETS)
