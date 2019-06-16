from BayesianNetModel import BayesianNetModel
from PrismModel import PrismModel
from PrismModelDT import PrismModelDT
import pyAgrum as gum

ba = BayesianNetModel()

bn = ba.bn

def compareAllInference(bn, solution ,evs={}, epsilon=10 ** -5, epsilonRate=1e-6, maxTime=50):
    ies = [gum.LazyPropagation(bn),
           gum.LoopyBeliefPropagation(bn),
           gum.GibbsSampling(bn),
           gum.LoopyGibbsSampling(bn),
           gum.WeightedSampling(bn),
           gum.LoopyWeightedSampling(bn),
           gum.ImportanceSampling(bn),
           gum.LoopyImportanceSampling(bn)]

    iest = ["LazyPropagation(bn)",
           "LoopyBeliefPropagation(bn)",
           "GibbsSampling(bn)",
           "LoopyGibbsSampling(bn)",
           "WeightedSampling(bn)",
           "LoopyWeightedSampling(bn)",
           "ImportanceSampling(bn)",
           "LoopyImportanceSampling(bn)"]

    # burn in for Gibbs samplings
    for i in [2, 3]:
        ies[i].setBurnIn(600)
        ies[i].setDrawnAtRandom(True)

    for i in range(2, len(ies)):
        ies[i].setEpsilon(epsilon)
        ies[i].setMinEpsilonRate(epsilonRate)
        ies[i].setPeriodSize(300)
        ies[i].setMaxTime(maxTime)

    for i in range(len(ies)):
        ies[i].setEvidence(evs)
        ies[i].makeInference()
        print(iest[i],ies[i].posterior(solution)[1])

ies = gum.LazyPropagation(bn)
ies.makeInference()
print(ies.posterior("er")[1])
pm = PrismModel()
print(pm.result())

pmdt = PrismModelDT()
print(pmdt.result())