import requests_store
import sys

try:
    num_worker = int(sys.argv[2])
    num_tasks = int(sys.argv[3])
    url = sys.argv[1]
except:
    num_worker = 10
    num_tasks = 100
    url = 'http://localhost:8080'

a = requests_store.Task(url, num_worker = num_worker, num_tasks = num_tasks)
# print "Status: %s" % a.status
a.start()
# print "Status: %s" % a.status
print a.json_output_status()
print a.json_output_timeseries()
# a.stop()
# print "Status: %s" % a.status
