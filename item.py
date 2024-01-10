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

