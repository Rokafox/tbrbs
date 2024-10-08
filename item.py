from block import *


class Item(Block):
    def __init__(self, name, description):
        super().__init__(name, description)


class Cash(Item):
    def __init__(self, stack: int):
        super().__init__("Cash", "The most common currency in the world.")
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.image = "cash"
        self.rarity = "Common"

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "type": self.type,
            "current_stack": self.current_stack,
        }


class SliverIngot(Item):
    def __init__(self, stack: int):
        super().__init__("Sliver Ingot", "A shiny piece of silver ingot.")
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.image = "sliver_ingot_111000"
        self.rarity = "Rare"
        self.market_value = 111000

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "type": self.type,
            "current_stack": self.current_stack,
        }
    

class GoldIngot(Item):
    def __init__(self, stack: int):
        super().__init__("Gold Ingot", "A shiny piece of gold ingot.")
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.image = "gold_ingot_9820000"
        self.rarity = "Epic"
        self.market_value = 9820000

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "type": self.type,
            "current_stack": self.current_stack,
        }
    

class DiamondIngot(Item):
    def __init__(self, stack: int):
        super().__init__("Diamond Ingot", "A shiny piece of diamond ingot.")
        self.current_stack = max(1, stack)
        self.current_stack = min(self.current_stack, self.max_stack)
        self.image = "diamond_ingot_62000000"
        self.rarity = "Unique"
        self.market_value = 62000000

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "type": self.type,
            "current_stack": self.current_stack,
        }