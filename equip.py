from itertools import cycle
from block import *
import random


def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = random.normalvariate(mean, std)
        if value >= min_value and value <= max_value:
            return value

class Equip(Block):
    def __init__(self, name: str, type: str, rarity: str, eq_set: str="None", level: int=40):
        # lists, changing them likely wont give an error.
        super().__init__(name, "")
        self.type_list = ["Weapon", "Armor", "Accessory", "Boots"] # do not change this list.
        self.eq_set_list = ["None", "Arasaka", "KangTao", "Militech", "NUSA", "Sovereign", 
                            "Snowflake", "Void", "Flute", "Rainbow", "Dawn", "Bamboo", "Rose", "OldRusty",
                            "Liquidation"]
        self.level = level
        self.level_max = 1000
        self.type = type
        self.rarity = rarity
        self.check_eq_set(eq_set)
        self.maxhp_percent = 0.00
        self.atk_percent = 0.00
        self.def_percent = 0.00
        self.spd = 0.00
        self.eva = 0.00
        self.acc = 0.00
        self.crit = 0.00
        self.critdmg = 0.00
        self.critdef = 0.00
        self.penetration = 0.00
        self.heal_efficiency = 0.00
        self.maxhp_flat = 0
        self.atk_flat = 0
        self.def_flat = 0
        self.spd_flat = 0
        # Effect from upgrade
        self.stars_rating = 0 # 0 to 15
        self.stars_rating_max = 15
        self.star_enhence_cost = self.upgrade_stars_rating_cost()
        self.level_cost = self.level_up_cost()
        self.maxhp_extra = 0
        self.atk_extra = 0
        self.def_extra = 0
        self.spd_extra = 0

        self.image = self.process_image_str()
        self.can_be_stacked = False
        self.max_stack = 1

    def to_dict(self):
        return {
            "object": str(self.__class__),
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "type": self.type,
            "eq_set": self.eq_set,
            "level": self.level,
            "maxhp_percent": self.maxhp_percent,
            "atk_percent": self.atk_percent,
            "def_percent": self.def_percent,
            "spd": self.spd,
            "eva": self.eva,
            "acc": self.acc,
            "crit": self.crit,
            "critdmg": self.critdmg,
            "critdef": self.critdef,
            "penetration": self.penetration,
            "heal_efficiency": self.heal_efficiency,
            "maxhp_flat": self.maxhp_flat,
            "atk_flat": self.atk_flat,
            "def_flat": self.def_flat,
            "spd_flat": self.spd_flat,
            "market_value": self.market_value,
            "image": self.image,
            "stars_rating": self.stars_rating,
            "stars_rating_max": self.stars_rating_max,
            "star_enhence_cost": self.star_enhence_cost,
            "level_cost": self.level_cost,
            "maxhp_extra": self.maxhp_extra,
            "atk_extra": self.atk_extra,
            "def_extra": self.def_extra,
            "spd_extra": self.spd_extra
        }


    def get_raritytypeeqset_list(self):
        return self.rarity_list, self.type_list, self.eq_set_list

    def __str__(self):
        eq_set_str = "" if self.eq_set == "None" else f"{self.eq_set} "
        return f"lv{self.level} {eq_set_str}{self.rarity} {self.type}"

    def process_image_str(self) -> str:
        # string generated from self.eq_set and self.type, for example, NUSA_Armor
        if self.eq_set == "None":
            return "Generic" + "_" + self.type
        elif self.eq_set == "Void":
            return "void"
        else:
            return self.eq_set + "_" + self.type

    def check_eq_set(self, name):
        if name in self.eq_set_list:
            self.eq_set = name
        else:
            raise Exception("Invalid equipment set")

    def enhance_by_rarity(self):
        values = [1.00, 1.10, 1.25, 1.45, 1.70, 2.00]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, values)}
        multiplier = rarity_multipliers.get(self.rarity)
        if multiplier is None:
            raise Exception("Invalid rarity")

        for attr in dir(self):
            if attr in ["atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency", "maxhp_flat", "atk_flat", "def_flat", "spd_flat"]:
                if getattr(self, attr) == 0:
                    continue
                # print(f"Enhancing {attr} by {multiplier}, old value: {getattr(self, attr)}, new value: {getattr(self, attr) * multiplier}")
                setattr(self, attr, getattr(self, attr) * multiplier)
        self.estimate_market_price()

    def upgrade_stars_func(self, is_upgrade=True):
        # stars will clamp between 0 and 15
        current_stars = self.stars_rating
        if is_upgrade:
            self.stars_rating += 1
            self.stars_rating = min(self.stars_rating, 15)
        else:
            self.stars_rating -= 1
            self.stars_rating = max(self.stars_rating, 0)
        self.update_stats_from_upgrade()
        self.star_enhence_cost = self.upgrade_stars_rating_cost()
        return current_stars, self.stars_rating

    def stars_effect(self, n) -> float:
        return 1 + (self.stars_rating ** n) / (self.stars_rating_max ** n)

    def upgrade_stars_rating_cost(self) -> int:
        if self.stars_rating == self.stars_rating_max:
            return 0
        values = [1.00, 1.10, 1.20, 1.30, 1.40, 1.60]
        rarity_values = {rarity: value for rarity, value in zip(self.rarity_list, values)}
        rarity_multiplier = rarity_values.get(self.rarity, 1.0)
        return int(2000 * (self.stars_rating + 1) ** 2 * rarity_multiplier)

    def update_stats_from_upgrade(self):
        values = [1.00, 1.10, 1.20, 1.30, 1.40, 1.60]
        rarity_values = {rarity: value for rarity, value in zip(self.rarity_list, values)}

        type_bonus = {
            self.type_list[2]: ("maxhp_extra", 200 / 40 * self.level),
            self.type_list[0]: ("atk_extra", 10 / 40 * self.level),
            self.type_list[1]: ("def_extra", 10 / 40 * self.level),
            self.type_list[3]: ("spd_extra", 10 / 40 * self.level)
        }

        if self.type in type_bonus:
            stat, base_value = type_bonus[self.type]
            rarity_multiplier = rarity_values.get(self.rarity, 1.0)
            bonus_value = base_value * self.stars_rating * rarity_multiplier
            setattr(self, stat, bonus_value * self.stars_effect(3))

        self.estimate_market_price()
        return None

    def fake_dice(self):
        sides = [1, 2, 3, 4, 5, 6]
        weights = [60, 30, 10, 5, 2, 1]
        return random.choices(sides, weights=weights, k=1)[0]

    def generate(self):
        level = self.level
        extra_lines_to_generate = self.fake_dice() - 1
        
        if self.type == self.type_list[2]:
            self.maxhp_flat = max(normal_distribution(1, 3000, 1000, 500), 1)
            self.maxhp_flat /= 40
            self.maxhp_flat *= level
        elif self.type == self.type_list[0]:
            self.atk_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
            self.atk_flat /= 40
            self.atk_flat *= level
        elif self.type == self.type_list[1]:
            self.def_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
            self.def_flat /= 40
            self.def_flat *= level
        elif self.type == self.type_list[3]:
            self.spd_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
            self.spd_flat /= 40
            self.spd_flat *= level
        else:
            raise Exception("Invalid type")
        
        if extra_lines_to_generate > 0:
            for i in range(extra_lines_to_generate):
                attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                      "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                value = normal_distribution(1, 3000, 1000, 500) * 0.0001
                setattr(self, attr, getattr(self, attr) + value)
        
        self.enhance_by_rarity()


    def generate_void(self):
        """
        Only for Void Force on monsters
        """
        level = self.level
        if level < 200:
            extra_lines_to_generate = 1
        elif 200 <= level < 400:
            extra_lines_to_generate = 1
        elif 400 <= level < 600:
            extra_lines_to_generate = 2
        elif 600 <= level < 800:
            extra_lines_to_generate = 3
        elif 800 <= level < 1000:
            extra_lines_to_generate = 4
        elif 1000 <= level < 2000:
            extra_lines_to_generate = 5
        elif 2000 <= level:
            extra_lines_to_generate = 5
        else:
            extra_lines_to_generate = 0
        
        if self.type == self.type_list[2]:
            self.maxhp_flat = max(normal_distribution(1, 5000, 2000, 500), 1)
            self.maxhp_flat /= 40
            self.maxhp_flat *= level
        elif self.type == self.type_list[0]:
            self.atk_flat = max(normal_distribution(1, 3000, 1200, 500) * 0.05, 1)
            self.atk_flat /= 40
            self.atk_flat *= level
        elif self.type == self.type_list[1]:
            self.def_flat = max(normal_distribution(1, 3000, 1200, 500) * 0.05, 1)
            self.def_flat /= 40
            self.def_flat *= level
        elif self.type == self.type_list[3]:
            self.spd_flat = max(normal_distribution(1, 3000, 1200, 500) * 0.05, 1)
            self.spd_flat /= 40
            self.spd_flat *= level
        else:
            raise Exception("Invalid type")
        
        attributes = ["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                      "crit", "critdmg", "critdef", "penetration", "heal_efficiency"]
        if extra_lines_to_generate > 0:
            selected_attributes = random.sample(attributes, extra_lines_to_generate)
            
            for attr in selected_attributes:
                value = normal_distribution(1, 2000, 500, 500) * 0.00015
                setattr(self, attr, getattr(self, attr) + value)
        
        self.enhance_by_rarity()


    def level_change(self, increment):
        prev_level = self.level
        new_level = self.level + increment
        self.level = max(min(new_level, self.level_max), 1)
        
        if self.type == self.type_list[2]:
            self.maxhp_flat = self.maxhp_flat / prev_level # base value is divided by previous level
            self.maxhp_flat *= new_level
        elif self.type == self.type_list[0]:
            self.atk_flat = self.atk_flat / prev_level
            self.atk_flat *= new_level
        elif self.type == self.type_list[1]:
            self.def_flat = self.def_flat / prev_level
            self.def_flat *= new_level
        elif self.type == self.type_list[3]:
            self.spd_flat = self.spd_flat / prev_level
            self.spd_flat *= new_level
        else:
            raise Exception("Invalid type")
        
        self.update_stats_from_upgrade()
        self.level_cost = self.level_up_cost()
        return prev_level, new_level
    
    def level_up_cost(self):
        if self.level == self.level_max:
            return 0
        base_cost = 0.01  
        return int(base_cost * (self.level ** 1.955))  # Approximatly 2500000 from 1 to 1000
    
    def level_up_as_possible(self, funds: int):
        previous_funds = funds
        cost = 0
        while self.level_cost <= funds and self.level < self.level_max:
            funds -= self.level_cost
            self.level_change(1)
        cost = previous_funds - funds
        return funds, cost

    def estimate_market_price(self):
        base_value = sum([self.maxhp_flat, self.atk_flat * 20, self.def_flat * 20, self.spd_flat * 20])
        base_value_b = sum([self.maxhp_percent * 200, self.atk_percent * 4000, self.def_percent * 4000, self.spd * 4000, 
                            self.eva * 4000, self.acc * 4000, self.crit * 4000, 
                          self.critdmg * 4000, self.critdef * 4000, self.penetration * 6000, self.heal_efficiency * 3000])
        base_value_b /= 40
        base_value_b *= self.level
        base_value_c = sum([self.maxhp_extra * 0.6, self.atk_extra * 12, self.def_extra * 12, self.spd_extra * 12])
        rarity_values = [1.00, 1.10, 1.25, 1.45, 1.70, 2.00]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, rarity_values)}
        rarity_multiplier = rarity_multipliers.get(self.rarity)
        random_multiplier = random.uniform(0.95, 1.05)
        if self.eq_set == "None":
            self.market_value = (base_value + base_value_b + base_value_c) * rarity_multiplier * random_multiplier * 0.66
            return self.market_value
        else:
            self.market_value = (base_value + base_value_b + base_value_c) * rarity_multiplier * random_multiplier 
            return self.market_value

    def print_stats(self):
        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "
        stats = "lv" + str(self.level) + " " + eq_set_str() + self.rarity + " " + self.type + "\n"
        
        if self.maxhp_flat != 0:
            stats += "Max HP: " + str(self.maxhp_flat) + "\n"
        if self.atk_flat != 0:
            stats += "Attack: " + str(self.atk_flat) + "\n"
        if self.def_flat != 0:
            stats += "Defense: " + str(self.def_flat) + "\n"
        if self.spd_flat != 0:
            stats += "Speed: " + str(self.spd_flat) + "\n"
        if self.maxhp_percent != 0:
            stats += "Max HP: " + "{:.2f}%".format(self.maxhp_percent*100) + "\n"
        if self.atk_percent != 0:
            stats += "Attack: " + "{:.2f}%".format(self.atk_percent*100) + "\n"
        if self.def_percent != 0:
            stats += "Defense: " + "{:.2f}%".format(self.def_percent*100) + "\n"
        if self.spd != 0:
            stats += "Speed: " + "{:.2f}%".format(self.spd*100) + "\n"
        if self.eva != 0:
            stats += "Evasion: " + "{:.2f}%".format(self.eva*100) + "\n"
        if self.acc != 0:
            stats += "Accuracy: " + "{:.2f}%".format(self.acc*100) + "\n"
        if self.crit != 0:
            stats += "Critical Chance: " + "{:.2f}%".format(self.crit*100) + "\n"
        if self.critdmg != 0:
            stats += "Critical Damage: " + "{:.2f}%".format(self.critdmg*100) + "\n"
        if self.critdef != 0:
            stats += "Critical Defense: " + "{:.2f}%".format(self.critdef*100) + "\n"
        if self.penetration != 0:
            stats += "Penetration: " + "{:.2f}%".format(self.penetration*100) + "\n"
        if self.heal_efficiency != 0:
            stats += "Heal Efficiency: " + "{:.2f}%".format(self.heal_efficiency*100) + "\n"
        
        return stats


    def print_stats_html(self, include_market_price=True):
        match self.rarity:
            case "Common":
                color = "#2c2c2c"
            case "Uncommon":
                color = "#B87333"
            case "Rare":
                color = "#FF0000"
            case "Epic":
                color = "#659a00"
            case "Unique":
                color = "#9966CC"
            case "Legendary":
                color = "#21d6ff"
        star_color = "#3746A7" # blue
        market_color = "#202d82" # blue
        star_color_purple = "#9B30FF" # purple
        star_color_red = "#FF0000" # red
        star_color_gold = "#FFD700" # gold
        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "

        if not self.eq_set == "Void":
            stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>" + "lv" + str(self.level) + " " + eq_set_str() + self.rarity + " " + self.type + "</b></font></shadow>\n"
        else:
            stats = f"Void Force\n"
        if self.stars_rating > 0:
            stats += "<font color=" + star_color + ">" + '★'*min(int(self.stars_rating), 5) + "</font>" 
        if self.stars_rating > 5:
            stats += "<font color=" + star_color_purple + ">" + '★'*min(int(self.stars_rating-5), 5) + "</font>"
        if self.stars_rating > 10:
            stats += "<font color=" + star_color_red + ">" + '★'*min(int(self.stars_rating-10), 5) + "</font>" 
        stats += "\n" if self.stars_rating > 0 else ""
        stats += "<font color=" + color + ">"
        def star_font_color() -> str:
            if self.stars_rating <= 5:
                return star_color
            elif 5 < self.stars_rating <= 10:
                return star_color_purple
            elif 10 < self.stars_rating <= 15:
                return star_color_red
            else:
                return star_color_gold

        def add_stat_with_color(stat_name: str, stat_value: int, stat_extra: int) -> str:
            return stat_name + ": " + str(stat_value) + "<font color=" + star_font_color() + ">" + f" (+{stat_extra})" + "</font>" + "\n"

        if self.maxhp_flat != 0:
            stats += add_stat_with_color("Max HP", round(self.maxhp_flat, 3), self.maxhp_extra)
        if self.atk_flat != 0:
            stats += add_stat_with_color("Attack", round(self.atk_flat, 3), self.atk_extra)
        if self.def_flat != 0:
            stats += add_stat_with_color("Defense", round(self.def_flat, 3), self.def_extra)
        if self.spd_flat != 0:
            stats += add_stat_with_color("Speed", round(self.spd_flat, 3), self.spd_extra)
        if self.maxhp_percent != 0:
            stats += "Max HP: " + "{:.2f}%".format(self.maxhp_percent*100) + "\n"
        if self.atk_percent != 0:
            stats += "Attack: " + "{:.2f}%".format(self.atk_percent*100) + "\n"
        if self.def_percent != 0:
            stats += "Defense: " + "{:.2f}%".format(self.def_percent*100) + "\n"
        if self.spd != 0:
            stats += "Speed: " + "{:.2f}%".format(self.spd*100) + "\n"
        if self.eva != 0:
            stats += "Evasion: " + "{:.2f}%".format(self.eva*100) + "\n"
        if self.acc != 0:
            stats += "Accuracy: " + "{:.2f}%".format(self.acc*100) + "\n"
        if self.crit != 0:
            stats += "Critical Chance: " + "{:.2f}%".format(self.crit*100) + "\n"
        if self.critdmg != 0:
            stats += "Critical Damage: " + "{:.2f}%".format(self.critdmg*100) + "\n"
        if self.critdef != 0:
            stats += "Critical Defense: " + "{:.2f}%".format(self.critdef*100) + "\n"
        if self.penetration != 0:
            stats += "Penetration: " + "{:.2f}%".format(self.penetration*100) + "\n"
        if self.heal_efficiency != 0:
            stats += "Heal Efficiency: " + "{:.2f}%".format(self.heal_efficiency*100) + "</font>\n"
        if self.eq_set == "Void":
            return stats
        if self.stars_rating < self.stars_rating_max:
            stats += f"<font color=#AF6E4D>Stars enhancement cost: {self.star_enhence_cost} </font>\n"
        else:
            stats += f"<font color=#AF6E4D>Stars enhancement cost: MAX </font>\n"
        if self.level < self.level_max:
            stats += f"<font color=#702963>Level up cost: {self.level_cost} </font>\n"
        else:
            stats += f"<font color=#702963>Level up cost: MAX </font>\n"
        if include_market_price:
            stats += "<font color=" + market_color + ">" + f"Market Price: {int(self.market_value)}" + "</font>\n"
        stats += "</font>"

        return stats


def generate_equips_list(num=1, locked_type=None, locked_eq_set=None, locked_rarity=None, random_full_eqset=False, 
                         eq_level=40, include_void=False) -> list:
    items = []
    rarity_pool, types, eq_set_pool = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()
    if not include_void:
        eq_set_pool.remove("Void")
    types_cycle = cycle(types)
    if random_full_eqset:
        random_eq_set = random.choice(eq_set_pool[1:])
    for i in range(num):
        item_type = locked_type if locked_type else next(types_cycle)
        if random_full_eqset:
            item_eq_set = random_eq_set
        else:
            item_eq_set = locked_eq_set if locked_eq_set else random.choice(eq_set_pool)
        item_rarity = locked_rarity if locked_rarity else random.choice(rarity_pool)

        item = Equip(f"Item_{i + 1}", item_type, item_rarity, item_eq_set, level=eq_level)
        if include_void and item_eq_set == "Void":
            item.generate_void()
        else:
            item.generate()
        items.append(item)

    return items

def adventure_generate_random_equip_with_weight() -> Equip:
    rarity_pool, types, eq_set_pool = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()
    eq_set_pool.remove("Void")
    rarity_weights = list(range(len(rarity_pool), 0, -1)) 
    eq_set_weights = [len(eq_set_pool)] + [1] * (len(eq_set_pool) - 1)
 
    rarity = random.choices(rarity_pool, weights=rarity_weights, k=1)[0]
    type = random.choice(types)
    eq_set = random.choices(eq_set_pool, weights=eq_set_weights, k=1)[0]
    item = Equip("Foo", type, rarity, eq_set, level=1)
    item.generate()
    return item



# nd_list = [normal_distribution(1, 3000, 1000, 500) for i in range(1000)]
# avg = sum(nd_list)/len(nd_list)
# print(avg) # near 1000
# print(generate_equips_list(4, locked_eq_set="Arasaka"))
