import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

r = 2
d = [i for i in range(r)]
q = 256

x = np.sort(np.union1d(np.arange(0, 256) + 0.01, np.arange(0, 256) - 0.01))
y = np.zeros(len(x))

for k, i in enumerate(x):
    for j in d[:]:
        y[k] += (np.sin(np.pi * ((j * q) / r - i)) / np.sin(np.pi * (j / r - i / q))) ** 2
    y[k] = y[k] / (r * q ** 2)

sns.set(style="whitegrid")
plt.figure(figsize=(10, 5))
plt.plot(x, y, color='blue', linewidth=1.5)
plt.title("Plot of x vs y", fontsize=14)
plt.show()
