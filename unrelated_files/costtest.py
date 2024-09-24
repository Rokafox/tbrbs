# Further reduce the base cost and check the results
def level_up_cost_adjusted_fine(level, level_max=1000):
    if level == level_max:
        return 0
    base_cost = 0.01  # Further reduce the base cost
    return int(base_cost * (level ** 1.955))  # Keeping quadratic growth

# Recalculate the total cost from level 1 to 1000
total_cost_adjusted_fine = sum(level_up_cost_adjusted_fine(level) for level in range(1, 1001))
print(total_cost_adjusted_fine) 
