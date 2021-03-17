from Evaluation.generators.SimpleExample import  SimpleExample
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData

from Evaluation.executors.memory.NaiveBNCPTsize import  NaiveBNCPTsize
from Evaluation.executors.memory.NaiveBNFilesize import NaiveBNFilesize
from Evaluation.executors.memory.ScalableBNCPTsize import ScalableBNCPTsize
from Evaluation.executors.memory.ScalableBNFilesize import  ScalableBNFilesize


title = "Simple Memory Test 30 "

generator = lambda n: SimpleExample(n, int(n / 2) + 1)
tests =range(3,32,2)
experiment = ExperimentData()

instances = [
     ScalableBNCPTsize('ScgCPT' ,'BN Exact Inference', experiment),
     ScalableBNFilesize('ScbnFile' ,'BN Approx Inference', experiment),
     NaiveBNCPTsize('NavgCPT' ,'BN Exact Inference', experiment),
     NaiveBNFilesize('NaiveFile' ,'BN Approx Inference', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "NavgCPT": 27,
                    "NaiveFile" : 27
                },
                run_file=__file__)
r.run(generator,experiment)