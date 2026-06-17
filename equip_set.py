from dataclasses import dataclass


@dataclass
class EqSet:
    name: str
    desc_2: str
    desc_4: str
    desc_jp_2: str
    desc_jp_4: str
    desc_1: str = ""
    desc_3: str = ""
    desc_jp_1: str = ""
    desc_jp_3: str = ""

    @property
    def description(self) -> dict:
        return {1: self.desc_1, 2: self.desc_2, 3: self.desc_3, 4: self.desc_4}

    @property
    def description_jp(self) -> dict:
        return {1: self.desc_jp_1, 2: self.desc_jp_2, 3: self.desc_jp_3, 4: self.desc_jp_4}


_SETS = [
    EqSet(
        name="Arasaka",
        desc_2="Once per battle, leave with 1 hp when taking fatal damage, when triggered, gain immunity to damage for 2 turns.",
        desc_4="Extend damage immunity duration by 4 turns.",
        desc_jp_2="バトル中に一度だけ、致命的なダメージを受けた時にHP1で生存する。発動時、2ターンの間ダメージ無効。",
        desc_jp_4="ダメージ無効の持続時間を4ターン延長する。",
    ),
    EqSet(
        name="KangTao",
        desc_2="At start of battle, compare atk and def, apply the lower value * 500% as shield on self.",
        desc_4="Shield value is increased by the higher value * 500%.",
        desc_jp_2="バトル開始時に攻撃力と防御力を比較し、低い方の値の500%をシールドとして自身に付与する。",
        desc_jp_4="シールド値が高い方の値の500%分増加する。",
    ),
    EqSet(
        name="Militech",
        desc_2="Increase speed by 50% when hp falls below 30%.",
        desc_4="Gain additional 70% speed increase (total 120%).",
        desc_jp_2="HPが30%未満になった時、速度が50%増加する。",
        desc_jp_4="追加で70%の速度増加を得る（合計120%）。",
    ),
    EqSet(
        name="NUSA",
        desc_2="Increase atk by 3%, def by 3%, and maxhp by 3% for each ally alive including self.",
        desc_4="Gain additional 3% increase for each stat.",
        desc_jp_2="自身を含む生存している味方1体につき、攻撃力、防御力、最大HPがそれぞれ3%増加する。",
        desc_jp_4="各ステータスがさらに3%増加する。",
    ),
    EqSet(
        name="Sovereign",
        desc_2="Apply Sovereign effect when taking damage, Sovereign increases atk by 20% and lasts 4 turns. Max 2 active effects.",
        desc_4="Max active effects increased by 3 (total 5).",
        desc_jp_2="ダメージを受けた時に主権効果を付与する。主権効果は攻撃力を20%増加させ、4ターン持続する。最大同時発動数は2。",
        desc_jp_4="最大同時発動数が3増加する（合計5）。",
    ),
    EqSet(
        name="Snowflake",
        desc_2=(
            "Gain 1 piece of Snowflake at the end of action. When 6 pieces are accumulated, heal 12% hp and gain the following effect for 4 turns: "
            "atk, def, maxhp, spd are increased by 12%. Each activation of this effect increases the stats bonus and healing by 12%."
        ),
        desc_4="Stat and healing bonus increased by 13% (total 25%). Effect duration increased by 2 turns (total 6 turns).",
        desc_jp_2="行動終了時に雪花の一片を獲得する。6つ集まるとHPを12%回復し、4ターンの間以下の効果を得る：攻撃力、防御力、最大HP、速度が12%増加。この効果の発動ごとに、ステータスボーナスと回復量が12%増加する。",
        desc_jp_4="ステータスと回復量のボーナスが13%増加する（合計25%）。効果の持続時間が2ターン延長される（合計6ターン）。",
    ),
    EqSet(
        name="Flute",
        desc_2="On one action, when successfully attacking enemy 4 times, all enemies take status damage equal to 60% of self atk.",
        desc_4="Damage increased by 70% (total 130%).",
        desc_jp_2="1回の行動で敵への攻撃に4回成功した時、すべての敵に自身の攻撃力の60%に相当する状態異常ダメージを与える。",
        desc_jp_4="ダメージが70%増加する（合計130%）。",
    ),
    EqSet(
        name="Rainbow",
        desc_2="While attacking, damage increases by 40%/15%/-10%/-35%/-60% depending on the proximity of the target.",
        desc_4="Damage bonus increased by 20% for each proximity level.",
        desc_jp_2="攻撃時、ターゲットとの距離に応じてダメージが40%/15%/-10%/-35%/-60%増加する。",
        desc_jp_4="距離レベルごとにダメージボーナスが20%増加する。",
    ),
    EqSet(
        name="Dawn",
        desc_2="Atk increased by 12%, crit increased by 12% when hp is full.",
        desc_4="Stat increased by additional 12%. One time only, when dealing normal or skill attack damage, damage is increased by 100%.",
        desc_jp_2="HPが満タンの時、攻撃力が12%、クリティカル率が12%増加する。",
        desc_jp_4="ステータスがさらに12%増加する。通常攻撃またはスキル攻撃でダメージを与える時、一度だけダメージが100%増加する。",
    ),
    EqSet(
        name="Bamboo",
        desc_2=(
            "After taking down an enemy with normal or skill attack, for 4 turns, recovers 10% of max hp each turn and increases atk, def, spd by 45%, crit and crit damage by 22%. "
            "Cannot be triggered when buff effect is active."
        ),
        desc_4="Stat bonus and effect duration is doubled.",
        desc_jp_2="通常攻撃またはスキル攻撃で敵を倒した後、4ターンの間毎ターン最大HPの10%を回復し、攻撃力、防御力、速度が45%、クリティカル率とクリティカルダメージが22%増加する。バフ効果が既に発動された場合は発動しない。",
        desc_jp_4="ステータスボーナスと効果の持続時間が2倍になる。",
    ),
    EqSet(
        name="Rose",
        desc_2=(
            "Heal efficiency is increased by 10%. Before heal, increase target's heal efficiency by 50% for 2 turns, increase your defense by 15% for 10 turns. "
            "Cannot be triggered by hp recover."
        ),
        desc_4="Stat bonus is doubled.",
        desc_jp_2="回復効率が10%増加する。治療を行う前に、対象の回復効率を2ターンの間50%増加させ、自身の防御力を10ターンの間15%増加させる。HP回復効果では発動しない。",
        desc_jp_4="ステータスボーナスが2倍になる。",
    ),
    EqSet(
        name="OldRusty",
        desc_2="After using skill 1, 30% chance to reset cooldown of that skill.",
        desc_4="Increase reset chance by 33% (total 63%).",
        desc_jp_2="スキル1を使用した後、30%の確率でそのスキルのクールダウンをリセットする。",
        desc_jp_4="リセット確率が33%増加する（合計63%）。",
    ),
    EqSet(
        name="Purplestar",
        desc_2="After using skill 2, 30% chance to reset cooldown of that skill.",
        desc_4="Increase reset chance by 33% (total 63%).",
        desc_jp_2="スキル2を使用した後、30%の確率でそのスキルのクールダウンをリセットする。",
        desc_jp_4="リセット確率が33%増加する（合計63%）。",
    ),
    EqSet(
        name="Liquidation",
        desc_2=(
            "When taking damage, for each of the following stats that is lower than attacker's, damage is reduced by 10%: hp, atk, def, spd."
            " If the protector is taking damage for an ally, damage reduction effect is reduced by 50%."
        ),
        desc_4="Damage reduction bonus is doubled (20% per stat).",
        desc_jp_2="ダメージを受けた時、以下のステータスのうち攻撃側より低いもの1つにつき、ダメージが10%減少する：HP、攻撃力、防御力、速度。守護者が味方のためにダメージを受けている場合、ダメージ軽減効果が50%減少する。",
        desc_jp_4="ダメージ軽減ボーナスが2倍になる（各ステータス20%）。",
    ),
    EqSet(
        name="Cosmic",
        desc_2="Every turn, max hp is increased by 0.8% of current maxhp.",
        desc_4="Gain additional max hp increase by 1%.",
        desc_jp_2="毎ターン、現在の最大HPの0.8%分、最大HPが増加する。",
        desc_jp_4="追加で最大HPが1%増加する。",
    ),
    EqSet(
        name="Newspaper",
        desc_2="When dealing damage to enemy, if the enemy has more maxhp then self, damage is increased by 7% of the maxhp difference.",
        desc_4="Damage bonus increased by 8% of the maxhp difference (total 15%).",
        desc_jp_2="敵にダメージを与える時、敵の最大HPが自身よりも高い場合、最大HPの差の7%分ダメージが増加する。",
        desc_jp_4="ダメージボーナスが最大HPの差の8%分増加する（合計15%）。",
    ),
    EqSet(
        name="Cloud",
        desc_2=(
            "Increase speed by 5%, decrease atk by 10% and grant hide for 50 turns at the start of battle. You cannot be targeted unless for skills that targets 5 enemies."
            " Hide effect is removed when all allies are hidden."
        ),
        desc_4=(
            "When this hide effect is removed, apply Full Cloud on self, for 12 turns, speed is increased by 100%,"
            " final damage taken is reduced by 40%."
        ),
        desc_jp_2="バトル開始時に速度が5%増加し、攻撃力が10%減少する。また50ターンの間、自身に雲隠状態を付与する。雲隠状態中は、5体の敵を対象とするスキル以外ではターゲットにされない。味方全員が隠れた時、雲隠効果は解除される。",
        desc_jp_4="この雲隠効果が解除された時、自身に「雲満」を付与する。12ターンの間、速度が100%増加し、最終被ダメージが40%減少する。",
    ),
    EqSet(
        name="1987",
        desc_2=(
            "Select the highest one from 3 of your main stats: atk, def, spd. 12% of the selected stat is added to the ally"
            " who has the lowest value of the selected stat."
        ),
        desc_4="Stat bonus increased by 13.55% (total 25.55%).",
        desc_jp_2="自身の主要3ステータス（攻撃力、防御力、速度）の中から最も高いものを選択する。選択したステータスの12%分が、そのステータスの値が最も低い味方に加算される。",
        desc_jp_4="ステータスボーナスが13.55%増加する（合計25.55%）。",
    ),
    EqSet(
        name="7891",
        desc_2=(
            "Select the lowest one from 3 of your main stats: atk, def, spd. 25% of the selected stat is added to the ally"
            " who has the highest value of the selected stat."
        ),
        desc_4="Stat bonus increased by 30.55% (total 55.55%).",
        desc_jp_2="自身の主要3ステータス（攻撃力、防御力、速度）の中から最も低いものを選択する。選択したステータスの25%分が、そのステータスの値が最も高い味方に加算される。",
        desc_jp_4="ステータスボーナスが30.55%増加する（合計55.55%）。",
    ),
    EqSet(
        name="Freight",
        desc_2="Prioritize skill 2 over skill 1 if both are available. Before an action, heal hp by 50% of speed.",
        desc_4="Before an action, for 4 turns, speed is increased by 25%",
        desc_jp_2="両方が使用可能な場合、スキル1よりもスキル2を優先して使用する。行動前にHPを速度の50%分回復する。",
        desc_jp_4="行動前に4ターンの間、速度が25%増加する。",
    ),
    EqSet(
        name="Runic",
        desc_2=(
            "Critical rate is increased by 40%, critical damage is decreased by 20%."
            " When dealing critical damage and critical rate is over 100%, damage is increased by the excess critical rate."
        ),
        desc_4="Critical rate bonus increased by 60%, critical damage decreased by 30%.",
        desc_jp_2="クリティカル率が40%増加し、クリティカルダメージが20%減少する。クリティカルダメージを与える時にクリティカル率が100%を超えている場合、超過したクリティカル率の分だけダメージが増加する。",
        desc_jp_4="クリティカル率ボーナスがさらに60%増加し、クリティカルダメージがさらに30%減少する。",
    ),
    EqSet(
        name="Grassland",
        desc_2=(
            "If you haven't taken action yet in current battle, speed is increased by 60%, final damage taken is reduced by 14%."
            " This effect is removed after taken action."
        ),
        desc_4="Speed bonus increased by 70%, final damage reduction increased by 16%.",
        desc_jp_2="現在のバトルでまだ行動していない場合、速度が60%増加し、最終被ダメージが14%減少する。この効果は行動した後に解除される。",
        desc_jp_4="速度ボーナスがさらに70%増加し、最終被ダメージ軽減が16%増加する。",
    ),
    EqSet(
        name="Tigris",
        desc_2="When targeting multiple enemies, for each enemy that is missing, damage is increased by 40% for that attack or skill.",
        desc_4="Gain additional 50% damage increase.",
        desc_jp_2="複数の敵をターゲットにする時、敵が1体不足しているごとに、その攻撃またはスキルのダメージが40%増加する。",
        desc_jp_4="さらに50%の追加ダメージ増加を得る。",
    ),
    EqSet(
        name="Armygreen",
        desc_2="Crit, Critdmg, Accuracy + 15%, penetration + 5%.",
        desc_4="Stat bonus is doubled.",
        desc_jp_2="クリティカル率、クリティカルダメージ、命中率が15%増加し、貫通率が5%増加する。",
        desc_jp_4="ステータスボーナスが2倍になる。",
    ),
    EqSet(
        name="Armydesert",
        desc_2="Critdef, heal efficiency + 25%, eva + 10%.",
        desc_4="Stat bonus is doubled.",
        desc_jp_2="クリティカル防御、回復効率が25%増加し、回避率が10%増加する。",
        desc_jp_4="ステータスボーナスが2倍になる。",
    ),
]

# Registry: name -> EqSet  (includes "None" as a sentinel with empty descriptions)
EQ_SET_REGISTRY: dict[str, EqSet] = {s.name: s for s in _SETS}
EQ_SET_REGISTRY["None"] = EqSet(name="None", desc_2="", desc_4="", desc_jp_2="", desc_jp_4="")
EQ_SET_REGISTRY["Void"] = EqSet(name="Void", desc_2="", desc_4="", desc_jp_2="", desc_jp_4="")
