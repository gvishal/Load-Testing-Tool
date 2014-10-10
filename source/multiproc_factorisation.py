from multiprocessing import Queue, Process
import math

def factorize(n):
    if n < 2:
        return []
    factors = []
    p = 2
    while True:
	if n == 1:
	    return factors
	r = n % p
	if r == 0:
	    factors.append(p)
	    n = n/p
	elif p * p >= n:
	    factors.append(n)
	    return factors
	elif p > 2:
	    p += 2
	else:
	    p += 1
    assert False, "unreachable"

def factorizer(nums, nprocs):
    def worker(nums, out_q):
	outdict = {}
	for n in nums:
	    outdict[n] = factorize(n)
	out_q.put(outdict)

    out_q = Queue()
    chunksize = int(math.ceil(len(nums) / float(nprocs)))
    procs = []

    for i in range(nprocs):
	p = Process(target = worker, args= (nums[chunksize * i:chunksize * (i + 1)], out_q))
	procs.append(p)
	p.start()

    resultdict = {}
    for i in range(nprocs):
	resultdict.update(out_q.get())

    for p in procs:
        p.join()

    return resultdict

if __name__ == '__main__':
    ans = {}
    nums = []
    for i in range(100000):
	nums.append(i)
    ans = factorizer(nums, 500)
#    print ans
