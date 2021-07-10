from HarmonySearch.Candidate import Candidate
from typing import List

class Improvisation:

    def __init__(self,candidates: List[Candidate],loss:float = float('inf')):
        self.candidates = candidates
        self.loss = loss
