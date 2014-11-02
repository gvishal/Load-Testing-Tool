#! /usr/bin/env python
""" This is a simple program which makes use of a task queue from which various workers take tasks and complete item
    Author: Vishal Gupta
"""
import time
import gevent
from gevent import queue
import requests

start = time.time()
tic = lambda: '%1.5f seconds' % (time.time() - start)


def do_work(item):
#   gevent.sleep(0.2)
    print time.mktime(time.localtime())
    requests.get('http://localhost:8080')
    pass

def worker():
    while True:
        item = task_queue.get()
        try:
       #     print 'ok'
            do_work(item)
        finally:
            task_queue.task_done()


task_queue = gevent.queue.JoinableQueue()

num_worker_threads = 1000
num_tasks = 10000
start = time.time()

for i in xrange(num_worker_threads):
    x = gevent.spawn(worker)

#print 'Time taken to spawn %s workers' % num_worker_threads, tic()

for item in xrange(num_tasks):
    task_queue.put(item)

start = time.time()

task_queue.join()  # block until all tasks are done

#print 'Time taken for %s tasks ' % num_tasks, tic()

