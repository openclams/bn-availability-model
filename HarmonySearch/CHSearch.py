from typing import List, Callable
from functools import partial
from HarmonySearch.Improvisation import Improvisation
from HarmonySearch.Candidate import Candidate
import random
from multiprocessing import Pool, Lock,  Array
import numpy as np
import ctypes as c


HM = []

L = []

lock = Lock()


def CHSearch(candidate_space: List[List[Candidate]],
             loss_function: Callable[[List[Candidate]],float],
             harmony_memory_size = 5,
             harmony_memory_consideration_rate = 0.95, # probability to select from HM or generate a new imporvisation
             pitch_adjustment_rate = 0.1,
             termination = 1000,
             num_processes = 8,
             ):

    global HM

    global L

    global lock

    HMS = harmony_memory_size

    HMCR = harmony_memory_consideration_rate

    PAR = pitch_adjustment_rate

    candidate_space = candidate_space

    prepare_space(candidate_space)

    init_HM = [] # HM only contains a list of list of integers (indexes)

    init_L = [] # The loss vector

    # Init harmony memory
    for i in range(HMS):

        h, l = create_random_improvisation(candidate_space, loss_function)

        init_HM.append(h)

        init_L.append(l)

    hm_array = Array(c.c_longlong,HMS*len(candidate_space))

    shared_buffer = np.frombuffer(hm_array.get_obj(),dtype=np.int64)

    # make it two-dimensional
    HM = shared_buffer.reshape((HMS, len(candidate_space)))  # b and arr share the same memory

    HM.astype(np.int64)

    for i in  range(HMS):

        for j in range(len(candidate_space)):

            HM[i][j] = int(init_HM[i][j])

    l_array = Array('d',len(init_L))

    L = np.frombuffer(l_array.get_obj(),dtype=np.float64)

    for i in range(HMS):

        L[i] = init_L[i]

    #Create new improvisations
    with Pool(processes=num_processes,initializer=init, initargs=(HM,L,lock)) as pool:

        pool.map(partial(proc_F , candidate_space=candidate_space, HMCR=HMCR, PAR=PAR, loss_function=loss_function), range(termination))

        job = pool.apply_async(best_solution, (candidate_space,))

        return job.get()

def best_solution(candidate_space):
    global HM
    global L

    best_idx = np.argmin(L)

    return Improvisation([candidate_space[i][val] for i, val in enumerate(HM[best_idx])], L[best_idx])

def init(hm,ll,lo):
    global HM
    global L
    global lock
    HM = hm
    L = ll
    lock = lo

def prepare_space( candidate_space ):

    for dimension in candidate_space:

        for index, candidate in enumerate(dimension):

            candidate.link(dimension,index)


def proc_F(idx,candidate_space, HMCR, PAR, loss_function):
    global HM
    global L
    global lock

    h, l = create_improvisation(candidate_space, HM, HMCR, PAR, loss_function)

    lock.acquire()

    worst_improvisation_idx = np.argmax(L)

    if L[worst_improvisation_idx] > l:

        HM[worst_improvisation_idx] = h

        L[worst_improvisation_idx] = l

    lock.release()




def create_random_improvisation(candidate_space, loss_function):

    candidates:List[Candidate] = []

    for dimension in candidate_space:

        candidates.append(random.choice(dimension))

    loss = loss_function(candidates)

    return [c.index for c in candidates], loss



def create_improvisation(candidate_space, HM, HMCR, PAR, loss_function):

    candidates:List[int] = []

    for i in range(len(candidate_space)):

        if random.random() < HMCR:

            candidate = random.choice([h[i] for h in HM])

            if random.random() < PAR:

                candidate = pitch_adjustment(candidate_space[i][candidate])

        else:

            candidate = random.choice(candidate_space[i]).index

        candidates.append(candidate)

    loss = loss_function([candidate_space[i][val] for i,val in enumerate(candidates)])

    return candidates, loss


def pitch_adjustment(candidate):

     dimension_len  = len(candidate.dimension)

     if candidate.index == 0 and dimension_len > 1:

         return candidate.dimension[1].index

     elif candidate.index == dimension_len - 1 and dimension_len > 1:

        return candidate.dimension[dimension_len - 2].index

     elif dimension_len > 2:

        if random.random() >= 0.5:

            return candidate.dimension[candidate.index + 1].index

        else:

            return candidate.dimension[candidate.index -1].index

     return candidate.index



