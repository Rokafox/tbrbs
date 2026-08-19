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
        sides = [0, 1, 2, 3, 4, 5, 6, 7]
        weights = {
            "bad": [60, 30, 10, 5, 2, 1, 0, 0],
            "normal": [30, 40, 20, 10, 5, 2, 1, 0],
            "good": [10, 20, 30, 20, 10, 5, 2, 1],
        }
        return random.choices(sides, weights=weights[tier], k=1)[0]

    def generate(self, tier: str):
        """
        Generate stats. [tier] can be "bad", "normal", "good", "void".
        void is only used only for Void Force on monsters on adventure mode. 
        The higher the tier, the more likely to generate more substats based on
        the fake dice function. And more likely to generate higher mainstats.
        """
        substats = ["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency"]
        for attr in substats:
            setattr(self, attr, 0)

        if tier == "void":
            # depending on self level. Default 1 line. Every 500 level, add 1 line. Max 7.
            extra_lines_to_generate = min(1 + self.level // 500, 7)
        else:
            extra_lines_to_generate = self.fake_dice(tier)
        msndmav = 4000 # mainstats_nd_base_max_allowed_value

        match tier:
            case "bad": 
                mainstats_nd_base_value = (1, msndmav, 1000, 1000)
            case "normal":
                mainstats_nd_base_value = (250, msndmav, 1250, 1000)
            case "good" | "void":
                mainstats_nd_base_value = (500, msndmav, 1500, 1000)
            case _:
                raise Exception("Invalid tier")
        
        if self.type == self.type_list[2]:  # Accessory
            v = normal_distribution(*mainstats_nd_base_value)
            self._mainstat_potential = v / msndmav
            v /= 40
            v *= self.level
            self.maxhp_flat = v

        elif self.type == self.type_list[0]: # Weapon
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (msndmav * 0.05)
            v /= 40
            v *= self.level
            self.atk_flat = v
        elif self.type == self.type_list[1]: # Armor
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (msndmav * 0.05)
            v /= 40
            v *= self.level
            self.def_flat = v
        elif self.type == self.type_list[3]: # Boots
            v = max(normal_distribution(*mainstats_nd_base_value) * 0.05, 1)
            self._mainstat_potential = v / (msndmav * 0.05)
            v /= 40
            v *= self.level
            self.spd_flat = v
        else:
            raise Exception("Invalid type")
        
        if extra_lines_to_generate > 0:
            for i in range(extra_lines_to_generate):
                attr = substats.pop(substats.index(random.choice(substats)))

                if attr == "penetration":
                    value = normal_distribution(1, 2000, 400, 600) * 0.0001
                elif attr == "def_percent":
                    # slightly better for def to reduce fully equipped OTK.
                    value = normal_distribution(1, 4000, 1200, 1000) * 0.0001
                elif attr == "eva":
                    # slightly lower, so eva can never win against high acc.
                    value = normal_distribution(1, 3000, 750, 800) * 0.0001
                else:
                    value = normal_distribution(1, 4000, 1000, 1000) * 0.0001
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
        process_cost = 20  
        return int(base_cost * (current_level ** 1.985)) + process_cost  # appx 3015329 from 1 to 1000
    
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
        self.market_value = (base_value + base_value_b + base_value_c) * rarity_multiplier * random_multiplier
        self.market_value *= level_multiplier
        if self.eq_set == "None":
            self.market_value *= 0.66 
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


    def print_stats_html(self, include_market_price=True, item_to_compare=None, include_set_effect=True, language="en"):
        """
        item_to_compare: another Equip object to compare with, all stats, attack value, support value,
        market value will be displayed side by side including the difference.
        If there is something to compare, the stats that this item does not have but the other item has
        will also be displayed.

        language: "en" or "ja"
        """
        lang = "ja" if str(language).lower().startswith("ja") else "en"

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

        if lang == "ja":
            empty_owner = "なし"
            void_header = "虚空の呪"
            header_prefix = "レベル"
            owner_label = "所有者"
            attack_value_label = "攻撃相性"
            support_value_label = "防御相性"
            market_label = "市場価格"
            star_cost_label = "スター強化コスト"
            level_cost_label = "レベルアップコスト"
            set_effect_suffix = "セット効果"
            title_stat_names = {
                "Max HP": "最大HP",
                "Attack": "攻撃",
                "Defense": "防御",
                "Speed": "速度",
                "Evasion": "回避",
                "Accuracy": "命中",
                "Critical Chance": "クリティカル確率",
                "Critical Damage": "クリティカルダメージ",
                "Critical Defense": "クリティカル防御",
                "Penetration": "貫通",
                "Heal Efficiency": "回復効率",
                "Extra Max HP": "追加最大HP",
                "Extra Attack": "追加攻撃",
                "Extra Defense": "追加防御",
                "Extra Speed": "追加速度",
            }
            flat_stat_names = {
                "Max HP": "最大HP",
                "Attack": "攻撃",
                "Defense": "防御",
                "Speed": "速度",
            }
            flat_potential_suffix = "潜在値"
            set_effect_label = "{count}セット効果"
            eq_set_desc_key = "description_jp"
        else:
            empty_owner = "None"
            void_header = "Void Force"
            header_prefix = "lv"
            owner_label = "Owner"
            attack_value_label = "Attack Value"
            support_value_label = "Support Value"
            market_label = "Market Price"
            star_cost_label = "Stars Enhancement Cost"
            level_cost_label = "Level Up Cost"
            set_effect_suffix = "Set Effect"
            title_stat_names = {
                "Max HP": "Max HP",
                "Attack": "Attack",
                "Defense": "Defense",
                "Speed": "Speed",
                "Evasion": "Evasion",
                "Accuracy": "Accuracy",
                "Critical Chance": "Critical Chance",
                "Critical Damage": "Critical Damage",
                "Critical Defense": "Critical Defense",
                "Penetration": "Penetration",
                "Heal Efficiency": "Heal Efficiency",
                "Extra Max HP": "Extra Max HP",
                "Extra Attack": "Extra Attack",
                "Extra Defense": "Extra Defense",
                "Extra Speed": "Extra Speed",
            }
            flat_stat_names = {
                "Max HP": "Max HP",
                "Attack": "Attack",
                "Defense": "Defense",
                "Speed": "Speed",
            }
            flat_potential_suffix = "Potential"
            set_effect_label = "{count} Set Effect"
            eq_set_desc_key = "description"

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
                label = title_stat_names.get(stat_name, stat_name)
                if item_to_compare:
                    if is_percent:
                        line = f"{label}: {self_val * 100:.2f}% | " + diff_str_percent(self_val, cmp_val) + "\n"
                    else:
                        line = f"{label}: {self_val} | " + diff_str(self_val, cmp_val) + "\n"
                else:
                    if is_percent:
                        line = f"{label}: {self_val * 100:.2f}%\n"
                    else:
                        line = f"{label}: {self_val}\n"
                if extra_color:
                    return f"<font color={extra_color}>{line}</font>"
                return line
            return ""

        if self.eq_set != "Void":
            stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>{header_prefix}{self.level} {eq_set_str()}{self.rarity} {self.type}</b></font></shadow>\n"
        else:
            stats = f"{void_header}\n"

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
                stats += f"{flat_stat_names['Max HP']}: {round(self.maxhp_flat, 3)}\n"
            else:
                self_val = round(self._mainstat_potential if lang == "ja" else self.maxhp_flat, 3)
                cmp_val = round(item_to_compare._mainstat_potential if lang == "ja" else item_to_compare.maxhp_flat, 3)
                label = f"{flat_stat_names['Max HP']}{flat_potential_suffix}"
                stats += f"{label}: {self_val} | {diff_str(self_val, cmp_val)}\n"

        if (self.atk_flat != 0):
            if not item_to_compare:
                stats += f"{flat_stat_names['Attack']}: {round(self.atk_flat, 3)}\n"
            else:
                self_val = round(self._mainstat_potential if lang == "ja" else self.atk_flat, 3)
                cmp_val = round(item_to_compare._mainstat_potential if lang == "ja" else item_to_compare.atk_flat, 3)
                label = f"{flat_stat_names['Attack']}{flat_potential_suffix}"
                stats += f"{label}: {self_val} | {diff_str(self_val, cmp_val)}\n"

        if (self.def_flat != 0):
            if not item_to_compare:
                stats += f"{flat_stat_names['Defense']}: {round(self.def_flat, 3)}\n"
            else:
                self_val = round(self._mainstat_potential if lang == "ja" else self.def_flat, 3)
                cmp_val = round(item_to_compare._mainstat_potential if lang == "ja" else item_to_compare.def_flat, 3)
                label = f"{flat_stat_names['Defense']}{flat_potential_suffix}"
                stats += f"{label}: {self_val} | {diff_str(self_val, cmp_val)}\n"

        if (self.spd_flat != 0):
            if not item_to_compare:
                stats += f"{flat_stat_names['Speed']}: {round(self.spd_flat, 3)}\n"
            else:
                self_val = round(self._mainstat_potential if lang == "ja" else self.spd_flat, 3)
                cmp_val = round(item_to_compare._mainstat_potential if lang == "ja" else item_to_compare.spd_flat, 3)
                label = f"{flat_stat_names['Speed']}{flat_potential_suffix}"
                stats += f"{label}: {self_val} | {diff_str(self_val, cmp_val)}\n"

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
            self_val = self.owner if self.owner else empty_owner
            cmp_val = cmp.owner if (cmp and cmp.owner) else empty_owner
            if cmp:
                if self_val == cmp_val:
                    diff_owner = f"<font color=#6495ed>{cmp_val} → 0</font>"
                else:
                    diff_owner = f"<font color=#898900>{cmp_val} ≠</font>"
                stats += f"<font color={owner_color}>{owner_label}: {self_val} | {diff_owner}</font>\n"
            else:
                stats += f"<font color={owner_color}>{owner_label}: {self_val}</font>\n"

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
                stats += f"<font color={attacker_value_color}>{attack_value_label}: {self_val:.4f} | {diff_str_att}</font>\n"
            else:
                stats += f"<font color={attacker_value_color}>{attack_value_label}: {self_val:.4f}</font>\n"

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
                stats += f"<font color={support_value_color}>{support_value_label}: {self_val:.4f} | {diff_str_sup}</font>\n"
            else:
                stats += f"<font color={support_value_color}>{support_value_label}: {self_val:.4f}</font>\n"

        if not item_to_compare:
            if self.stars_rating < self.stars_rating_max:
                stats += f"<font color=#AF6E4D>{star_cost_label}: {self.star_enhence_cost} </font>\n"
            else:
                stats += f"<font color=#AF6E4D>{star_cost_label}: MAX </font>\n"
            if self.level < self.level_max:
                stats += f"<font color=#702963>{level_cost_label}: {self.level_cost} </font>\n"
            else:
                stats += f"<font color=#702963>{level_cost_label}: MAX </font>\n"

        if not item_to_compare and include_market_price:
            stats += f"<font color={market_color}>{market_label}: {int(self.market_value)}</font>\n"

        stats += "</font>"

        def set_effect_display_color(count):
            if self.set_effect_is_acive >= count:
                return "#444B74"
            else:
                return "#BCC0D9"

        if include_set_effect:
            eq_set = EQ_SET_REGISTRY.get(self.eq_set)
            eq_set_desc = getattr(eq_set, eq_set_desc_key) if eq_set else {}
            for set_count, description in eq_set_desc.items():
                if description:
                    stats += f"<font color={set_effect_display_color(set_count)}>{set_count}{set_effect_suffix}:\n{description}</font>\n"

        return stats

    def print_stats_html_jp(self, include_market_price=True, item_to_compare=None, include_set_effect=True):
        return self.print_stats_html(
            include_market_price=include_market_price,
            item_to_compare=item_to_compare,
            include_set_effect=include_set_effect,
            language="ja",
        )


def generate_equips_list(num=1, locked_type=None, locked_eq_set=None, locked_rarity=None, random_full_eqset=False, 
                         eq_level=40, min_market_value=1, tier="bad") -> list:
    """
    [tier] can be "bad", "normal", "good", "random", "void"
    """
    items = []
    rarity_pool, types, eq_set_pool = Equip("Foo", "Weapon", "Common").get_raritytypeeqset_list()
    eq_set_pool_no_void = [eq_set for eq_set in eq_set_pool if eq_set != "Void"]
    types_cycle = cycle(types)
    if random_full_eqset:
        random_eq_set = random.choice(eq_set_pool_no_void[1:])
    for i in range(num):
        item_type = locked_type if locked_type else next(types_cycle)
        if random_full_eqset:
            item_eq_set = random_eq_set
        else:
            item_eq_set = locked_eq_set if locked_eq_set else random.choice(eq_set_pool_no_void)
        item_rarity = locked_rarity if locked_rarity else random.choice(rarity_pool)

        item = Equip(f"EQ_", item_type, item_rarity, item_eq_set, level=eq_level)
        item.name += item.misc_generate_uuid()
        if tier == "random":
            tier = random.choice(["bad", "normal", "good"])

        while item.market_value < min_market_value:
            item.generate(tier=tier)

        items.append(item)

    return items


# print(generate_equips_list(4, locked_eq_set="Arasaka"))
