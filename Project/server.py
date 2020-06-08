from multiprocessing.managers import BaseManager
from multiprocessing import Queue


if __name__ == '__main__':    
    register_queue = Queue()
    input_queue = Queue()
    results_queue = Queue()
    BaseManager.register('register_queue', callable=lambda:register_queue)
    BaseManager.register('input_queue', callable=lambda:input_queue)
    BaseManager.register('results_queue', callable=lambda:results_queue)
    manager = BaseManager(address=('', 8080), authkey=b'blah')
    server = manager.get_server()
    server.serve_forever()
