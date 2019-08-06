__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import concurrent.futures

class Worker(object):

    def __init__(self, n_threads=10):
        self.n_threads = n_threads
        self.tasks = []

    def add_task(self, func, *args, **kwargs):
        """ add task

        :type func: function
        :type args: tuple
        :type kwargs: dict
        """
        self.tasks.append([func, args, kwargs])

    def clear_tasks(self):
        """ reset task list
        """
        self.tasks = []

    def run(self):
        """ run all tasks and return result list (by task-inserted order)

        :return: list[object]
        """
        results = [None] * len(self.tasks)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.n_threads) as executor:
            #for task in self.tasks:
            #    task[2]['pe'] = executor
            future_tasks = dict((executor.submit(self._task_thread, task, task_id), task) for task_id, task in enumerate(self.tasks))
            for future in concurrent.futures.as_completed(future_tasks):
                (task_id, ret) = future.result()
                results[task_id] = ret
        return results

    def _task_thread(self, task, task_id):
        """ thread method to run a single task
        return task id and result from task
        """
        (func, args, kwargs) = task
        return (task_id, func(*args, **kwargs))
