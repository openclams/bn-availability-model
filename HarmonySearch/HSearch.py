from typing import List, Callable

from HarmonySearch.Improvisation import Improvisation
from HarmonySearch.Candidate import Candidate
import random

class HSearch():

    def __init__(self,
                 candidate_space: List[List[Candidate]],
                 loss_function: Callable[[List[Candidate]],float],
                 harmony_memory_size = 5,
                 harmony_memory_consideration_rate = 0.95, # probability to select from HM or generate a new imporvisation
                 pitch_adjustment_rate = 0.1,
                 termination = 1000
                 ):
        self.HMS = harmony_memory_size

        self.HMCR = harmony_memory_consideration_rate

        self.PAR = pitch_adjustment_rate

        self.termination = termination

        self.candidate_space = candidate_space

        self.prepare_space()

        self.loss_function = loss_function

        self.HM = self.init_harmony_memory()


    def prepare_space(self):

        for dimension in self.candidate_space:

            for index, candidate in enumerate(dimension):

                candidate.link(dimension,index)

    def print(self):

        for index , improvisation in enumerate(self.HM):

            print(index,'-',[v.value for v in improvisation.candidates], improvisation.loss)


    def run(self) -> Improvisation:

        for i in range(self.termination):

            improvisation = self.create_improvisation()

            self.test_and_replace(improvisation)

        return min(self.HM, key=lambda imp: imp.loss)


    def init_harmony_memory(self) -> List[Improvisation]:

        HM:List[Improvisation] = []

        for i in range(self.HMS):

            HM.append(self.create_random_improvisation())

        return HM


    def create_random_improvisation(self) -> Improvisation:

        candidates:List[Candidate] = []

        for dimension in self.candidate_space:

            candidates.append(random.choice(dimension))

        loss = self.loss_function(candidates)

        return Improvisation(candidates,loss)


    def test_and_replace(self,improvisation: Improvisation):

        worst_improvisation = max(self.HM, key=lambda imp: imp.loss)

        worst_improvisation_idx = self.HM.index(worst_improvisation)

        # self.print()

        if worst_improvisation.loss > improvisation.loss:

            # print("replce idx",worst_improvisation_idx," with loss",worst_improvisation.loss,
            #       'with',[ v.value for v in improvisation.candidates],'and loss', improvisation.loss)

            self.HM[worst_improvisation_idx] = improvisation




    def create_improvisation(self) -> Improvisation:

        candidates:List[Candidate] = []

        for i in range(len(self.candidate_space)):

            if random.random() < self.HMCR:

                candidate = random.choice([imp.candidates[i] for imp in self.HM])

                if random.random() < self.PAR:

                    candidate = self.pitch_adjustment(candidate)

            else:

                candidate = random.choice(self.candidate_space[i])

            candidates.append(candidate)

        loss = self.loss_function(candidates)

        return Improvisation(candidates,loss)


    def pitch_adjustment(self,candidate)->Candidate:

         dimension_len  = len(candidate.dimension)

         if candidate.index == 0 and dimension_len > 1:

             return candidate.dimension[1]

         elif candidate.index == dimension_len - 1 and dimension_len > 1:

            return candidate.dimension[dimension_len - 2]

         elif dimension_len > 2:

            if random.random() >= 0.5:

                return candidate.dimension[candidate.index + 1]

            else:

                return candidate.dimension[candidate.index -1]

         return candidate



