import time
import json

STATS_NAME_WIDTH = 60

class RequestStatsAdditionError(Exception):
    pass


class RequestStats(object):
    def __init__(self):
        self.entries = {}
        self.errors = {}
        self.num_requests = 0
        self.num_failures = 0
        self.max_requests = None
        self.last_request_timestamp = None
        self.start_time = time.time()
    
    def get(self, name, method, jobKey):
        """
        Retrieve a StatsEntry instance by name and method
        """
        entry = self.entries.get((name, method, jobKey))
        if not entry:
            entry = StatsEntry(self, name, method)
            self.entries[(name, method, jobKey)] = entry
        return entry
    
    def aggregated_stats(self, name="Total", full_request_history=False):
        """
        Returns a StatsEntry which is an aggregate of all stats entries 
        within entries.
        """
        total = StatsEntry(self, name, method=None)
        for r in self.entries.itervalues():
            total.extend(r, full_request_history=full_request_history)
        return total
    
    def reset_all(self):
        """
        Go through all stats entries and reset them to zero
        """
        self.start_time = time.time()
        self.num_requests = 0
        self.num_failures = 0
        for r in self.entries.itervalues():
            r.reset()
    
    def clear_all(self):
        """
        Remove all stats entries and errors
        """
        self.num_requests = 0
        self.num_failures = 0
        self.entries = {}
        self.errors = {}
        self.max_requests = None
        self.last_request_timestamp = int(time.time())
        self.start_time = time.time()

class StatsEntry(object):
    """
    Represents a single stats entry (name and method)
    """
    
    name = None
    """ Name (URL) of this stats entry """
    
    method = None
    """ Method (GET, POST, PUT, etc.) """
    
    num_requests = None
    """ The number of requests made """
    
    num_failures = None
    """ Number of failed request """
    
    total_response_time = None
    """ Total sum of the response times """
    
    min_response_time = None
    """ Minimum response time """
    
    max_response_time = None
    """ Maximum response time """
    
    num_reqs_per_sec = None
    """ A {second => request_count} dict that holds the number of requests made per second """

    data_reqs_per_sec = None
    """ A {second => data} dict that holds data per second """

    json_data = None
    """ A [{'timestamp': ,'requests': 0, 'failures': 0, 'response_time': 0, 'min_response_time': 100000, 
        'max_response_time': 0, 'size': 0}] list"""
    
    response_times = None
    """
    A {response_time => count} dict that holds the response time distribution of all
    the requests.
    
    The keys (the response time in ms) are rounded to store 1, 2, ... 9, 10, 20. .. 90, 
    100, 200 .. 900, 1000, 2000 ... 9000, in order to save memory.
    
    This dict is used to calculate the median and percentile response times.
    """
    
    total_content_length = None
    """ The sum of the content length of all the requests for this entry """
    
    start_time = time.time()
    """ Time of the first request for this entry """
    
    last_request_timestamp = int(time.time())
    """ Time of the last request for this entry """
    
    def __init__(self, stats, name, method):
        self.stats = stats
        self.name = name
        self.method = method
        self.reset()
    
    def reset(self):
        self.start_time = time.time()
        self.num_requests = 0
        self.num_failures = 0
        self.total_response_time = 0
        self.response_times = {}
        self.min_response_time = 1000000
        self.max_response_time = 0
        self.last_request_timestamp = int(time.time())
        self.num_reqs_per_sec = {}
        self.data_per_sec = {}
        self.json_data = []
        self.total_content_length = 0
    
    def log(self, response_time, content_length):
        self.stats.num_requests += 1
        self.num_requests += 1

        self._log_time_of_request()
        self._log_response_time(response_time)
        self._log_data(response_time, content_length)

        # increase total content-length
        self.total_content_length += content_length

    def _log_time_of_request(self):
        t = int(time.time())
        self.num_reqs_per_sec[t] = self.num_reqs_per_sec.setdefault(t, 0) + 1
        self.last_request_timestamp = t
        self.stats.last_request_timestamp = t

    def _log_data(self, response_time = None, content_length = None, failure = False):
        """ (Timestamp,data) dictionary """
        t = int(time.time())*1000
        self.data_per_sec[t] = self.data_per_sec.setdefault(t, {'requests': 0, 'failures': 0, 'response_time': 0, 'min_response_time': 100000, 'max_response_time': 0, 'size': 0})
        self.data_per_sec[t]['requests'] = self.data_per_sec[t].setdefault('requests', 0) + 1
         
        if failure:
            self.data_per_sec[t]['failures'] = self.data_per_sec[t].setdefault('failures', 0) + 1
        else:
            self.data_per_sec[t]['size'] = content_length
            self.data_per_sec[t]['response_time'] = self.data_per_sec[t].setdefault('response_time', 0) + response_time
            self.data_per_sec[t]['min_response_time'] = min(response_time, self.data_per_sec[t]['min_response_time'])
            self.data_per_sec[t]['max_response_time'] = max(response_time, self.data_per_sec[t]['max_response_time'])

    def json_output_timeseries(self):
        """ Returns Data by timestamp, used for creating graphs """
        self.json_data  = []
        for key,value in dict(sorted(self.data_per_sec.iteritems())).items():
            value['timestamp'] = key
            value['avg_response_time'] = round(self.avg_response_time, 3)
            # value['min_requests'] = value['requests']
            # value['max_requests'] = value['requests']
            # value['min_failures'] = value['failures']
            # value['max_failures'] = value['failures']
            # value['min_size'] = value['size']
            # value['max_size'] = value['size']
            self.json_data.append(value)
        return json.dumps(self.json_data)

    def json_output_status(self):
        """ Ouputs current status """
        data = {}
        data['name'] = self.name
        data['method'] = self.method
        data['num_requests'] = self.num_requests
        data['num_failures'] = self.num_failures
        data['median_response_time'] = self.median_response_time
        data['avg_response_time'] = round(self.avg_response_time, 3)
        data['min_response_time'] = self.min_response_time
        data['max_response_time'] = self.max_response_time
        data['content_length'] = self.avg_content_length
        data['num_reqs_per_sec'] = self.current_rps
        return json.dumps(data)

    def _log_response_time(self, response_time):
        # print self.total_response_time/self.num_requests,response_time
        self.total_response_time += response_time

        if self.min_response_time is None:
            self.min_response_time = response_time

        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)

        # to avoid to much data that has to be transfered to the master node when
        # running in distributed mode, we save the response time rounded in a dict
        # so that 147 becomes 150, 3432 becomes 3400 and 58760 becomes 59000
        if response_time < 100:
            rounded_response_time = response_time
        elif response_time < 1000:
            rounded_response_time = int(round(response_time, -1))
        elif response_time < 10000:
            rounded_response_time = int(round(response_time, -2))
        else:
            rounded_response_time = int(round(response_time, -3))

        # increase request count for the rounded key in response time dict
        self.response_times.setdefault(rounded_response_time, 0)
        self.response_times[rounded_response_time] += 1

    def log_error(self, error):
        self.num_failures += 1
        self.stats.num_failures += 1
        self._log_data(failure = True)
        # key = StatsError.create_key(self.method, self.name, error)
        # entry = self.stats.errors.get(key)
        # if not entry:
        #     entry = StatsError(self.method, self.name, error)
        #     self.stats.errors[key] = entry

        # entry.occured()

    @property
    def fail_ratio(self):
        try:
            return float(self.num_failures) / (self.num_requests + self.num_failures)
        except ZeroDivisionError:
            if self.num_failures > 0:
                return 1.0
            else:
                return 0.0

    @property
    def avg_response_time(self):
        try:
            return float(self.total_response_time) / self.num_requests
        except ZeroDivisionError:
            return 0

    @property
    def median_response_time(self):
        if not self.response_times:
            return 0

        return median_from_dict(self.num_requests, self.response_times)

    @property
    def current_rps(self):
        if self.stats.last_request_timestamp is None:
            return 0
        slice_start_time = max(self.stats.last_request_timestamp - 12, int(self.stats.start_time or 0))

        reqs = [self.num_reqs_per_sec.get(t, 0) for t in range(slice_start_time, self.stats.last_request_timestamp-2)]
        return avg(reqs)

    @property
    def total_rps(self):
        if not self.stats.last_request_timestamp or not self.stats.start_time:
            return 0.0

        return self.num_requests / max(self.stats.last_request_timestamp - self.stats.start_time, 1)

    @property
    def avg_content_length(self):
        try:
            return self.total_content_length / self.num_requests
        except ZeroDivisionError:
            return 0

class StatsError(object):
    def __init__(self, method, name, error, occurences=0):
        self.method = method
        self.name = name
        self.error = error
        self.occurences = occurences

    @classmethod
    def create_key(cls, method, name, error):
        key = "%s.%s.%r" % (method, name, error)
        return hashlib.md5(key).hexdigest()

    def occured(self):
        self.occurences += 1

    def to_name(self):
        return "%s %s: %r" % (self.method, 
            self.name, repr(self.error))

    def to_dict(self):
        return {
            "method": self.method,
            "name": self.name,
            "error": repr(self.error),
            "occurences": self.occurences
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["method"], 
            data["name"], 
            data["error"], 
            data["occurences"]
        )


def avg(values):
    return sum(values, 0.0) / max(len(values), 1)

def median_from_dict(total, count):
    """
    total is the number of requests made
    count is a dict {response_time: count}
    """
    pos = (total - 1) / 2
    for k in sorted(count.iterkeys()):
        if pos < count[k]:
            return k
        pos -= count[k]

global_stats = RequestStats()

def on_request_success(request_type, name, response_time, response_length, jobKey):
    global_stats.get(name, request_type, jobKey).log(response_time, response_length)

def on_request_failure(request_type, name, response_time, jobKey, exception='Error'):
    global_stats.get(name, request_type, jobKey).log_error(exception)
