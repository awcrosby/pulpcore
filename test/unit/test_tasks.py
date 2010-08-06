import pprint
import time
import unittest

from pulp.tasking.task import (
    Task, task_created, task_waiting, task_finished, task_error,
    task_complete_states)
from pulp.tasking.queue.fifo import FIFOTaskQueue


def noop():
    pass

def args(*args):
    assert len(args) > 0
    
def kwargs(**kwargs):
    assert len(kwargs) > 0

def result():
    return True

def error():
    raise Exception('Aaaargh!')


class TaskTester(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_task_create(self):
        task = Task(noop)
        self.assertTrue(task.state == task_created)

    def test_task_noop(self):
        task = Task(noop)
        task.run()
        self.assertTrue(task.state == task_finished)

    def test_task_args(self):
        task = Task(args, 1, 2, 'foo')
        task.run()
        self.assertTrue(task.state == task_finished)

    def test_task_kwargs(self):
        task = Task(kwargs, arg1=1, arg2=2, argfoo='foo')
        task.run()
        self.assertTrue(task.state == task_finished)

    def test_task_result(self):
        task = Task(result)
        task.run()
        self.assertTrue(task.state == task_finished)
        self.assertTrue(task.result is True)

    def test_task_error(self):
        task = Task(error)
        task.run()
        self.assertTrue(task.state == task_error)
        self.assertTrue(task.traceback is not None)


class QueueTester(unittest.TestCase):
    
    def _wait_for_task(self, task):
        while task.state not in task_complete_states:
            time.sleep(0.005)
        if task.state == task_error:
            pprint.pprint(task.traceback)
            

class FIFOQueueTester(QueueTester):

    def setUp(self):
        self.queue = FIFOTaskQueue()

    def tearDown(self):
        pass
            
    def test_task_enqueue(self):
        task = Task(noop)
        self.queue.enqueue(task)
        self.assertTrue(task.state == task_waiting)

    def test_task_dispatch(self):
        task = Task(noop)
        self.queue.enqueue(task)
        self._wait_for_task(task)
        self.assertTrue(task.state == task_finished)
        
    def test_task_find(self):
        task1 = Task(noop)
        self.queue.enqueue(task1)
        task2 = self.queue.find(id=task1.id)
        self.assertTrue(task1 is task2)
        
    def test_task_status(self):
        task = Task(noop)
        self.queue.enqueue(task)
        self._wait_for_task(task)
        status = self.queue.find(id=task.id)
        self.assertTrue(status.state == task.state)
        
# run the unit tests ----------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
