"""Implementing gevent CodedBy: Pooja Shamili Ganti"""

import gevent
from gevent import queue
import time

START_TIME = time.time()
class RandomClass:
    """Random Class"""
    def __init__(self, q_queue):
        """Init function"""
        self.q_queue = q_queue
        self.greenlets = []
        self.s_s = 0

    def worker(self):
        """Worker function"""
        while self.q_queue.empty() != True:
            l_data = self.q_queue.get_nowait()
            gevent.sleep()
            self.s_s += l_data

    def insert(self, n_num):
        """Insert function"""
        for j in xrange(n_num):
            self.q_queue.put(j*j)
R_QUEUE = queue.Queue()
P_INST = RandomClass(R_QUEUE)
P_INST.insert(100000)
for i in xrange(10000):
    P_INST.greenlets.append(gevent.spawn(P_INST.worker))
gevent.joinall(P_INST.greenlets)

print P_INST.s_s
