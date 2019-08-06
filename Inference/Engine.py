class Engine:

    def __init__(self,bn):
        self.bn = bn
        self.repetition = 1
        self.meanTime = 0
        self.timeData = []
        self.meanAvailability = 0
        self.availabilityData = []
        self.is_successful = False
        self.is_exact_algorithm = True
        self.error_message = ""

    def run(self,*argv):
        pass

