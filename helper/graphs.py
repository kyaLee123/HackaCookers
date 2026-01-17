import matplotlib.pyplot as plt
import numpy as np

# Generates sample data
def series(n=500, start=-0.8, k=0.01, noise_base=0.6, noise_floor=0.05):
    
    x = np.zeros(n)
    x[0] = start

    for t in range(1, n):
        # deterministic drift toward 1
        drift = k * (1 - x[t-1])

        # noise decays over time
        noise_scale = noise_floor + noise_base * np.exp(-t / (n/3))
        noise = np.random.normal(0, noise_scale)

        x[t] = x[t-1] + drift + noise
        x[t] = np.clip(x[t], -1, 1)

    return x

# Geneerates rolling mean
def rollingMean(x, window):
    x = np.asarray(x)
    kernel = np.ones(window) / window
    return np.convolve(x, kernel, mode="same")

y = series()

# Create the plot
plt.plot(rollingMean(y, 50), marker="o")
plt.plot(y, marker="o")
plt.xlabel("Video Number")
plt.ylabel("Rolling Mean")
plt.title("Hi")
plt.show()