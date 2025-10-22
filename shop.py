import random
import block
import consumable
import equip




class Shop:
    def __init__(self, name, description, currency="Cash"):
        """
        currency must mach the class name of any Block item.
        """
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
                self.inventory[k] = (k.market_value * k.current_stack, d, f)

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



class Armory_Brand_Specific(Shop):
    def __init__(self, name, description, brand_name):
        super().__init__(name, description)
        self.equippricedecide_random_low = 600
        self.equippricedecide_random_high = 700
        self.equipdiscountdecide_chance = 0.25
        self.brand_name = brand_name
        if not self.description:
            self.description = f"{brand_name}のブランド専門店。適正な価格で一品物の装備を提供し、その品質と信頼性は常に保証されています。"


    def get_items_from_manufacturers(self):
        package_of_items = []
        package_of_items.extend(equip.generate_equips_list(5, eq_level=1, min_market_value=-1, locked_eq_set=self.brand_name))

        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)


class Armory_Brand_Specific_Reforged(Shop):
    def __init__(self, name, description, brand_name):
        super().__init__(name, description)
        self.currency = "SliverIngot"
        self.equippricedecide_random_low = 1
        self.equippricedecide_random_high = 1
        self.equipdiscountdecide_chance = 0
        self.brand_name = brand_name
        if not self.description:
            self.description = f"{brand_name}のリフォージ専門店。装備の質は稀に伝説的なものにまで高められることがありますが、その代償は途方もない価格となることが知られています。"


    def get_items_from_manufacturers(self):
        package_of_items = []
        package_of_items.extend(equip.generate_equips_list(9, eq_level=1, min_market_value=100, locked_eq_set=self.brand_name))
        package_of_items.append(consumable.EquipPackageBrandSpecific(random.randint(1, 20), self.brand_name))

        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)

    def decide_price(self):
        for k, (s, d, f) in self.inventory.copy().items():
            if k.__class__ == equip.Equip:
                price = k.market_value // 50
            else:
                price = k.market_value * k.current_stack // 55500
            self.inventory[k] = (price, d, f)

    def decide_discount(self):
        for k, (s, d, f) in self.inventory.copy().items():
            self.inventory[k] = (s, 0, f)



class Armory_Brand_Specific_Premium(Shop):
    def __init__(self, name, description, brand_name):
        super().__init__(name, description)
        self.currency = "GoldIngot"
        self.equippricedecide_random_low = 1
        self.equippricedecide_random_high = 1
        self.equipdiscountdecide_chance = 0
        self.brand_name = brand_name
        if not self.description:
            self.description = f"{brand_name}の最高峰専門店。唯一無二の装備を求める者にとって、ここは宝の山です。伝説級の質を誇る装備が取り揃えられ、その価値と価格は他に類を見ません。"


    def get_items_from_manufacturers(self):
        package_of_items = []
        package_of_items.extend(equip.generate_equips_list(5, eq_level=1, min_market_value=200, locked_eq_set=self.brand_name, locked_rarity="Legendary"))

        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)

    def decide_price(self):
        for k, (s, d, f) in self.inventory.copy().items():
            price = k.market_value // 200
            # price *= k.market_value // 100
            self.inventory[k] = (price, d, f)

    def decide_discount(self):
        for k, (s, d, f) in self.inventory.copy().items():
            self.inventory[k] = (s, 0, f)





class Gulid_SliverWolf(Shop):
    def __init__(self, name, description):
        super().__init__(name, description)
        if not self.description:
            self.description = "冒険者ギルド「銀狼の誓約」は、古代遺跡で冒険を繰り広げ、名声を築いてきました。メンバーはHP極振りの戦術で知られており、レイドでの実績を持っています。" \
            "メンバーたちは冒険で回収した宝箱を厳選し、品質を保証した上で販売しています。" 

    def get_items_from_manufacturers(self):
        # get all classes from consumable whose .type is 'Eqpackage'
        package_of_items = []
        
        # Stupid code
        package_of_items.append(consumable.EquipPackage(random.randint(1, 10)))
        package_of_items.append(consumable.EquipPackage2(random.randint(1, 10)))
        package_of_items.append(consumable.EquipPackage3(random.randint(1, 10)))
        package_of_items.append(consumable.EquipPackage4(random.randint(1, 10)))
        package_of_items.append(consumable.EquipPackage5(random.randint(1, 10)))
        package_of_items.append(consumable.EquipPackage6(random.randint(1, 10)))

        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)


class RoyalMint(Shop):
    def __init__(self, name, description):
        super().__init__(name, description)
        if not self.description:
            self.description = "ロイヤルミントは貴金属を中心に取り扱う商店です。" 

    def get_items_from_manufacturers(self):
        # get all classes from consumable whose .type is 'Eqpackage'
        package_of_items = []
        import item
        
        # Stupid code
        package_of_items.append(item.SliverIngot(random.randint(1, 100))) # UnboundLocalError: cannot access local variable 'item' where it is not associated with a value
        package_of_items.append(item.SliverIngot(random.randint(1, 100)))
        package_of_items.append(item.SliverIngot(random.randint(1, 100)))
        package_of_items.append(item.GoldIngot(random.randint(1, 20)))
        package_of_items.append(item.DiamondIngot(random.randint(1, 2)))


        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)

    def decide_discount(self):
        # 1% chance to have a 5% discount, 0.1% chance to have a 10% discount, 0.01% chance to have a 20% discount
        for k, (s, d, f) in self.inventory.copy().items():
            discount = 0
            if random.random() < 0.01:
                discount = 0.05
            elif random.random() < 0.001:
                discount = 0.1
            elif random.random() < 0.0001:
                discount = 0.2
            self.inventory[k] = (s, discount, f)




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

        package_of_items.append(consumable.FoodPackage(random.randint(1, 5)))
        package_of_items.append(consumable.FoodPackage2(random.randint(1, 5)))
        package_of_items.append(consumable.FoodPackage3(random.randint(1, 5)))

        package_of_items.append(consumable.Apple(random.randint(100, 500)))
        package_of_items.append(consumable.Coconuts(random.randint(100, 500)))
        package_of_items.append(consumable.Banana(random.randint(100, 500)))
        package_of_items.append(consumable.Orange(random.randint(100, 500)))
        package_of_items.append(consumable.Kiwi(random.randint(100, 500)))
        package_of_items.append(consumable.Fried_Shrimp(random.randint(100, 500)))
        package_of_items.append(consumable.Pomegranate(random.randint(100, 500)))
        package_of_items.append(consumable.Strawberry(random.randint(100, 500)))
        package_of_items.append(consumable.Orange_Juice_60(random.randint(100, 500)))
        package_of_items.append(consumable.Milk(random.randint(100, 500)))
        package_of_items.append(consumable.Sandwich(random.randint(100, 500)))
        package_of_items.append(consumable.Pancake(random.randint(100, 500)))
        package_of_items.append(consumable.Swiss_Roll(random.randint(100, 500)))
        package_of_items.append(consumable.Chocolate(random.randint(100, 500)))
        package_of_items.append(consumable.Mantou(random.randint(100, 500)))
        package_of_items.append(consumable.Ramen(random.randint(100, 500)))
        package_of_items.append(consumable.Orange_Juice(random.randint(100, 500)))
        package_of_items.append(consumable.Matcha_Roll(random.randint(100, 500)))
        package_of_items.append(consumable.Icecream(random.randint(100, 500)))
        package_of_items.append(consumable.Fries(random.randint(100, 500)))

        # Choose 5 random items from the package_of_items
        if len(package_of_items) < 5:
            raise ValueError(f"Not enough items in the package_of_items, only {len(package_of_items)} items is available.")
        if len(package_of_items) >= 5:
            for item in random.sample(package_of_items, 5):
                self.inventory[item] = (0, 0.0, 0)











