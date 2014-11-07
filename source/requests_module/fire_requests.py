import requests_store
import sys

try:
    num_worker = int(sys.argv[1])
    num_tasks = int(sys.argv[2])
except:
    num_worker = 10
    num_tasks = 100

a = requests_store.Start(url='http://localhost:8080', num_worker = num_worker, num_tasks = num_tasks)