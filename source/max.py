import multiprocessing
#maximum of 2500 processes for a task of printing
#maximum of 1000 processes for task like factorisation
def do_calculation(num):
    return num * num
	
if __name__ == '__main__':
    inputs = list(range(1000))
    pool_size = multiprocessing.cpu_count() * 300
    pool = multiprocessing.Pool(processes = pool_size)
    pool_outputs = pool.map(do_calculation, inputs)
    pool.close()
    pool.join()

    print 'Output',pool_outputs
    
    
