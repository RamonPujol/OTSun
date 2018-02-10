from __future__ import print_function

import os
import json


class StatusLogger(object):
    def __init__(self, manager, total, root_folder):
        self.val = manager.Value('i', 0)
        self.lock = manager.Lock()
        self.total = total
        self.root_folder = root_folder
        self.status_file = os.path.join(root_folder, 'status.json')
        self.data_status = {'status': 'started', 'percentage': 'N/A'}
        self.save_status()

    def increment(self):
        with self.lock:
            self.val.value += 1
            value = self.val.value
            if (value == self.total) or ((value % (int(self.total / 100)+1)) == 0):
                self.update_data()
            else:
                print("not updating at {}".format(value))

    def value(self):
        with self.lock:
            return self.val.value

    def update_data(self):
        # print("updating data {}".format(self.data_status))
        if self.val.value == self.total:
            status = 'finished'
        else:
            status = 'running'
        percentage = (100*self.val.value)/self.total
        self.data_status['status'] = status
        self.data_status['percentage'] = percentage
        self.save_status()

    def save_status(self):
        print("saving data: {}".format(self.data_status))
        with open(self.status_file, 'w') as fh:
            json.dump(self.data_status, fh)


if __name__ == '__main__':
    from multiprocessing import Manager, Pool
    import random
    import time


    def f(args):
        counter = args[1]
        y = args[0]
        print('Proc {} starts on {}'.format(os.getpid(), y))
        for _ in range(50):
            time.sleep(random.random() / 10.0)
        counter.increment()
        print('Proc {} ends'.format(os.getpid()))
        return args[0] ** 2

    def main():
        manager = Manager()
        counter = StatusLogger(manager, 25, '/tmp')

        pool = Pool(processes=4)

        input_data = [(_, counter) for _ in range(25)]
        counter.total = len(input_data)
        output_data = pool.map(f, input_data)
        print('Count: {}'.format(counter.value()))
        # print(result)
        print(output_data)

    main()
