import random


# Design choice: We should not give much power to equipment, the uniqueness of each character should be preserved.
# Normal Distribution with max and min value
def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = int(random.normalvariate(mean, std))
        if value >= min_value and value <= max_value:
            return value

class Equip:
    def __init__(self, name, type, rarity, eq_set="None"):
        self.name = name
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
        self.upgrade_stars = 0 # 0 to 15
        self.upgrade_stars_max = 15
        self.maxhp_extra = 0
        self.atk_extra = 0
        self.def_extra = 0
        self.spd_extra = 0


    def __str__(self):
        return f"{self.name} {self.type} {self.eq_set} {self.rarity} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency} {self.maxhp_extra} {self.atk_extra} {self.def_extra} {self.spd_extra}"

    def __repr__(self):
        return f"{self.name} {self.type} {self.eq_set} {self.rarity} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency} {self.maxhp_extra} {self.atk_extra} {self.def_extra} {self.spd_extra}"

    def get_nonzero_nonstring_attributes(self):
        return [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and getattr(self, attr) != 0 and not isinstance(getattr(self, attr), str)]

    def check_eq_set(self, name):
        if name in ["None", "Arasaka", "KangTao", "Militech", "NUSA", "Sovereign"]:
            self.eq_set = name
        else:
            raise Exception("Invalid equipment set")

    def enhance_by_rarity(self):
        rarity_multipliers = {
            "Common": 1.00,
            "Uncommon": 1.10,
            "Rare": 1.25,
            "Epic": 1.45,
            "Unique": 1.70,
            "Legendary": 2.00
        }

        multiplier = rarity_multipliers.get(self.rarity)
        if multiplier is None:
            raise Exception("Invalid rarity")

        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str) and not attr.startswith("upgrade_stars"):
                setattr(self, attr, getattr(self, attr) * multiplier)

        # Convert flat attributes to integer
        # No longer needed as float is needed for scalability.
        # for attr in ["maxhp_flat", "atk_flat", "def_flat", "spd_flat"]:
        #     if hasattr(self, attr):
        #         setattr(self, attr, int(getattr(self, attr)))

    def upgrade_stars_func(self, is_upgrade=True):
        # stars will clamp between 0 and 15
        current_stars = self.upgrade_stars
        if is_upgrade:
            self.upgrade_stars += 1
            self.upgrade_stars = min(self.upgrade_stars, 15)
        else:
            self.upgrade_stars -= 1
            self.upgrade_stars = max(self.upgrade_stars, 0)
        self.update_stats_from_upgrade()
        return current_stars, self.upgrade_stars

    def stars_effect(self, n) -> float:
        # stars will clamp between 0 and self.upgrade_stars_max, 
        # Return value start from 1.0, as stars closer to self.upgrade_stars_max, the return value will be closer to 2.0
        # However, the graph should not be linear, it climbs faster near the end, slower at the beginning
        return 1 + (self.upgrade_stars ** n) / (self.upgrade_stars_max ** n)

    def update_stats_from_upgrade(self):
        rarity_values = {
            "Common": 1.0,
            "Uncommon": 1.1,
            "Rare": 1.2,
            "Epic": 1.3,
            "Unique": 1.4,
            "Legendary": 1.6
        }

        type_bonus = {
            "Accessory": ("maxhp_extra", 200),
            "Weapon": ("atk_extra", 10),
            "Armor": ("def_extra", 10),
            "Boots": ("spd_extra", 10)
        }

        if self.type in type_bonus:
            stat, base_value = type_bonus[self.type]
            rarity_multiplier = rarity_values.get(self.rarity, 1.0)
            bonus_value = int(base_value * self.upgrade_stars * rarity_multiplier)
            setattr(self, stat, bonus_value * self.stars_effect(3))

        return None

    def fake_dice(self):
        sides = [1, 2, 3, 4, 5, 6]
        weights = [60, 30, 10, 5, 2, 1]
        return random.choices(sides, weights=weights, k=1)[0]

    def generate(self):
        extra_lines_to_generate = self.fake_dice() - 1
        
        if self.type == "Accessory":
            self.maxhp_flat = max(normal_distribution(1, 3000, 1000, 500), 1)
        elif self.type == "Weapon":
            self.atk_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
        elif self.type == "Armor":
            self.def_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
        elif self.type == "Boots":
            self.spd_flat = max(normal_distribution(1, 3000, 1000, 500) * 0.05, 1)
        else:
            raise Exception("Invalid type")
        
        if extra_lines_to_generate > 0:
            for i in range(extra_lines_to_generate):
                attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                      "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                value = normal_distribution(1, 3000, 1000, 500) * 0.0001
                setattr(self, attr, getattr(self, attr) + value)
        
        self.enhance_by_rarity()

    # Print the rune's stats. Only print non-zero stats, including type, rarity.
    def print_stats(self):
        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "
        stats = eq_set_str() + self.rarity + " " + self.type + "\n"
        
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


    def print_stats_html(self):
        color = ""
        if self.rarity == "Common":
            color = "#2c2c2c"
        elif self.rarity == "Uncommon":
            color = "#B87333"
        elif self.rarity == "Rare":
            color = "#FF0000"
        elif self.rarity == "Epic":
            color = "#659a00"
        elif self.rarity == "Unique":
            color = "#9966CC"
        elif self.rarity == "Legendary":
            color = "#21d6ff"
        star_color = "#3746A7" # blue
        star_color_purple = "#9B30FF" # purple
        star_color_red = "#FF0000" # red
        star_color_gold = "#FFD700" # gold
        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "

        stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>" + eq_set_str() + self.rarity + " " + self.type + "</b></font></shadow>\n"
        if self.upgrade_stars > 0:
            stats += "<font color=" + star_color + ">" + '★'*min(int(self.upgrade_stars), 5) + "</font>" 
        if self.upgrade_stars > 5:
            stats += "<font color=" + star_color_purple + ">" + '★'*min(int(self.upgrade_stars-5), 5) + "</font>"
        if self.upgrade_stars > 10:
            stats += "<font color=" + star_color_red + ">" + '★'*min(int(self.upgrade_stars-10), 5) + "</font>" 
        stats += "\n" if self.upgrade_stars > 0 else ""
        stats += "<font color=" + color + ">"
        def star_font_color() -> str:
            if self.upgrade_stars <= 5:
                return star_color
            elif 5 < self.upgrade_stars <= 10:
                return star_color_purple
            elif 10 < self.upgrade_stars <= 15:
                return star_color_red
            else:
                return star_color_gold

        def add_stat_with_color(stat_name: str, stat_value: int, stat_extra: int) -> str:
            return stat_name + ": " + str(stat_value) + "<font color=" + star_font_color() + ">" + f" (+{int(stat_extra)})" + "</font>" + "\n"

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
        stats += "</font>"

        return stats


def generate_equips_list(num, the_type=None, force_eqset="All") -> list:
    items = []
    for i in range(num):
        types = ["Weapon", "Armor", "Accessory", "Boots"]
        if force_eqset == "All":
            eq_set_pool = ["None", "Arasaka", "KangTao", "Militech", "NUSA", "Sovereign"]
        else:
            eq_set_pool = [force_eqset]
        if the_type:
            item = Equip("Item_" + str(i+1), the_type, random.choice(["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]), random.choice(eq_set_pool))
        else:
            item = Equip("Item_" + str(i+1), types[i], random.choice(["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]), random.choice(eq_set_pool))
        item.generate()
        items.append(item)
    return items

# nd_list = [normal_distribution(1, 3000, 1000, 500) for i in range(1000)]
# avg = sum(nd_list)/len(nd_list)
# print(avg) # near 1000