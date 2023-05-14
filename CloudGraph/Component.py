from typing import List, Set, Dict


class Component:
    """ A cloud component.

    This class describes a generic cloud component such as
    a data center building, switch, power supply, VM (from
    the infrastructure), racks, or hosts.
    However, hosts are treated special and have their own
    class.
    """

    def __init__(self,name:str,availability:float):
        self.name: str = name
        self.availability: float = availability
        self.network_links: Dict[str, Set[Component]] = {'parents': set(), 'children': set()}
        self.fault_dependencies:  Dict[str, List[Component]] = {'parents': [], 'children': []}
        self.ft = {}


