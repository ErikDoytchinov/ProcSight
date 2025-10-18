import matplotlib.pyplot as plt


def plot_cpu_usage(
    data,
    times,
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
):
    fig, ax = plt.subplots()
    ax.plot(times, [cpu_usage.percent for cpu_usage, _ in data])
    ax.set_ylabel("Cpu Usage (%)")
    ax.set_xlabel("Time (s)")

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)

    if show:
        plt.show()

    plt.close(fig)


def plot_memory_usage(
    data,
    times,
    *,
    show: bool = True,
    save_path: str | None = None,
    dpi: int = 144,
    transparent: bool = False,
):
    fig, ax = plt.subplots()
    ax.plot(times, [memory_usage.rss for _, memory_usage in data])
    ax.set_ylabel("RSS (MB)")
    ax.set_xlabel("Time (s)")

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", transparent=transparent)

    if show:
        plt.show()

    plt.close(fig)
