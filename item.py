from block import *


class Item(Block):
    def __init__(self, name, description):
        super().__init__(name, description)


class Cash(Item):
    def __init__(self, stack: int):
        super().__init__("Cash", "世界で最も一般的な通貨。")
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
        super().__init__("Sliver Ingot", "輝く銀のインゴット。")
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
        super().__init__("Gold Ingot", "輝く金のインゴット。")
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