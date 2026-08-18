from itertools import cycle
from block import *
import random
from equip_set import EQ_SET_REGISTRY 


def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = random.normalvariate(mean, std)
        if value >= min_value and value <= max_value:
            return value

class Equip(Block):
    def __init__(self, name: str, type: str, rarity: str, eq_set: str="None", level: int=40):
        super().__init__(name, "")
        self.type_list = ["Weapon", "Armor", "Accessory", "Boots"] # do not change this list.
        self.eq_set_list = ["None", "Arasaka", "KangTao", "Militech", "NUSA", "Sovereign", 
                            "Snowflake", "Void", "Flute", "Rainbow", "Dawn", "Bamboo", "Rose", "OldRusty",
                            "Liquidation", "Cosmic", "Newspaper", "Cloud", "Purplestar", "1987", "7891", "Freight",
                            "Runic", "Grassland", "Tigris", "Armygreen", "Armydesert"]
        # self.eq_set_list = ["None", "Void", "Statstestatk", "Statstestdef", "Statstestspd", "Statstestmaxhp", "Statstestcrit",
        #                     "Statstestcritdmg", "Statstesthe", "Statstestpen", "Statstesteva", "Statstestacc", "Statstestcritdef"]
        self.level = level
        self.level_max = 1000
        self.type = type
        self.rarity = rarity
        self.eq_set = eq_set
        if self.eq_set not in self.eq_set_list:
            raise Exception("Invalid eq_set")
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
        self.market_value = 0
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

        self.set_effect_is_acive: int = 0

        self.owner: str | None = None
        self.for_attacker_value = 0
        self.for_support_value = 0

        self._mainstat_potential = 0 # value calculated when stat being generated.


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
            "spd_extra": self.spd_extra,
            "owner": self.owner,
            "_mainstat_potential": self._mainstat_potential
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

    def enhance_by_rarity(self):
        values = [1.00, 1.10, 1.25, 1.45, 1.70, 2.00]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, values)}
        multiplier = rarity_multipliers.get(self.rarity)
        if multiplier is None:
            raise Exception("Invalid rarity")

        for attr in dir(self):
            if attr in ["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency", "maxhp_flat", "atk_flat", "def_flat", "spd_flat"]:
                if getattr(self, attr) == 0:
                    continue
                # print(f"Enhancing {attr} by {multiplier}, old value: {getattr(self, attr)}, new value: {getattr(self, attr) * multiplier}")
                setattr(self, attr, getattr(self, attr) * multiplier)
        self.estimate_market_price()
        self.for_attacker_value = self.estimate_value_for_attacker()
        self.for_support_value = self.estimate_value_for_support()

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
        return int(2000 * (self.stars_rating + 1) ** 1.90 * rarity_multiplier)

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

    def fake_dice(self, tier: str) -> int:
        sides = [1, 2, 3, 4, 5, 6, 7, 8]
        weights = {
            "bad": [60, 30, 10, 5, 2, 1, 0, 0],
            "normal": [30, 40, 20, 10, 5, 2, 1, 0],
            "good": [10, 20, 30, 20, 10, 5, 2, 1],
        }
        return random.choices(sides, weights=weights[tier], k=1)[0]

    def generate(self, tier: str):
        """
        Generate stats. [tier] can be "bad", "normal", or "good". 
        The higher the tier, the more likely to generate more stats.
        """
        level = self.level
        # All substats are reset to 0
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
        substats = ["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency"]
        lines_already_have = []
        lines_already_generated = 0
        for ss in substats:
            if eval(f"self.{ss}") > 0:
                lines_already_generated += 1
                lines_already_have.append(ss)

        extra_lines_to_generate = self.fake_dice(tier) - 1
        mainstats_nd_base_max_allowed_value = 4000

        match tier:
            case "bad": 
                mainstats_nd_base_value = (1, mainstats_nd_base_max_allowed_value, 1000, 1000)
            case "normal":
                mainstats_nd_base_value = (250, mainstats_nd_base_max_allowed_value, 1250, 1000)
            case "good":
                mainstats_nd_base_value = (500, mainstats_nd_base_max_allowed_value, 1500, 1000)
            case _:
                raise Exception("Invalid tier")
        
        if self.type == self.type_list[2]:  # Accessory
            v = normal_distribution(*mainstats_nd_base_value)
            self._mainstat_potential = v / mainstats_nd_base_max_allowed_value
            v /= 40
            v *= level
            self.maxhp_flat = v

        elif self.type == self.type_list[0]: # Weapon
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (mainstats_nd_base_max_allowed_value * 0.05)
            v /= 40
            v *= level
            self.atk_flat = v
        elif self.type == self.type_list[1]: # Armor
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (mainstats_nd_base_max_allowed_value * 0.05)
            v /= 40
            v *= level
            self.def_flat = v
        elif self.type == self.type_list[3]: # Boots
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (mainstats_nd_base_max_allowed_value * 0.05)
            v /= 40
            v *= level
            self.spd_flat = v
        else:
            raise Exception("Invalid type")
        
        if extra_lines_to_generate > 0:
            for i in range(extra_lines_to_generate):
                if len(lines_already_have) < 6:
                    attr = random.choice(substats)
                    if attr not in lines_already_have:
                        lines_already_have.append(attr)
                else:
                    attr = random.choice(lines_already_have)
                if attr == "penetration":
                    value = normal_distribution(1, 4000, 400, 600) * 0.0001
                elif attr == "def_percent":
                    value = normal_distribution(1, 4000, 1200, 1000) * 0.0001
                elif attr == "eva":
                    value = normal_distribution(1, 4000, 750, 800) * 0.0001
                else:
                    value = normal_distribution(1, 4000, 1000, 1000) * 0.0001
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
        elif 2000 <= level < 2500:
            extra_lines_to_generate = 6
        elif 2500 <= level:
            extra_lines_to_generate = 7
        else:
            extra_lines_to_generate = 0
        
        if self.type == self.type_list[2]:
            self.maxhp_flat = max(normal_distribution(1, 4000, 1200, 1000), 1)
            self.maxhp_flat /= 40
            self.maxhp_flat *= level
        elif self.type == self.type_list[0]:
            self.atk_flat = max(normal_distribution(1, 3000, 1200, 500) * 0.05, 1)
            self.atk_flat /= 40
            self.atk_flat *= level
        elif self.type == self.type_list[1]:
            self.def_flat = max(normal_distribution(1, 4000, 1600, 666) * 0.05, 1)
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
                if attr == "penetration":
                    value = normal_distribution(1, 2000, 400, 500) * 0.0001
                elif attr == "def_percent":
                    value = normal_distribution(1, 2000, 800, 500) * 0.00015
                elif attr == "eva":
                    value = normal_distribution(1, 2000, 400, 500) * 0.0001
                else:
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
    
    def level_up_cost(self, current_level=None):
        if not current_level:
            current_level = self.level
        if current_level == self.level_max:
            return 0
        base_cost = 0.01  
        return int(base_cost * (current_level ** 1.985))  # 3015329 from 1 to 1000
    
    def level_up_cost_multilevel(self, levels: int) -> int:
        # calculate the cost of leveling up multiple levels from current level
        if levels < 0:
            raise Exception("Invalid levels")

        total_cost = 0
        current_level = self.level
        for i in range(levels):
            if current_level >= self.level_max:
                break
            total_cost += self.level_up_cost(current_level)
            current_level += 1

        return total_cost

    
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
        base_value_b = sum([self.maxhp_percent * 200, self.atk_percent * 4000, self.def_percent * 3333, self.spd * 4000, 
                            self.eva * 4400, self.acc * 4000, self.crit * 4000, 
                          self.critdmg * 4000, self.critdef * 4000, self.penetration * 8000, self.heal_efficiency * 3000])
        base_value_b /= 40
        base_value_c = sum([self.maxhp_extra * 0.6, self.atk_extra * 12, self.def_extra * 12, self.spd_extra * 12])
        rarity_values = [1.00, 1.10, 1.25, 1.45, 1.70, 2.00]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, rarity_values)}
        rarity_multiplier = rarity_multipliers.get(self.rarity)
        random_multiplier = random.uniform(0.95, 1.05)
        level_multiplier = max(1, 0.006 * (self.level ** 1.333))
        if self.eq_set == "None":
            self.market_value = (base_value + base_value_b + base_value_c) * rarity_multiplier * random_multiplier * 0.66
            self.market_value *= level_multiplier
            return self.market_value
        else:
            self.market_value = (base_value + base_value_b + base_value_c) * rarity_multiplier * random_multiplier
            self.market_value *= level_multiplier 
            return self.market_value

    def estimate_value_for_attacker(self):
        """
        How much does this equipment worth for an attacker?
        An attacker would need atk_flat, atk_percent, crit, critdmg, penetration, spd_flat, spd, acc
        Score is decided by trial and error
        """
        rarity_values = [1.00, 1.15, 1.30, 1.45, 1.60, 1.75]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, rarity_values)}
        rarity_multiplier = rarity_multipliers.get(self.rarity)

        total_score = 0
        atk_score = (5 + self.atk_flat * rarity_multiplier / self.level) * (1 + self.atk_percent) - 5
        spd_score = (5 + self.spd_flat * rarity_multiplier / self.level) * (1 + self.spd) - 5
        # after some testing, 100% crit is roughly worth 2.5 points of atk
        # so 1% crit is worth 2.5 / 100 points = 0.025 points
        crit_score = self.crit * 100 * 0.025
        # 150% critdmg is worth 2.5 points of atk
        # so 1% critdmg is worth 2.5 / 150 points = 0.016666666666666666 points
        critdmg_score = self.critdmg * 100 * 0.016666666666666666
        # penetration: 50% for 2.5
        # so 1% penetration is worth 2.5 / 50 points = 0.05 points
        penetration_score = self.penetration * 100 * 0.05
        # acc: 75% for 2.5
        # so 1% acc is worth 2.5 / 75 points = 0.03333333333333333 points
        acc_score = self.acc * 100 * 0.03333333333333333

        def_score = (5 + self.def_flat * rarity_multiplier / self.level) * (1 + self.def_percent) - 5
        maxhp_score = (5 + self.maxhp_flat * rarity_multiplier / self.level) * (1 + self.maxhp_percent) - 5
        maxhp_score = maxhp_score / 20
        # eva: 50% for 2.5
        # so 1% eva is worth 2.5 / 50 points = 0.05 points
        eva_score = self.eva * 100 * 0.05
        # critdef: 150% for 2.5
        # so 1% critdef is worth 2.5 / 150 points = 0.016666666666666666 points
        critdef_score = self.critdef * 100 * 0.016666666666666666
        # heal_efficiency: 150% for 2.5
        he_score = self.heal_efficiency * 100 * 0.016666666666666666


        attack_total_score = atk_score + spd_score + crit_score + critdmg_score + penetration_score + acc_score
        support_total_score = def_score + maxhp_score + eva_score + critdef_score + he_score

        total_score = attack_total_score + support_total_score * 0.33
        assert total_score >= 0
        return total_score 


    def estimate_value_for_support(self):
        """
        A support would need maxhp_flat, maxhp_percent, def_flat, def_percent, critdef, eva, heal_efficiency, spd_flat, spd
        Score is decided by trial and error
        """
        rarity_values = [1.00, 1.15, 1.30, 1.45, 1.60, 1.75]
        rarity_multipliers = {rarity: value for rarity, value in zip(self.rarity_list, rarity_values)}
        rarity_multiplier = rarity_multipliers.get(self.rarity)

        total_score = 0
        atk_score = (5 + self.atk_flat * rarity_multiplier / self.level) * (1 + self.atk_percent) - 5
        spd_score = (5 + self.spd_flat * rarity_multiplier / self.level) * (1 + self.spd) - 5
        crit_score = self.crit * 100 * 0.025
        critdmg_score = self.critdmg * 100 * 0.016666666666666666
        penetration_score = self.penetration * 100 * 0.05
        acc_score = self.acc * 100 * 0.03333333333333333

        def_score = (5 + self.def_flat * rarity_multiplier / self.level) * (1 + self.def_percent) - 5
        maxhp_score = (5 + self.maxhp_flat * rarity_multiplier / self.level) * (1 + self.maxhp_percent) - 5
        maxhp_score = maxhp_score / 20
        eva_score = self.eva * 100 * 0.05
        critdef_score = self.critdef * 100 * 0.016666666666666666
        he_score = self.heal_efficiency * 100 * 0.016666666666666666

        attack_total_score = atk_score + spd_score + crit_score + critdmg_score + penetration_score + acc_score
        support_total_score = def_score + maxhp_score + spd_score + eva_score + critdef_score + he_score

        total_score = attack_total_score * 0.33 + support_total_score
        assert total_score >= 0
        return total_score 
    

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


    def print_stats_html(self, include_market_price=True, item_to_compare=None, include_set_effect=True):
        """
        item_to_compare: another Equip object to compare with, all stats, attack value, support value,
        market value will be displayed side by side including the difference
        If there is something to compare, the stats that this item does not have but the other item has will also be displayed
        """
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

        star_color = "#3746A7"
        market_color = "#202d82"
        owner_color = "#0e492a"
        attacker_value_color = "#ffa500"
        support_value_color = "#00cc84"
        star_color_purple = "#9B30FF"
        star_color_red = "#FF0000"
        star_color_gold = "#FFD700"

        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "

        def star_font_color() -> str:
            if self.stars_rating <= 5:
                return star_color
            elif 5 < self.stars_rating <= 10:
                return star_color_purple
            elif 10 < self.stars_rating <= 15:
                return star_color_red
            else:
                return star_color_gold

        def diff_str(self_val, cmp_val):
            diff = self_val - cmp_val
            if diff > 0:
                return f"<font color=#00FF00>{cmp_val} ↑ {abs(diff)}</font>"
            elif diff < 0:
                return f"<font color=#FF0000>{cmp_val} ↓ {abs(diff)}</font>"
            else:
                return f"<font color=#6495ed>{cmp_val} → {abs(diff)}</font>"

        def diff_str_percent(self_val, cmp_val):
            diff = (self_val - cmp_val) * 100
            if diff > 0:
                return f"<font color=#00FF00>{cmp_val * 100:.2f}% ↑ {abs(diff):.2f}%</font>"
            elif diff < 0:
                return f"<font color=#FF0000>{cmp_val * 100:.2f}% ↓ {abs(diff):.2f}%</font>"
            else:
                return f"<font color=#6495ed>{cmp_val * 100:.2f}% → {abs(diff):.2f}%</font>"

        def add_stat_line(stat_name: str, self_val, cmp_val=0, is_percent=False, extra_color=None):
            if (self_val != 0) or (item_to_compare and cmp_val != 0):
                if item_to_compare:
                    if is_percent:
                        line = f"{stat_name}: {self_val * 100:.2f}% | " + diff_str_percent(self_val, cmp_val) + "\n"
                    else:
                        line = f"{stat_name}: {self_val} | " + diff_str(self_val, cmp_val) + "\n"
                else:
                    if is_percent:
                        line = f"{stat_name}: {self_val * 100:.2f}%\n"
                    else:
                        line = f"{stat_name}: {self_val}\n"

                if extra_color:
                    return f"<font color={extra_color}>{line}</font>"
                return line
            return ""

        if not self.eq_set == "Void":
            stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>lv{self.level} {eq_set_str()}{self.rarity} {self.type}</b></font></shadow>\n"
        else:
            stats = "Void Force\n"

        if self.stars_rating > 0:
            stats += "<font color=" + star_color + ">" + '★' * min(int(self.stars_rating), 5) + "</font>"
        if self.stars_rating > 5:
            stats += "<font color=" + star_color_purple + ">" + '★' * min(int(self.stars_rating - 5), 5) + "</font>"
        if self.stars_rating > 10:
            stats += "<font color=" + star_color_red + ">" + '★' * min(int(self.stars_rating - 10), 5) + "</font>"
        stats += "\n" if self.stars_rating > 0 else ""
        stats += "<font color=" + color + ">"

        cmp = item_to_compare

        if (self.maxhp_flat != 0):
            if not item_to_compare:
                stats += "Max HP: " + str(round(self.maxhp_flat, 3)) + "\n"
            else:
                self_val = round(self.maxhp_flat, 3)
                cmp_val = round(item_to_compare.maxhp_flat, 3)
                stats += "Max HP Potential: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        if (self.atk_flat != 0):
            if not item_to_compare:
                stats += "Attack: " + str(round(self.atk_flat, 3)) + "\n"
            else:
                self_val = round(self.atk_flat, 3)
                cmp_val = round(item_to_compare.atk_flat, 3)
                stats += "Attack Potential: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        if (self.def_flat != 0):
            if not item_to_compare:
                stats += "Defense: " + str(round(self.def_flat, 3)) + "\n"
            else:
                self_val = round(self.def_flat, 3)
                cmp_val = round(item_to_compare.def_flat, 3)
                stats += "Defense Potential: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        if (self.spd_flat != 0):
            if not item_to_compare:
                stats += "Speed: " + str(round(self.spd_flat, 3)) + "\n"
            else:
                self_val = round(self.spd_flat, 3)
                cmp_val = round(item_to_compare.spd_flat, 3)
                stats += "Speed Potential: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        stats += add_stat_line("Max HP", self.maxhp_percent, cmp.maxhp_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("Attack", self.atk_percent, cmp.atk_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("Defense", self.def_percent, cmp.def_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("Speed", self.spd, cmp.spd if cmp else 0, is_percent=True)
        stats += add_stat_line("Evasion", self.eva, cmp.eva if cmp else 0, is_percent=True)
        stats += add_stat_line("Accuracy", self.acc, cmp.acc if cmp else 0, is_percent=True)
        stats += add_stat_line("Critical Chance", self.crit, cmp.crit if cmp else 0, is_percent=True)
        stats += add_stat_line("Critical Damage", self.critdmg, cmp.critdmg if cmp else 0, is_percent=True)
        stats += add_stat_line("Critical Defense", self.critdef, cmp.critdef if cmp else 0, is_percent=True)
        stats += add_stat_line("Penetration", self.penetration, cmp.penetration if cmp else 0, is_percent=True)

        heal_line = add_stat_line("Heal Efficiency", self.heal_efficiency, cmp.heal_efficiency if cmp else 0, is_percent=True)
        if heal_line:
            heal_line = heal_line.rstrip("\n") + "</font>\n"
            stats += heal_line

        stats += add_stat_line("Extra Max HP", self.maxhp_extra, cmp.maxhp_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("Extra Attack", self.atk_extra, cmp.atk_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("Extra Defense", self.def_extra, cmp.def_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("Extra Speed", self.spd_extra, cmp.spd_extra if cmp else 0, extra_color=star_font_color())

        if self.eq_set == "Void":
            return stats

        if self.owner or (cmp and cmp.owner):
            self_val = self.owner if self.owner else "None"
            cmp_val = cmp.owner if (cmp and cmp.owner) else "None"
            if cmp:
                if self_val == cmp_val:
                    diff_owner = f"<font color=#6495ed>{cmp_val} → 0</font>"
                else:
                    diff_owner = f"<font color=#898900>{cmp_val} ≠</font>"
                stats += f"<font color={owner_color}>Owner: {self_val} | {diff_owner}</font>\n"
            else:
                stats += f"<font color={owner_color}>Owner: {self_val}</font>\n"

        if (self.for_attacker_value > 0) or (cmp and cmp.for_attacker_value > 0):
            self_val = self.for_attacker_value
            cmp_val = cmp.for_attacker_value if cmp else 0
            diff = self_val - cmp_val
            if cmp:
                if diff > 0:
                    diff_str_att = f"<font color=#00FF00>{cmp_val:.4f} ↑ {abs(diff):.4f}</font>"
                elif diff < 0:
                    diff_str_att = f"<font color=#FF0000>{cmp_val:.4f} ↓ {abs(diff):.4f}</font>"
                else:
                    diff_str_att = f"<font color=#6495ed>{cmp_val:.4f} → {abs(diff):.4f}</font>"
                stats += f"<font color={attacker_value_color}>Attack Value: {self_val:.4f} | {diff_str_att}</font>\n"
            else:
                stats += f"<font color={attacker_value_color}>Attack Value: {self_val:.4f}</font>\n"

        if (self.for_support_value > 0) or (cmp and cmp.for_support_value > 0):
            self_val = self.for_support_value
            cmp_val = cmp.for_support_value if cmp else 0
            diff = self_val - cmp_val
            if cmp:
                if diff > 0:
                    diff_str_sup = f"<font color=#00FF00>{cmp_val:.4f} ↑ {abs(diff):.4f}</font>"
                elif diff < 0:
                    diff_str_sup = f"<font color=#FF0000>{cmp_val:.4f} ↓ {abs(diff):.4f}</font>"
                else:
                    diff_str_sup = f"<font color=#6495ed>{cmp_val:.4f} → {abs(diff):.4f}</font>"
                stats += f"<font color={support_value_color}>Support Value: {self_val:.4f} | {diff_str_sup}</font>\n"
            else:
                stats += f"<font color={support_value_color}>Support Value: {self_val:.4f}</font>\n"

        if not item_to_compare:
            if self.stars_rating < self.stars_rating_max:
                stats += f"<font color=#AF6E4D>Stars Enhancement Cost: {self.star_enhence_cost} </font>\n"
            else:
                stats += f"<font color=#AF6E4D>Stars Enhancement Cost: MAX </font>\n"
            if self.level < self.level_max:
                stats += f"<font color=#702963>Level Up Cost: {self.level_cost} </font>\n"
            else:
                stats += f"<font color=#702963>Level Up Cost: MAX </font>\n"

        if not item_to_compare:
            if include_market_price:
                stats += "<font color=" + market_color + ">" + f"Market Price: {int(self.market_value)}" + "</font>\n"

        stats += "</font>"

        def set_effect_display_color(count):
            if self.set_effect_is_acive >= count:
                return "#444B74"
            else:
                return "#BCC0D9"

        if include_set_effect:
            eq_set = EQ_SET_REGISTRY.get(self.eq_set)
            eq_set_desc = eq_set.description if eq_set else {}
            for set_count, description in eq_set_desc.items():
                if description:
                    stats += f"<font color={set_effect_display_color(set_count)}>{set_count} Set Effect:\n{description}</font>\n"

        return stats


    def print_stats_html_jp(self, include_market_price=True, item_to_compare=None, include_set_effect=True):
        """
        item_to_compare: 比較用の別のEquipオブジェクト。
        全てのステータス、攻撃相性、防御相性、市場価格を並べて表示し、差分も表示します。
        比較対象が存在する場合、比較先に存在してこちらに存在しないステータスも表示します。
        """

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

        star_color = "#3746A7"
        market_color = "#202d82"
        owner_color = "#0e492a"
        attacker_value_color = "#ffa500"
        support_value_color = "#00cc84"
        star_color_purple = "#9B30FF"
        star_color_red = "#FF0000"
        star_color_gold = "#FFD700"

        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "

        def star_font_color() -> str:
            if self.stars_rating <= 5:
                return star_color
            elif 5 < self.stars_rating <= 10:
                return star_color_purple
            elif 10 < self.stars_rating <= 15:
                return star_color_red
            else:
                return star_color_gold

        # 差分表示用関数（通常値）
        def diff_str(self_val, cmp_val):
            diff = self_val - cmp_val
            if diff > 0:
                return f"<font color=#00FF00>{cmp_val} ↑ {abs(diff)}</font>"
            elif diff < 0:
                return f"<font color=#FF0000>{cmp_val} ↓ {abs(diff)}</font>"
            else:
                return f"<font color=#6495ed>{cmp_val} → {abs(diff)}</font>"

        # 差分表示用関数（パーセント）
        def diff_str_percent(self_val, cmp_val):
            diff = (self_val - cmp_val)*100
            if diff > 0:
                return f"<font color=#00FF00>{cmp_val*100:.2f}% ↑ {abs(diff):.2f}%</font>"
            elif diff < 0:
                return f"<font color=#FF0000>{cmp_val*100:.2f}% ↓ {abs(diff):.2f}%</font>"
            else:
                return f"<font color=#6495ed>{cmp_val*100:.2f}% → {abs(diff):.2f}%</font>"

        def add_stat_line(stat_name_jp: str, self_val, cmp_val=0, is_percent=False, extra_color=None):
            """
            ステータス行を追加する関数。
            item_to_compareがない場合は通常表示。
            item_to_compareがある場合は "現在値 | cmp値 差分" 形式で表示する。
            is_percent=Trueのときは%表記し差分計算も%で行う。
            extra_colorが指定されている場合、そのカラーで表示（日本語版では追加系ステータスなどに使用）
            """
            # 表示するか判断
            if (self_val != 0) or (item_to_compare and cmp_val != 0):
                if item_to_compare:
                    if is_percent:
                        line = f"{stat_name_jp}: {self_val*100:.2f}% | " + diff_str_percent(self_val, cmp_val) + "\n"
                    else:
                        line = f"{stat_name_jp}: {self_val} | " + diff_str(self_val, cmp_val) + "\n"
                else:
                    if is_percent:
                        line = f"{stat_name_jp}: {self_val*100:.2f}%\n"
                    else:
                        line = f"{stat_name_jp}: {self_val}\n"
                
                if extra_color:
                    return f"<font color={extra_color}>{line}</font>"
                return line
            return ""

        if not self.eq_set == "Void":
            stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>レベル{self.level} {eq_set_str()}{self.rarity} {self.type}</b></font></shadow>\n"
        else:
            stats = f"虚空の呪\n"

        if self.stars_rating > 0:
            stats += "<font color=" + star_color + ">" + '★'*min(int(self.stars_rating), 5) + "</font>"
        if self.stars_rating > 5:
            stats += "<font color=" + star_color_purple + ">" + '★'*min(int(self.stars_rating-5), 5) + "</font>"
        if self.stars_rating > 10:
            stats += "<font color=" + star_color_red + ">" + '★'*min(int(self.stars_rating-10), 5) + "</font>"
        stats += "\n" if self.stars_rating > 0 else ""
        stats += "<font color=" + color + ">"

        # 比較用値取得用ショートハンド
        cmp = item_to_compare

        # Flat系ステータス
        # maxhp_flat
        if (self.maxhp_flat != 0):
            if not item_to_compare:
                stats += "最大HP: " + str(round(self.maxhp_flat,3)) + "\n"
            else:
                # compare with self._mainstat_potential
                self_val = round(self._mainstat_potential,3)
                cmp_val = round(item_to_compare._mainstat_potential,3)
                stats += "最大HP潜在値: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        # atk_flat
        if (self.atk_flat != 0):
            if not item_to_compare:
                stats += "攻撃: " + str(round(self.atk_flat,3)) + "\n"
            else:
                self_val = round(self._mainstat_potential,3)
                cmp_val = round(item_to_compare._mainstat_potential,3)
                stats += "攻撃潜在値: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        # def_flat
        if (self.def_flat != 0):
            if not item_to_compare:
                stats += "防御: " + str(round(self.def_flat,3)) + "\n"
            else:
                self_val = round(self._mainstat_potential,3)
                cmp_val = round(item_to_compare._mainstat_potential,3)
                stats += "防御潜在値: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        # spd_flat
        if (self.spd_flat != 0):
            if not item_to_compare:
                stats += "速度: " + str(round(self.spd_flat,3)) + "\n"
            else:
                self_val = round(self._mainstat_potential,3)
                cmp_val = round(item_to_compare._mainstat_potential,3)
                stats += "速度潜在値: " + str(self_val) + " | " + diff_str(self_val, cmp_val) + "\n"

        # %系ステータス
        stats += add_stat_line("最大HP", self.maxhp_percent, cmp.maxhp_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("攻撃", self.atk_percent, cmp.atk_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("防御", self.def_percent, cmp.def_percent if cmp else 0, is_percent=True)
        stats += add_stat_line("速度", self.spd, cmp.spd if cmp else 0, is_percent=True)
        stats += add_stat_line("回避", self.eva, cmp.eva if cmp else 0, is_percent=True)
        stats += add_stat_line("命中", self.acc, cmp.acc if cmp else 0, is_percent=True)
        stats += add_stat_line("クリティカル確率", self.crit, cmp.crit if cmp else 0, is_percent=True)
        stats += add_stat_line("クリティカルダメージ", self.critdmg, cmp.critdmg if cmp else 0, is_percent=True)
        stats += add_stat_line("クリティカル防御", self.critdef, cmp.critdef if cmp else 0, is_percent=True)
        stats += add_stat_line("貫通", self.penetration, cmp.penetration if cmp else 0, is_percent=True)
        # 回復効率は最後に"</font>\n"が付いていたので同様にする
        heal_line = add_stat_line("回復効率", self.heal_efficiency, cmp.heal_efficiency if cmp else 0, is_percent=True)
        if heal_line:
            # 回復効率の行末に</font>を付ける
            heal_line = heal_line.rstrip("\n") + "</font>\n"
            stats += heal_line

        # 追加系ステータス
        stats += add_stat_line("追加最大HP", self.maxhp_extra, cmp.maxhp_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("追加攻撃", self.atk_extra, cmp.atk_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("追加防御", self.def_extra, cmp.def_extra if cmp else 0, extra_color=star_font_color())
        stats += add_stat_line("追加速度", self.spd_extra, cmp.spd_extra if cmp else 0, extra_color=star_font_color())

        if self.eq_set == "Void":
            return stats

        # 所有者
        if self.owner or (cmp and cmp.owner):
            self_val = self.owner if self.owner else "なし"
            cmp_val = cmp.owner if (cmp and cmp.owner) else "なし"
            if cmp:
                if self_val == cmp_val:
                    diff_owner = f"<font color=#6495ed>{cmp_val} → 0</font>"
                else:
                    # 名前に数値的な差分はないが、違いを示すため"≠"を使用
                    diff_owner = f"<font color=#898900>{cmp_val} ≠</font>"
                stats += f"<font color={owner_color}>所有者: {self_val} | {diff_owner}</font>\n"
            else:
                stats += f"<font color={owner_color}>所有者: {self_val}</font>\n"

        # 攻撃相性
        if (self.for_attacker_value > 0) or (cmp and cmp.for_attacker_value > 0):
            self_val = self.for_attacker_value
            cmp_val = cmp.for_attacker_value if cmp else 0
            diff = self_val - cmp_val
            if cmp:
                if diff > 0:
                    diff_str_att = f"<font color=#00FF00>{cmp_val:.4f} ↑ {abs(diff):.4f}</font>"
                elif diff < 0:
                    diff_str_att = f"<font color=#FF0000>{cmp_val:.4f} ↓ {abs(diff):.4f}</font>"
                else:
                    diff_str_att = f"<font color=#6495ed>{cmp_val:.4f} → {abs(diff):.4f}</font>"
                stats += f"<font color={attacker_value_color}>攻撃相性: {self_val:.4f} | {diff_str_att}</font>\n"
            else:
                stats += f"<font color={attacker_value_color}>攻撃相性: {self_val:.4f}</font>\n"

        # 防御相性
        if (self.for_support_value > 0) or (cmp and cmp.for_support_value > 0):
            self_val = self.for_support_value
            cmp_val = cmp.for_support_value if cmp else 0
            diff = self_val - cmp_val
            if cmp:
                if diff > 0:
                    diff_str_sup = f"<font color=#00FF00>{cmp_val:.4f} ↑ {abs(diff):.4f}</font>"
                elif diff < 0:
                    diff_str_sup = f"<font color=#FF0000>{cmp_val:.4f} ↓ {abs(diff):.4f}</font>"
                else:
                    diff_str_sup = f"<font color=#6495ed>{cmp_val:.4f} → {abs(diff):.4f}</font>"
                stats += f"<font color={support_value_color}>防御相性: {self_val:.4f} | {diff_str_sup}</font>\n"
            else:
                stats += f"<font color={support_value_color}>防御相性: {self_val:.4f}</font>\n"

        # スター強化コスト
        if not item_to_compare:
            if self.stars_rating < self.stars_rating_max:
                stats += f"<font color=#AF6E4D>スター強化コスト: {self.star_enhence_cost} </font>\n"
            else:
                stats += f"<font color=#AF6E4D>スター強化コスト: MAX </font>\n"

        # レベルアップコスト
        if not item_to_compare:
            if self.level < self.level_max:
                stats += f"<font color=#702963>レベルアップコスト: {self.level_cost} </font>\n"
            else:
                stats += f"<font color=#702963>レベルアップコスト: MAX </font>\n"

        # 市場価格
        if not item_to_compare:
            if include_market_price:
                stats += "<font color=" + market_color + ">" + f"市場価格: {int(self.market_value)}" + "</font>\n"

        stats += "</font>"

        # セット効果
        def set_effect_display_color(count):
            if self.set_effect_is_acive >= count:
                return "#444B74"
            else:
                return "#BCC0D9"

        if include_set_effect:
            eq_set = EQ_SET_REGISTRY.get(self.eq_set)
            eq_set_desc = eq_set.description_jp if eq_set else {}
            for set_count, description in eq_set_desc.items():
                if description:
                    stats += f"<font color={set_effect_display_color(set_count)}>{set_count}セット効果:\n{description}</font>\n"

        return stats


def generate_equips_list(num=1, locked_type=None, locked_eq_set=None, locked_rarity=None, random_full_eqset=False, 
                         eq_level=40, include_void=False, min_market_value=1, tier="bad") -> list:
    """
    [tier] can be "bad", "normal", "good", or "random".
    """
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
        if tier == "random":
            tier = random.choice(["bad", "normal", "good"])
        if include_void and item_eq_set == "Void":
            item.generate_void()
        else:
            while item.market_value < min_market_value:
                item.generate(tier=tier)
        items.append(item)

    return items

# nd_list = [normal_distribution(1, 3000, 1000, 500) for i in range(1000)]
# avg = sum(nd_list)/len(nd_list)
# print(avg) # near 1000
# print(generate_equips_list(4, locked_eq_set="Arasaka"))
