
class Candidate:

    def __init__(self,obj):
        self.value = obj
        self.index = 0
        self.dimension = None

    def link(self, dimension, index):
        self.index = index
        self.dimension = dimension
