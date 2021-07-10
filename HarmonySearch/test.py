from HarmonySearch.Candidate import Candidate
from HarmonySearch.HSearch import HSearch
import numpy

#Test

def f(x):
    return ((x[0]-2)**2 )+ ((x[1]-1)**2)

def g1(x):
    return x[0]-2*x[1]+1

def g2(x):
    return (x[0]**2)/4 - x[1]**2 + 1

def loss_fn(candidates):

    x = (candidates[0].value,candidates[1].value)

    if g2(x) < 0 or g1(x) != 0:
        return float('inf')
    return f(x)

x = [
        [ Candidate(i) for _ , i in enumerate(numpy.linspace(0, 1.0, num=3000, retstep=False))],
        [ Candidate(i) for _ , i in enumerate(numpy.linspace(0, 1.0, num=3000, retstep=False))]
    ]

hs = HSearch(candidate_space=x,loss_function=loss_fn,
             termination=40000,
             harmony_memory_size=30,
             harmony_memory_consideration_rate=0.3,
             pitch_adjustment_rate=0.1)

imp = hs.run()

xs = [ v.value for v in imp.candidates]
print(xs,imp.loss,f(xs),g1(xs),g2(xs))

hs.print()