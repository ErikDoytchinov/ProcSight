import matplotlib.pyplot as plt


def plot_cpu_usage(data, times):
    plt.plot(
        times,
        [cpu_usage.percent for cpu_usage, _ in data],
    )
    plt.ylabel("Cpu Usage (%)")
    plt.xlabel("Time (s)")
    plt.show()


def plot_memory_usage(data, times):
    plt.plot(
        times,
        [memory_usage.rss for _, memory_usage in data],
    )
    plt.ylabel("RSS (MB)")
    plt.xlabel("Time (s)")
    plt.show()
