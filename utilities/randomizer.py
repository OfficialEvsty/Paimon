import random


class Randomizer:
    _digits_to_round = 4

    def __init__(self, chances: []):
        self._chances_list = Randomizer._recalculate(chances)
        self._clear_chances_list = chances

    @classmethod
    def _recalculate(cls, chances: []) -> []:
        recalculated_chances = []
        modifier = round(1 / len(chances), cls._digits_to_round)
        for each in chances:
            each *= modifier
            recalculated_chances.append(each)
        return recalculated_chances

    def run(self) -> int:
        rand = random.random()
        summary = 0
        for i in range(len(self._chances_list)):
            summary += self._chances_list[i]
            if summary >= rand:
                return i
            elif i == len(self._chances_list) - 1:
                return i

    def run_each(self) -> []:
        chances = self._clear_chances_list
        selected = []
        for i in range(len(chances)):
            rand = random.random()
            if rand <= chances[i]:
                selected.append(i)
        return selected

    @staticmethod
    def get_rand() -> float:
        return random.random()
