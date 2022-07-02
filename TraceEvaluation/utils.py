import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import roc_curve
from matplotlib import pyplot
from google.cloud import bigquery
from google.oauth2 import service_account
import os.path

def print_data(data):
    user_map = {}
    user_count = 1

    for idx, service in enumerate(list(data.keys())):

        print('Service', idx)

        for user in data[service]:

            if user not in user_map:
                user_map[user] = 'User ' + str(user_count)
                user_count = user_count + 1

            print('\t', user_map[user])

            worked = 0
            failed = 0

            for jdx, job in enumerate(data[service][user]):

                if data[service][user][job]['failed']:
                    failed = failed + 1
                else:
                    worked = worked + 1

                # text = 'Worked'
                # if data[service][user][job]['failed']:
                #     text = 'Failed'
                #
                # print('\t\t', 'Job', jdx, text)

                # up = 0
                # down = 0
                # for t in data[service][user][job]['tasks']:
                #     if data[service][user][job]['failed'][t]:
                #         down = down + 1
                #     else:
                #         up = up + 1
                #     print('\t\t', up, down)

            print('\t\t', worked, failed)


def connect():
    key_path = "/Users/ottob/Downloads/central-phalanx-346114-11dc0d238891.json"

    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    return bigquery.Client(credentials=credentials, project=credentials.project_id)


# Receivers operating characteristics (ROC)
def roc_plot(job_state, availability):

    # plot no skill
    pyplot.plot([0, 1], [0, 1], linestyle='--')
    # plot the roc curve for the model
    aa = []
    ab = []
    ac = []
    for a in availability:
        aa.append(a[0])
        ab.append(a[1])
        ac.append(a[2])

    fpr, tpr, thresholds = roc_curve(np.array(job_state), np.array(aa))
    pyplot.scatter(fpr, tpr, label='1/n')

    fpr, tpr, thresholds = roc_curve(np.array(job_state), np.array(ab))
    pyplot.scatter(fpr, tpr, label='MAJ')

    fpr, tpr, thresholds = roc_curve(np.array(job_state), np.array(ac))


    # print(ac)
    # print(job_state)
    # print(fpr)
    # print(tpr)
    # print(thresholds)

    pyplot.scatter(fpr, tpr, label='n/n')
    pyplot.legend()
    # show the plot
    pyplot.show()



