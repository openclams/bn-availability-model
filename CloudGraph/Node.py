class Node:

    def __init__(self,name,availability):
        self.name = name
        self.availability = availability
        self.net = {'parents': set(), 'children': set()}
        self.cfc = {'parents': [], 'children': []}
        self.host_group_name = ""
        self.host_group = [] #Reference to the other hosts
        self.servers = [] #Array of server represented by string IDs

