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
                            "Liquidation", "Cosmic", "Newspaper", "Cloud", "Purplestar", "1987", "7891", "Freight",
                            "Runic", "Grassland"]
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

        self.set_effect_is_acive = False
        self.four_set_effect_description = ""
        self.four_set_effect_description = self.assign_four_set_effect_description()
        self.four_set_effect_description_jp = self.assign_four_set_effect_description_jp()

        self.owner: str | None = None
        self.for_attacker_value = 0
        self.for_support_value = 0


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
            "owner": self.owner
        }
    
    def assign_four_set_effect_description(self):
        match self.eq_set:
            case "Arasaka":
                return (
                    "Once per battle, leave with 1 hp when taking fatal damage, when triggered, gain immunity to damage for 6 turns."
                )
            case "KangTao":
                return (
                    "Compare atk and def, apply the higher value * 999% as absorption shield on self at start of battle."
                )
            case "Militech":
                return (
                    "Increase speed by 120% when hp falls below 30%."
                )
            case "NUSA":
                return (
                    "Increase atk by 6%, def by 6%, and maxhp by 6% for each ally alive including self."
                )
            case "Sovereign":
                return (
                    "Apply Sovereign effect when taking damage, Sovereign increases atk by 20% and lasts 4 turns. Max 5 active effects."
                )
            case "Snowflake":
                return (
                    "Gain 1 piece of Snowflake at the end of action. When 6 pieces are accumulated, heal 25% hp and gain the following effect for 6 turns: "
                    "atk, def, maxhp, spd are increased by 25%. Each activation of this effect increases the stats bonus and healing by 25%."
                )
            case "Flute":
                return (
                    "On one action, when successfully attacking enemy 4 times, all enemies take status damage equal to 130% of self atk."
                )
            case "Rainbow":
                return (
                    # {0: 1.60, 1: 1.35, 2: 1.10, 3: 0.85, 4: 0.60}
                    "While attacking, damage increases by 60%/35%/10%/-15%/-40% depending on the proximity of the target."
                )
            case "Dawn":
                return (
                    "Atk increased by 24%, crit increased by 24% when hp is full. One time only, when dealing normal or skill attack damage, damage is increased by 120%."
                )
            case "Bamboo":
                return (
                    "After taking down an enemy with normal or skill attack, for 7 turns, recovers 20% of max hp each turn and increases atk, def, spd by 90%, crit and crit damage by 45%. "
                    "Cannot be triggered when buff effect is active."
                )
            case "Rose":
                return (
                    "Heal efficiency is increased by 20%. Before heal, increase target's heal efficiency by 100% for 2 turns, increase your defense by 30% for 10 turns. "
                    "Cannot be triggered by hp recover."
                )
            case "OldRusty":
                return (
                    "After using skill 1, 65% chance to reset cooldown of that skill."
                )
            case "Liquidation":
                return (
                    "When taking damage, for each of the following stats that is lower than attacker's, damage is reduced by 20%: hp, atk, def, spd." \
                    " If the protector is taking damage for an ally, damage reduction effect is reduced by 50%."
                )
            case "Cosmic":
                return (
                    "Every turn, max hp is increased by 1.8% of current maxhp."
                )
            case "Newspaper":
                return (
                    "When dealing damage to enemy, if the enemy has more maxhp then self, damage is increased by 15% of the maxhp difference."
                )
            case "Cloud":
                return (
                    "increase speed by 5%, decrease atk by 10% and grant hide for 50 turns at the start of battle. You cannot be targeted unless for skills that targets 5 enemies." \
                    " Hide effect is removed when all allies are hidden. When this hide effect is removed, apply Full Cloud, for 10 turns, speed is increased by 100%," \
                    " final damage taken is reduced by 40%." 
                )
            case "Purplestar":
                return (
                    "After using skill 2, 85% chance to reset cooldown of that skill."
                )
            case "1987":
                return (
                    "Select the highest one from 3 of your main stats: atk, def, spd. 25.55% of the selected stat is added to the ally" \
                    " who has the lowest value of the selected stat."
                )
            case "7891":
                return (
                    "Select the lowest one from 3 of your main stats: atk, def, spd. 55.55% of the selected stat is added to the ally" \
                    " who has the highest value of the selected stat."
                )
            case "Freight":
                return (
                    "Prioritize skill 2 over skill 1 if both are available. Before an action, heal hp by 50% of speed. For 4 turns, speed is increased by 30%."
                )
            case "Runic":
                # Set skill design: The reason why we have this is simply because some characters are too good
                # when having 100% crit rate, calculating their true strength should be easier with this.
                return (
                    "Critical rate is increased by 100%, critical damage is decreased by 50%." \
                    " When dealing critical damage and critical rate is over 100%, damage is increased by the excess critical rate."
                )
            case "Grassland":
                return (
                    "If you haven't taken action yet in current battle, speed is increased by 100%, final damage taken is reduced by 30%." \
                    " This effect is removed after taken action."
                )
            case _:
                return ""


    def assign_four_set_effect_description_jp(self):
        match self.eq_set:
            case "Arasaka":
                return (
                    "バトル中に一度だけ、致命的なダメージを受けた時にHP1で生存する。発動時、6ターンの間ダメージ無効。"
                )
            case "KangTao":
                return (
                    "攻撃力と防御力を比較し、より高い方の値の999%の分を吸収シールドとしてバトル開始時に自身に付与する。"
                )
            case "Militech":
                return (
                    "HPが30%未満になった時、速度が120%増加する。"
                )
            case "NUSA":
                return (
                    "自分を含む味方の生存数に応じて、攻撃力、防御力、最大HPがそれぞれ6%増加する。"
                )
            case "Sovereign":
                return (
                    "ダメージを受けた時に主権効果を付与する。攻撃力を20%増加させ、4ターン持続する。最大5つの効果が同時に適用される。"
                )
            case "Snowflake":
                return (
                    "行動終了時に雪花の一片を獲得。ピースを6つ集まるとHPが25%回復し、6ターンの間以下の効果を得ます：攻撃力、防御力、最大HP、速度が25%増加。この効果の発動ごとに、ステータスボーナスと回復量が25%増加する。"
                )
            case "Flute":
                return (
                    "1回の行動で敵を4回攻撃に成功すると、全ての敵に自身の攻撃力の130%に相当する状態異常ダメージを与える。"
                )
            case "Rainbow":
                return (
                    "攻撃時、対象との距離に応じてダメージが60%/35%/10%/-15%/-40%に増加する。"
                )
            case "Dawn":
                return (
                    "HPが満タンの時、攻撃力が24%、クリティカル率が24%増加する。1回のみ、通常攻撃またはスキル攻撃時にダメージが120%増加する。"
                )
            case "Bamboo":
                return (
                    "通常攻撃またはスキル攻撃で敵を倒した後、7ターンの間毎ターン最大HPの20%を回復し、攻撃力、防御力、速度が90%、クリティカル率とクリティカルダメージが45%増加する。"
                    "バフ効果が既に発動された場合は発動しない。"
                )
            case "Rose":
                return (
                    "回復効率が20%増加する。治療の前に、対象の回復効率を2ターンの間100%増加させ、自分の防御力を10ターン30%増加する。"
                    "HP回復効果は発動しない。"
                )
            case "OldRusty":
                return (
                    "スキル1を使用した後、65%の確率でそのスキルのクールダウンをリセットする。"
                )
            case "Liquidation":
                return (
                    "ダメージを受けた時、以下のステータスのうち、攻撃側より低いもの1つにつき、ダメージが20％減少：HP、攻撃力、防御力、速度。" \
                    "守護者が味方のためにダメージを受けている場合、ダメージ軽減効果が50%減少。"
                )
            case "Cosmic":
                return (
                    "毎ターン、現在の最大HPの1.8%に相当する最大HPが増加する。"
                )
            case "Newspaper":
                return (
                    "敵にダメージを与えた際、敵の最大HPが自身よりも高い場合、その最大HPの差分の15%分ダメージが増加する。"
                )
            case "Cloud":
                return (
                    "バトル開始時に速度が5%増加し攻撃力が10%減少する。50ターンの間雲隠状態を付与される。雲隠状態中は、5体の敵を対象とするスキル以外のターゲットにはされません。"
                    "雲隠状態が解除されると、雲満を付与し、10ターンの間速度が100%増加し、最終ダメージ倍率40%減少する。"
                )
            case "Purplestar":
                return (
                    "スキル2を使用した後、85%の確率でそのスキルのクールダウンをリセットする。"
                )
            case "1987":
                return (
                    "攻撃力、防御力、速度の3つのステータスの中から最も高いものを選択し、選択したステータスの25.55%分が、選択したステータスの値が最も低い味方に付加される。"
                )
            case "7891":
                return (
                    "攻撃力、防御力、速度の3つのステータスの中から最も低いものを選択し、選択したステータスの55.55%分が、選択したステータスの値が最も高い味方に付加される。"
                )
            case "Freight":
                return (
                    "スキル1よりもスキル2を優先して使用する。行動前にHPを速度の50%分回復する。4ターンの間、速度が30%増加する。"
                )
            case "Runic":
                return (
                    "クリティカル率が100%増加し、クリティカルダメージが50%減少する。" \
                    "クリティカル率100%以上でクリティカルダメージを与えた場合、クリティカル率超過分ダメージが増加する。"
                )
            case "Grassland":
                return (
                    "現在のバトルでまだ行動していない場合、速度が100%増加し、最終ダメージ倍率が30%減少する。" \
                    "この効果は行動を取った後に解除される。"
                )
            case _:
                return ""



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

    def fake_dice(self):
        sides = [1, 2, 3, 4, 5, 6]
        weights = [60, 30, 10, 5, 2, 1]
        return random.choices(sides, weights=weights, k=1)[0]

    def generate(self):
        level = self.level
        # self.maxhp_percent = 0.00
        # self.atk_percent = 0.00
        # self.def_percent = 0.00
        # self.spd = 0.00
        # self.eva = 0.00
        # self.acc = 0.00
        # self.crit = 0.00
        # self.critdmg = 0.00
        # self.critdef = 0.00
        # self.penetration = 0.00
        # self.heal_efficiency = 0.00
        substats = ["maxhp_percent", "atk_percent", "def_percent", "spd", "eva", "acc", "crit", "critdmg", "critdef", "penetration", "heal_efficiency"]
        lines_already_have = []
        lines_already_generated = 0
        for ss in substats:
            if eval(f"self.{ss}") > 0:
                lines_already_generated += 1
                lines_already_have.append(ss)

        extra_lines_to_generate = self.fake_dice() - 1
        
        if self.type == self.type_list[2]:
            if self.maxhp_flat == 0:
                v = max(normal_distribution(1, 4000, 1000, 1000), 1)
            else:
                # should generate a higher value
                v = max(normal_distribution(500, 4000, 1500, 1000), 1)
            v /= 40
            v *= level
            self.maxhp_flat += v
        elif self.type == self.type_list[0]:
            if self.atk_flat == 0:
                v = max(normal_distribution(1, 4000, 1000, 1000) * 0.05, 1)
            else:
                v = max(normal_distribution(500, 4000, 1500, 1000) * 0.05, 1)
            v /= 40
            v *= level
            self.atk_flat += v
        elif self.type == self.type_list[1]:
            if self.def_flat == 0:
                v = max(normal_distribution(1, 4000, 1000, 1000) * 0.05, 1)
            else:
                v = max(normal_distribution(500, 4000, 1500, 1000) * 0.05, 1)
            v /= 40
            v *= level
            self.def_flat += v
        elif self.type == self.type_list[3]:
            if self.spd_flat == 0:
                v = max(normal_distribution(1, 4000, 1000, 1000) * 0.05, 1)
            else:
                v = max(normal_distribution(500, 4000, 1500, 1000) * 0.05, 1)
            v /= 40
            v *= level
            self.spd_flat += v
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
        total_score = 0
        atk_score = (5 + self.atk_flat) * (1 + self.atk_percent) + self.atk_extra
        spd_score = (5 + self.spd_flat) * (1 + self.spd) + self.spd_extra
        crit_score = self.crit * 20
        critdmg_score = self.critdmg * 20
        penetration_score = self.penetration * 20
        acc_score = self.acc * 20
        total_score = atk_score + spd_score + crit_score + critdmg_score + penetration_score + acc_score
        return total_score 

    def estimate_value_for_support(self):
        """
        A support would need maxhp_flat, maxhp_percent, def_flat, def_percent, critdef, eva, heal_efficiency, spd_flat, spd
        Score is decided by trial and error
        """
        total_score = 0
        maxhp_score = ((5 + self.maxhp_flat) * (1 + self.maxhp_percent) + self.maxhp_extra) / 20
        def_score = (5 + self.def_flat) * (1 + self.def_percent) + self.def_extra
        critdef_score = self.critdef * 20
        eva_score = self.eva * 20
        heal_score = self.heal_efficiency * 20 * 0.5 # heal efficiency is not important
        spd_score = (5 + self.spd_flat) * (1 + self.spd) + self.spd_extra
        total_score = maxhp_score + def_score + critdef_score + eva_score + heal_score + spd_score
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
        owner_color = "#0e492a"
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
        if self.owner:
            stats += f"<font color={owner_color}>Owner: {self.owner}</font>\n"
        if self.stars_rating < self.stars_rating_max:
            stats += f"<font color=#AF6E4D>Stars Enhancement Cost: {self.star_enhence_cost} </font>\n"
        else:
            stats += f"<font color=#AF6E4D>Stars Enhancement Cost: MAX </font>\n"
        if self.level < self.level_max:
            stats += f"<font color=#702963>Level Up Cost: {self.level_cost} </font>\n"
        else:
            stats += f"<font color=#702963>Level Up Cost: MAX </font>\n"
        if include_market_price:
            stats += "<font color=" + market_color + ">" + f"Market Price: {int(self.market_value)}" + "</font>\n"
        stats += "</font>"

        def set_effect_display_color():
            if self.set_effect_is_acive:
                return "#444B74"
            else:
                return "#BCC0D9"

        if self.four_set_effect_description:
            stats += f"<font color={set_effect_display_color()}>4 Set Effect:\n{self.four_set_effect_description}</font>"

        return stats


    def print_stats_html_jp(self, include_market_price=True):
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
        
        star_color = "#3746A7"  # 青
        market_color = "#202d82"  # 青
        owner_color = "#0e492a"
        star_color_purple = "#9B30FF"  # 紫
        star_color_red = "#FF0000"  # 赤
        star_color_gold = "#FFD700"  # 金色
        
        def eq_set_str():
            if self.eq_set == "None":
                return ""
            else:
                return str(self.eq_set) + " "

        if not self.eq_set == "Void":
            stats = f"<shadow size=0.5 offset=0,0 color={star_color_gold}><font color={color}><b>" + "レベル" + str(self.level) + " " + eq_set_str() + self.rarity + " " + self.type + "</b></font></shadow>\n"
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

        def star_font_color() -> str:
            if self.stars_rating <= 5:
                return star_color
            elif 5 < self.stars_rating <= 10:
                return star_color_purple
            elif 10 < self.stars_rating <= 15:
                return star_color_red
            else:
                return star_color_gold
        
        def add_stat_with_color(stat_name_jp: str, stat_value: int, stat_extra: int) -> str:
            return stat_name_jp + ": " + str(stat_value) + "<font color=" + star_font_color() + ">" + f" (+{stat_extra})" + "</font>" + "\n"
        
        if self.maxhp_flat != 0:
            stats += add_stat_with_color("最大HP", round(self.maxhp_flat, 3), self.maxhp_extra)
        if self.atk_flat != 0:
            stats += add_stat_with_color("攻撃", round(self.atk_flat, 3), self.atk_extra)
        if self.def_flat != 0:
            stats += add_stat_with_color("防御", round(self.def_flat, 3), self.def_extra)
        if self.spd_flat != 0:
            stats += add_stat_with_color("速度", round(self.spd_flat, 3), self.spd_extra)
        
        if self.maxhp_percent != 0:
            stats += "最大HP: " + "{:.2f}%".format(self.maxhp_percent*100) + "\n"
        if self.atk_percent != 0:
            stats += "攻撃: " + "{:.2f}%".format(self.atk_percent*100) + "\n"
        if self.def_percent != 0:
            stats += "防御: " + "{:.2f}%".format(self.def_percent*100) + "\n"
        if self.spd != 0:
            stats += "速度: " + "{:.2f}%".format(self.spd*100) + "\n"
        if self.eva != 0:
            stats += "回避: " + "{:.2f}%".format(self.eva*100) + "\n"
        if self.acc != 0:
            stats += "命中: " + "{:.2f}%".format(self.acc*100) + "\n"
        if self.crit != 0:
            stats += "クリティカル確率: " + "{:.2f}%".format(self.crit*100) + "\n"
        if self.critdmg != 0:
            stats += "クリティカルダメージ: " + "{:.2f}%".format(self.critdmg*100) + "\n"
        if self.critdef != 0:
            stats += "クリティカル防御: " + "{:.2f}%".format(self.critdef*100) + "\n"
        if self.penetration != 0:
            stats += "貫通: " + "{:.2f}%".format(self.penetration*100) + "\n"
        if self.heal_efficiency != 0:
            stats += "回復効率: " + "{:.2f}%".format(self.heal_efficiency*100) + "</font>\n"
        
        if self.eq_set == "Void":
            return stats
        if self.owner:
            stats += f"<font color={owner_color}>所有: {self.owner}</font>\n"
        if self.stars_rating < self.stars_rating_max:
            stats += f"<font color=#AF6E4D>スター強化コスト: {self.star_enhence_cost} </font>\n"
        else:
            stats += f"<font color=#AF6E4D>スター強化コスト: MAX </font>\n"
        if self.level < self.level_max:
            stats += f"<font color=#702963>レベルアップコスト: {self.level_cost} </font>\n"
        else:
            stats += f"<font color=#702963>レベルアップコスト: MAX </font>\n"
        
        if include_market_price:
            stats += "<font color=" + market_color + ">" + f"市場価格: {int(self.market_value)}" + "</font>\n"
        stats += "</font>"
        
        def set_effect_display_color():
            if self.set_effect_is_acive:
                return "#444B74"
            else:
                return "#BCC0D9"

        if self.four_set_effect_description_jp:
            stats += f"<font color={set_effect_display_color()}>4セット効果:\n{self.four_set_effect_description_jp}</font>"
        
        return stats



def generate_equips_list(num=1, locked_type=None, locked_eq_set=None, locked_rarity=None, random_full_eqset=False, 
                         eq_level=40, include_void=False, min_market_value=-1) -> list:
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
            while True:
                item.generate()
                if item.market_value >= min_market_value:
                    break
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
