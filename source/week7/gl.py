"""Finding maximum concurrency CodedBy: Pooja Shamili G"""
import gevent
from gevent import pool
import requests
import time
import sys

POOL_P = pool.Pool(300)
COUNT_NUM = 10
GREEN_LETS = []
START_TIME = time.localtime()
S_TIME = time.mktime(START_TIME)
sys.stdout = open('out.txt', 'w')
def web_info():
    """Worker Function"""
    t_m = time.localtime()
    t_1 = time.mktime(t_m)
    t_1 = t_1 - S_TIME
    requests.get(sys.argv[1])
for i in xrange(300):
    GREEN_LETS.append(POOL_P.spawn(web_info))
gevent.joinall(GREEN_LETS)
