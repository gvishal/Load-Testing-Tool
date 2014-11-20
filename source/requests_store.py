#! /usr/bin/env python

import time
import signal

import gevent
from gevent import queue, monkey
from gevent.pool import Group

monkey.patch_all(thread=False)

import requests
from requests import Response, Request
import json

import requests_stats
from requests_stats import global_stats
from datetime import timedelta

from requests.exceptions import (RequestException, MissingSchema,
    InvalidSchema, InvalidURL)

start_time = time.time()
tic = lambda: '%1.5f seconds' % (time.time() - start_time)

STATE_INIT, STATE_HATCHING, STATE_RUNNING, STATE_STOPPED, STATE_FINISHED = ["ready", "hatching", "running", "stopped", "finished"]

class LocustResponse(Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        Response.raise_for_status(self)


class Task:
    """ Usage:  import requests_store
                a = requests_store.Start(url, num_worker, num_tasks)
        It will start some fixed number workers who will do some fixed
        no of tasks.After finishing they will stats
    """
    def __init__(self, url='http://localhost:8080', num_worker = 10, num_tasks = 100, jobKey=None):
        self.task_queue = gevent.queue.JoinableQueue()
        
        self.greenlet = Group()
        self._status = STATE_INIT
        self.url = url
        self.num_worker = num_worker
        self.num_tasks = num_tasks
        self.jobKey = jobKey
        self.spawn_workers()

        self.add_to_queue()

        self._status = STATE_HATCHING

    def status():
        doc = "The status property."
        def fget(self):
            return self._status
        def fset(self, value):
            self._status = value
        def fdel(self):
            del self._status
        return locals()
    status = property(**status())

    def start(self, masterUrl, masterPort, slavePort, jobKey):
        """Call object.start to start spawning"""
        start_time = time.time()
        self._status = STATE_RUNNING
        self.task_queue.join()  # block until all tasks are done
        self._status = STATE_FINISHED
        final_report = {}
        final_report["summary"] = json.loads(self.json_output_status(jobKey))
        final_report["time_series"] = json.loads(self.json_output_timeseries(jobKey))
        final_report["time_stamp"] = json.loads(self.json_output_timestamp(jobKey))
        final_report["job_status"] = self.status
        final_report["port"] = slavePort
        final_report['jobKey'] = jobKey
        requests.post("http://" + masterUrl + ":" + masterPort + "/jobresult", data = json.dumps(final_report))  

    def stop(self):
        """ Set self.work False so that condition in worker becomes false."""
        self.greenlet.kill()
        self._status = STATE_STOPPED

    def spawn_workers(self):
        for i in xrange(self.num_worker):
            self.greenlet.spawn(self.worker)

    def add_to_queue(self):
        for item in xrange(self.num_tasks):
            self.task_queue.put(item)

    def print_results(self):
        """Important stats are printed here"""

        # print "Num Workers: %s \nNumtasks: %s" %(self.num_worker, self.num_tasks)
        # print "Total requests saved: %s" %requests_stats.global_stats.num_requests
        # print "Total requests failed: %s" %requests_stats.global_stats.num_failures
        # print requests_stats.global_stats.entries

        # print 'Time taken for %s tasks ' % self.num_tasks, tic()

        # for key in requests_stats.global_stats.get('/', 'GET').__dict__.keys():
        #     print '%s: %s' % (key,requests_stats.global_stats.get('/', 'GET').__dict__[key])

        # print 'data_per_sec: %s' % requests_stats.global_stats.get('/', 'GET').data_per_sec
        # print requests_stats.global_stats.get('/', 'GET').json_output_timeseries()
        # print requests_stats.global_stats.get('/', 'GET').json_output_status()
        # print 'Median Response Time: %s' % requests_stats.global_stats.get('/', 'GET').median_response_time

    def json_output_timeseries(self, jobKey):
        return requests_stats.global_stats.get('/', 'GET', jobKey).json_output_timeseries()

    def json_output_timestamp(self, jobKey):
        return json.dumps(requests_stats.global_stats.get('/', 'GET', jobKey).data_per_sec)

    def json_output_status(self, jobKey):
        return requests_stats.global_stats.get('/', 'GET', jobKey).json_output_status()

    def reset_stats(self):
        """ Resets all stats """
        requests_stats.global_stats.get('/', 'GET').reset()

    def do_work(self,item):
        """This method defines the task that the workers have to do."""
        self.request('GET', self.url)
        # gevent.sleep(1)
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
        request_meta = {"jobKey" : self.jobKey}
        
        # # set up pre_request hook for attaching meta data to the request object
        # request_meta["start_time"] = time.time()
        # gevent.sleep(1)
        print method, url
        
        response = self._send_request_safe_mode(method, url, **kwargs)

        # record the consumed time in milliseconds
        request_meta["response_time"] = round(timedelta.total_seconds(response.elapsed)*1000,3) or 0
        
        request_meta["request_type"] = response.request.method
        # request_meta["name"] = name or (response.history and response.history[0] or response).request.path_url
        request_meta["name"] = '/'
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
