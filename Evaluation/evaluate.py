from Evaluation.executors.ExperimentData import ExperimentData
import pandas as pn
import os
from pgmpy.models import BayesianModel
import time
import gc

import datetime
import shutil
import Evaluation.render as re


import logging
logging.disable(logging.WARNING)


class Evaluate:

    def __init__(self,instances, project_folder,tests, skip_engines = [],timeout = 300,add_to_skip_list={},run_file=None):
        timestamp = datetime.datetime.today().strftime("%d.%m.%Y %H-%M-%S")
        project_folder = project_folder + timestamp

        if not os.path.exists(project_folder):
            os.makedirs(project_folder)

        if not os.path.exists(project_folder+'/raw/'):
            os.makedirs(project_folder+'/raw/')

        if run_file:
            shutil.copy(run_file,project_folder+"/run.py")

        self.timeout = timeout
        self.project_folder = project_folder
        self.instances = instances
        self.skip_engines = skip_engines

        self.tests = tests
        self.add_to_skip_list = add_to_skip_list



    def run(self,generator,experiment):

        for n in self.tests:
            se = generator(n)

            # Add first column to result file
            experiment.addInstance(n)

            # for instance in self.instances:
            #
            #     instance.setGenerator(se)
            #
            #     if instance.name not in self.skip_engines:
            #         instance.build()
            #     else:
            #         instance.ignoreBuild()
            #
            # res = pn.DataFrame(experiment.mem_dic)
            # res.to_csv(self.project_folder + '/tmp_memory.csv', index=None, header=True)
            # del res
            #
            # res = pn.DataFrame(experiment.build_time_dic)
            # res.to_csv(self.project_folder + '/tmp_build_time.csv', index=None, header=True)
            # del res

            # Evaluate each engine
            for instance in self.instances:

                print(' ')
                print(instance.title, se.k, ":", se.n)
                print('-' * 30)
                print(instance.name)

                instance.setGenerator(se)

                if instance.name not in self.skip_engines:
                    instance.build()
                else:
                    instance.ignoreBuild()

                # and before until it reaches its limit
                if( instance.name in self.add_to_skip_list and self.add_to_skip_list[instance.name] < se.n):
                    self.skip_engines.append(instance.name)
                    print("Max experiment number reached.")

                # Execute the experiment if it is not in the skip list

                if instance.name not in self.skip_engines:
                    try:
                        instance.setEngine()
                        #instance.engine.repetition = 1
                    except:
                        print("Engine exception occurred")
                        print("Pass")
                        instance.ignoreRun()
                        continue

                    result = instance.run()

                    # print('Mean Availability',result.meanAvailability)
                    # print('Inference Mean Time', result.meanTime,'sec')
                    # print('Total Time', total_time,'sec')

                    #ouput timing and availability data as raw

                    res = pn.DataFrame({"availability":instance.engine.availabilityData})
                    res.to_csv(self.project_folder + '/raw/'+str(n)+'_'+instance.name+'_availability.csv', index=None, header=True)
                    del res

                    res = pn.DataFrame({"time":instance.engine.timeData})
                    res.to_csv(self.project_folder + '/raw/'+str(n)+'_'+instance.name+'_time.csv', index=None, header=True)
                    del res


                    # When to ignore any engine
                    # if eng['engine'].meanTime > self.timeout:
                    #     print("Inference time exceeded 1s: Set to ignore.")
                    #     self.skip_engines.append(eng['name'])
                else:
                    print("Pass")
                    instance.ignoreRun()

            res = pn.DataFrame(experiment.res_dic)
            res.to_csv(self.project_folder+'/tmp_availability.csv', index=None, header=True)
            del res

            res = pn.DataFrame(experiment.time_dic)
            res.to_csv(self.project_folder+'/tmp_inference_time.csv', index=None, header=True)
            del res

            res = pn.DataFrame(experiment.total_time_dic)
            res.to_csv(self.project_folder + '/tmp_total_time.csv', index=None, header=True)
            del res

            instance.clean()

            gc.collect()

        res = pn.DataFrame(experiment.res_dic)
        res.to_csv(self.project_folder + '/final_availability.csv', index=None, header=True)

        res = pn.DataFrame(experiment.time_dic)
        res.to_csv(self.project_folder + '/final_inference_time.csv', index=None, header=True)

        res = pn.DataFrame(experiment.mem_dic)
        res.to_csv(self.project_folder + '/final_memory.csv', index=None, header=True)

        res = pn.DataFrame(experiment.build_time_dic)
        res.to_csv(self.project_folder + '/final_build_time.csv', index=None, header=True)

        res = pn.DataFrame(experiment.total_time_dic)
        res.to_csv(self.project_folder + '/final_total_time.csv', index=None, header=True)

        print('Finished')


        #avaibility + raw avaibility
        re.render(self.project_folder, file="final_inference_time.csv", xLabel='#Processes', yLabel='Computation time [s]',legend=self.instances, errorbars=True, raw="time", skip=self.skip_engines,semilog=True)
        #inference_time + time
        re.render(self.project_folder, file="final_availability.csv", xLabel='#Processes', yLabel='Availability',legend=self.instances, errorbars=True, raw="availability", skip=self.skip_engines)













