from block import *
from effect import *
import random


# NOTE:
# 1. name must be equal to class name, see load_player() in bs
# 2. Every time a new consumable is added, add it to get_1_random_consumable() in consumable.py


# Price : common < uncommon < rare < epic < unique < legendary, 50, 100, 250, 500, 1000, 2500
class Consumable(Block):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.can_use_for_auto_battle = True
        self.can_use_on_dead = False

    def auto_E_condition(self, user, player):
        """
        Returns True if the item should be used automatically.
        """
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return True



class Banana(Consumable):
    def __init__(self, stack: int):
        super().__init__("Banana", "Recover 15% of hp.")
        self.image = "banana"
        self.rarity = "Common"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 45
        self.name_jp = "バナナ"
        self.description_jp = "最大HPの15%分HPを回復する。"

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.15, self)
        return f"{user.name} healed 15% of max hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp * 0.8
        


class Kiwi(Consumable):
    def __init__(self, stack: int):
        super().__init__("Kiwi", "Recover 25% of hp.")
        self.image = "kiwi"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 80
        self.name_jp = "キウイ"
        self.description_jp = "最大HPの25%分HPを回復する。"

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.25, self)
        return f"{user.name} healed 25% of max hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp * 0.7


class Strawberry(Consumable):
    def __init__(self, stack: int):
        super().__init__("Strawberry", "")
        self.description = "Recover 5% of hp, every turn, recover 5% of lost hp for 6 turns."
        self.image = "strawberry"
        self.rarity = "Uncommon"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 100
        self.name_jp = "イチゴ"
        self.description_jp = "最大HPの5%分HPを回復し、6ターンの間、毎ターン最大HPの5%分HPを回復する。"

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.05, self)
        user.apply_effect(ContinuousHealEffect("Strawberry", 6, True, (user.maxhp - user.hp) * 0.05, False))
        return f"{user.name} healed 5% of max hp, and will heal 5% of lost hp for 4 turns by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp * 0.7


class Pancake(Consumable):
    def __init__(self, stack: int):
        super().__init__("Pancake", "Recover 50% of hp.")
        self.image = "pancake"
        self.rarity = "Rare"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 245
        self.name_jp = "パンケーキ"
        self.description_jp = "最大HPの50%分HPを回復する。"

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.5, self)
        return f"{user.name} healed 50% of max hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp * 0.5
        

class Mantou(Consumable):
    def __init__(self, stack: int):
        super().__init__("Mantou", "Recover 75% of hp.")
        self.image = "mantou"
        self.rarity = "Epic"
        self.type = "Food"
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.market_value = 499
        self.name_jp = "饅頭"
        self.description_jp = "最大HPの75%分HPを回復する。"

    def E(self, user, player):
        user.heal_hp(user.maxhp * 0.75, self)
        return f"{user.name} healed 75% of max hp by {self.name}."
    
    def auto_E_condition(self, user, player):
        if not self.can_use_on_dead and user.is_dead():
            return False
        else:
            return user.hp < user.maxhp * 0.3


def get_1_random_consumable():
    consumable_list = [Banana(1), Kiwi(1), Strawberry(1), Pancake(1), Mantou(1)]
    return random.choice(consumable_list)