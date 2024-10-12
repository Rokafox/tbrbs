import matplotlib.pyplot as plt
import random

def normal_distribution(min_value, max_value, mean, std):
    while True:
        value = random.normalvariate(mean, std)
        if value >= min_value and value <= max_value:
            return value

data = []
for i in range(6000):
    data.append(normal_distribution(1, 8000, 4000, 1000)) 

plt.figure(figsize=(10, 6))
plt.hist(data, bins=50, alpha=0.7)
plt.title("Normal Distribution (Std = 1000)")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()