import random
import block
import consumable
import equip





class Shop:
    def __init__(self, name, description, currency="Cash"):
        self.name = name
        self.description = description
        # self.inventory: item class: (sell_price, discount, final_price)
        self.inventory: dict[block.Block, tuple[int, float, int]] = {}
        self.currency = currency
        self.equippricedecide_random_low = 100
        self.equippricedecide_random_high = 120
        self.equipdiscountdecide_chance = 0.4

    def get_items_from_manufacturers(self):
        # This method is used to fill the inventory, can also be used when restocking.
        pass

    def decide_price(self):
        for k, (s, d, f) in self.inventory.copy().items():
            if k.__class__ == equip.Equip:
                # By default, the sale price is 100-120 times the market value for single equipment, decided by shop owner.
                random_multiplier = random.uniform(self.equippricedecide_random_low, self.equippricedecide_random_high)
                self.inventory[k] = (k.market_value * random_multiplier, d, f)
            elif k.type in ["Eqpackage", "Foodpackage"]:
                # The equipment package is normally sold at market value, with rarely any discount.
                self.inventory[k] = (k.market_value * k.current_stack, d, f)
            elif k.type == "Food":
                # The food is normally sold at market value, with rarely any discount.
                self.inventory[k] = (k.market_value * k.current_stack, d, f)
            else:
                raise ValueError(f"Item {k} cannot be sold because the price cannot be decided.")

    def decide_discount(self):
        for k, (s, d, f) in self.inventory.copy().items():
            if k.__class__ == equip.Equip:
                # there is a 40% chance to have a discount.
                if random.random() < self.equipdiscountdecide_chance:
                    # 0- 100% discount, with a average of 20% discount
                    discount = equip.normal_distribution(1, 100, 20, 30) * 0.01
                else:
                    discount = 0
                self.inventory[k] = (s, discount, f)
            elif k.type in ["Eqpackage", "Foodpackage"]:
                # with a 4% chance to have a 5% discount, 1% to have 10% discount, 0.2% to have 20% discount
                discount = 0
                if random.random() < 0.04:
                    discount = 0.05
                elif random.random() < 0.01:
                    discount = 0.1
                elif random.random() < 0.002:
                    discount = 0.2
                self.inventory[k] = (s, discount, f)
            elif k.type == "Food":
                # 30% chance to have a 30% discount, 3% chance to have a 50% discount, 0.3% chance to have a 70% discount
                discount = 0
                if random.random() < 0.3:
                    discount = 0.3
                elif random.random() < 0.03:
                    discount = 0.5
                elif random.random() < 0.003:
                    discount = 0.7
                self.inventory[k] = (s, discount, f)
        
            
    def calculate_final_price(self):
        # final sale price is s * (1 - d)
        for k, (s, d, f) in self.inventory.copy().items():
            self.inventory[k] = (s, d, int(s * (1 - d)))


class Armory_Banana(Shop):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.equippricedecide_random_low = 440
        self.equippricedecide_random_high = 460
        self.equipdiscountdecide_chance = 0.1
        if not self.description:
            self.description = "バナナ兵器工場は、究極の武器と防具を提供するショップです。" \
                "しかし、他の店とは一線を画し、すべてのアイテムは高額な価格で販売されています。なぜかと言えば、" \
                "特別な品々だからです。" \
                "品質、そして驚愕の価格――バナナ兵器工場は、あなたの財力を試す究極の場所です。"



    def get_items_from_manufacturers(self):
        # get all classes from consumable whose .type is 'Eqpackage'
        package_of_items = []
        

        package_of_items.extend(equip.generate_equips_list(3, eq_level=1, locked_rarity="Legendary", min_market_value=200))
        package_of_items.extend(equip.generate_equips_list(4, eq_level=1, locked_rarity="Unique", min_market_value=180))
        package_of_items.extend(equip.generate_equips_list(5, eq_level=1, locked_rarity="Epic", min_market_value=160))

        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)


class Gulid_SliverWolf(Shop):
    def __init__(self, name, description):
        super().__init__(name, description)
        if not self.description:
            self.description = "冒険者ギルド「銀狼の誓約」は、古代遺跡で冒険を繰り広げ、名声を築いてきました。メンバーは直感の戦術で知られており、レイド実績を持っています。" \
            "メンバーたちは冒険で回収した宝箱を厳選し、品質を保証した上で販売しています。" 

    def get_items_from_manufacturers(self):
        # get all classes from consumable whose .type is 'Eqpackage'
        package_of_items = []
        
        # Stupid code
        # package_of_items.append(consumable.EquipPackage(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage2(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage3(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage4(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage5(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage6(random.randint(1, 10)))

        package_of_items.append(consumable.EquipPackage(1))
        package_of_items.append(consumable.EquipPackage2(1))
        package_of_items.append(consumable.EquipPackage3(1))
        package_of_items.append(consumable.EquipPackage4(1))
        package_of_items.append(consumable.EquipPackage5(1))
        package_of_items.append(consumable.EquipPackage6(1))

        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)


class Big_Food_Market(Shop):
    def __init__(self, name, description):
        super().__init__(name, description)
        if not self.description:
            self.description = "ビッグ・フードは、あらゆる種類の食品を取り揃えた楽園です。" 

    def get_items_from_manufacturers(self):
        # get all classes from consumable whose .type is 'Eqpackage'
        package_of_items = []
        
        # Stupid code
        # package_of_items.append(consumable.EquipPackage(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage2(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage3(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage4(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage5(random.randint(1, 10)))
        # package_of_items.append(consumable.EquipPackage6(random.randint(1, 10)))

        package_of_items.append(consumable.FoodPackage(1))
        package_of_items.append(consumable.FoodPackage2(1))
        package_of_items.append(consumable.FoodPackage3(1))


        package_of_items.append(consumable.Banana(random.randint(1, 300)))
        package_of_items.append(consumable.Kiwi(random.randint(1, 300)))
        package_of_items.append(consumable.Strawberry(random.randint(1, 300)))
        package_of_items.append(consumable.Pancake(random.randint(1, 300)))
        package_of_items.append(consumable.Mantou(random.randint(1, 300)))

        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)
