from CloudGraph.Component import Component
from typing import List

class Host(Component):
    """A special instance of a cloud component
    """
    def __init__(self,name : str, availability : float):
        Component.__init__(self,name,availability)

        # Array of server represented by string IDs
        self.servers: List[str] = []