# Turn based RPG battle simulator
## Description
This RPG Battle Simulator is designed to simulate automatic, turn-based battles between characters with diverse skill sets and item effects. In each turn, a character is selected for action based on their speed attribute through a weighted random process. The battle concludes when all members of one party are no longer alive, irrespective of any status effects.
## Features
- Simulate Battles: Automatically run turn-based battles between various characters.
- Calculate Win Rates: Determine the win rate for each character under different conditions.
- Data Analysis: Generate and analyze data on battle outcomes and character performance.
## Installation
```bash
pip install -r requirements.txt
```
## Usage
### Launching the Simulator:
To launch a simple Pygame GUI for the battle simulator, run:
```bash
python battle_simulator.py 
```
### Calculating Winrate:
To calculate the winrate for each character with different item sets and save the data to win_loss_data.csv, use the following command. Replace [sample] with the number of samples you want to run:
```bash
python calculate_winrate.py [sample]
```
### Generating Reports:
If Pandas, Matplotlib, and Seaborn are installed, performance.txt and heatmap.png will be generated in the ./reports directory.