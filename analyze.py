import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_report():
    # Load the data from the uploaded CSV file
    file_path = './win_loss_data.csv'
    data = pd.read_csv(file_path)

    # Grouping by character_name to find the average winrate for each character
    character_performance = data.groupby('character_name')['winrate'].mean().sort_values(ascending=False)

    # Grouping by equipment_set to find the average winrate for each equipment set
    equipment_performance = data.groupby('equipment_set')['winrate'].mean().sort_values(ascending=False)
    # Create a text file to document the performance
    with open('./reports/performance.txt', 'w') as file:
        # Write character performance to the file
        file.write("Character Performance:\n")
        file.write(str(character_performance))

        # Write equipment performance to the file
        file.write("\n\nEquipment Performance:\n")
        file.write(str(equipment_performance))
    return data

def generate_heatmap(data):
    # Pivot the table to create a matrix format suitable for a heatmap
    heatmap_data = data.pivot(index='character_name', columns='equipment_set', values='winrate')

    # Create the heatmap
    plt.figure(figsize=(15, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="coolwarm")
    plt.title("Win Rates of Characters with Different Equipment Sets")
    plt.xlabel("Equipment Set")
    plt.ylabel("Character Name")

    # Save the heatmap to a file
    plt.savefig('./reports/heatmap.png')




