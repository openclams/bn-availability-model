from CloudGraph.Component import Component
import CloudGraph.HostGroup as hg
from typing import List, Set

class Host(Component):
    """A special instance of a cloud component

    Host can belong to hosts groups/
    """

    def __init__(self,name : str, availability : float):
        Component.__init__(self,name,availability)

        self.host_groups: Set[hg.HostGroup] = set()

        # Array of server represented by string IDs
        self.servers: List[str] = []