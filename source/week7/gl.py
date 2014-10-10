#import gevent.monkey
#gevent.monkey.patch_all()

import gevent
from gevent import pool
import requests
import time
import sys

pools = pool.Pool(300)
count = 10
greenlets = []
start = time.localtime()
s = time.mktime(start)
avg = 0
sys.stdout = open('out.txt','w');
def WebInfo(i):
	global avg
#	global prev
#global t
	tm = time.localtime()
	t1 = time.mktime(tm)
	t1 = t1 - s
	r = requests.get(sys.argv[1])
	tm = time.localtime()
#prev = t
	t = time.mktime(tm)
	t = t - s
#	t = t - prev
#       avg = avg + t
        avg = t
#	print avg
	print t - t1
#	print r.url

for i in xrange(300):
	global avg
	greenlets.append(pools.spawn(WebInfo, i))
#	gevent.sleep(1)

gevent.joinall(greenlets)
avg = avg/200
print avg
