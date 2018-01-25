from utils.statuslogger import StatusLogger
from multiprocessing import Manager, Pool
import random
import time
import os


def f(args):
    mycounter = args[1]
    y = args[0]
    print('Proc {} starts on {}'.format(os.getpid(), y))
    for _ in range(50):
        time.sleep(random.random() / 10.0)
    mycounter.increment()
    print('Proc {} ends'.format(os.getpid()))
    return args[0]**2


manager = Manager()
counter = StatusLogger(manager, 0, '/tmp')

pool = Pool(processes=4)

input_data = [(_, counter) for _ in range(25)]
counter.total = len(input_data)
output_data = pool.map(f, input_data)
print('Count: {}'.format(counter.value()))
# print(result)
print(output_data)
