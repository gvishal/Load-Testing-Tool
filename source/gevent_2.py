"""Implementing gevent"""

import gevent
from gevent import queue

class Random():
    def __init__(self, q):
        self.q = q
        self.greenlets = []
        self.s = 0

    def worker(self):
        while self.q.empty() != True:
            l = self.q.get_nowait()
            gevent.sleep()
            self.s += l

    def insert(self, n):
        for i in xrange(n):
            self.q.put(i*i)

r = queue.Queue()
p = Random(r)
p.insert(100000)

for i in xrange(10000):
    p.greenlets.append(gevent.spawn(p.worker))
gevent.joinall(p.greenlets)

print p.s
