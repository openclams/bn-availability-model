
import pandas as pn
import os
from pgmpy.models import BayesianModel
import time
import gc
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import datetime
import shutil
env_path = Path(os.getcwd()) / ".." / '.env'
load_dotenv(dotenv_path=env_path)


# def set_repetition(eng, n, c=None):
#     eng.repetition = n
#     return c

class Evaluate:

    def __init__(self,engines, project_folder,tests, skip_engines = [],timeout = 300,add_to_skip_list={},run_file=None):
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
        self.engines = engines
        self.skip_engines = skip_engines
        self.naive_engine_names = [ eng['name'] for eng in self.engines if eng['is_naive'] and ('is_prism' not in eng  or ('is_prism' in eng and (eng["is_prism"] is False)))]
        self.scalable_engine_names = [eng['name'] for eng in self.engines if not eng['is_naive'] and ('is_prism' not in eng  or ('is_prism' in eng and (eng["is_prism"] is False)))]
        self.tests = tests
        self.add_to_skip_list = add_to_skip_list

    def bn_memory(self,bn: BayesianModel):
        size = 0;
        for n in bn.nodes():
            n = bn.get_cpds(n).get_values()
            size = size + (n.size * n.itemsize)
        return size

    def run(self,generator):

        has_prism = any([eng['is_prism'] for eng in self.engines])

        res_dic = {}
        res_dic['n'] = []

        time_dic = {}
        time_dic['n'] = []

        mem_dic = {}
        mem_dic['n'] = []
        mem_dic['size_nv'] = []
        mem_dic['size_sc'] = []
        if has_prism:
            mem_dic['size_prism'] = []

        build_time_dic = {}
        build_time_dic['n'] = []
        build_time_dic['time_nv'] = []
        build_time_dic['time_sc'] = []
        if has_prism:
            build_time_dic['time_prism'] = []

        total_time_dic = {}
        total_time_dic['n'] = []

        for eng in self.engines:
            if eng['name'] not in res_dic:
                res_dic[eng['name']] = []
            if eng['name'] not in time_dic:
                time_dic[eng['name']] = []
            if eng['name'] not in total_time_dic:
                total_time_dic[eng['name']] = []

        for n in self.tests:
            se = generator(n)

            # Add first column to result file
            res_dic['n'].append(n)
            time_dic['n'].append(n)
            mem_dic['n'].append(n)
            build_time_dic['n'].append(n)
            total_time_dic['n'].append(n)

            mem_sc = 0
            mem_nv = 0

            start_build_time_nv = time.time()
            if all(elm in self.skip_engines for elm in self.naive_engine_names):
                bn = BayesianModel()
            else:
                bn = se.createNaiveNetwork()
                mem_nv = self.bn_memory(bn)
            build_time_nv = time.time() - start_build_time_nv

            start_build_time_sc = time.time()
            if all(elm in self.skip_engines for elm in self.scalable_engine_names):
                bs = BayesianModel()
            else:
                bs = se.createScalableNetwork()
                mem_sc = self.bn_memory(bs)
            build_time_sc = time.time() - start_build_time_sc

            if has_prism:
                start_build_prism = time.time()
                se.createPrism()
                mem_prism = 0
                build_time_prism = time.time() - start_build_prism
                build_time_dic['time_prism'].append(build_time_prism)
                mem_dic['size_prism'].append(mem_prism)

            build_time_dic['time_nv'].append(build_time_nv)
            build_time_dic['time_sc'].append(build_time_sc)

            mem_dic['size_nv'].append(mem_nv)
            mem_dic['size_sc'].append(mem_sc)

            res = pn.DataFrame(mem_dic)
            res.to_csv(self.project_folder + '/tmp_memory.csv', index=None, header=True)
            del res

            res = pn.DataFrame(build_time_dic)
            res.to_csv(self.project_folder + '/tmp_build_time.csv', index=None, header=True)
            del res

            # Evaluate each engine
            for eng in self.engines:
                print(' ')
                print(eng['title'], se.k, ":", se.n)
                print('-' * 30)
                print(eng['name'])

                # and before until it reaches its limit
                if( eng['name'] in self.add_to_skip_list and self.add_to_skip_list[eng['name']] < se.n):
                    self.skip_engines.append(eng['name'])
                    print("Max experiment number reached.")

                # Execute the experiment if it is not in the skip list

                if eng['name'] not in self.skip_engines:
                    if eng['is_prism']:
                        #try:
                        eng['engine'] = eng['fn'](self.skip_engines)
                        #except:
                            # print("PRISM model exception occurred")
                            # print("Pass")
                            # res_dic[eng['name']].append(float('inf'))
                            # time_dic[eng['name']].append(float('inf'))
                            # total_time_dic[eng['name']].append(float('inf'))
                            # continue
                    else:
                        try:
                            if eng['is_naive']:
                                eng['engine'] = eng['fn'](bn, self.skip_engines)
                            else:
                                eng['engine'] = eng['fn'](bs, self.skip_engines)
                        except:
                            print("BN model exception occurred")
                            print("Pass")
                            res_dic[eng['name']].append(float('inf'))
                            time_dic[eng['name']].append(float('inf'))
                            total_time_dic[eng['name']].append(float('inf'))
                            continue
                    run_param = eng['run_parameters'](eng['engine'])

                    start_total_time = time.time()

                    if run_param is not None:
                        eng['engine'].run(se.solution, run_param)
                    else:
                        eng['engine'].run(se.solution)

                    total_time =  time.time() - start_total_time
                    print('Mean Availability', eng['engine'].meanAvailability)
                    print('Inference Mean Time', eng['engine'].meanTime,'sec')
                    print('Total Time', total_time,'sec')

                    if not eng['is_prism']:
                        if eng['is_naive']:
                            print('Memory', mem_nv, 'bytes')
                            print('Pgmpy Build Time', build_time_nv, 'sec')
                        else:
                            print('Memory', mem_sc, 'bytes')
                            print('Pgmpy Build Time', build_time_sc, 'sec')
                    else:
                        print('Memory', mem_prism, 'bytes')
                        print('Prism Build Time', build_time_prism, 'sec')

                    res_dic[eng['name']].append(eng['engine'].meanAvailability)
                    time_dic[eng['name']].append(eng['engine'].meanTime)
                    total_time_dic[eng['name']].append(total_time)
                    print(res_dic)

                    #ouput timing and availability data as raw
                    print(eng['engine'].availabilityData)
                    res = pn.DataFrame({"availability":eng['engine'].availabilityData})
                    res.to_csv(self.project_folder + '/raw/'+str(n)+'_'+eng['name']+'_availability.csv', index=None, header=True)
                    del res

                    res = pn.DataFrame({"time":eng['engine'].timeData})
                    res.to_csv(self.project_folder + '/raw/'+str(n)+'_'+eng['name']+'_time.csv', index=None, header=True)
                    del res


                    # When to ignore any engine
                    # if eng['engine'].meanTime > self.timeout:
                    #     print("Inference time exceeded 1s: Set to ignore.")
                    #     self.skip_engines.append(eng['name'])
                else:
                    print("Pass")
                    res_dic[eng['name']].append(float('inf'))
                    time_dic[eng['name']].append(float('inf'))
                    total_time_dic[eng['name']].append(float('inf'))

            res = pn.DataFrame(res_dic)
            res.to_csv(self.project_folder+'/tmp_availability.csv', index=None, header=True)
            del res

            res = pn.DataFrame(time_dic)
            res.to_csv(self.project_folder+'/tmp_inference_time.csv', index=None, header=True)
            del res

            res = pn.DataFrame(total_time_dic)
            res.to_csv(self.project_folder + '/tmp_total_time.csv', index=None, header=True)
            del res

            del bs, bn

            gc.collect()

        res = pn.DataFrame(res_dic)
        res.to_csv(self.project_folder + '/final_availability.csv', index=None, header=True)

        res = pn.DataFrame(time_dic)
        res.to_csv(self.project_folder + '/final_inference_time.csv', index=None, header=True)

        res = pn.DataFrame(mem_dic)
        res.to_csv(self.project_folder + '/final_memory.csv', index=None, header=True)

        res = pn.DataFrame(build_time_dic)
        res.to_csv(self.project_folder + '/final_build_time.csv', index=None, header=True)

        res = pn.DataFrame(total_time_dic)
        res.to_csv(self.project_folder + '/final_total_time.csv', index=None, header=True)

        print('Finished')













