import random


class Randomizer:
    digits_to_round = 4

    def __init__(self, chances: []):
        self.chances_list = Randomizer.recalculate(chances)

    @classmethod
    def recalculate(cls, chances: []) -> []:
        recalculated_chances = []
        modifier = round(1 / len(chances), cls.digits_to_round)
        for each in chances:
            each *= modifier
            recalculated_chances.append(each)
        return recalculated_chances

    def run(self) -> int:
        rand = random.random()
        summary = 0
        for i in range(len(self.chances_list)):
            summary += self.chances_list[i]
            if summary >= rand:
                return i
            elif i == len(self.chances_list) - 1:
                return i
