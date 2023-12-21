import pandas as pd


# Load the data from the uploaded CSV file
file_path = './win_loss_data.csv'
data = pd.read_csv(file_path)

# Grouping by character_name to find the average winrate for each character
character_performance = data.groupby('character_name')['winrate'].mean().sort_values(ascending=False)

# Grouping by equipment_set to find the average winrate for each equipment set
equipment_performance = data.groupby('equipment_set')['winrate'].mean().sort_values(ascending=False)

print(character_performance)
print(equipment_performance)