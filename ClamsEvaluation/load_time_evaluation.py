import logging
import numpy
import requests
import json
import time
import pandas as pd
import sys

logger = logging.getLogger()
logger.disabled = True

root_dir = './'


def get_depth(component):
    url = "http://localhost/api/component/" + str(component['id']) + '/depth'
    resp = requests.get(url=url)

    data = resp.json()

    return data


def get_leaves(component):
    url = "http://localhost/api/component/" + str(component['id']) + '/leafs'
    resp = requests.get(url=url)

    data = resp.json()

    return data


def get_struct(component):
    return {
        'availability': 0,
        'cost': 0,
        'component': component
    }




# get the max depth for each component
if __name__ == '__main__':

    pd.set_option('display.max_columns', None)

    pd.set_option('display.expand_frame_repr', False)

    for i in range(1,32):

        file_name = root_dir+"ClamsEvaluation/TestCases/{}.json".format(i)

        print('\n',file_name)

        with open(file_name) as jsonFile:

            project = json.load(jsonFile)

            model = project['model']

            components = model['components']
            s = 0;
            dd = []
            for component in components:

                # Warm up
                for j in range(10):
                    get_leaves(component)

                # Start time recording
                for j in range(40):
                    start = time.time()
                    get_leaves(component)
                    dd.append(time.time()-start)

            print(i,numpy.mean(dd),numpy.var(dd),dd)

sys.stdout.close()