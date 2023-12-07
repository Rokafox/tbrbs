import random


# Design choice: We should not give much power to equipment, the uniqueness of each character should be preserved.
# Normal Distribution with max and min value
def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = int(random.normalvariate(mean, std))
        if value >= min_value and value <= max_value:
            return value

class Equip:
    def __init__(self, name, type, rarity, set="None"):
        self.name = name
        self.type = type
        self.set = set
        self.rarity = rarity
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
        self.upgrade_stars = 0 # 0 to 5
        self.maxhp_extra = 0
        self.atk_extra = 0
        self.def_extra = 0
        self.spd_extra = 0


    def __str__(self):
        return f"{self.name} {self.type} {self.set} {self.rarity} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency} {self.maxhp_extra} {self.atk_extra} {self.def_extra} {self.spd_extra}"

    def __repr__(self):
        return f"{self.name} {self.type} {self.set} {self.rarity} {self.maxhp_percent} {self.atk_percent} {self.def_percent} {self.spd} {self.eva} {self.acc} {self.crit} {self.critdmg} {self.critdef} {self.penetration} {self.maxhp_flat} {self.atk_flat} {self.def_flat} {self.spd_flat} {self.heal_efficiency} {self.maxhp_extra} {self.atk_extra} {self.def_extra} {self.spd_extra}"

    def get_nonzero_nonstring_attributes(self):
        return [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and getattr(self, attr) != 0 and not isinstance(getattr(self, attr), str)]

    def enhance_by_rarity(self):
        if self.rarity == "Common":
            pass
        elif self.rarity == "Uncommon":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.10)
        elif self.rarity == "Rare":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.25)
        elif self.rarity == "Epic":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.45)
        elif self.rarity == "Unique":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 1.70)
        elif self.rarity == "Legendary":
            for attr in dir(self):
                if not callable(getattr(self, attr)) and not attr.startswith("__") and not isinstance(getattr(self, attr), str):
                    setattr(self, attr, getattr(self, attr) * 2.00)
        else:
            raise Exception("Invalid rarity")
        # Convert flat attributes to integer
        self.maxhp_flat = int(self.maxhp_flat)
        self.atk_flat = int(self.atk_flat)
        self.def_flat = int(self.def_flat)
        self.spd_flat = int(self.spd_flat)

    def upgrade_stars_func(self, is_upgrade=True):
        # stars will clamp between 0 and 5
        current_stars = self.upgrade_stars
        if is_upgrade:
            self.upgrade_stars += 1
            self.upgrade_stars = min(self.upgrade_stars, 5)
        else:
            self.upgrade_stars -= 1
            self.upgrade_stars = max(self.upgrade_stars, 0)
        self.update_stats_from_upgrade()
        return current_stars, self.upgrade_stars

    def update_stats_from_upgrade(self):
        rarity = ["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]
        types = ["Accessory", "Weapon", "Armor", "Boots"]
        if self.type == types[0]:
            if self.rarity == rarity[0]:
                self.maxhp_extra = int(200*self.upgrade_stars)
            elif self.rarity == rarity[1]:
                self.maxhp_extra = int(220*self.upgrade_stars)
            elif self.rarity == rarity[2]:
                self.maxhp_extra = int(242*self.upgrade_stars)
            elif self.rarity == rarity[3]:
                self.maxhp_extra = int(266*self.upgrade_stars)
            elif self.rarity == rarity[4]:
                self.maxhp_extra = int(292*self.upgrade_stars)
            elif self.rarity == rarity[5]:
                self.maxhp_extra = int(321*self.upgrade_stars)
        elif self.type == types[1]:
            if self.rarity == rarity[0]:
                self.atk_extra = int(10*self.upgrade_stars)
            elif self.rarity == rarity[1]:
                self.atk_extra = int(11*self.upgrade_stars)
            elif self.rarity == rarity[2]:
                self.atk_extra = int(12*self.upgrade_stars)
            elif self.rarity == rarity[3]:
                self.atk_extra = int(13*self.upgrade_stars)
            elif self.rarity == rarity[4]:
                self.atk_extra = int(14*self.upgrade_stars)
            elif self.rarity == rarity[5]:
                self.atk_extra = int(16*self.upgrade_stars)
        elif self.type == types[2]:
            if self.rarity == rarity[0]:
                self.def_extra = int(10*self.upgrade_stars)
            elif self.rarity == rarity[1]:
                self.def_extra = int(11*self.upgrade_stars)
            elif self.rarity == rarity[2]:
                self.def_extra = int(12*self.upgrade_stars)
            elif self.rarity == rarity[3]:
                self.def_extra = int(13*self.upgrade_stars)
            elif self.rarity == rarity[4]:
                self.def_extra = int(14*self.upgrade_stars)
            elif self.rarity == rarity[5]:
                self.def_extra = int(16*self.upgrade_stars)
        elif self.type == types[3]:
            if self.rarity == rarity[0]:
                self.spd_extra = int(10*self.upgrade_stars)
            elif self.rarity == rarity[1]:
                self.spd_extra = int(11*self.upgrade_stars)
            elif self.rarity == rarity[2]:
                self.spd_extra = int(12*self.upgrade_stars)
            elif self.rarity == rarity[3]:
                self.spd_extra = int(13*self.upgrade_stars)
            elif self.rarity == rarity[4]:
                self.spd_extra = int(14*self.upgrade_stars)
            elif self.rarity == rarity[5]:
                self.spd_extra = int(16*self.upgrade_stars)
        return None


    def fake_dice(self):
        sides = [1, 2, 3, 4, 5, 6]
        weights = [60, 30, 10, 5, 2, 1]
        return random.choices(sides, weights=weights, k=1)[0]

    def generate(self):
        extra_lines_to_generate = self.fake_dice() - 1
        if self.type == "Accessory":
            self.maxhp_flat = normal_distribution(1, 3000, 1000, 500) 
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    # randomly choose a non-flat attribute
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    # generate a random value between (0, 0.3) for the attribute
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    # add the value to the attribute
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Weapon":
            self.atk_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Armor":
            self.def_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        elif self.type == "Boots":
            self.spd_flat = normal_distribution(1, 3000, 1000, 500)*0.05
            if extra_lines_to_generate > 0:
                for i in range(extra_lines_to_generate):
                    attr = random.choice(["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc",
                                            "crit", "critdmg", "critdef", "penetration", "heal_efficiency"])
                    value = normal_distribution(1, 3000, 1000, 500)*0.0001
                    setattr(self, str(attr), getattr(self, str(attr)) + value)
        else:
            raise Exception("Invalid type")
        self.enhance_by_rarity()

    # Print the rune's stats. Only print non-zero stats, including type, rarity.
    def print_stats(self):
        stats = self.rarity + " " + self.type + "\n"
        
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
        star_color = "#3746A7"

        stats = "<font color=" + color + ">" + self.rarity + " " + self.type + "</font>" 
        stats += "<font color=" + star_color + ">" + '★'*int(self.upgrade_stars) + "</font>" + "<font color=" + color + ">" + "\n"
        if self.maxhp_flat != 0:
            stats += "Max HP: " + str(self.maxhp_flat) + "<font color=" + star_color + ">" + f" (+{int(self.maxhp_extra)})" + "</font>" + "\n"
        if self.atk_flat != 0:
            stats += "Attack: " + str(self.atk_flat) + "<font color=" + star_color + ">" + f" (+{int(self.atk_extra)})" + "</font>" + "\n"
        if self.def_flat != 0:
            stats += "Defense: " + str(self.def_flat) + "<font color=" + star_color + ">" + f" (+{int(self.def_extra)})" + "</font>" + "\n"
        if self.spd_flat != 0:
            stats += "Speed: " + str(self.spd_flat) + "<font color=" + star_color + ">" + f" (+{int(self.spd_extra)})" + "</font>" + "\n"
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

        return stats


def generate_equips_list(num, the_type=None) -> list:
    items = []
    for i in range(num):
        types = ["Weapon", "Armor", "Accessory", "Boots"]
        if the_type:
            item = Equip("Item_" + str(i+1), the_type, random.choice(["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]))
        else:
            item = Equip("Item_" + str(i+1), types[i], random.choice(["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]))
        item.generate()
        items.append(item)
    return items

# nd_list = [normal_distribution(1, 3000, 1000, 500) for i in range(1000)]
# avg = sum(nd_list)/len(nd_list)
# print(avg) # near 1000