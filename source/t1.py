from multiprocessing import Process, Queue
import math
from Queue import Empty
import time

start = time.time()
#tic = lambda: print time.time()-start
def isprime(n):
	if  n<2:
		return False
	if n==2:
		return True
	max = int(math.ceil(math.sqrt(n)))
	i=2
	while i<=max:
		if n%i == 0:
			return False
		i+=1
	return True

def sum_primes(n):
	return sum([x for x in xrange(2,n) if isprime(x)])

def do_work(q):
	while True:
		try:
			x = q.get(block = False)
			sum_primes(x)
		except Empty:
			break

if __name__ == '__main__':
	work_queue = Queue()
	for i in xrange(1, 1000):
		work_queue.put(i)
	
	processes = [Process(target = do_work, args = (work_queue,)) for i in range(1)]
	print time.time()-start
	for p in processes:
		p.start()
#	a = raw_input()
	for p in processes:
		p.join()
	print time.time()-start
