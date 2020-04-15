import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import numpy as np
import pandas as pd
import seaborn
import math
seaborn.set(style='ticks')
plt.close('all')


project_folder = "Prism_validate_majority_consensus14.04.2020 19-52-43"


def render(project_folder, file="",legend={},errorbars=False,raw=""):
    dataFrame = pd.read_csv(project_folder+"/"+file);


    data = dataFrame.values

    fig = plt.figure(figsize=(8,6), dpi=72, facecolor="white")
    axes = plt.subplot(111)
    axes.set_xlabel('#Processes (n)')
    axes.set_ylabel('Prediction Time [s]')
    axes.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

    interval = []
    if errorbars:
        for c in list(dataFrame.columns):
            interval.append([])

        for n in dataFrame['n']:
            idx = 0
            for c in list(dataFrame.columns):
                if( c == 'n'):
                    idx = idx + 1
                    continue
                try:
                    rawDataFrame = pd.read_csv(project_folder + '/raw/'+str(int(n))+'_'+c+'_'+raw+'.csv')

                    p025 = rawDataFrame['time'].quantile(0.025)
                    p975 = rawDataFrame['time'].quantile(0.975)
                    mean = rawDataFrame['time'].mean()
                    interval[idx].append((p025, p975))
                    print(p025,mean,p975)
                except:
                    pass

                idx = idx + 1

    colors = ["","r","b","y","g"]

    for i in range(1,len(data)):
        plt.plot(data[:,0],data[:,i],colors[i]+"x")
        plt.plot(data[:,0],data[:,i],colors[i]+"-",alpha=0.7)

        if errorbars:
            for idx, inv in enumerate(interval[i]):
                plt.errorbar(data[idx,0], data[idx,i], yerr=[[data[idx,i] - inv[0]], [inv[1]- data[idx,i]]])


    #seaborn.despine(ax=axes, offset=10, trim=True)
    fig.tight_layout()
    plt.legend()
    plt.show()

    print(data)