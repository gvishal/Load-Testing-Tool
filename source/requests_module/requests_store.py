#! /usr/bin/env python

import time
import gevent
from gevent import queue

import requests
from requests import Response, Request

import requests_stats
from datetime import timedelta

from requests.exceptions import (RequestException, MissingSchema,
    InvalidSchema, InvalidURL)

start = time.time()
tic = lambda: '%1.5f seconds' % (time.time() - start)

class LocustResponse(Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        Response.raise_for_status(self)


class Start:
    """ Usage:  import requests_store
                a = requests_store.Start(url, num_worker, num_tasks)
        It will start some fixed number workers who will do some fixed
        no of tasks.After finishing they will stats
    """
    def __init__(self, url='http://localhost:8080', num_worker = 10, num_tasks = 100):
        self.task_queue = gevent.queue.JoinableQueue()
        self.url = url
        self.num_worker = num_worker
        self.num_tasks = num_tasks
        start = time.time()

        """ Methods called in init for now.Should require explicit call 
            and hence removed from here.
        """
        self.spawn_workers()

        self.add_to_queue()

        start = time.time()

        self.task_queue.join()  # block until all tasks are done

        self.print_results()

    def spawn_workers(self):
        for i in xrange(self.num_worker):
            x = gevent.spawn(self.worker)

    def add_to_queue(self):
        for item in xrange(self.num_tasks):
            self.task_queue.put(item)

    def print_results(self):
        """Important stats are printed here"""

        print "Num Workers: %s \nNumtasks: %s" %(self.num_worker, self.num_tasks)
        print "Total requests saved: %s" %requests_stats.global_stats.num_requests
        print "Total requests failed: %s" %requests_stats.global_stats.num_failures
        print requests_stats.global_stats.entries

        print 'Time taken for %s tasks ' % self.num_tasks, tic()
        # print 'Min Response Time %s' % requests_stats.global_stats.get('GET', '/').min_response_time

    def do_work(self,item):
        """This method defines the task that the workers have to do."""
        self.request('GET', self.url)
        # try:
        #     r = requests.get(self.url)
        #     if r.status_code == 200:
        #         requests_stats.on_request_success(r.request.method, '/', timedelta.total_seconds(r.elapsed)*1000, len(r.content))
        # except (MissingSchema, InvalidSchema, InvalidURL):
        #     raise
        # except RequestException as e:
        #     requests_stats.on_request_failure('GET', '/', e)

    def worker(self):
        """Each worker picks a task from task_queue and completes it."""

        while True:
            item = self.task_queue.get()
            try:
                self.do_work(item)
            finally:
                self.task_queue.task_done()

    def request(self, method, url, name = None, **kwargs):
        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {}
        
        # # set up pre_request hook for attaching meta data to the request object
        # request_meta["start_time"] = time.time()
        
        response = self._send_request_safe_mode(method, url, **kwargs)
        
        # record the consumed time
        request_meta["response_time"] = timedelta.total_seconds(response.elapsed) or 0
        
        request_meta["request_type"] = response.request.method
        request_meta["name"] = name or (response.history and response.history[0] or response).request.path_url

        try:
            response.raise_for_status()
        except RequestException as e:
            request_meta['exception'] = e
            requests_stats.on_request_failure(**request_meta)
        else:
            request_meta["response_length"] = len(response.content or "")
            requests_stats.on_request_success(**request_meta)

    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to connection problems.
        
        Safe mode has been removed from requests 1.x.
        """
        try:
            return requests.request(method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as e:
            r = LocustResponse()
            r.error = e
            r.status_code = 0  # with this status_code, content returns None
            r.request = Request(method, url).prepare() 
            return r
