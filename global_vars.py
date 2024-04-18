import re

turn_info_string = ""
turn = 1 # Not used

def translate_to_jp(string) -> str:
    replacements = {
        "skill2_cooldown_max": "スキル2最大クールダウン",
        "skill1_cooldown_max": "スキル1最大クールダウン",
        "final_damage_taken_multipler": "最終被ダメージ",
        "heal_efficiency": "回復効率",
        "penetration": "貫通率",
        "critdef": "クリティカル防御力",
        "critdmg": "クリティカルダメージ",
        "crit": "クリティカル率",
        "acc": "命中率",
        "eva": "回避率",
        "spd": "速度",
        "defense": "防御力",
        "atk": "攻撃力",
        "maxhp": "最大HP",
        "hp": "HP",
        "maxexp": "最大経験値",
        "exp": "経験値",
        "level": "レベル",
    }
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in replacements.keys()) + r')\b')
    return pattern.sub(lambda x: replacements[x.group()], string)
