import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import Locator
import numpy as np
import pandas as pd
#import seaborn
import math
#seaborn.set(style='ticks')
plt.close('all')

class MinorSymLogLocator(Locator):
    """
    Dynamically find minor tick positions based on the positions of
    major ticks for a symlog scaling.
    """
    def __init__(self, linthresh):
        """
        Ticks will be placed between the major ticks.
        The placement is linear for x between -linthresh and linthresh,
        otherwise its logarithmically
        """
        self.linthresh = linthresh

    def __call__(self):
        'Return the locations of the ticks'
        majorlocs = self.axis.get_majorticklocs()

        # iterate through minor locs
        minorlocs = []

        # handle the lowest part
        for i in range(1, len(majorlocs)):
            majorstep = majorlocs[i] - majorlocs[i-1]
            if abs(majorlocs[i-1] + majorstep/2) < self.linthresh:
                ndivs = 10
            else:
                ndivs = 9
            minorstep = majorstep / ndivs
            locs = np.arange(majorlocs[i-1], majorlocs[i], minorstep)[1:]
            minorlocs.extend(locs)

        return self.raise_if_exceeds(np.array(minorlocs))

    def tick_values(self, vmin, vmax):
        raise NotImplementedError('Cannot get tick locations for a '
                                  '%s type.' % type(self))


def render(project_folder, file="",xLabel='',yLabel='',legend={},errorbars=False,raw="",skip=[],semilog=False):
    dataFrame = pd.read_csv(project_folder+"/"+file);
    data = dataFrame.values
    skip = []
    fig = plt.figure(figsize=(8,6), dpi=100, facecolor="white")

    axes = plt.subplot(111)
    #plt.style.use('classic')
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    if semilog:
        plt.yscale('symlog')
        axes.yaxis.set_minor_locator(MinorSymLogLocator(1e-3))

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

                    p025 = rawDataFrame[raw].quantile(0.025)
                    p975 = rawDataFrame[raw].quantile(0.975)
                    mean = rawDataFrame[raw].mean()
                    interval[idx].append((p025, p975))
                    #print(p025,mean,p975)
                except:
                    pass

                idx = idx + 1


    lines = []
    labels = []
    for i in range(1,data.shape[1]):
        if legend[i-1].name in skip:
            continue

        c = legend[i-1].color
        m = legend[i - 1].marker
        l = legend[i-1].linestyle
        p1 = plt.plot(data[:,0],data[:,i],linestyle='', color=c,marker=m,label=legend[i-1].title)
        p2 = plt.plot(data[:,0],data[:,i],color=c,linestyle=l,alpha=0.5)
        # plt returns an array with one element. The element contains the plot object
        lines.append((p1[0],p2[0]))
        labels.append(legend[i-1].title)
        if errorbars:
            for idx, inv in enumerate(interval[i]):
                plt.errorbar(data[idx,0], data[idx,i], yerr=[[data[idx,i] - inv[0]], [inv[1]- data[idx,i]]],ecolor=c)

    # for l in plt.gca().lines:
    #     l.set_alpha(.5)
    # print(lines)
    axes.grid()
    #seaborn.despine(ax=axes, offset=10, trim=True)
    fig.tight_layout()
    plt.legend(lines,labels)
    plt.savefig(project_folder+"/"+file+'.png')
