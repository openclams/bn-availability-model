import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import pylab as plt


def plot(BN, save=False, name="f"):
    pos = graphviz_layout(BN, prog='dot')
    nx.draw(BN, pos, with_labels=True, arrows=True)

    if save:
        plt.savefig(name)
    else:
        plt.show()
    plt.close()