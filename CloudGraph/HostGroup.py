import CloudGraph.Host as h
from typing import Set, List

class HostGroup:
    """Named set of hosts"""

    def __init__(self,name : str):
        self.name: str  = name
        self.hosts: Set[h.Host] = set()  # Reference to the  hosts
