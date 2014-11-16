#! /usr/bin/env python
""" This is a simple program which makes use of a task queue from which
    various workers take tasks and complete them.
    Author: Vishal Gupta
"""
import time
import gevent

START = time.time()
TIC = lambda: '%1.5f seconds' % (time.time() - START)

def do_work(item):
    """ Duh!!!"""
    item = 0
    gevent.sleep(0.2)

def worker():
    """ Worker to work"""
    while True:
        item = TASK_QUEUE.get()
        try:
            do_work(item)
        finally:
            TASK_QUEUE.task_done()


TASK_QUEUE = gevent.queue.JoinableQueue()

NUM_WORKER_THREADS = 1000
NUM_TASKS = 10000

START = time.time()

for i in xrange(NUM_WORKER_THREADS):
    X = gevent.spawn(worker)

print 'Time taken to spawn %s workers' % NUM_WORKER_THREADS, TIC()

for i in xrange(NUM_TASKS):
    TASK_QUEUE.put(i)

START = time.time()

TASK_QUEUE.join()  # block until all tasks are done

print 'Time taken for %s tasks ' % NUM_TASKS, TIC()

# prevent the process from exiting so we can check its usage
X = raw_input("Enter to exit")
