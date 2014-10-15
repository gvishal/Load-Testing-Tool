"""Program to calculate maximum numbers of sub-processes"""

#maximum of 2500 processes for a task of printing
#maximum of 1000 processes for task like factorisation

import multiprocessing

def do_calculation(num):
    """Performs calculation"""
    return num * num

if __name__ == '__main__':
    INPUTS = list(range(1000))
    POOL_SIZE = multiprocessing.cpu_count() * 300
    POOL = multiprocessing.Pool(processes=POOL_SIZE)
    POOL_OUTPUTS = POOL.map(do_calculation, INPUTS)
    POOL.close()
    POOL.join()
#    print 'Output', pool_outputs
