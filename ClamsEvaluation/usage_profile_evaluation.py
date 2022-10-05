import numpy as np
import time
np.set_printoptions(edgeitems=30, linewidth=100000,formatter=dict(float=lambda x: "%.3g" % x))

def generate_availabilities(n):

    return np.random.beta(8760,1,n)

def build_simple_grpah(S):

    n = len(S)

    Q = np.zeros([n,n])

    for i in range(n-1):

        Q[i,i+1] = S[i]

    return Q


def build_complex_grpah(S):

    n = len(S)

    Q = np.zeros([n, n])

    for i in range(n-2):
        for j in range(n - 1):
            p = S[i]*1/(n-1)

            Q[i,j] = p

    i = n-2
    for j in range(n):
        p = S[i] * 1 / (n)

        Q[i, j] = p

    return Q

def build_complex_grpah_steps(S):

    n = len(S)

    Q = np.zeros([n, n])

    for i in range(n-2):
        for j in range(n - 1):
            p = 1/(n-1)

            Q[i,j] = p

    i = n-2
    for j in range(n):
        p = 1 / (n)

        Q[i, j] = p

    return Q



def compute_user_oriented_availability(Q,S):

    n = Q.shape[0]

    P = np.linalg.inv(np.identity(n) - Q)

    return P[0, n - 1] * S[n - 1]


def test():

    S = [0.94,0.95,0.98,0.94]

    Q = np.array([
         [0, 0.94, 0,    0],
         [0, 0,    0.19, 0.76],
         [0, 0.98, 0,    0],
         [0, 0,    0,    0]])

    np.testing.assert_almost_equal(0.825, compute_user_oriented_availability(Q,S),decimal=3)

def test2():
    n = 10

    S = generate_availabilities(n)

    Q = build_simple_grpah(S)

    np.testing.assert_almost_equal(compute_user_oriented_availability(Q, S), np.prod(S))

if __name__ == '__main__':
    test()

    test2()

    n_max = 101
    repetition = 400

    print('n,time,complex,simple,stdTime')

    for n in range(3,n_max):

        S = generate_availabilities(n)

        times = []

        res = []

        Q = build_complex_grpah(S)

        for i in range(repetition):

            start = time.time()

            res.append(compute_user_oriented_availability(Q, S))

            times.append(time.time() - start)

        print(n,np.mean(times),np.mean(res),np.prod(S),np.std(times))
