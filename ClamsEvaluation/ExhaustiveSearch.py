from multiprocessing import  Pool, Value, Array
from functools import partial

# def get_candidates(counts, candidate_space):
#     return [candidate_space[i][counts[i]] for i in range(len(candidate_space))]


class IterateSearchSpace:

    """Iterator that counts upward forever."""

    def __init__(self, candidate_space):
        self.candidate_space = candidate_space

    def __iter__(self):
        self.counts = [0 for _ in range(len(self.candidate_space))]
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

def init(ml,br):
    global minimal_loss
    global best_result
    minimal_loss = ml
    best_result = br


def worker(counts,candidate_space=[],loss_function=None):
    #print(counts,candidate_space,loss_function)

    global best_result

    global minimal_loss

    candidates = [candidate_space[i][counts[i]] for i in range(len(candidate_space))]

    l = loss_function(candidates)

    if minimal_loss.value > l:
        with minimal_loss.get_lock():
            minimal_loss.value = l

        for i in range(len(counts)):
            best_result[i] = counts[i]

    # if l == 0.0:
    #
    #     break


def exhaustive_search(candidate_space,loss_function,num_processes=30):

    global minimal_loss
    global best_result

    best_result = Array('i', [0 for _ in range(len(candidate_space))])

    # for counts in IterateSearchSpace(candidate_space):
    #
    #    worker(counts,candidate_space,loss_function,minimal_loss,best_result)

    with Pool(processes=num_processes,initializer=init, initargs=(minimal_loss,best_result)) as pool:
        pool.map(partial(worker, candidate_space=candidate_space,loss_function=loss_function),IterateSearchSpace(candidate_space))


    return minimal_loss.value #, get_candidates(best_result, candidate_space)