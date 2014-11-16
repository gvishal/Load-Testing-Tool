from multiprocessing import Process, Array
import urllib2
import time

def data(q,i):
	start = time.localtime()
	s = time.mktime(start)
	response = urllib2.urlopen('http://www.flipkart.com/')
	
	finish = time.localtime()
#	html = response.read()
#	finish = time.localtime()
	f = time.mktime(finish)
	q[i]=(f-s)

if __name__ == '__main__':
	arr = Array('f',range(100))
	for i in range(100):
		p = Process(target = data,args =(arr,i))
		p.start()
		p.join()

	print arr[:]
	avg= 0.0
	for i in range(100):
		avg = avg+arr[i]
	
	print avg/100
