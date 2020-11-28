import Evaluation.generate as gn
import Inference.bnlearn.BNLearn as bnlearn
import Inference.grain.gRain as grain
import Inference.prism.PrismExact as prismExc
import Inference.prism.PrismSim as prismSim
import Evaluation.evaluate as ev
import os


def set_repetition(eng, n, c=None):
    eng.repetition = n
    return c


inferenceEngines = [
    {
        'is_naive': False,
        'is_prism': False,
        'name': 'ScBNlearn',
        'title': 'BN approx inference',
        'color': 'r',
        'marker': 'X',
        'fn': lambda Bnet, skip_list: bnlearn.BNLearn(Bnet, driver="R", use_cached_file=False,
                                                      tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 2)
    },{
        'is_naive': False,
        'is_prism': False,
        'name': 'ScgRain',
        'title': 'BN exact inference',
        'color': 'b',
        'marker': 'D',
        'fn': lambda Bnet, skip_list: grain.gRain(Bnet, driver="R",
                                                  use_cached_file=('ScBNlearn' not in skip_list),
                                                  tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 1)
    },
    {
        'is_naive': False,
        'is_prism': True,
        'name': 'PrismRes',
        'title': 'PRISM Model (exact)',
        'color': 'y',
        'marker': '^',
        'fn': lambda skip_list: prismExc.PrismExact("cim.sm", prism_location=os.getenv("PRISM_PATH"),
                                                    prism_bin_path=os.getenv("PRISM_LOCATION")),
        'run_parameters': lambda eng: set_repetition(eng, 1)
    },
    {
        'is_naive': True,
        'is_prism': True,
        'name': 'PrismSim',
        'title': 'PRISM Model  (simulation)',
        'color': 'g',
        'marker': 'o',
        'fn': lambda skip_list: prismSim.PrismSim("cim.sm", prism_location=os.getenv("PRISM_PATH"),
                                                  prism_bin_path=os.getenv("PRISM_LOCATION")),
        'run_parameters': lambda eng: set_repetition(eng, 1)
    }
]


cim = "../Tests/simple_service/graph.json"
#cim = "/home/bibartoo/spinoza-scripts/Tests/service_X/graph.json"
r = ev.Evaluate(inferenceEngines,
                '10 H test', #Project title
                range(12,83,10),#10e01m1111set
                skip_engines = ['ScgRain','PrismRes'],
                add_to_skip_list={
                    "ScgRain": 5  # Stop after n=5,
                },
                run_file=__file__)
r.run(lambda n: gn.PrismComparisonExample(n, int(n / 2) + 1, cim,init='G1'))
