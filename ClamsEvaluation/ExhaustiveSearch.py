from multiprocessing import  Pool, Value, Array
from functools import partial

# def get_candidates(counts, candidate_space):
#     return [candidate_space[i][counts[i]] for i in range(len(candidate_space))]
import sys

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

class IterateSearchSpace:

    """Iterator that counts upward forever."""

    def __init__(self, candidate_space):
        self.candidate_space = candidate_space

    def __iter__(self):
        self.counts = [0 for _ in range(len(self.candidate_space))]
        if(len(self.counts) > 0):
            self.counts[0] = -1
        self.termination_criteria = [len(s) - 1 for s in self.candidate_space]

        return self

    def __next__(self):
        if self.counts != self.termination_criteria:

            for a in range(len(self.counts)):
                if a == 0:
                    self.counts[a] += 1
                else:
                    if self.counts[a - 1] > self.termination_criteria[a - 1]:
                        self.counts[a - 1] = 0
                        self.counts[a] += 1

            return [ c for c in self.counts]
        else:
            raise StopIteration

minimal_loss = Value('d',float('inf'))

best_result = None

progress_count = 0

def init(ml,br,pc):
    global minimal_loss
    global best_result
    global progress_count
    minimal_loss = ml
    best_result = br
    progress_count = pc


def worker(counts,candidate_space=[],loss_function=None):

    global best_result

    global minimal_loss

    global progress_count

    candidates = [candidate_space[i][counts[i]] for i in range(len(candidate_space))]

    l = loss_function(candidates)

    with minimal_loss.get_lock():
        if minimal_loss.value > l:
            minimal_loss.value = l

        for i in range(len(counts)):
            best_result[i] = counts[i]

    # if l == 0.0:
    #
    #     break


def exhaustive_search(candidate_space,loss_function,num_processes=30):

    global minimal_loss
    global best_result
    global progress_count

    progress_count = Value('i', 0)
    minimal_loss = Value('d', float('inf'))
    best_result = Array('i', [0 for _ in range(len(candidate_space))])

    # for counts in IterateSearchSpace(candidate_space):
    #
    #    worker(counts,candidate_space,loss_function,minimal_loss,best_result)

    with Pool(processes=num_processes,initializer=init, initargs=(minimal_loss,best_result,progress_count)) as pool:
        pool.map(partial(worker, candidate_space=candidate_space,loss_function=loss_function),IterateSearchSpace(candidate_space))


    return minimal_loss.value #, get_candidates(best_result, candidate_space)