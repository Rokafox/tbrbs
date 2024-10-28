# Further reduce the base cost and check the results
def level_up_cost_adjusted_fine(level, level_max=1000):
    if level == level_max:
        return 0
    base_cost = 0.01  # Further reduce the base cost
    return int(base_cost * (level ** 1.985))  # Keeping quadratic growth

# Recalculate the total cost from level 1 to 1000
total_cost_adjusted_fine = sum(level_up_cost_adjusted_fine(level) for level in range(1, 1001))
print(total_cost_adjusted_fine) 


def upgrade_stars_rating_cost(rarity) -> int:
    stars_rating = 0
    stars_rating_max = 15
    self_rarity = rarity
    values = [1.00, 1.10, 1.20, 1.30, 1.40, 1.60]
    rarity_list = ["Common", "Uncommon", "Rare", "Epic", "Unique", "Legendary"]
    rarity_values = {rarity: value for rarity, value in zip(rarity_list, values)}
    rarity_multiplier = rarity_values.get(self_rarity, 1.0)
    
    total_cost = sum(
        int(2000 * (stars + 1) ** 1.90 * rarity_multiplier)
        for stars in range(stars_rating, stars_rating_max)
    )
    
    return total_cost


# Recalculate the total cost from 0 to 15 stars
total_cost_stars_rating = upgrade_stars_rating_cost("Legendary")
print(total_cost_stars_rating)


"""
3015329
3121018
"""