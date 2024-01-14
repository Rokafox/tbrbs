from block import *
from effect import *
import random


# NOTE:
# 1. name must be equal to class name, see load_player() in bs
# 2. Every time a new consumable is added, add it to get_1_random_consumable() in consumable.py


# Price : common < uncommon < rare < epic < unique < legendary, 10, 20, 50, 100, 200, 500
class Consumable(Block):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.can_use_on_dead = False


class Banana(Consumable):
    def __init__(self, stack: int):
        super().__init__("Banana", "Recover 15% of hp.")
        self.image = "banana"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 9

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.2, self)
        return f"{user.name} healed 15% of max hp."


class Kiwi(Consumable):
    def __init__(self, stack: int):
        super().__init__("Kiwi", "Recover 25% of hp.")
        self.image = "kiwi"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 16

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.25, self)
        return f"{user.name} healed 25% of max hp."


class Strawberry(Consumable):
    def __init__(self, stack: int):
        super().__init__("Strawberry", "")
        self.description = "Recover 5% of hp, every turn, recover 5% of lost hp for 6 turns."
        self.image = "strawberry"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 20

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.05, self)
        user.apply_effect(ContinuousHealEffect("Strawberry", 6, True, (user.maxhp - user.hp) * 0.05, False))
        return f"{user.name} healed 5% of max hp, and will heal 5% of lost hp for 4 turns."


class Pancake(Consumable):
    def __init__(self, stack: int):
        super().__init__("Pancake", "Recover 50% of hp.")
        self.image = "pancake"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 49

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.5, self)
        return f"{user.name} healed 50% of max hp."

class Mantou(Consumable):
    def __init__(self, stack: int):
        super().__init__("Mantou", "Recover 75% of hp.")
        self.image = "mantou"
        self.rarity = "Epic"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 99

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.75, self)
        return f"{user.name} healed 75% of max hp."


def get_1_random_consumable():
    consumable_list = [Banana(1), Kiwi(1), Strawberry(1), Pancake(1), Mantou(1)]
    return random.choice(consumable_list)